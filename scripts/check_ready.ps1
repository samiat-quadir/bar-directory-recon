param()
function Ping($u) { try { (Invoke-WebRequest -UseBasicParsing -Uri $u -TimeoutSec 6).StatusCode } catch { 0 } }
Set-Location $PSScriptRoot\..\
$am = Ping "http://localhost:9093/-/ready"
$pm = Ping "http://localhost:9090/-/ready"
$dcJson = if (Test-Path ".devcontainer/devcontainer.json") { Get-Content ".devcontainer/devcontainer.json" -Raw } else { "" }
$df = if (Test-Path ".devcontainer/Dockerfile") { Get-Content ".devcontainer/Dockerfile" -Raw } else { "" }
$ok = ($dcJson -match "devcontainers/python" -and $dcJson -match "3\.11") -or ($df -match "devcontainers/python:.*3\.11")
Write-Host "SUMMARY >> task=codespaces-heartbeat status=$([bool]($am -eq 200 -and $pm -eq 200 -and $ok)) am=$am prom=$pm devcontainer=$ok"
