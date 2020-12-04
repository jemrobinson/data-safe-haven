param(
    [Parameter(Position = 0, Mandatory = $true, HelpMessage = "Enter SRE config ID. This will be the concatenation of <SHM ID> and <SRE ID> (eg. 'testasandbox' for SRE 'sandbox' in SHM 'testa')")]
    [string]$configId
)

Import-Module Az -ErrorAction Stop
Import-Module $PSScriptRoot/../../common/Configuration -Force -ErrorAction Stop
Import-Module $PSScriptRoot/../../common/Deployments -Force -ErrorAction Stop
Import-Module $PSScriptRoot/../../common/Logging -Force -ErrorAction Stop
Import-Module $PSScriptRoot/../../common/Networking -Force -ErrorAction Stop
Import-Module $PSScriptRoot/../../common/Templates -Force -ErrorAction Stop


# Get config and original context before changing subscription
# ------------------------------------------------------------
$config = Get-SreConfig $configId
$originalContext = Get-AzContext
$null = Set-AzContext -SubscriptionId $config.sre.subscriptionName -ErrorAction Stop


# Create VNet resource group if it does not exist
# -----------------------------------------------
$null = Deploy-ResourceGroup -Name $config.sre.network.vnet.rg -Location $config.sre.location


# Create VNet and subnets
# -----------------------
$vnet = Deploy-VirtualNetwork -Name $config.sre.network.vnet.name -ResourceGroupName $config.sre.network.vnet.rg -AddressPrefix $config.sre.network.vnet.cidr -Location $config.sre.location -DnsServer $config.shm.dc.ip, $config.shm.dcb.ip
$computeSubnet = Deploy-Subnet -Name $config.sre.network.vnet.subnets.compute.name -VirtualNetwork $vnet -AddressPrefix $config.sre.network.vnet.subnets.compute.cidr
$null = Deploy-Subnet -Name $config.sre.network.vnet.subnets.data.name -VirtualNetwork $vnet -AddressPrefix $config.sre.network.vnet.subnets.data.cidr
$databasesSubnet = Deploy-Subnet -Name $config.sre.network.vnet.subnets.databases.name -VirtualNetwork $vnet -AddressPrefix $config.sre.network.vnet.subnets.databases.cidr
$deploymentSubnet = Deploy-Subnet -Name $config.sre.network.vnet.subnets.deployment.name -VirtualNetwork $vnet -AddressPrefix $config.sre.network.vnet.subnets.deployment.cidr
$null = Deploy-Subnet -Name $config.sre.network.vnet.subnets.identity.name -VirtualNetwork $vnet -AddressPrefix $config.sre.network.vnet.subnets.identity.cidr
$null = Deploy-Subnet -Name $config.sre.network.vnet.subnets.rds.name -VirtualNetwork $vnet -AddressPrefix $config.sre.network.vnet.subnets.rds.cidr


# Peer repository vnet to SHM vnet
# --------------------------------
Set-VnetPeering -Vnet1Name $config.sre.network.vnet.name `
                -Vnet1ResourceGroup $config.sre.network.vnet.rg `
                -Vnet1SubscriptionName $config.sre.subscriptionName `
                -Vnet2Name $config.shm.network.vnet.name `
                -Vnet2ResourceGroup $config.shm.network.vnet.rg `
                -Vnet2SubscriptionName $config.shm.subscriptionName `
                -AllowRemoteGatewayFromVNet 2


# Ensure that compute NSG exists with correct rules and attach it to the compute subnet
# -------------------------------------------------------------------------------------
$computeNsg = Deploy-NetworkSecurityGroup -Name $config.sre.network.vnet.subnets.compute.nsg.name -ResourceGroupName $config.sre.network.vnet.rg -Location $config.sre.location
$rules = Get-JsonFromMustacheTemplate -TemplatePath (Join-Path $PSScriptRoot ".." "network_rules" $config.sre.network.vnet.subnets.compute.nsg.rules) -ArrayJoiner '"' -Parameters $config -AsHashtable
$null = Set-NetworkSecurityGroupRules -NetworkSecurityGroup $computeNsg -Rules $rules
$computeSubnet = Set-SubnetNetworkSecurityGroup -Subnet $computeSubnet -NetworkSecurityGroup $computeNsg


# Ensure that database NSG exists with correct rules and attach it to the deployment subnet
# -----------------------------------------------------------------------------------------
$databasesNsg = Deploy-NetworkSecurityGroup -Name $config.sre.network.vnet.subnets.databases.nsg.name -ResourceGroupName $config.sre.network.vnet.rg -Location $config.sre.location
$rules = Get-JsonFromMustacheTemplate -TemplatePath (Join-Path $PSScriptRoot ".." "network_rules" $config.sre.network.vnet.subnets.databases.nsg.rules) -ArrayJoiner '"' -Parameters $config -AsHashtable
$null = Set-NetworkSecurityGroupRules -NetworkSecurityGroup $databasesNsg -Rules $rules
$databasesSubnet = Set-SubnetNetworkSecurityGroup -Subnet $databasesSubnet -NetworkSecurityGroup $databasesNsg


# Ensure that deployment NSG exists with correct rules and attach it to the deployment subnet
# -------------------------------------------------------------------------------------------
$deploymentNsg = Deploy-NetworkSecurityGroup -Name $config.sre.network.vnet.subnets.deployment.nsg.name -ResourceGroupName $config.sre.network.vnet.rg -Location $config.sre.location
$rules = Get-JsonFromMustacheTemplate -TemplatePath (Join-Path $PSScriptRoot ".." "network_rules" $config.sre.network.vnet.subnets.deployment.nsg.rules) -ArrayJoiner '"' -Parameters $config -AsHashtable
$null = Set-NetworkSecurityGroupRules -NetworkSecurityGroup $deploymentNsg -Rules $rules
$deploymentSubnet = Set-SubnetNetworkSecurityGroup -Subnet $deploymentSubnet -NetworkSecurityGroup $deploymentNsg


# Ensure that gateway NSG exists with correct rules
# -------------------------------------------------
$gatewayNsg = Deploy-NetworkSecurityGroup -Name $config.sre.rds.gateway.nsg.name -ResourceGroupName $config.sre.network.vnet.rg -Location $config.sre.location
$rules = Get-JsonFromMustacheTemplate -TemplatePath (Join-Path $PSScriptRoot ".." "network_rules" $config.sre.rds.gateway.nsg.rules) -ArrayJoiner '"' -Parameters $config -AsHashtable
$null = Set-NetworkSecurityGroupRules -NetworkSecurityGroup $gatewayNsg -Rules $rules


# Ensure that session host NSG exists with correct rules
# ------------------------=-----------------------------
$sessionHostNsg = Deploy-NetworkSecurityGroup -Name $config.sre.rds.appSessionHost.nsg.name -ResourceGroupName $config.sre.network.vnet.rg -Location $config.sre.location
$rules = Get-JsonFromMustacheTemplate -TemplatePath (Join-Path $PSScriptRoot ".." "network_rules" $config.sre.rds.appSessionHost.nsg.rules) -ArrayJoiner '"' -Parameters $config -AsHashtable
$null = Set-NetworkSecurityGroupRules -NetworkSecurityGroup $sessionHostNsg -Rules $rules


# Switch back to original subscription
# ------------------------------------
$null = Set-AzContext -Context $originalContext -ErrorAction Stop