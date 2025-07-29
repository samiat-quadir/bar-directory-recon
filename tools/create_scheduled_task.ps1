# Create Scheduled Task for Nightly Checks
# =========================================

Write-Host "Creating scheduled task for nightly checks..." -ForegroundColor Green

try {
    # Define task parameters
    $TaskName = "Bar Directory Recon Nightly Checks"
    $ScriptPath = Join-Path $PSScriptRoot "run_nightly_checks.ps1"
    $WorkingDirectory = $PSScriptRoot

    # Create task action
    $Action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File `"$ScriptPath`"" -WorkingDirectory $WorkingDirectory

    # Create task trigger (daily at 2 AM)
    $Trigger = New-ScheduledTaskTrigger -Daily -At "2:00 AM"

    # Create task settings
    $Settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

    # Create task principal (run as current user)
    $Principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

    # Register the task
    Register-ScheduledTask -TaskName $TaskName -Action $Action -Trigger $Trigger -Settings $Settings -Principal $Principal -Force

    Write-Host "✅ Scheduled task '$TaskName' created successfully" -ForegroundColor Green
    Write-Host "   - Runs daily at 2:00 AM" -ForegroundColor Yellow
    Write-Host "   - Script: $ScriptPath" -ForegroundColor Yellow
    Write-Host "   - Working Directory: $WorkingDirectory" -ForegroundColor Yellow

    # Verify task was created
    $Task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
    if ($Task) {
        Write-Host "✅ Task verification successful" -ForegroundColor Green
        Write-Host "   State: $($Task.State)" -ForegroundColor Yellow
    }
    else {
        Write-Host "❌ Task verification failed" -ForegroundColor Red
    }

}
catch {
    Write-Host "❌ Failed to create scheduled task: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host "`nTo view the scheduled task:" -ForegroundColor Cyan
Write-Host "Get-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Gray

Write-Host "`nTo run the task manually:" -ForegroundColor Cyan
Write-Host "Start-ScheduledTask -TaskName '$TaskName'" -ForegroundColor Gray

Write-Host "`nTo view task history:" -ForegroundColor Cyan
Write-Host "Get-WinEvent -LogName 'Microsoft-Windows-TaskScheduler/Operational' | Where-Object {`$_.Message -like '*$TaskName*'}" -ForegroundColor Gray
