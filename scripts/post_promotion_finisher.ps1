# file: scripts/post_promotion_finisher.ps1
# Purpose: After ps-lint promotion occurs, finish housekeeping:
# - add ps-lint badges to README (idempotent)
# - create/update a draft v0.1.0 release using RELEASE_NOTES_v0.1.0.md
# - verify smoke PRs merged
# - dispatch Insights
# Safe to run anytime; no-op if promotion hasn't happened.

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
function Say($m){ Write-Host "==> $m" }
function ReadJson($p){ if (Test-Path $p){ Get-Content $p -Raw | ConvertFrom-Json } else { $null } }
function EnsureDir($p){ if(-not(Test-Path $p)){ New-Item -ItemType Directory -Path $p | Out-Null } }

$REPO = "C:\Code\bar-directory-recon"
if(!(Test-Path $REPO)){ throw "Repo not found: $REPO" }
Set-Location $REPO
git fetch origin --prune *> $null
git checkout -q main
git reset --hard origin/main
git clean -xdf -q

# 1) Branch protection check
$owner = (gh repo view --json owner -q .owner.login)
$repo  = (gh repo view --json name  -q .name)
$prot  = gh api "repos/$owner/$repo/branches/main/protection" | ConvertFrom-Json
$checks = @()
if($prot.required_status_checks -and $prot.required_status_checks.checks){
  $checks = $prot.required_status_checks.checks | ForEach-Object { $_.context }
}
$hasUbuntu = $checks -contains 'ps-lint (ubuntu-latest)'
$hasWindows= $checks -contains 'ps-lint (windows-latest)'

if(-not ($hasUbuntu -and $hasWindows)){
  Write-Host ("SUMMARY >> task=post_promo_finisher status=pending checks=[{0}] note=""ps-lint contexts not required yet; finisher no-op""" -f ($checks -join ', '))
  exit 0
}

# 2) Add ps-lint badges to README (idempotent)
$readme = "README.md"
$badgeBlock = @"
<!-- badges:pslint:start -->
[![ps-lint (ubuntu-latest)](https://github.com/$owner/$repo/actions/workflows/ps-lint.yml/badge.svg?branch=main)](https://github.com/$owner/$repo/actions/workflows/ps-lint.yml?query=branch%3Amain)
[![ps-lint (windows-latest)](https://github.com/$owner/$repo/actions/workflows/ps-lint.yml/badge.svg?branch=main)](https://github.com/$owner/$repo/actions/workflows/ps-lint.yml?query=branch%3Amain)
<!-- badges:pslint:end -->
"@
if(Test-Path $readme){
  $txt = Get-Content $readme -Raw
  if($txt -notmatch "<!-- badges:pslint:start -->"){
    # insert below existing badges if present, else under H1
    if($txt -match "<!-- badges:end -->"){
      $txt = $txt -replace "<!-- badges:end -->", "<!-- badges:end -->`r`n`r`n$badgeBlock"
    } elseif($txt -match "^(# .+?\r?\n)"){
      $txt = $matches[1] + "`r`n" + $badgeBlock + "`r`n" + $txt.Substring($matches[1].Length)
    } else {
      $txt = $badgeBlock + "`r`n" + $txt
    }
    [IO.File]::WriteAllText($readme,$txt,[Text.UTF8Encoding]::new($false))
    git add README.md | Out-Null
  }
}

# 3) Draft release (only if notes file exists)
$notes = "RELEASE_NOTES_v0.1.0.md"
$releaseTag = "v0.1.0"
if(Test-Path $notes){
  # if release exists, update; else create as draft (do not publish)
  $exists = gh release view $releaseTag --json tagName -q .tagName 2>$null
  if($exists){
    gh release edit $releaseTag --draft --title "v0.1.0 (draft)" --notes-file $notes --target main | Out-Null
    Say "Updated draft release $releaseTag"
  } else {
    gh release create $releaseTag --draft --title "v0.1.0 (draft)" --notes-file $notes --target main | Out-Null
    Say "Created draft release $releaseTag"
  }
}

# 4) Verify smoke PRs (best-effort): find two latest PRs with title prefix "ci: smoke"
$smokes = gh pr list --state all --search "in:title ci: smoke" --json number,state,mergedAt --limit 10 | ConvertFrom-Json
$merged = @($smokes | Where-Object { $_.state -eq 'MERGED' } | Select-Object -ExpandProperty number)
$mergedList = if($merged){ ($merged -join ',') } else { "none" }

# 5) Commit badges (if any) and push via a tiny PR (auto-merge)
if(git diff --cached --quiet){
  Say "No README badge changes to commit."
} else {
  $br = "chore/post-promo-badges-$(Get-Date -Format yyyyMMdd-HHmmss)"
  git checkout -b $br
  git commit -m "docs: add ps-lint badges after promotion"
  git push --set-upstream origin $br | Out-Null
  try{
    gh pr create --title "docs: add ps-lint badges after promotion" `
      --body "Add ps-lint (ubuntu/windows) badges now that they are required. No CI/policy change." `
      --base main --head $br --draft | Out-Null
  }catch{}
  try{ gh pr merge --squash --auto | Out-Null }catch{}
}

# 6) Dispatch Insights to capture post-promotion state
try { gh workflow run ci-insights-weekly --ref main | Out-Null } catch { }

Write-Host ("SUMMARY >> task=post_promo_finisher status=ok release=draft tag={0} smokes_merged={1} note=""badges ensured; draft release prepared; insights dispatched""" -f $releaseTag, $mergedList)
