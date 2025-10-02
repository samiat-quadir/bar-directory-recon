param()
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Say($m) { Write-Host "==> $m" }

Set-Location (Resolve-Path "${PSScriptRoot}\..")
Say "repo: $(Get-Location)"

# Fetch latest remote refs
git fetch origin --prune --quiet

$PR = 203
$BR = (gh pr view $PR --json headRefName -q '.headRefName')
if (-not $BR) { throw "Cannot read PR headRefName" }
$BR = $BR.Trim()
Say "PR $PR head: $BR"

# Checkout PR head (create or reset local branch)
try {
    git checkout -B $BR origin/$BR 2>$null
}
catch {
    git checkout -B $BR 2>$null
}

# Prepare output dir
$OUT = "artifacts\pr${PR}_analysis"
if (Test-Path $OUT) { Remove-Item -LiteralPath $OUT -Recurse -Force -ErrorAction SilentlyContinue }
New-Item -ItemType Directory -Path $OUT | Out-Null

# Merge origin/main --no-commit to surface conflicts (no commit/push)
Try {
    git merge --no-commit origin/main 2>$null
}
Catch {
    # merge may produce conflicts; continue
    Write-Host "merge staged (or up to date)"
}

# Collect conflicts
git diff --name-only --diff-filter=U > "$OUT\conflicts.txt"

# Snapshot current workflows list
if (Test-Path ".github\workflows") {
    Get-ChildItem .github\workflows -Filter *.yml -File | ForEach-Object { $_.Name } | Set-Content "$OUT\workflows_current.txt"
    # Save bodies
    Get-ChildItem .github\workflows -Filter *.yml -File | ForEach-Object {
        $n = $_.Name.Replace('.yml', '') + ".yml.txt"
        Get-Content $_.FullName -Raw | Out-File -Encoding utf8 "$OUT\wf_$n"
    }
}
else { '' | Out-File -Encoding utf8 "$OUT\workflows_current.txt" }

# Keep-core list
@(
    "score_leads.py",
    "tools/cross_device/validate_device_profiles.py",
    "universal_recon/utils/overlay_visualizer.py",
    "universal_recon/utils/validator_drift_overlay.py",
    "universal_recon/utils/record_field_validator_v3.py",
    "universal_recon/utils/test_score_visualizer.py",
    "universal_recon/utils/record_normalizer.py",
    "universal_recon/utils/score_visualizer.py",
    "universal_recon/utils/validator_loader.py",
    "universal_recon/utils/validator_drift_badges.py",
    "universal_recon/utils/fieldmap_domain_linter.py",
    "universal_recon/utils/run_phase_21b_analysis.py",
    "universal_recon/utils/validation_matrix.py"
) | Set-Content "$OUT\keep_core.txt"

# Delete candidates via rules
$delRules = @(
    '^archive/', '^automation/', '^audits/', '^logs/',
    '^(ASUS_.*|ALIENWARE_.*|notify_agent\.(asus|alienware)\.py|git_commit_and_notify_.*\.py)$',
    '^src/(hallandale_.*|ut_bar\.py)$',
    '^test_.*\.py$'
) -join '|'

git ls-files | Where-Object { $_ -match $delRules } | Set-Content "$OUT\delete_candidates.txt"

# Save previews
if (Test-Path ".gitignore") { Get-Content .gitignore -Raw | Out-File -Encoding utf8 "$OUT\gitignore_current.txt" }
if (Test-Path ".coveragerc") { Get-Content .coveragerc -Raw | Out-File -Encoding utf8 "$OUT\coveragerc_current.txt" }

# Expected required checks
@("audit", "fast-tests (ubuntu-latest)", "fast-tests (windows-latest)") | Set-Content "$OUT\required_checks.txt"

# Abort merge to leave working tree clean
git merge --abort 2>$null || Write-Host "no merge to abort"

# Summary counts
$c = (Get-Content "$OUT\conflicts.txt" -ErrorAction SilentlyContinue | Measure-Object -Line).Lines
$d = (Get-Content "$OUT\delete_candidates.txt" -ErrorAction SilentlyContinue | Measure-Object -Line).Lines
$k = (Get-Content "$OUT\keep_core.txt" -ErrorAction SilentlyContinue | Measure-Object -Line).Lines

Write-Host "SUMMARY >> task=pr${PR}_dryrun status=ok conflicts=$c delete=$d keep=$k note=analysis_pack_ready at=$OUT"

Exit 0
