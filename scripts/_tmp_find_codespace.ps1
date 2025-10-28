$list = gh codespace list --json name,displayName,repository,state,createdAt,lastUsedAt,machineName | ConvertFrom-Json
$sel = $list | Where-Object { $_.displayName -like 'bdr-ace-smoke*' -and $_.repository -like '*bar-directory-recon*' } | Sort-Object createdAt -Descending | Select-Object -First 1
if (-not $sel) { Write-Output 'NO_MATCH'; exit 0 }
$sel | ConvertTo-Json -Compress | Write-Output
