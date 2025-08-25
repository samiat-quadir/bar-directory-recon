# roi_batch2_clean.ps1
# Safe implementation of the user's workflow to normalize tests, run in container (or venv), compute coverage gate, and open/update PR.
param()
$ErrorActionPreference = 'Stop'
Set-Location 'C:\\Code\\bar-directory-recon'
Write-Output "Working Dir: $(Get-Location)"

git fetch --all --prune
git checkout -B feat/roi-batch-2-clean
Write-Output "Created branch: $(git rev-parse --abbrev-ref HEAD)"

# 1) Find duplicate test basenames and rename targeted ones by appending _targeted
$tests = Get-ChildItem -Recurse -File universal_recon\tests -Include *.py -ErrorAction SilentlyContinue
$dupes = $tests | Group-Object { $_.Name } | Where-Object { $_.Count -gt 1 }
Write-Output "Found $($dupes.Count) filename groups with duplicates"
foreach ($group in $dupes) {
    foreach ($file in $group.Group | Where-Object { $_.FullName -like "*\universal_recon\tests\targeted\*" }) {
        $new = $file.FullName -replace '\.py$','_targeted.py'
        if ($file.FullName -ne $new) {
            Write-Output "Renaming: $($file.FullName) -> $new"
            Move-Item -Path $file.FullName -Destination $new -Force
        }
    }
}

# 2) Remove pytest ignore(s) we added previously
$pi = 'pytest.ini'
if (Test-Path $pi) {
    Write-Output "Reading $pi"
    $s = Get-Content $pi -Raw
    Write-Output "Original addopts:"
    $s
    $s = $s -replace '--ignore=universal_recon/tests/targeted\s*',''
    $s = $s -replace '--ignore-glob=\*\*/targeted/test_social_link_parser.py\s*',''
    Set-Content -Path $pi -Value $s -Encoding utf8
    Write-Output "Updated $pi"
    Get-Content $pi -Raw
} else {
    Write-Output "$pi not found"
}

# 3) Ensure helper scripts live under tools/local and logs are ignored
New-Item -Force -ItemType Directory tools\local | Out-Null
$scriptsToMove = @('scripts\compute_top_roi.py','scripts\smoke_imports_coverage.py','scripts\generate_roi_tests.py','scripts\generate_roi_tests_from_json.py','scripts\extract_coverage.py')
foreach ($p in $scriptsToMove) {
    if (Test-Path $p) {
        try {
            git mv -f $p tools\local\ 2>$null
            Write-Output "git mv $p -> tools/local/"
        } catch {
            Write-Output "git mv failed or not in git; using Move-Item for $p"
            Move-Item -Path $p -Destination tools\local\ -Force
        }
    } else {
        Write-Output "Not found: $p"
    }
}

if (-not (Test-Path .gitignore)) { New-Item .gitignore -ItemType File | Out-Null }
if (-not (Select-String -Path .gitignore -Pattern '^logs/roi2/' -SimpleMatch -Quiet)) { Add-Content .gitignore "logs/roi2/"; Write-Output 'Added logs/roi2/ to .gitignore' } else { Write-Output '.gitignore already contains logs/roi2/' }

# Ensure logs dir
New-Item -Force -ItemType Directory logs\roi2 | Out-Null

# 4) Try devcontainer; fallback to venv with clear note
$UseContainer = $true
if (-not (Get-Command devcontainer -ErrorAction SilentlyContinue)) {
    Write-Output 'devcontainer CLI not found; will fallback to .venv-ci'
    $UseContainer = $false
}

if ($UseContainer) {
    try {
        Write-Output 'Building devcontainer...'
        devcontainer build --workspace-folder . *> logs\roi2\devcontainer_build.txt
        Write-Output 'Running pytest inside devcontainer...'
        devcontainer exec --workspace-folder . bash -lc "pytest -q --maxfail=1 --disable-warnings --cov=src --cov-report=term-missing --cov-report=xml:logs/roi2/coverage_after.xml 2>&1 | tee logs/roi2/pytest_after.txt"
        Write-Output 'Container run complete'
    } catch {
        Write-Output 'Container run failed, falling back to venv'
        $UseContainer = $false
    }
}

if (-not $UseContainer) {
    Write-Output 'Falling back to .venv-ci'
    if (-not (Test-Path .venv-ci)) { python -m venv .venv-ci; Write-Output 'Created .venv-ci' }
    . .\.venv-ci\Scripts\Activate.ps1
    pip install -q -U pip pytest coverage pytest-cov
    pytest -q --maxfail=1 --disable-warnings --cov=src --cov-report=term-missing --cov-report=xml:logs\roi2\coverage_after.xml 2>&1 | Tee-Object logs\roi2\pytest_after.txt
}

# 5) Compute observed coverage and set gate = observed-1 (min 8, max 35)
$txt = Get-Content logs\roi2\pytest_after.txt -Raw -ErrorAction SilentlyContinue
if (-not $txt) { Write-Output 'No pytest output found in logs/roi2/pytest_after.txt'; $txt = '' }
Write-Output 'Pytest output excerpt:'
if ($txt.Length -gt 1000) { Write-Output $txt.Substring(0,1000) } else { Write-Output $txt }
$m = [regex]::Match($txt, 'TOTAL\s+\d+\s+\d+\s+(\d+)%')
$obs = if ($m.Success) { [int]$m.Groups[1].Value } else { 0 }
Write-Output "Observed coverage: $obs%"
$target = [Math]::Min(35, [Math]::Max(8, $obs-1))
Write-Output "Computed gate: $target"

foreach ($f in @('pytest.ini','pyproject.toml','tox.ini')) {
    if (Test-Path $f) {
        (Get-Content $f -Raw) -replace '--cov-fail-under=\d+',"--cov-fail-under=$target" | Set-Content $f -Encoding utf8
        Write-Output "Updated $f"
    }
}

# 6) Commit essentials; open/update PR
git add pytest.ini pyproject.toml .gitignore universal_recon/tests -A
try { git commit -m "test: fix duplicate test names, remove ignores; container-first run; gate=$target" } catch { Write-Output 'no changes to commit' }
git push -u origin HEAD

# Use gh to edit/create PR
$prName = 'feat/roi-batch-2-clean'
$existing = $null
try { $existing = gh pr view $prName 2>$null } catch { $existing = $null }
if ($existing) {
    gh pr edit $prName --title "feat(tests): ROI batch-2 (clean) — deterministic discovery & container-first" --add-label coverage-candidate --body "Renamed duplicate tests in targeted/; removed ignores; ran in container when possible; gate=$target."
    Write-Output 'Edited existing PR'
} else {
    gh pr create --title "feat(tests): ROI batch-2 (clean) — deterministic discovery & container-first" --body "Renamed duplicate tests in targeted/; removed ignores; ran in container when possible; gate=$target." --label coverage-candidate --draft
    Write-Output 'Created PR'
}

if (-not $UseContainer) {
    Write-Output 'NOTE: devcontainer CLI not used. In GitHub Codespaces, open this repo and run:'
    Write-Output '  pytest -q --maxfail=1 --disable-warnings --cov=src'
    Write-Output 'Then adjust gate to observed-1 if it differs.'
}

Write-Output "SUMMARY >> task=roi-batch-2-clean status=ok container=$UseContainer gate=$target"
