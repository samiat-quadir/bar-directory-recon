# monitoring\doctor.ps1
$ErrorActionPreference="Continue"
$here=(Get-Location).Path; Write-Host "PWD=$here"
$svc="windows_exporter"
$svcOk=(Get-Service $svc -ErrorAction SilentlyContinue).Status -eq 'Running'
$bind=(netstat -ano | findstr /r /c:":9182 .*LISTENING" | Select-Object -First 1)
try { $http=(iwr http://localhost:9182/metrics -UseBasicParsing -TimeoutSec 3).StatusCode } catch { $http=$_.Exception.Message }
try { $prom=(iwr http://localhost:9090/-/ready -UseBasicParsing -TimeoutSec 3).StatusCode } catch { $prom=$_.Exception.Message }
try { $targets=(iwr http://localhost:9090/api/v1/targets -UseBasicParsing -TimeoutSec 3).Content } catch { $targets='' }
$ts=(tailscale ip -4 2>$null); $ts = ($ts -split "`r?`n" | ? {$_ -match '^100\.'} | select -f 1)
Write-Host "SUMMARY >> exporter=$svcOk bind='$bind' exporter_http=$http prom_ready=$prom tailscale_ip=$ts ace_target='host.docker.internal:9182'"
