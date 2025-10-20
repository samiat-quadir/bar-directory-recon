# Snapshots current required checks and prints 7-day ps-lint counters (no PUT).
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$owner=(gh repo view --json owner -q .owner.login)
$repo=(gh repo view --json name -q .name)
if(!(Test-Path artifacts\pslint)){ New-Item -ItemType Directory -Path artifacts\pslint | Out-Null }
gh api "repos/$owner/$repo/branches/main/protection" > artifacts\pslint\branch_protection_before.json
$wfId = gh api "repos/$owner/$repo/actions/workflows" --jq '.workflows[] | select(.path|test("ps-lint.yml$")) | .id' | Select-Object -First 1
if(-not $wfId){ throw "ps-lint workflow not found" }
$since=(Get-Date).AddDays(-7)
$runs = gh api "repos/$owner/$repo/actions/workflows/$wfId/runs" --paginate | ConvertFrom-Json
$recent=$runs.workflow_runs | Where-Object { (Get-Date $_.created_at) -ge $since }
$total = ($recent | Measure-Object).Count
$bad   = ($recent | Where-Object { $_.conclusion -in @('failure','timed_out') } | Measure-Object).Count
$bp     = Get-Content artifacts\pslint\branch_protection_before.json -Raw | ConvertFrom-Json
$checks = @()
if($bp.required_status_checks -and $bp.required_status_checks.checks){
  $checks = @($bp.required_status_checks.checks | ForEach-Object { @{ context = $_.context } })
}
$want = @('ps-lint (ubuntu-latest)','ps-lint (windows-latest)')
foreach($ctx in $want){ if(-not ($checks | Where-Object { $_.context -eq $ctx })){ $checks += @{ context = $ctx } } }
$out = @{ required_status_checks = @{ strict = $true; checks = $checks } } | ConvertTo-Json -Depth 6
$out | Out-File artifacts\pslint\branch_protection_preview.json -Encoding UTF8
Write-Host ("SUMMARY >> task=pslint_preview status=ok failures={0} total={1} note=""preview JSON written; no PUT""" -f $bad,$total)
