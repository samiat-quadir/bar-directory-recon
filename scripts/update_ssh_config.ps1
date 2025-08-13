<#
Updates user SSH config with provided Tailscale host definitions (idempotent merge).
#>
$ConfigPath = Join-Path $env:USERPROFILE ".ssh\config"
$Block = @'
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
'@

if (-not (Test-Path (Split-Path $ConfigPath))) { New-Item -ItemType Directory -Path (Split-Path $ConfigPath) | Out-Null }
if (-not (Test-Path $ConfigPath)) { New-Item -ItemType File -Path $ConfigPath | Out-Null }

$Content = Get-Content $ConfigPath -Raw
$Updated = $false

foreach ($HostName in @('mothership', 'rog-lucci')) {
    if ($Content -notmatch "Host\s+$HostName(\r?\n|$)") { $Updated = $true }
    else {
        # Remove existing block for clean replacement
        $Pattern = "Host\s+$HostName(?:\r?\n(?:\s+.*)?)*"
        $Content = [regex]::Replace($Content, $Pattern, '', 'IgnoreCase')
        $Updated = $true
    }
}

if ($Updated) {
    # Append cleaned content and new block
    $Clean = ($Content.Trim() + "`n`n").Trim()
    Set-Content -Path $ConfigPath -Value ($Clean + $Block) -Encoding ascii
    Write-Host "[SSH-CONFIG] Updated host blocks written to $ConfigPath"
}
else {
    Write-Host "[SSH-CONFIG] Host blocks already present; no changes"
}
