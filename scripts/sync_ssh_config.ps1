# Idempotently ensure SSH config host entries with keepalive and compression
$ConfigPath = "$env:USERPROFILE/.ssh/config"
$Hosts = @(
    @{
        Name = 'mothership'; HostName = '100.124.245.90'; User = 'samqu'
    },
    @{
        Name = 'rog-lucci'; HostName = '100.89.12.61'; User = 'samqu'
    }
)
$keyPath = "$env:USERPROFILE/.ssh/id_ed25519_clear"
if (!(Test-Path $ConfigPath)) { New-Item -ItemType File -Path $ConfigPath -Force | Out-Null }
$content = Get-Content $ConfigPath -Raw

function Build-Block($h) {
    @"
Host $($h.Name)
    HostName $($h.HostName)
    User $($h.User)
    IdentityFile $keyPath
    IdentitiesOnly yes
    ServerAliveInterval 30
    ServerAliveCountMax 4
    ConnectTimeout 10
    Compression yes
"@
}

$updated = $false
foreach ($h in $Hosts) {
    if ($content -notmatch "Host\s+$($h.Name)(?s).*?Compression yes") {
        $block = Build-Block $h
        # Remove existing block for host (simple approach)
        $content = ($content -split "(?m)^Host ") | ForEach-Object {
            if ($_ -match "^$($h.Name)\b") { return $null } else { return $_ }
        } | Where-Object { $_ } | ForEach-Object { if ($_ -notmatch '^Host ') { 'Host ' + $_ } else { $_ } } | Out-String
        $content = ($content.Trim() + "`n" + $block.Trim() + "`n")
        $updated = $true
    }
}
if ($updated) { Set-Content -Path $ConfigPath -Value $content -Encoding utf8; Write-Host "[UPDATED] SSH config entries applied." } else { Write-Host "[OK] SSH config already up to date." }
