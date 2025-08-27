<#
Run inside devcontainer to compute coverage gate and update pyproject.toml addopts.
Usage: .\scripts\devcontainer_hygiene.ps1
#>
Set-StrictMode -Version Latest

function Abort([string]$msg) {
    Write-Error $msg
    exit 2
}

# Ensure running inside devcontainer
$containerName = $env:CONTAINER_NAME
if ([string]::IsNullOrEmpty($containerName)) {
    Abort 'This script must be run inside the devcontainer. $env:CONTAINER_NAME is empty.'
}
Write-Host "Container: $containerName"

Write-Host 'Checking git status for reports/ or logs/ changes...'
$status = git status --porcelain 2>$null
if ($status) {
    if ($status -match '(^|\n)([AMDRC]|\?\?)\s+(reports/|logs/)') {
        Abort 'Aborting: git status shows changes under reports/ or logs/. Please clean them before running this script.'
    }
}

Write-Host 'Running pytest to generate coverage report...'
mkdir -Force reports | Out-Null

# Safely invoke pytest; rely on pytest in PATH inside devcontainer
$pytestArgs = @('-q','--cov=src','--cov=universal_recon','--cov-report=xml:reports/coverage.xml','-k','not slow and not e2e and not integration')
Write-Host "Invoking: pytest $($pytestArgs -join ' ')"
& pytest @pytestArgs
if ($LASTEXITCODE -ne 0) {
    Abort "pytest failed (exit code $LASTEXITCODE). Fix tests before running hygiene."
}

if (-not (Test-Path 'reports/coverage.xml')) {
    Abort 'coverage.xml not produced at reports/coverage.xml'
}

[xml]$xml = Get-Content -Path 'reports/coverage.xml' -Raw
$root = $xml.documentElement
$lineRateAttr = $root.GetAttribute('line-rate')
if (-not $lineRateAttr) {
    Abort 'Could not read line-rate from reports/coverage.xml'
}
$observed = [math]::Floor([double]$lineRateAttr * 100)
Write-Host "Observed coverage (percent): $observed%"

# gate = clamp(floor(obs)-1, 8, 35)
$gate = [math]::Floor($observed - 1)
if ($gate -lt 8) { $gate = 8 }
if ($gate -gt 35) { $gate = 35 }
Write-Host "Computed gate: $gate%"

Write-Host "Updating pyproject.toml pytest addopts to include --cov-fail-under=$gate"
$path = 'pyproject.toml'
$lines = Get-Content -Path $path -Raw -ErrorAction Stop -Encoding UTF8 -Raw | Out-String

# We'll operate on lines to avoid escaping issues
$allLines = [System.IO.File]::ReadAllLines($path)
$inSection = $false
$modified = $false
for ($i = 0; $i -lt $allLines.Length; $i++) {
    $line = $allLines[$i]
    if ($line -match '^[\s]*\[tool\.pytest\.ini_options\]') {
        $inSection = $true
        continue
    }
    if ($inSection -and $line -match '^[\s]*\[') {
        # left the section
        break
    }
    if ($inSection -and $line -match '^[\s]*addopts\s*=\s*"(.*)"') {
        $current = $matches[1]
        if ($current -match '--cov-fail-under=\d+') {
            $newAddopts = ($current -replace '--cov-fail-under=\d+', "--cov-fail-under=$gate")
        } else {
            $newAddopts = "$current --cov-fail-under=$gate"
        }
        $allLines[$i] = "addopts = \"$newAddopts\""
        $modified = $true
        break
    }
}

if (-not $modified) {
    Abort 'Failed to find addopts under [tool.pytest.ini_options] to update. Please update pyproject.toml manually.'
}

[System.IO.File]::WriteAllLines($path, $allLines, [System.Text.Encoding]::UTF8)

Write-Host 'Staging pyproject.toml'
git add pyproject.toml

Write-Host 'Create commit? (y/N)'
$resp = Read-Host
if ($resp -ne 'y') {
    Write-Host 'Aborting before commit. pyproject.toml modified locally.'
    exit 0
}

git commit -m "chore(hygiene): apply coverage gate based on devcontainer run ($observed%)"
Write-Host 'Committed. Please push branch and open PR as needed.'

Write-Host "Result: observed=$observed gate=$gate"

exit 0
