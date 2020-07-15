param(
    [Parameter(Mandatory = $true, HelpMessage = "Enter SHM ID")]
    [string]$shmId,
    [Parameter(Mandatory = $true, HelpMessage = "Enter VM Size for all VMs")]
    [ValidateSet("Tiny","Small")]
    [string]$Size
)

Import-Module Az
Import-Module $PSScriptRoot/../common/Configuration.psm1 -Force
Import-Module $PSScriptRoot/../common/Deployments.psm1 -Force
Import-Module $PSScriptRoot/../common/Logging.psm1 -Force


# Get config and original context before changing subscription
# ------------------------------------------------------------
$config = Get-ShmFullConfig $shmId
$originalContext = Get-AzContext
$null = Set-AzContext -SubscriptionId $config.subscriptionName


$vmsByRg = Get-ShmOrSreVMsByResourceGroup -ResourceGroupPrefix $config.rgPrefix

if($Size -eq "Tiny") {
    $vmSize = "Standard_B2ms"
} elseif ($Size -eq "Small") {
    $vmSize = "Standard_D2_v3"
}

foreach($key in $vmsByRg.Keys) {
    $rgVms = $vmsByRg[$key]
    $rgName = $rgVms[0].ResourceGroupName
    Add-LogMessage -Level Info "Ensuring VMs in resource group '$rgName' are resized to '$vmSize'..."
    foreach($vm in $rgVms) {
        if($vm.HardwareProfile.VmSize -eq $vmSize) {
            Add-LogMessage -Level InfoSuccess "VM '$($VM.Name)' is already size '$vmSize'."
        } else {
            $vmStatuses = (Get-AzVM -Name $vm.Name -ResourceGroupName $vm.ResourceGroupName -Status).Statuses.Code
            if($vmStatuses -contains "ProvisioningState/succeeded") {
                $vm.HardwareProfile.VmSize = $vmSize
                $result = Update-AzVM -VM $vm -ResourceGroupName $vm.ResourceGroupName -NoWait
                if($result.IsSuccessStatusCode) {
                    Add-LogMessage -Level Success "Resize request to '$vmSize' accepted for VM '$($vm.Name)'.'"
                } else {
                    Add-LogMessage -Level Fatal "Unexpected status '$($result.StatusCode) ($($result.ReasonPhrase))' encountered when requesting resize of VM '$($vm.Name)' to '$vmSize').'"
                }
            } else {
                Add-LogMessage -Level Warning "VM '$($vm.Name)' not in supported status: $vmStatus. No asction taken."
            }
        }
    }
}


# Switch back to original subscription
# ------------------------------------
$null = Set-AzContext -Context $originalContext
