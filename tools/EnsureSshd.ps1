[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Ensure OpenSSH Server service
Set-Service sshd -StartupType Automatic -ErrorAction SilentlyContinue
Start-Service sshd -ErrorAction SilentlyContinue

# Enable built-in firewall rule or create one
$rule = Get-NetFirewallRule -Name "OpenSSH-Server-In-TCP" -ErrorAction SilentlyContinue
if ($rule) {
    Set-NetFirewallRule -Name "OpenSSH-Server-In-TCP" -Enabled True -Profile Domain, Private, Public | Out-Null
}
else {
    New-NetFirewallRule -DisplayName "OpenSSH Server (sshd)" -Direction Inbound -Action Allow -Protocol TCP -LocalPort 22 | Out-Null
}

$tcp = Test-NetConnection -ComputerName localhost -Port 22
if (-not $tcp.TcpTestSucceeded) { Write-Error "Port 22 not reachable locally."; exit 1 }
Write-Host "sshd + firewall OK"
