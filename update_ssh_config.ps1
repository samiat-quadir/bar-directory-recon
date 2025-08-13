$configPath = Join-Path $env:USERPROFILE ".ssh\config"
if (!(Test-Path (Split-Path $configPath))) { New-Item -ItemType Directory -Force -Path (Split-Path $configPath) | Out-Null }
if (Test-Path $configPath) { $existing = Get-Content $configPath -Raw } else { $existing = "" }
$block = @"
Host mothership
    HostName 100.124.245.90
    User samqu
    IdentityFile C:/Users/samqu/.ssh/id_ed25519_clear
    IdentitiesOnly yes
    ServerAliveInterval 30
    ServerAliveCountMax 4
    Compression yes

Host rog-lucci
    HostName 100.89.12.61
    User samqu
    IdentityFile C:/Users/samqu/.ssh/id_ed25519_clear
    IdentitiesOnly yes
    ServerAliveInterval 30
    ServerAliveCountMax 4
    Compression yes
"@

# Remove old Host entries for these hosts if present
$clean = ($existing -split "`n`n") | Where-Object { $_ -notmatch "Host mothership" -and $_ -notmatch "Host rog-lucci" }
$clean += $block.Trim()
$final = ($clean -join "`n`n").Trim() + "`n"
Set-Content -Path $configPath -Value $final -Encoding UTF8
Write-Host "Updated SSH config at $configPath"
