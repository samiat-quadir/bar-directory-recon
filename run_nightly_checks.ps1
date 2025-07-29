# Nightly Automated Checks for Bar Directory Recon
# =================================================

param(
    [string]$LogPath = "logs\nightly_checks_$(Get-Date -Format 'yyyy-MM-dd').log",
    [switch]$Verbose
)

$ErrorActionPreference = "Continue"
$StartTime = Get-Date

function Write-Log {
    param($Message, $Level = "INFO")
    $Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $LogEntry = "[$Timestamp] [$Level] $Message"
    Write-Output $LogEntry
    Add-Content -Path $LogPath -Value $LogEntry
}

function Test-PythonEnvironment {
    Write-Log "Testing Python environment..." "INFO"

    try {
        # Activate virtual environment
        & ".venv\Scripts\Activate.ps1"

        # Check Python version
        $PythonVersion = & python --version 2>&1
        Write-Log "Python version: $PythonVersion" "INFO"

        # Check key packages
        $RequiredPackages = @("pytest", "requests", "pandas", "beautifulsoup4", "selenium")
        foreach ($Package in $RequiredPackages) {
            $PackageInfo = & python -m pip show $Package 2>&1
            if ($LASTEXITCODE -eq 0) {
                $Version = ($PackageInfo | Select-String "Version:").ToString().Split(":")[1].Trim()
                Write-Log "Package $Package: $Version" "INFO"
            }
            else {
                Write-Log "Package $Package: NOT FOUND" "ERROR"
            }
        }

        return $true
    }
    catch {
        Write-Log "Python environment test failed: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Run-TestSuite {
    Write-Log "Running test suite..." "INFO"

    try {
        # Run pytest with coverage
        $TestOutput = & python -m pytest -v --tb=short --cov=. --cov-report=term-missing 2>&1
        $TestExitCode = $LASTEXITCODE

        # Log test output
        $TestOutput | ForEach-Object { Write-Log $_ "TEST" }

        if ($TestExitCode -eq 0) {
            Write-Log "All tests passed successfully" "INFO"
            return $true
        }
        else {
            Write-Log "Some tests failed (exit code: $TestExitCode)" "ERROR"
            return $false
        }
    }
    catch {
        Write-Log "Test suite execution failed: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Run-SecurityScan {
    Write-Log "Running security scan..." "INFO"

    try {
        if (Test-Path "tools\secrets_scan.py") {
            $ScanOutput = & python tools\secrets_scan.py --directory . --severity medium 2>&1
            $ScanExitCode = $LASTEXITCODE

            $ScanOutput | ForEach-Object { Write-Log $_ "SECURITY" }

            if ($ScanExitCode -eq 0) {
                Write-Log "Security scan completed - no issues found" "INFO"
                return $true
            }
            else {
                Write-Log "Security scan found issues (exit code: $ScanExitCode)" "WARN"
                return $false
            }
        }
        else {
            Write-Log "Security scan script not found, skipping..." "WARN"
            return $true
        }
    }
    catch {
        Write-Log "Security scan failed: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Run-LinternightlyChecks {
    Write-Log "Running code quality checks..." "INFO"

    try {
        # Run flake8
        $FlakeOutput = & python -m flake8 --max-line-length=120 --ignore=E203, W503 . 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Log "Flake8: PASSED" "INFO"
        }
        else {
            Write-Log "Flake8: FAILED" "ERROR"
            $FlakeOutput | ForEach-Object { Write-Log $_ "LINT" }
        }

        # Run mypy if available
        $MypyOutput = & python -m mypy --config-file pyproject.toml . 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Log "MyPy: PASSED" "INFO"
        }
        else {
            Write-Log "MyPy: FAILED" "ERROR"
            $MypyOutput | ForEach-Object { Write-Log $_ "TYPE" }
        }

        return $true
    }
    catch {
        Write-Log "Code quality checks failed: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Check-GitStatus {
    Write-Log "Checking Git repository status..." "INFO"

    try {
        # Check for uncommitted changes
        $GitStatus = & git status --porcelain 2>&1
        if ($GitStatus) {
            Write-Log "Uncommitted changes detected:" "WARN"
            $GitStatus | ForEach-Object { Write-Log "  $_" "WARN" }
        }
        else {
            Write-Log "Git repository is clean" "INFO"
        }

        # Check remote sync status
        & git fetch origin 2>&1 | Out-Null
        $BehindCommits = & git rev-list HEAD..origin/main --count 2>&1
        $AheadCommits = & git rev-list origin/main..HEAD --count 2>&1

        if ($BehindCommits -gt 0) {
            Write-Log "Local branch is $BehindCommits commits behind origin/main" "WARN"
        }
        if ($AheadCommits -gt 0) {
            Write-Log "Local branch is $AheadCommits commits ahead of origin/main" "INFO"
        }
        if ($BehindCommits -eq 0 -and $AheadCommits -eq 0) {
            Write-Log "Local branch is up to date with origin/main" "INFO"
        }

        return $true
    }
    catch {
        Write-Log "Git status check failed: $($_.Exception.Message)" "ERROR"
        return $false
    }
}

function Generate-HealthReport {
    param($Results)

    Write-Log "Generating health report..." "INFO"

    $ReportPath = "logs\nightly_health_report_$(Get-Date -Format 'yyyy-MM-dd').html"

    $Html = @"
<!DOCTYPE html>
<html>
<head>
    <title>Nightly Health Report - $(Get-Date -Format 'yyyy-MM-dd')</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { background-color: #f0f0f0; padding: 20px; border-radius: 5px; }
        .success { color: green; font-weight: bold; }
        .warning { color: orange; font-weight: bold; }
        .error { color: red; font-weight: bold; }
        .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }
        .timestamp { color: #666; font-size: 0.9em; }
    </style>
</head>
<body>
    <div class="header">
        <h1>Bar Directory Recon - Nightly Health Report</h1>
        <p class="timestamp">Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')</p>
    </div>

    <div class="section">
        <h2>Summary</h2>
        <ul>
            <li>Python Environment: <span class="$(if($Results.PythonEnv) {'success'} else {'error'})">$(if($Results.PythonEnv) {'✅ PASS'} else {'❌ FAIL'})</span></li>
            <li>Test Suite: <span class="$(if($Results.Tests) {'success'} else {'error'})">$(if($Results.Tests) {'✅ PASS'} else {'❌ FAIL'})</span></li>
            <li>Security Scan: <span class="$(if($Results.Security) {'success'} else {'warning'})">$(if($Results.Security) {'✅ PASS'} else {'⚠️ WARN'})</span></li>
            <li>Code Quality: <span class="$(if($Results.Quality) {'success'} else {'warning'})">$(if($Results.Quality) {'✅ PASS'} else {'⚠️ WARN'})</span></li>
            <li>Git Status: <span class="$(if($Results.Git) {'success'} else {'warning'})">$(if($Results.Git) {'✅ PASS'} else {'⚠️ WARN'})</span></li>
        </ul>
    </div>

    <div class="section">
        <h2>Execution Time</h2>
        <p>Total Duration: $((Get-Date) - $StartTime)</p>
    </div>

    <div class="section">
        <h2>Detailed Logs</h2>
        <p>Full logs available at: <code>$LogPath</code></p>
    </div>

    <div class="section">
        <h2>Next Actions</h2>
        <ul>
"@

    if (-not $Results.PythonEnv) {
        $Html += "<li class='error'>Fix Python environment configuration</li>"
    }
    if (-not $Results.Tests) {
        $Html += "<li class='error'>Investigate and fix failing tests</li>"
    }
    if (-not $Results.Security) {
        $Html += "<li class='warning'>Review security scan results</li>"
    }
    if (-not $Results.Quality) {
        $Html += "<li class='warning'>Address code quality issues</li>"
    }
    if (-not $Results.Git) {
        $Html += "<li class='warning'>Sync Git repository</li>"
    }

    if ($Results.PythonEnv -and $Results.Tests -and $Results.Security -and $Results.Quality -and $Results.Git) {
        $Html += "<li class='success'>All systems healthy - no action required</li>"
    }

    $Html += @"
        </ul>
    </div>
</body>
</html>
"@

    $Html | Out-File -FilePath $ReportPath -Encoding UTF8
    Write-Log "Health report generated: $ReportPath" "INFO"
}

# Main execution
Write-Log "Starting nightly automated checks..." "INFO"
Write-Log "Working directory: $(Get-Location)" "INFO"

# Ensure logs directory exists
if (-not (Test-Path "logs")) {
    New-Item -ItemType Directory -Path "logs" -Force | Out-Null
}

# Change to project directory
Set-Location $PSScriptRoot

# Execute all checks
$Results = @{
    PythonEnv = Test-PythonEnvironment
    Tests     = Run-TestSuite
    Security  = Run-SecurityScan
    Quality   = Run-LinternightlyChecks
    Git       = Check-GitStatus
}

# Generate summary
$SuccessCount = ($Results.Values | Where-Object { $_ -eq $true }).Count
$TotalChecks = $Results.Count
$Duration = (Get-Date) - $StartTime

Write-Log "=" * 50 "INFO"
Write-Log "NIGHTLY CHECKS COMPLETED" "INFO"
Write-Log "Successful checks: $SuccessCount/$TotalChecks" "INFO"
Write-Log "Total duration: $Duration" "INFO"
Write-Log "=" * 50 "INFO"

# Generate health report
Generate-HealthReport -Results $Results

# Set exit code based on critical failures
if (-not $Results.PythonEnv -or -not $Results.Tests) {
    Write-Log "Critical failures detected - exit code 1" "ERROR"
    exit 1
}
else {
    Write-Log "Nightly checks completed successfully" "INFO"
    exit 0
}
