# Update SSH config with Tailscale IPs and keepalive settings
$sshConfigPath = "$env:USERPROFILE\.ssh\config"
$configContent = @"
Host mothership
    HostName 100.124.245.90
    User samqu
    IdentityFile C:/Users/samqu/.ssh/id_ed25519_clear
    IdentitiesOnly yes
    ServerAliveInterval 30
    ServerAliveCountMax 4
    ConnectTimeout 10
    Compression yes

Host rog-lucci
    HostName 100.89.12.61
    User samqu
    IdentityFile C:/Users/samqu/.ssh/id_ed25519_clear
    IdentitiesOnly yes
    ServerAliveInterval 30
    ServerAliveCountMax 4
    ConnectTimeout 10
    Compression yes
"@

# Ensure SSH directory exists
$sshDir = Split-Path $sshConfigPath -Parent
if (-not (Test-Path $sshDir)) {
    New-Item -ItemType Directory -Path $sshDir -Force | Out-Null
}

# Write config file
Set-Content -Path $sshConfigPath -Value $configContent -Encoding UTF8
Write-Host "SSH config updated at: $sshConfigPath"
