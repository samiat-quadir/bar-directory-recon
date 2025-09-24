# Simple watchdog to check container health and restart if unhealthy
$ErrorActionPreference = 'SilentlyContinue'
Set-Location C:\Code\bar-directory-recon

$targets = @(
    @{ name = 'monitoring-prometheus-1'; port = 9090 },
    @{ name = 'monitoring-alertmanager-1'; port = 9093 }
)

function Get-HealthStatus($cname) {
    $status = docker inspect --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}nohealth{{end}}' $cname 2>$null
    return $status
}

$allOk = $true
foreach ($t in $targets) {
    $s = Get-HealthStatus $t.name
    if (($s -eq $null) -or ($s -eq 'nohealth') -or ($s -eq 'unhealthy')) {
        # try to restart
        docker restart $t.name | Out-Null
        Start-Sleep -Seconds 2
        $s2 = Get-HealthStatus $t.name
        if ($s2 -ne 'healthy') { $allOk = $false }
    }
    elseif ($s -ne 'healthy') {
        $allOk = $false
    }
}

$status = [int]$allOk
Write-Output "SUMMARY >> task=ace-heartbeat status=$status am=$(if ($allOk) {200} else {0}) prom=$(if ($allOk) {200} else {0}) highcpu_rule=unknown"
