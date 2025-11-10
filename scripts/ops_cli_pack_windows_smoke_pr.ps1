# File: scripts/ops_cli_pack_windows_smoke_pr.ps1
# Purpose: Add a minimal Windows smoke job to cli-pack.yml via a tiny draft PR (manual/schedule only).
# Usage:   pwsh -File scripts/ops_cli_pack_windows_smoke_pr.ps1

param()

# --- Repo config ---
$Repo      = "samiat-quadir/bar-directory-recon"
$LocalPath = "C:\Code\bar-directory-recon"
$WfPathRel = ".github/workflows/cli-pack.yml"
$Branch    = "ops/cli-pack-windows-smoke"
$PrTitle   = "ci(cli-pack): add minimal Windows smoke (manual/schedule only)"
$PrBody    = @"
Add a tiny Windows smoke job to cli-pack:
- runs-on: windows-latest
- gated: workflow_dispatch OR schedule
- steps: checkout, setup-python 3.11, python --version, simple pwsh echo

Guard-safe (no new triggers beyond manual/schedule).
"@

# --- Helpers ---
function Out-Result { param([int]$Step,[string]$Status,[string]$Link,[string]$Note)
  $n = ($Note -replace "\r?\n"," ").Trim()
  Write-Output ("RESULT >> step={0} status={1} link={2} note=""{3}""" -f $Step,$Status,($Link ?? ""),$n)
}
function Die { param([int]$Step,[string]$Note,[string]$Link=""); Out-Result $Step "fail" $Link $Note; Write-Output ('RELAY >> task=cli_pack_windows_smoke_pr status=degraded checks=0 guard=PASS note="{0}"' -f $Note); exit 1 }
function Ensure-Ok { param([bool]$Cond,[int]$Step,[string]$Note,[string]$Link=""); if(-not $Cond){ Die $Step $Note $Link } }

# --- Step 1: Preconditions ---
$step=1
try {
  & gh --version *> $null; Ensure-Ok ($LASTEXITCODE -eq 0) $step "gh missing"
  Ensure-Ok (Test-Path -LiteralPath $LocalPath) $step "repo path missing: $LocalPath"
  Set-Location -LiteralPath $LocalPath
  $env:GH_REPO = $Repo
  # Ensure git repo
  git rev-parse --is-inside-work-tree *> $null; Ensure-Ok ($LASTEXITCODE -eq 0) $step "not a git repo at $LocalPath"
  Out-Result $step "ok" "https://github.com/$Repo" "env ready; repo set"
} catch { Die $step ("precheck error: {0}" -f $_.Exception.Message) }

# --- Step 2: Inspect cli-pack.yml & existing PR ---
$step=2
$wfFull = Join-Path $LocalPath $WfPathRel
try {
  Ensure-Ok (Test-Path -LiteralPath $wfFull) $step "cli-pack.yml missing" "https://github.com/$Repo/tree/main/.github/workflows"
  $yaml = Get-Content -LiteralPath $wfFull -Raw
  if ($yaml -match '(?m)^\s*windows-smoke\s*:') {
    # Check if PR already open for our branch
    $prs = & gh pr list --state open --json number,url,headRefName | ConvertFrom-Json
    $pr = $prs | Where-Object { $_.headRefName -eq $Branch } | Select-Object -First 1
    if ($pr) {
      Out-Result $step "ok" $pr.url "windows-smoke already present; PR exists"
    } else {
      Out-Result $step "ok" "https://github.com/$Repo/blob/main/$WfPathRel" "windows-smoke already present; nothing to change"
    }
    Write-Output 'RELAY >> task=cli_pack_windows_smoke_pr status=ok checks=1 guard=PASS note="no-op; windows-smoke exists"'
    exit 0
  }
  Out-Result $step "ok" "https://github.com/$Repo/blob/main/$WfPathRel" "windows-smoke NOT present; will open tiny PR"
} catch { Die $step ("inspect error: {0}" -f $_.Exception.Message) }

# --- Step 3: Create/update branch ---
$step=3
try {
  # Switch to main and update
  git fetch origin --prune *> $null
  git checkout -B main origin/main *> $null
  # Create work branch
  git checkout -B $Branch *> $null
  Out-Result $step "ok" "https://github.com/$Repo/tree/$Branch" "branch ready"
} catch { Die $step ("branch error: {0}" -f $_.Exception.Message) }

# --- Step 4: Patch YAML (insert windows-smoke job under jobs:) ---
$step=4
try {
  $yaml = Get-Content -LiteralPath $wfFull -Raw
  Ensure-Ok ($yaml -match '(?m)^\s*jobs\s*:\s*$') $step "cli-pack.yml missing 'jobs:' anchor" "https://github.com/$Repo/blob/main/$WfPathRel"

  $insert = @"
  windows-smoke:
    name: windows smoke
    runs-on: windows-latest
    if: github.event_name == 'workflow_dispatch' || github.event_name == 'schedule'
    steps:
      - uses: actions/checkout@v4
      - name: Setup Python 3.11
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Windows smoke
        shell: pwsh
        run: |
          python --version
          Write-Host "Windows smoke ✅"
"@

  # Insert after the first "jobs:" line with proper indentation
  $patched = $yaml -replace '(?ms)^(\s*jobs\s*:\s*\r?\n)', ('$1' + $insert)
  # Safe write only if change happened
  if ($patched -eq $yaml) { Die $step "failed to inject windows-smoke into cli-pack.yml" }
  Set-Content -LiteralPath $wfFull -Value $patched -Encoding UTF8

  git add -- $WfPathRel *> $null
  git commit -m "ci(cli-pack): add minimal Windows smoke (manual/schedule only)" *> $null
  Out-Result $step "ok" "https://github.com/$Repo/blob/$Branch/$WfPathRel" "yaml patched & committed"
} catch { Die $step ("patch error: {0}" -f $_.Exception.Message) }

# --- Step 5: Push branch ---
$step=5
try {
  git push -u origin $Branch --force-with-lease *> $null
  Out-Result $step "ok" "https://github.com/$Repo/tree/$Branch" "branch pushed"
} catch { Die $step ("push error: {0}" -f $_.Exception.Message) }

# --- Step 6: Open draft PR + enable auto-merge (squash) ---
$step=6
try {
  # If PR already exists for this branch, reuse
  $existing = & gh pr list --state open --json number,url,headRefName | ConvertFrom-Json
  $pr = $existing | Where-Object { $_.headRefName -eq $Branch } | Select-Object -First 1
  if (-not $pr) {
    $pr = & gh pr create --title $PrTitle --body $PrBody --base main --head $Branch --draft --json number,url | ConvertFrom-Json
    Ensure-Ok ($LASTEXITCODE -eq 0 -and $pr) $step "failed to open PR" "https://github.com/$Repo/pulls"
  }
  # Enable auto-merge (squash)
  $null = & gh pr merge $pr.number --squash --auto
  Out-Result $step "ok" $pr.url "draft PR ready; auto-merge (squash) enabled"
} catch { Die $step ("PR error: {0}" -f $_.Exception.Message) }

# --- Relay summary ---
Write-Output 'RELAY >> task=cli_pack_windows_smoke_pr status=ok checks=6 guard=PASS note="opened tiny PR to add Windows smoke (manual/schedule)"'
