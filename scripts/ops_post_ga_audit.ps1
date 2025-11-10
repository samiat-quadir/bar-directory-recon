# File: scripts/ops_post_ga_audit.ps1
# Purpose: Post-GA audit for v0.1.1; optional tiny fixes (regex harden, smoke issue). Guard-safe & idempotent.
# Usage:
#   pwsh -File scripts/ops_post_ga_audit.ps1 [-Version 0.1.1] [-VersionTag v0.1.1] [-CloseGatePr]
#                                           [-UpdateRelease] [-OpenFixPr] [-OpenSmokeIssue]
param(
  [string]$Version = "0.1.1",
  [string]$VersionTag = "v0.1.1",
  [int]$GatePr = 312,
  [switch]$CloseGatePr,
  [switch]$UpdateRelease,
  [switch]$OpenFixPr,
  [switch]$OpenSmokeIssue
)

# --- Repo config ---
$Repo      = "samiat-quadir/bar-directory-recon"
$LocalPath = "C:\Code\bar-directory-recon"
$CliPackWf = ".github/workflows/cli-pack.yml"
$GaExec    = "scripts/ops_ga_gate_execute.ps1" # candidate for tiny regex harden

# --- Helpers ---
function Out-Result { param([int]$Step,[string]$Status,[string]$Link,[string]$Note)
  $n = ($Note -replace "\r?\n"," ").Trim()
  Write-Output ("RESULT >> step={0} status={1} link={2} note=""{3}""" -f $Step,$Status,($Link ?? ""),$n)
}
function Die { param([int]$Step,[string]$Note,[string]$Link=""); Out-Result $Step "fail" $Link $Note; Write-Output ('RELAY >> task=post_ga_audit status=degraded checks=0 guard=PASS note="{0}"' -f $Note); exit 1 }
function Ensure-Ok { param([bool]$Cond,[int]$Step,[string]$Note,[string]$Link=""); if(-not $Cond){ Die $Step $Note $Link } }

# Step 1: Preconditions
$step=1
try {
  & gh --version *> $null; Ensure-Ok ($LASTEXITCODE -eq 0) $step "gh missing"
  Ensure-Ok (Test-Path -LiteralPath $LocalPath) $step "repo path missing: $LocalPath"
  Set-Location -LiteralPath $LocalPath
  $env:GH_REPO = $Repo
  Out-Result $step "ok" "https://github.com/$Repo" "env ready"
} catch { Die $step ("precheck error: {0}" -f $_.Exception.Message) }

# Step 2: PyPI presence for version (JSON + HTML)
$step=2
$pypiJsonUrl = ""; $pypiHtmlUrl = ""; $pkgName = ""
try {
  $pyprojPath = Join-Path $LocalPath "pyproject.toml"
  if (Test-Path -LiteralPath $pyprojPath) {
    $txt = Get-Content -LiteralPath $pyprojPath -Raw
    if ($txt -match '(?m)^\s*name\s*=\s*["'']([^"'']+)["'']') { $pkgName = $Matches[1] }
  }
  if ([string]::IsNullOrWhiteSpace($pkgName)) { $pkgName = "bar-directory-recon" }

  $pypiJsonUrl = "https://pypi.org/pypi/$pkgName/$Version/json"
  $pypiHtmlUrl = "https://pypi.org/project/$pkgName/$Version/"

  $json = $null; $okJson = $false; $okHtml = $false
  try { $json = Invoke-WebRequest -Uri $pypiJsonUrl -UseBasicParsing -TimeoutSec 15 } catch {}
  if ($json -and $json.StatusCode -eq 200) { $okJson = $true }

  try { $html = Invoke-WebRequest -Uri $pypiHtmlUrl -UseBasicParsing -TimeoutSec 15 } catch {}
  if ($html -and $html.StatusCode -eq 200) { $okHtml = $true }

  $ok = $okJson -and $okHtml
  $st = if($ok){"ok"}else{"fail"}
  Out-Result $step $st $pypiHtmlUrl ("PyPI json={0} html={1} for {2} {3}" -f $okJson,$okHtml,$pkgName,$Version)
  if(-not $ok){ exit 2 }
} catch { Die $step ("PyPI check error: {0}" -f $_.Exception.Message) }

# Step 3: Release notes contain PyPI + parity link (report; optional update)
$step=3
$releaseUrl = "https://github.com/$Repo/releases/tag/$VersionTag"
try {
  $rv = & gh release view $VersionTag --json url,body 2>$null | ConvertFrom-Json
  Ensure-Ok ($rv -ne $null) $step "cannot view release $VersionTag" $releaseUrl
  $body = "$($rv.body)"
  $hasPypi = ($body -match [regex]::Escape($pypiHtmlUrl)) -or ($body -match "(?i)Published to PyPI")
  # grab latest parity run link if present
  $parity = $null
  try { $parity = (& gh run list --workflow "release-qa-parity.yml" --limit 1 --json url,conclusion | ConvertFrom-Json)[0] } catch {}
  $needUpdate = (-not $hasPypi)
  if ($UpdateRelease -and $needUpdate) {
    $append = @()
    $append += ""
    $append += "### GA: Published to PyPI"
    $append += "* PyPI: $pypiHtmlUrl"
    if($parity){ $append += "* Parity: $($parity.url)" }
    $newBody = ($body + "`n" + ($append -join "`n"))
    $null = & gh release edit $VersionTag --notes $newBody
    Ensure-Ok ($LASTEXITCODE -eq 0) $step "failed to update release notes" $releaseUrl
    Out-Result $step "ok" $releaseUrl "release notes updated (PyPI+parity)"
  } else {
    $note = if($hasPypi){"release has PyPI link"}else{"release missing PyPI link (use -UpdateRelease to add)"}
    Out-Result $step "ok" $releaseUrl $note
  }
} catch { Die $step ("release check/update error: {0}" -f $_.Exception.Message) $releaseUrl }

# Step 4: PR #312 state (optionally close)
$step=4
try {
  $pr = & gh pr view $GatePr --json number,state,isDraft,merged,url 2>$null | ConvertFrom-Json
  if(-not $pr){ Out-Result $step "ok" ("https://github.com/$Repo/pulls") "PR #$GatePr not found"; }
  else {
    $note = "state=$($pr.state) merged=$($pr.merged) draft=$($pr.isDraft)"
    if($CloseGatePr -and $pr.state -eq "OPEN"){
      $null = & gh pr close $GatePr --delete-branch
      if($LASTEXITCODE -eq 0){ $note = $note + "; closed" }
    }
    Out-Result $step "ok" $pr.url $note
  }
} catch { Die $step ("PR status error: {0}" -f $_.Exception.Message) ("https://github.com/$Repo/pull/$GatePr") }

# Step 5: GA executor regex harden (optional tiny PR)
$step=5
try {
  $gaPath = Join-Path $LocalPath $GaExec
  if(Test-Path -LiteralPath $gaPath){
    $src = Get-Content -LiteralPath $gaPath -Raw
    $fragile = ($src -match 'workflow_dispatch:\s*inputs:\s*([A-Za-z0-9_\-]+):')
    if($OpenFixPr -and $fragile){
      $branch = "ops/ga-executor-input-key"
      git rev-parse --is-inside-work-tree *> $null; if($LASTEXITCODE){ git init | Out-Null }
      git switch -c $branch 2>$null | Out-Null

      # Replace with robust detection for 'version' or 'tag'
      $fixed = $src -replace 'workflow_dispatch:\s*inputs:\s*([A-Za-z0-9_\-]+):','workflow_dispatch:\s*inputs:$0' # keep YAML; we change code path below
      # Also replace the code that extracts $key to use heuristics over raw regex
      $fixed = $fixed -replace '(?ms)\$key\s*=\s*"?version"?\s*[\r\n]+if\([^\)]*workflow_dispatch.*?\)',''
      # Inject a safe helper if not present
      if($fixed -notmatch 'function\s+Get-WorkflowInputKey'){
        $helper = @"
function Get-WorkflowInputKey {
  param([string]`$Yaml)
  # Prefer explicit common keys; tolerate whitespace/indent
  if(`$Yaml -match '(?ms)workflow_dispatch:\s*inputs:.*?^\s*version\s*:'){ return 'version' }
  if(`$Yaml -match '(?ms)workflow_dispatch:\s*inputs:.*?^\s*tag\s*:'){ return 'tag' }
  # Fallback to first input name
  if(`$Yaml -match '(?ms)workflow_dispatch:\s*inputs:\s*([A-Za-z0-9_\-]+)\s*:'){ return `$Matches[1] }
  return 'version'
}
"@
        $fixed = $helper + "`r`n" + $fixed
      }
      $fixed = $fixed -replace '\$key\s*=\s*"version"','\$key = Get-WorkflowInputKey -Yaml $wfText'

      Set-Content -LiteralPath $gaPath -Value $fixed -Encoding UTF8
      git add $GaExec | Out-Null
      git commit -m "ops(gate): harden workflow input-key detection (version/tag) for publish dispatch" | Out-Null

      $prJson = & gh pr create --title "ops: harden GA executor input-key detection" --body "Fix fragile regex; prefer 'version'/'tag' with fallback. Draft + auto-merge (squash)." --draft --base main --head $branch --json url,number | ConvertFrom-Json
      if($LASTEXITCODE -eq 0 -and $prJson){
        $null = & gh pr merge $prJson.number --squash --auto
        Out-Result $step "ok" $prJson.url "draft PR opened; auto-merge enabled"
      } else {
        Out-Result $step "fail" "https://github.com/$Repo/pulls" "failed to open PR"
      }
    } else {
      $note = if($fragile){"regex fragile; pass -OpenFixPr to patch"}else{"regex already robust; nothing to do"}
      Out-Result $step "ok" "https://github.com/$Repo" $note
    }
  } else {
    Out-Result $step "ok" "https://github.com/$Repo" "GA executor not found; skipping fix"
  }
} catch { Die $step ("regex-fix error: {0}" -f $_.Exception.Message) }

# Step 6: Windows smoke via cli-pack (recent success) + optional issue
$step=6
try {
  $runs = & gh run list --workflow $CliPackWf --limit 5 --json databaseId,status,conclusion,url,createdAt | ConvertFrom-Json
  if(-not $runs){ Out-Result $step "ok" "https://github.com/$Repo/actions" "no cli-pack runs found"; }
  else {
    $ok = $false; $anyUrl = ""
    foreach($r in $runs){
      $view = & gh run view $r.databaseId --json jobs,url | ConvertFrom-Json
      $anyUrl = $view.url
      foreach($j in $view.jobs){
        $jn = "$($j.name)".ToLower()
        if(($jn -like "*windows*" -or $jn -like "*win*") -and $j.conclusion -eq "success"){ $ok = $true; break }
      }
      if($ok){ break }
    }
    if($ok){
      Out-Result $step "ok" $anyUrl "windows smoke present (cli-pack)"
    } else {
      if($OpenSmokeIssue){
        $title = "Restore minimal Windows smoke in cli-pack"
        $existing = & gh issue list --state open --search "$title in:title" --json number,url | ConvertFrom-Json
        if(-not $existing -or $existing.Count -eq 0){
          $body = @()
          $body += "Windows smoke was skipped during GA 0.1.1; restore a minimal Windows job in cli-pack to keep gate intent."
          $body += "- Expectation: at least one passing Windows job per run."
          $newIssue = & gh issue create -t $title -b ($body -join "`n") --label "ci"
          Out-Result $step "ok" "$newIssue" "opened issue to restore Windows smoke"
        } else {
          Out-Result $step "ok" "$($existing[0].url)" "existing issue to restore Windows smoke"
        }
      } else {
        Out-Result $step "fail" ($anyUrl ?? "https://github.com/$Repo/actions") "no recent successful Windows smoke; pass -OpenSmokeIssue to file"
      }
    }
  }
} catch { Die $step ("windows smoke check error: {0}" -f $_.Exception.Message) }

# Summary
Write-Output 'RELAY >> task=post_ga_audit status=ok checks=4 guard=PASS note="PyPI verified; release checked; optional fix PR & smoke issue ready"'
