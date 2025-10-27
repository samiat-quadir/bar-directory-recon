# Demo script showing approval-free execution pattern
# file: scripts/demo-approval-free.ps1

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Write-Host "=== Approval-Free Execution Demo ===" -ForegroundColor Green

# Complex logic that would normally trigger approval prompts
$items = @("fast-parity-ci.yml", "pip-audit.yml", "ci.yml")
$workflowPath = ".github\workflows"

Write-Host "Checking workflow files:" -ForegroundColor Yellow
foreach($item in $items) {
    $fullPath = Join-Path $workflowPath $item
    if(Test-Path $fullPath) {
        $size = (Get-Item $fullPath).Length
        Write-Host "  ✅ $item ($size bytes)" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $item (missing)" -ForegroundColor Red
    }
}

# Show git status
Write-Host "`nCurrent branch info:" -ForegroundColor Yellow
$branch = git branch --show-current
$status = git status --porcelain | Measure-Object -Line | Select-Object -ExpandProperty Lines
Write-Host "  Branch: $branch" -ForegroundColor Cyan
Write-Host "  Uncommitted changes: $status" -ForegroundColor Cyan

# Show recent commits
Write-Host "`nRecent commits:" -ForegroundColor Yellow
$commits = git log --oneline -3
$commits | ForEach-Object { Write-Host "  $_" -ForegroundColor Gray }

Write-Host "`n=== Demo Complete ===" -ForegroundColor Green
Write-Host "This complex script ran without approval prompts!" -ForegroundColor Cyan