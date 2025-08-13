# PowerShell compatibility script for firewall and SSH setup
# Works with both older PowerShell versions and newer ones

Write-Host "Setting up SSH service and firewall..."

# Start SSH service
try {
    Set-Service sshd -StartupType Automatic
    Start-Service sshd
    Write-Host "SSH service started successfully"
}
catch {
    Write-Warning "Failed to configure SSH service: $_"
}

# Configure firewall using compatible method
$firewallConfigured = $false

# Try modern PowerShell cmdlets first
try {
    $rule = Get-NetFirewallRule -Name "OpenSSH-Server-In-TCP" -ErrorAction SilentlyContinue
    if ($rule) {
        Set-NetFirewallRule -Name "OpenSSH-Server-In-TCP" -Enabled True -Profile Domain, Private, Public
        Write-Host "Updated existing OpenSSH firewall rule"
    }
    else {
        New-NetFirewallRule -DisplayName "OpenSSH Server (sshd)" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 22
        Write-Host "Created new OpenSSH firewall rule"
    }
    $firewallConfigured = $true
}
catch {
    Write-Host "NetFirewall cmdlets not available, trying netsh..."
}

# Fallback to netsh if modern cmdlets not available
if (-not $firewallConfigured) {
    try {
        $result = netsh advfirewall firewall show rule name="OpenSSH Server (sshd)" 2>&1
        if ($LASTEXITCODE -eq 0) {
            netsh advfirewall firewall set rule name="OpenSSH Server (sshd)" new enable=yes
            Write-Host "Updated existing firewall rule using netsh"
        }
        else {
            netsh advfirewall firewall add rule name="OpenSSH Server (sshd)" dir=in action=allow protocol=TCP localport=22
            Write-Host "Created firewall rule using netsh"
        }
        $firewallConfigured = $true
    }
    catch {
        Write-Warning "Failed to configure firewall: $_"
    }
}

# Test connection using compatible method
try {
    $tcpClient = New-Object System.Net.Sockets.TcpClient
    $tcpClient.Connect("localhost", 22)
    $tcpClient.Close()
    Write-Host "SSH port 22 is accessible on localhost"
}
catch {
    Write-Warning "Cannot connect to SSH port 22: $_"
}

Write-Host "Setup complete. Check shell integration with: echo `$env:VSCODE_SHELL_INTEGRATION"
