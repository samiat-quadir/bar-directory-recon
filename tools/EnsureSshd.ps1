# EnsureSshd.ps1 - Ensure SSH daemon is running with proper configuration
# Mirrors Ali's implementation for cross-device parity

[CmdletBinding()]
param(
    [switch]$VerboseOutput
)

$ErrorActionPreference = "Stop"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] [$Level] $Message"
}

try {
    Write-Log "Starting SSH daemon configuration..."

    # Check if OpenSSH Server feature is installed
    $sshFeature = Get-WindowsCapability -Online | Where-Object Name -like "OpenSSH.Server*"
    if ($sshFeature.State -ne "Installed") {
        Write-Log "Installing OpenSSH Server feature..."
        Add-WindowsCapability -Online -Name OpenSSH.Server~~~~0.0.1.0
        Write-Log "OpenSSH Server feature installed"
    }
    else {
        Write-Log "OpenSSH Server feature already installed"
    }

    # Configure and start SSH service
    Write-Log "Configuring SSH service..."
    Set-Service -Name sshd -StartupType Automatic
    Start-Service sshd

    # Verify service status
    $service = Get-Service sshd
    if ($service.Status -eq "Running") {
        Write-Log "SSH service is running (Status: $($service.Status), StartType: $($service.StartType))"
    }
    else {
        throw "SSH service failed to start. Status: $($service.Status)"
    }

    # Configure firewall rule
    Write-Log "Configuring firewall rule..."
    $firewallRule = Get-NetFirewallRule -Name "OpenSSH-Server-In-TCP" -ErrorAction SilentlyContinue
    if ($firewallRule) {
        Set-NetFirewallRule -Name "OpenSSH-Server-In-TCP" -Enabled True -Profile Domain, Private, Public
        Write-Log "Firewall rule updated: OpenSSH-Server-In-TCP"
    }
    else {
        New-NetFirewallRule -DisplayName "OpenSSH Server (sshd)" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 22 -Name "OpenSSH-Server-In-TCP"
        Write-Log "Firewall rule created: OpenSSH-Server-In-TCP"
    }

    # Test connectivity
    Write-Log "Testing SSH connectivity..."
    $testResult = Test-NetConnection -ComputerName localhost -Port 22 -WarningAction SilentlyContinue
    if ($testResult.TcpTestSucceeded) {
        Write-Log "SSH connectivity test successful"
    }
    else {
        Write-Log "SSH connectivity test failed" -Level "WARNING"
    }

    # Check SSH configuration
    $sshdConfigPath = "C:\ProgramData\ssh\sshd_config"
    if (Test-Path $sshdConfigPath) {
        Write-Log "SSH configuration file exists: $sshdConfigPath"
        if ($VerboseOutput) {
            $config = Get-Content $sshdConfigPath | Where-Object { $_ -match "^[^#]" -and $_.Trim() -ne "" }
            Write-Log "Active SSH configuration lines:"
            $config | ForEach-Object { Write-Log "  $_" }
        }
    }

    Write-Log "SSH daemon configuration completed successfully" -Level "SUCCESS"
    exit 0

}
catch {
    Write-Log "Error configuring SSH daemon: $($_.Exception.Message)" -Level "ERROR"
    if ($VerboseOutput) {
        Write-Log "Full error details: $($_ | Out-String)" -Level "ERROR"
    }
    exit 1
}
