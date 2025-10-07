# Ensures monitoring docker-compose has restart policies and brings the stack up
$ErrorActionPreference = 'SilentlyContinue'
Set-Location C:\Code\bar-directory-recon

function Ensure-RestartPolicy($file) {
    if (-Not (Test-Path $file)) { return }
    $dc = Get-Content $file -Raw
    $changed = $false
    if ($dc -notmatch "restart:\s*unless-stopped") {
        $dc = $dc -replace "image:\s*(prom/prometheus[:\w\.-]*)", "$&`n    restart: unless-stopped"
        $dc = $dc -replace "image:\s*(prom/alertmanager[:\w\.-]*)", "$&`n    restart: unless-stopped"
        Set-Content -Path $file -Value $dc -Encoding utf8
        $changed = $true
    }
    return $changed
}

# Check both docker-compose files if present
$dc1 = Join-Path (Get-Location) "docker-compose.yml"
$dc2 = Join-Path (Get-Location) "monitoring\docker-compose.yml"
$changed1 = Ensure-RestartPolicy $dc1
$changed2 = Ensure-RestartPolicy $dc2

# Bring stack up
Write-Output "Bringing up docker compose (root docker-compose.yml)"
docker compose up -d
Start-Sleep -Seconds 2

# Probe endpoints
$am = 0
$pr = 0
try {
    $amResp = Invoke-RestMethod -Uri 'http://localhost:9093/-/ready' -Method Get -TimeoutSec 3
    if ($LASTEXITCODE -eq 0) { $am = 200 }
}
catch { $am = 0 }
try {
    $prResp = Invoke-RestMethod -Uri 'http://localhost:9090/-/ready' -Method Get -TimeoutSec 3
    if ($LASTEXITCODE -eq 0) { $pr = 200 }
}
catch { $pr = 0 }

# Check for HighCPU rule
$hasRule = $false
try {
    $rules = Invoke-RestMethod -Uri 'http://localhost:9090/api/v1/rules' -Method Get -TimeoutSec 3 | Out-String
    $hasRule = $rules -match 'HighCPU'
}
catch { $hasRule = $false }

$status = ([int]($am -eq 200 -and $pr -eq 200 -and $hasRule))
Write-Output "SUMMARY >> task=ace-heartbeat status=$status am=$am prom=$pr highcpu_rule=$hasRule"
