*** DELETE FILE
Param()
$ErrorActionPreference = 'Stop'
Set-Location -Path "C:\Code\bar-directory-recon"

try {
    $raw = gh codespace list --json name, repository, state, lastUsedAt --limit 50
}
catch {
    Write-Output 'NO_CODESPACES'
    exit 0
}

if (-not $raw) { Write-Output 'NO_CODESPACES'; exit 0 }

try {
    $arr = $raw | ConvertFrom-Json
}
catch {
    Write-Output 'PARSE_ERROR'
    exit 0
}

$sel = $arr | Where-Object { $_.repository -and ($_.repository -like '*bar-directory-recon*') -and $_.state -eq 'Available' } | Sort-Object { [datetime]$_.lastUsedAt } -Descending | Select-Object -First 1
if (-not $sel) { Write-Output 'NO_AVAILABLE'; exit 0 }

# Output the codespace name and displayName and lastUsedAt as JSON
$out = @{ name = $sel.name; displayName = $sel.displayName; lastUsedAt = $sel.lastUsedAt }
($out | ConvertTo-Json -Compress) | Write-Output
