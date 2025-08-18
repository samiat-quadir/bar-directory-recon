$ErrorActionPreference="Stop"
Set-Location $PSScriptRoot\..
$y="monitoring\prometheus.yml"
$ip = "100.0.0.0"
try {
  $q = ssh samqu@rog-lucci "powershell -NoProfile tailscale ip -4" 2>$null
  $v4 = $q -split "`r?`n" | ? {$_ -match '^100\.'} | select -f 1
  if ($v4){ $ip=$v4.Trim() }
} catch {}
(Get-Content $y -Raw) -replace '(\d{1,3}\.){3}\d{1,3}:9182',"$ip`:9182" | Set-Content $y -Encoding utf8
docker compose -f monitoring\docker-compose.yml restart prometheus | Out-Null
Write-Host "ALI_TARGET=$ip`:9182"
