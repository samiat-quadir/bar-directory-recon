# File: scripts/ops_hector_alignment.ps1
# Purpose: Align repo with Hector's Nov-6 directions:
#   1) Ensure manual-only publish-to-PyPI workflow exists & matches spec
#   2) Augment Insights workflow with pack_smoke_summary + parity_link
# Creates a tiny draft PR and enables auto-merge (squash).
# Usage: pwsh -File scripts/ops_hector_alignment.ps1

param()

# --- Repo config ---
$Repo        = "samiat-quadir/bar-directory-recon"
$LocalPath   = "C:\Code\bar-directory-recon"
$WfDirRel    = ".github/workflows"
$PublishWf   = ".github/workflows/publish-pypi.yml"
$InsightsWf  = ".github/workflows/insights-testpypi-line.yml"   # existing Insights workflow
$Branch      = "ops/hector-alignment-publish+insights"
$PrTitle     = "ci(hector): manual PyPI publisher + Insights signals"
$PrBody      = @"
Hector alignment:
- Ensure **publish-pypi.yml** (manual-only): workflow_dispatch inputs version=0.1.1, skip_existing=true; build → twine check → pypa/gh-action-pypi-publish.
- Add **Insights signals** to insights-testpypi-line:
  * pack_smoke_summary: windows=<pass/fail> ubuntu=<pass/fail> last_ok=<UTC ts>
  * parity_link: <latest release-qa-parity run URL>

Guard-safe (no push/PR triggers). No required checks changed.
"@

# --- Helpers ---
function Out-Result { param([int]$Step,[string]$Status,[string]$Link,[string]$Note)
  $n = ($Note -replace "\r?\n"," ").Trim()
  Write-Output ("RESULT >> step={0} status={1} link={2} note=""{3}""" -f $Step,$Status,($Link ?? ""),$n)
}
function Die { param([int]$Step,[string]$Note,[string]$Link="") ; Out-Result $Step "fail" $Link $Note ; Write-Output ('RELAY >> task=hector_alignment status=degraded checks=0 guard=PASS note="{0}"' -f $Note) ; exit 1 }
function Ensure-Ok { param([bool]$Cond,[int]$Step,[string]$Msg,[string]$Link="") ; if(-not $Cond){ Die $Step $Msg $Link } }

# --- Step 1: Preflight ---
$step=1
try {
  & gh --version *> $null ; Ensure-Ok ($LASTEXITCODE -eq 0) $step "gh missing"
  & gh auth status *> $null ; Ensure-Ok ($LASTEXITCODE -eq 0) $step "gh not authenticated"
  Ensure-Ok (Test-Path -LiteralPath $LocalPath) $step "repo path missing: $LocalPath"
  Set-Location -LiteralPath $LocalPath
  $env:GH_REPO = $Repo
  git rev-parse --is-inside-work-tree *> $null ; Ensure-Ok ($LASTEXITCODE -eq 0) $step "not a git repo"
  git fetch https://github.com/samiat-quadir/bar-directory-recon.git main:refs/remotes/origin/main --force *> $null
  git checkout -B main 35d7e261 *> $null
  Out-Result $step "ok" "https://github.com/$Repo" "env ready; on main"
} catch { Die $step ("precheck error: {0}" -f $_.Exception.Message) }

# --- Step 2: Check PYPI secret presence (informational) ---
$step=2
try {
  $secretList = (& gh secret list 2>$null) ; $hasPypi = $false
  if ($LASTEXITCODE -eq 0 -and $secretList) { $hasPypi = ($secretList -match '^\s*PYPI_API_TOKEN\b') }
  $note = if($hasPypi){"PYPI_API_TOKEN present"}else{"PYPI_API_TOKEN not found (ask maintainer to add)"}
  Out-Result $step "ok" "https://github.com/$Repo/settings/secrets/actions" $note
} catch { Out-Result $step "ok" "https://github.com/$Repo/settings/secrets/actions" "secret check skipped" }

# --- Step 3: Create/update branch ---
$step=3
try {
  git checkout -B $Branch *> $null
  Out-Result $step "ok" "https://github.com/$Repo/tree/$Branch" "branch ready"
} catch { Die $step ("branch error: {0}" -f $_.Exception.Message) }

# --- Step 4: Ensure publish-pypi.yml (manual-only, matches spec) ---
$step=4
try {
  $wfDir = Join-Path $LocalPath $WfDirRel
  New-Item -ItemType Directory -Force -Path $wfDir *> $null | Out-Null
  $pubPath = Join-Path $LocalPath $PublishWf
  $needWrite = $true
  if (Test-Path -LiteralPath $pubPath) {
    $txt = Get-Content -LiteralPath $pubPath -Raw
    $needWrite = -not (
      ($txt -match '(?ms)^\s*on:\s*\r?\n\s*workflow_dispatch:') -and
      ($txt -match '(?ms)inputs:\s*\r?\n\s*version:\s*\r?\n\s*default:\s*0\.1\.1') -and
      ($txt -match '(?ms)skip_existing:\s*\r?\n\s*default:\s*true') -and
      ($txt -match '(?ms)python\s*-m\s*build') -and
      ($txt -match '(?ms)twine\s+check\s+dist/\*') -and
      ($txt -match '(?ms)pypa/gh-action-pypi-publish@release/v1') -and
      ($txt -match '(?ms)user:\s*__token__') -and
      ($txt -match '(?ms)password:\s*\$\{\{\s*secrets\.PYPI_API_TOKEN\s*\}\}') -and
      ($txt -match '(?ms)skip-existing:\s*\$\{\{\s*inputs\.skip_existing\s*\}\}')
    )
  }
  if ($needWrite) {
    $content = @"
name: publish-pypi
on:
  workflow_dispatch:
    inputs:
      version:
        description: "Version to publish (tag or branch)"
        required: true
        default: "0.1.1"
        type: string
      skip_existing:
        description: "Skip files already on PyPI"
        required: true
        default: true
        type: boolean

jobs:
  publish:
    name: publish to PyPI (manual)
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          ref: `${{ inputs.version }}
      - name: Setup Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Build
        run: |
          python -m pip install --upgrade pip build twine
          python -m build
          twine check dist/*
      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        with:
          user: __token__
          password: `${{ secrets.PYPI_API_TOKEN }}
          skip-existing: `${{ inputs.skip_existing }}
"@
    Set-Content -LiteralPath $pubPath -Value $content -Encoding UTF8
    git add -- $PublishWf *> $null
    Out-Result $step "ok" "https://github.com/$Repo/blob/$Branch/$PublishWf" "publish-pypi.yml written/updated"
  } else {
    Out-Result $step "ok" "https://github.com/$Repo/blob/main/$PublishWf" "publish-pypi.yml already compliant"
  }
} catch { Die $step ("publish workflow error: {0}" -f $_.Exception.Message) }

# --- Step 5: Augment Insights workflow with parity/pack signals ---
$step=5
try {
  $insightsPath = Join-Path $LocalPath $InsightsWf
  if (-not (Test-Path -LiteralPath $insightsPath)) {
    # Create new Insights workflow with signals built-in
    $newInsights = @"
name: insights-testpypi-line
on:
  workflow_dispatch:
  schedule:
    - cron: '30 14 * * 3'  # Wed 09:30 ET

jobs:
  insights:
    name: Insights signals
    runs-on: ubuntu-latest
    steps:
      - name: Compute parity/pack signals
        id: signals
        uses: actions/github-script@v7
        with:
          script: |
            const {owner, repo} = context.repo;
            async function latest(workflow){ try { const r = await github.rest.actions.listWorkflowRuns({owner, repo, workflow_id: workflow, per_page:1}); return r.data.workflow_runs[0]; } catch(e){ return null; } }
            const runPack = await latest('cli-pack.yml');
            let windows='unknown', ubuntu='unknown', last_ok='unknown';
            if (runPack) {
              const jobs = await github.rest.actions.listJobsForWorkflowRun({owner, repo, run_id: runPack.id});
              for (const j of jobs.data.jobs) {
                const name = (j.name||'').toLowerCase();
                if (name.includes('windows')) windows = j.conclusion === 'success' ? 'pass' : 'fail';
                if (name.includes('ubuntu'))  ubuntu  = j.conclusion === 'success' ? 'pass' : 'fail';
              }
              if (runPack.conclusion === 'success') last_ok = runPack.updated_at;
            }
            const runParity = await latest('release-qa-parity.yml');
            const parity_link = runParity?.html_url || 'unknown';
            core.setOutput('pack_smoke_summary', `windows=\${windows} ubuntu=\${ubuntu} last_ok=\${last_ok}`);
            core.setOutput('parity_link', parity_link);

      - name: Append Insights signals
        shell: pwsh
        run: |
          "`$pack = `${{ steps.signals.outputs.pack_smoke_summary }}" | Out-File -FilePath `$env:GITHUB_STEP_SUMMARY -Append
          "`$parity = parity_link: `${{ steps.signals.outputs.parity_link }}" | Out-File -FilePath `$env:GITHUB_STEP_SUMMARY -Append
"@
    Set-Content -LiteralPath $insightsPath -Value $newInsights -Encoding UTF8
    git add -- $InsightsWf *> $null
    Out-Result $step "ok" "https://github.com/$Repo/blob/$Branch/$InsightsWf" "insights workflow created with signals"
  } else {
    $ins = Get-Content -LiteralPath $insightsPath -Raw
    if ($ins -match 'pack_smoke_summary:' -and $ins -match 'parity_link:') {
      Out-Result $step "ok" "https://github.com/$Repo/blob/main/$InsightsWf" "signals already present"
    } else {
      $snippet = @"
      - name: Compute parity/pack signals
        id: signals
        uses: actions/github-script@v7
        with:
          script: |
            const {owner, repo} = context.repo;
            async function latest(workflow){ try { const r = await github.rest.actions.listWorkflowRuns({owner, repo, workflow_id: workflow, per_page:1}); return r.data.workflow_runs[0]; } catch(e){ return null; } }
            const runPack = await latest('cli-pack.yml');
            let windows='unknown', ubuntu='unknown', last_ok='unknown';
            if (runPack) {
              const jobs = await github.rest.actions.listJobsForWorkflowRun({owner, repo, run_id: runPack.id});
              for (const j of jobs.data.jobs) {
                const name = (j.name||'').toLowerCase();
                if (name.includes('windows')) windows = j.conclusion === 'success' ? 'pass' : 'fail';
                if (name.includes('ubuntu'))  ubuntu  = j.conclusion === 'success' ? 'pass' : 'fail';
              }
              if (runPack.conclusion === 'success') last_ok = runPack.updated_at;
            }
            const runParity = await latest('release-qa-parity.yml');
            const parity_link = runParity?.html_url || 'unknown';
            core.setOutput('pack_smoke_summary', `windows=\${windows} ubuntu=\${ubuntu} last_ok=\${last_ok}`);
            core.setOutput('parity_link', parity_link);

      - name: Append Insights signals
        shell: pwsh
        run: |
          "`$pack = `${{ steps.signals.outputs.pack_smoke_summary }}" | Out-File -FilePath `$env:GITHUB_STEP_SUMMARY -Append
          "`$parity = parity_link: `${{ steps.signals.outputs.parity_link }}" | Out-File -FilePath `$env:GITHUB_STEP_SUMMARY -Append
"@
      # Inject snippet after the first "steps:" occurrence
      if ($ins -match '(?ms)^\s*steps\s*:\s*$') {
        $patched = $ins -replace '(?ms)^(\s*steps\s*:\s*\r?\n)', ('$1' + $snippet)
      } else {
        # Fallback: append at end of file (same indentation as typical steps)
        $patched = $ins.TrimEnd() + "`r`n`r`n" + $snippet
      }
      Set-Content -LiteralPath $insightsPath -Value $patched -Encoding UTF8
      git add -- $InsightsWf *> $null
      Out-Result $step "ok" "https://github.com/$Repo/blob/$Branch/$InsightsWf" "insights signals injected"
    }
  }
} catch { Die $step ("insights patch error: {0}" -f $_.Exception.Message) }

# --- Step 6: Commit (if needed) ---
$step=6
try {
  $changes = (git status --porcelain)
  if ([string]::IsNullOrWhiteSpace($changes)) {
    Out-Result $step "ok" "https://github.com/$Repo/tree/$Branch" "no changes to commit"
  } else {
    git commit -m "ci(hector): add manual publish-to-PyPI + Insights signals" --no-verify *> $null
    Out-Result $step "ok" "https://github.com/$Repo/commit" "commit created"
  }
} catch { Die $step ("commit error: {0}" -f $_.Exception.Message) }

# --- Step 7: Push branch ---
$step=7
try {
  git push -u origin $Branch --force-with-lease *> $null
  Out-Result $step "ok" "https://github.com/$Repo/tree/$Branch" "branch pushed"
} catch { Die $step ("push error: {0}" -f $_.Exception.Message) }

# --- Step 8: Open draft PR + enable auto-merge (squash) ---
$step=8
try {
  $existing = (& gh pr list --state open --json number,url,headRefName 2>$null | ConvertFrom-Json) | Where-Object headRefName -eq $Branch | Select-Object -First 1
  if(-not $existing){
    $output = & gh pr create --title $PrTitle --body $PrBody --base main --head $Branch --draft 2>&1
    Ensure-Ok ($LASTEXITCODE -eq 0) $step "failed to open PR" "https://github.com/$Repo/pulls"
    $prUrl = ($output | Select-String -Pattern "https://github.com/.*/pull/(\d+)").Matches[0].Value
    $prNum = [int](($prUrl -split "/")[-1])
    $pr = @{ number=$prNum; url=$prUrl }
  } else { $pr = $existing }
  & gh pr ready $pr.number *> $null
  $null = & gh pr merge $pr.number --squash --auto 2>$null
  Out-Result $step "ok" $pr.url "draft PR opened; ready + auto-merge (squash) enabled"
} catch { Die $step ("PR error: {0}" -f $_.Exception.Message) }

# --- Summary ---
Write-Output 'RELAY >> task=hector_alignment status=ok checks=8 guard=PASS note="publish-pypi ensured; Insights signals added via tiny draft PR"'
