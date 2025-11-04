# On Oct-23: if failures==0 in last 7d, PUT promotion (add ps-lint ubuntu/windows); else open defer issue. Then open two smoke PRs.
param([switch]$Execute)
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
$owner=(gh repo view --json owner -q .owner.login)
$repo=(gh repo view --json name -q .name)
$wfId = gh api "repos/$owner/$repo/actions/workflows" --jq '.workflows[] | select(.path|test("ps-lint.yml$")) | .id' | Select-Object -First 1
if(-not $wfId){ throw "ps-lint workflow not found" }
$since=(Get-Date).AddDays(-7)
$runs = gh api "repos/$owner/$repo/actions/workflows/$wfId/runs" --paginate | ConvertFrom-Json
$recent=$runs.workflow_runs | Where-Object { (Get-Date $_.created_at) -ge $since }
$total = ($recent | Measure-Object).Count
$bad   = ($recent | Where-Object { $_.conclusion -in @('failure','timed_out') } | Measure-Object).Count
gh api "repos/$owner/$repo/branches/main/protection" > artifacts\pslint\branch_protection_before_exec.json
$bp     = Get-Content artifacts\pslint\branch_protection_before_exec.json -Raw | ConvertFrom-Json
$checks = @()
if($bp.required_status_checks -and $bp.required_status_checks.checks){
  $checks = @($bp.required_status_checks.checks | ForEach-Object { @{ context = $_.context } })
}
$want = @('ps-lint (ubuntu-latest)','ps-lint (windows-latest)')
foreach($ctx in $want){ if(-not ($checks | Where-Object { $_.context -eq $ctx })){ $checks += @{ context = $ctx } } }
if($bad -gt 0 -or -not $Execute){
  if($bad -gt 0){
    $title = "Extend ps-lint burn-in 7 days"
    $exists = gh issue list --search "$title in:title" --json number -q '.[0].number'
    if(-not $exists){ gh issue create --title "$title" --body "ps-lint failures in last 7d: $bad/$total. Reassess in one week." --label "ci" | Out-Null }
    Write-Host ("SUMMARY >> task=pslint_promote status=deferred failures={0} total={1} note=""opened defer issue; no policy change""" -f $bad,$total)
    exit 0
  } else {
    # Dry-run preview only
    $final = @{ required_status_checks = @{ strict=$true; checks=$checks } } | ConvertTo-Json -Depth 6
    $final | Out-File artifacts\pslint\branch_protection_promote_dry.json -Encoding UTF8
    Write-Host ("SUMMARY >> task=pslint_promote status=preview_only failures={0} total={1} note=""ready to PUT on Oct-23 with -Execute""" -f $bad,$total)
    exit 0
  }
}
# Execute promotion
$final = @{ required_status_checks = @{ strict=$true; checks=$checks } }
$file = "artifacts\pslint\branch_protection_promote.json"
($final | ConvertTo-Json -Depth 6) | Out-File $file -Encoding UTF8
gh api -X PUT "repos/$owner/$repo/branches/main/protection" --input $file

function OpenSmoke([string]$title,[string]$touch,[string]$content){
  git fetch origin --quiet
  git checkout -B main origin/main
  git switch -c "chore/smoke-" + ($title -replace '\W','-').ToLower()
  ni -Force $touch -Value $content | Out-Null
  git add $touch
  git commit -m "ci: smoke ($title)"
  git push -u origin HEAD
  $pr = gh pr create -f -d -t "ci: smoke ($title)" -b "Automated smoke after ps-lint promotion."
  gh pr merge $pr --squash --auto | Out-Null
  return $pr
}
$pra = OpenSmoke "workflow-only sentinel" ".github\ci-sentinel.md" "# sentinel"
$prb = OpenSmoke "scripts touch" "scripts\_noop.ps1" "# noop"
Write-Host ("SUMMARY >> task=pslint_promote status=promoted failures={0} total={1} note=""policy updated; smoke queued: {2}, {3}""" -f $bad,$total,$pra,$prb)
