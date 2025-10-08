# Move generated artifacts into reports/ and local/ safely
Param()
$ErrorActionPreference = 'Stop'
$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location $repoRoot
$reportsDir = Join-Path $repoRoot 'reports'
$localDir = Join-Path $repoRoot 'local'
# Ensure directories exist
New-Item -ItemType Directory -Force -Path $reportsDir | Out-Null
New-Item -ItemType Directory -Force -Path $localDir | Out-Null

$moves = @(
    @{src = 'logs\\roi2'; dst = Join-Path $reportsDir 'roi2'},
    @{src = 'logs\\nightly'; dst = Join-Path $reportsDir 'nightly'},
    @{src = 'logs'; dst = Join-Path $reportsDir 'logs_root'},
    @{src = 'coverage.xml'; dst = Join-Path $reportsDir 'coverage.xml'},
    @{src = 'logs\\coverage_after.xml'; dst = Join-Path $reportsDir 'coverage_after.xml'},
    @{src = 'logs\\roi2\\coverage_after.xml'; dst = Join-Path $reportsDir 'roi2_coverage_after.xml'}
)

$moved = @()
foreach ($m in $moves) {
    if (Test-Path $m.src) {
        New-Item -ItemType Directory -Force -Path (Split-Path $m.dst -Parent) | Out-Null
        try {
            Move-Item -Force -Path $m.src -Destination $m.dst
            $moved += $m.dst
            Write-Host "Moved '$($m.src)' -> '$($m.dst)'"
        } catch {
            Write-Warning "Failed to move $($m.src): $_"
        }
    } else {
        Write-Host "Not found: $($m.src)"
    }
}

# Move patterns: coverage*.xml, pytest*.txt, pytest_*.txt, *.log
$patterns = @('coverage*.xml','pytest*.txt','pytest_*.txt','*.log')
foreach ($p in $patterns) {
    Get-ChildItem -Path $repoRoot -Recurse -Include $p -File -ErrorAction SilentlyContinue | ForEach-Object {
        $target = Join-Path $reportsDir $_.Name
        try {
            Move-Item -Force $_.FullName $target
            $moved += $target
            Write-Host "Moved '$($_.FullName)' -> '$target'"
        } catch {
            Write-Warning "Failed to move $($_.FullName): $_"
        }
    }
}

# Summary
if ($moved.Count -gt 0) {
    Write-Host "\nSummary: moved $($moved.Count) items into '$reportsDir'"
    $moved | ForEach-Object { Write-Host " - $_" }
} else {
    Write-Host "No artifacts found/moved. Reports dir contains:"; Get-ChildItem $reportsDir -Recurse | ForEach-Object { Write-Host $_.FullName }
}

Exit 0
