<#
Windows clone sanity check script
#>

param()
$ErrorActionPreference = 'Stop'
$repo = 'C:\Code\bar-directory-recon'

# 0) Preconditions
if (-not (Test-Path $repo)) {
    Write-Host "SUMMARY >> task=ace_win_sanity status=blocked reason=missing_repo path=$repo"
    exit 0
}
Push-Location $repo

# 1) Git sanity
git --version | Out-Null
try { git config --global core.longpaths true } catch {}
git config core.autocrlf false
git config core.eol lf
$origin = git remote get-url origin
if ($origin -notlike '*samiat-quadir/bar-directory-recon.git*') {
    Write-Host "SUMMARY >> task=ace_win_sanity status=blocked reason=unexpected_origin origin=$origin"
    Pop-Location; exit 0
}

# 2) Force-sync main
git fetch origin --prune
git checkout main
git reset --hard origin/main

# 3) Venv bootstrap
$venv = Join-Path $repo '.venv'
if (-not (Test-Path $venv)) { python -m venv $venv }
& "$venv\Scripts\pip.exe" install -U pip > $null
& "$venv\Scripts\pip.exe" install -e .[dev] > $null

# 4) Smoke test
$pytest = Join-Path $venv 'Scripts\pytest.exe'
if (-not (Test-Path $pytest)) {
    Write-Host "SUMMARY >> task=ace_win_sanity status=fail reason=pytest_missing"; Pop-Location; exit 0
}
$tmpOut = Join-Path $env:TEMP "pytest_win_smoke.txt"
& $pytest -q --maxfail=1 -k "not slow and not e2e and not integration" > $tmpOut 2>&1
$exit = $LASTEXITCODE
$tail = (Get-Content $tmpOut -Tail 3) -join ' | '

Pop-Location

# 5) Summarize
$status = if ($exit -eq 0) { 'ok' } else { 'degraded' }
Write-Host "SUMMARY >> task=ace_win_sanity status=$status exit=$exit tail=`"$tail`"`"
