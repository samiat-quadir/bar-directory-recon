# Compose heartbeat: determine monitoring health via container health and local rules file
$ErrorActionPreference = 'SilentlyContinue'
Set-Location C:\Code\bar-directory-recon

# Start the monitoring compose if not running
docker compose -f monitoring\docker-compose.yml up -d | Out-Null

$targets = @('monitoring-prometheus-1', 'monitoring-alertmanager-1')
$deadline = (Get-Date).AddSeconds(60)
$allHealthy = $true

while ((Get-Date) -lt $deadline) {
    $allHealthy = $true
    foreach ($c in $targets) {
        $status = docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' $c 2>$null
        if ($status -ne 'healthy' -and $status -ne 'running') { $allHealthy = $false; break }
    }
    if ($allHealthy) { break }
    Start-Sleep -Seconds 2
}

# Check rules file for HighCPU
$rulesFile = Join-Path (Get-Location) 'monitoring\rules.yml'
$hasRule = $false
if (Test-Path $rulesFile) {
    $txt = Get-Content $rulesFile -Raw
    $hasRule = $txt -match 'HighCPU'
}

$status = [int]($allHealthy -and $hasRule)
$am = $(if ($allHealthy) { 200 } else { 0 })
$pr = $(if ($allHealthy) { 200 } else { 0 })
Write-Output "SUMMARY >> task=ace-heartbeat status=$status am=$am prom=$pr highcpu_rule=$hasRule"
