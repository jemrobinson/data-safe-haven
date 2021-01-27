param(
    [Parameter(Position = 0, Mandatory = $true, HelpMessage = "Enter SRE config ID. This will be the concatenation of <SHM ID> and <SRE ID> (eg. 'testasandbox' for SRE 'sandbox' in SHM 'testa')")]
    [string]$configId
)

Import-Module Az -ErrorAction Stop
Import-Module $PSScriptRoot/../../common/Configuration -Force -ErrorAction Stop
Import-Module $PSScriptRoot/../../common/Deployments -Force -ErrorAction Stop
Import-Module $PSScriptRoot/../../common/Logging -Force -ErrorAction Stop
Import-Module $PSScriptRoot/../../common/Networking -Force -ErrorAction Stop
Import-Module $PSScriptRoot/../../common/Security -Force -ErrorAction Stop


# Get config and original context before changing subscription
# ------------------------------------------------------------
$config = Get-SreConfig $configId
$originalContext = Get-AzContext
$null = Set-AzContext -SubscriptionId $config.sre.subscriptionName -ErrorAction Stop


# Create secrets resource group if it does not exist
# --------------------------------------------------
$null = Deploy-ResourceGroup -Name $config.sre.keyVault.rg -Location $config.sre.location


# Ensure the Key Vault exists
# ---------------------------
$null = Deploy-KeyVault -Name $config.sre.keyVault.name -ResourceGroupName $config.sre.keyVault.rg -Location $config.sre.location
Set-KeyVaultPermissions -Name $config.sre.keyVault.name -GroupName $config.shm.azureAdminGroupName
Set-AzKeyVaultAccessPolicy -VaultName $config.sre.keyVault.name -ResourceGroupName $config.sre.keyVault.rg -EnabledForDeployment


# Ensure that secrets exist in the Key Vault
# -----------------------------------------
Add-LogMessage -Level Info "Ensuring that secrets exist in Key Vault '$($config.sre.keyVault.name)'..."
# :: Admin usernames
try {
    $null = Resolve-KeyVaultSecret -VaultName $config.sre.keyVault.name -SecretName $config.sre.keyVault.secretNames.adminUsername -DefaultValue "sre$($config.sre.id)admin".ToLower() -AsPlaintext
    Add-LogMessage -Level Success "Ensured that SRE admin usernames exist"
} catch {
    Add-LogMessage -Level Fatal "Failed to ensure that SRE admin usernames exist!"
}
# :: VM admin passwords
try {
    $null = Resolve-KeyVaultSecret -VaultName $config.sre.keyVault.name -SecretName $config.sre.dsvm.adminPasswordSecretName -DefaultLength 20 -AsPlaintext
    $null = Resolve-KeyVaultSecret -VaultName $config.sre.keyVault.name -SecretName $config.sre.rds.gateway.adminPasswordSecretName -DefaultLength 20 -AsPlaintext
    $null = Resolve-KeyVaultSecret -VaultName $config.sre.keyVault.name -SecretName $config.sre.rds.appSessionHost.adminPasswordSecretName -DefaultLength 20 -AsPlaintext
    $null = Resolve-KeyVaultSecret -VaultName $config.sre.keyVault.name -SecretName $config.sre.webapps.gitlab.adminPasswordSecretName -DefaultLength 20 -AsPlaintext
    $null = Resolve-KeyVaultSecret -VaultName $config.sre.keyVault.name -SecretName $config.sre.webapps.hackmd.adminPasswordSecretName -DefaultLength 20 -AsPlaintext
    Add-LogMessage -Level Success "Ensured that SRE VM admin passwords exist"
} catch {
    Add-LogMessage -Level Fatal "Failed to ensure that SRE VM admin passwords exist!"
}
# :: Databases
try {
    foreach ($keyName in $config.sre.databases.Keys) {
        if ($config.sre.databases[$keyName] -isnot [System.Collections.IDictionary]) { continue }
        $dbAdminUsername = ($keyName -eq "dbpostgresql") ? "postgres" : "sre$($config.sre.id)dbadmin".ToLower() # The postgres admin username is hardcoded as 'postgres' but we save it to the keyvault to ensure a consistent record structure
        $null = Resolve-KeyVaultSecret -VaultName $config.sre.keyVault.name -SecretName $config.sre.databases[$keyName].adminPasswordSecretName -DefaultLength 20 -AsPlaintext
        $null = Resolve-KeyVaultSecret -VaultName $config.sre.keyVault.name -SecretName $config.sre.databases[$keyName].dbAdminUsernameSecretName $dbAdminUsername -AsPlaintext
        $null = Resolve-KeyVaultSecret -VaultName $config.sre.keyVault.name -SecretName $config.sre.databases[$keyName].dbAdminPasswordSecretName -DefaultLength 20 -AsPlaintext
    }
    Add-LogMessage -Level Success "Ensured that SRE database secrets exist"
} catch {
    Add-LogMessage -Level Fatal "Failed to ensure that SRE database secrets exist!"
}
# :: Other secrets
try {
    $null = Resolve-KeyVaultSecret -VaultName $config.sre.keyVault.name -SecretName $config.sre.webapps.gitlab.rootPasswordSecretName -DefaultLength 20 -AsPlaintext
    $null = Resolve-KeyVaultSecret -VaultName $config.sre.keyVault.name -SecretName $config.sre.keyVault.secretNames.npsSecret -DefaultLength 12 -AsPlaintext
    Add-LogMessage -Level Success "Ensured that other SRE secrets exist"
} catch {
    Add-LogMessage -Level Fatal "Failed to ensure that other SRE secrets exist!"
}


# Tier-2 and above need to register service users with the SHM
# ------------------------------------------------------------
if (@(2, 3, 4).Contains([int]$config.sre.tier)) {
    # Retrieve passwords from the Key Vault
    # -------------------------------------
    Add-LogMessage -Level Info "Loading secrets for SRE users and groups..."
    # Load SRE groups
    $groups = $config.sre.domain.securityGroups
    # Load SRE service users
    $serviceUsers = $config.sre.users.serviceAccounts
    foreach ($user in $serviceUsers.Keys) {
        $serviceUsers[$user]["password"] = Resolve-KeyVaultSecret -VaultName $config.sre.keyVault.name -SecretName $serviceUsers[$user]["passwordSecretName"] -DefaultLength 20 -AsPlaintext
    }

    # Add SRE users and groups to SHM
    # -------------------------------
    Add-LogMessage -Level Info "[ ] Adding SRE users and groups to SHM..."
    $null = Set-AzContext -Subscription $config.shm.subscriptionName -ErrorAction Stop
    $scriptPath = Join-Path $PSScriptRoot ".." "remote" "configure_shm_dc" "scripts" "Create_New_SRE_User_Service_Accounts_Remote.ps1"
    $params = @{
        shmSystemAdministratorSgName = "`"$($config.shm.domain.securityGroups.serverAdmins.name)`""
        groupsB64                    = [Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes(($groups | ConvertTo-Json)))
        serviceUsersB64              = [Convert]::ToBase64String([System.Text.Encoding]::Unicode.GetBytes(($serviceUsers | ConvertTo-Json)))
        securityOuPath               = "`"$($config.shm.domain.ous.securityGroups.path)`""
        serviceOuPath                = "`"$($config.shm.domain.ous.serviceAccounts.path)`""
    }
    $null = Invoke-RemoteScript -Shell "PowerShell" -ScriptPath $scriptPath -VMName $config.shm.dc.vmName -ResourceGroupName $config.shm.dc.rg -Parameter $params
    $null = Set-AzContext -SubscriptionId $config.sre.subscriptionName -ErrorAction Stop
}


# Switch back to original subscription
# ------------------------------------
$null = Set-AzContext -Context $originalContext -ErrorAction Stop