# Windows Development Environment Tweaks
# =====================================

Write-Host "Applying Windows development environment tweaks..." -ForegroundColor Green

# Set PowerShell execution policy
try {
    Set-ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
    Write-Host "✅ PowerShell execution policy set to RemoteSigned" -ForegroundColor Green
}
catch {
    Write-Host "❌ Failed to set PowerShell execution policy: $($_.Exception.Message)" -ForegroundColor Red
}

# Enable Developer Mode
try {
    $regPath = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\AppModelUnlock"
    if (!(Test-Path $regPath)) {
        New-Item -Path $regPath -Force | Out-Null
    }
    Set-ItemProperty -Path $regPath -Name "AllowDevelopmentWithoutDevLicense" -Value 1 -Type DWord
    Write-Host "✅ Windows Developer Mode enabled" -ForegroundColor Green
}
catch {
    Write-Host "❌ Failed to enable Developer Mode: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   Note: This may require Administrator privileges" -ForegroundColor Yellow
}

# Enable Windows Subsystem for Linux (WSL) if not already enabled
try {
    $wslFeature = Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux
    if ($wslFeature.State -eq "Disabled") {
        Write-Host "Enabling WSL (requires restart)..." -ForegroundColor Yellow
        Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux -NoRestart
        Write-Host "✅ WSL enabled (restart required)" -ForegroundColor Green
    }
    else {
        Write-Host "✅ WSL already enabled" -ForegroundColor Green
    }
}
catch {
    Write-Host "❌ Failed to check/enable WSL: $($_.Exception.Message)" -ForegroundColor Red
}

# Set Git configuration for Windows
try {
    git config --global core.autocrlf true
    git config --global core.safecrlf false
    Write-Host "✅ Git line ending configuration set for Windows" -ForegroundColor Green
}
catch {
    Write-Host "❌ Failed to configure Git: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`nWindows development tweaks completed!" -ForegroundColor Green
Write-Host "Note: Some changes may require a system restart to take effect." -ForegroundColor Yellow
