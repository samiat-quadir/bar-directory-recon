# ScheduleDailyCrossDeviceHealthCheck.ps1
# Schedules a daily Windows Task Scheduler job to run Test-CrossDeviceCompatibility.ps1 at 8 AM

$taskName = "DailyCrossDeviceHealthCheck"
$scriptPath = Join-Path $PSScriptRoot "..\tools\Test-CrossDeviceCompatibility.ps1"
$logPath = Join-Path $PSScriptRoot "..\logs\cross_device_sync.log"

# Build the action to run PowerShell with the script
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`""

# Set the trigger for daily at 8 AM
$trigger = New-ScheduledTaskTrigger -Daily -At 8:00AM

# Set principal to run with highest privileges
$principal = New-ScheduledTaskPrincipal -UserId "NT AUTHORITY\\SYSTEM" -LogonType ServiceAccount -RunLevel Highest

# Register the scheduled task
try {
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal -Description "Run cross-device compatibility health check daily at 8 AM" -Force
    Add-Content -Path $logPath -Value "[$(Get-Date -Format o)] [SUCCESS] Scheduled $taskName to run Test-CrossDeviceCompatibility.ps1 daily at 8 AM."
    Write-Host "[SUCCESS] Scheduled $taskName to run Test-CrossDeviceCompatibility.ps1 daily at 8 AM."
}
catch {
    Add-Content -Path $logPath -Value "[$(Get-Date -Format o)] [ERROR] Failed to schedule $taskName: $($_.Exception.Message)"
    Write-Host "[ERROR] Failed to schedule $taskName: $($_.Exception.Message)"
}
