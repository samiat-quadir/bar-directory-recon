param(
    [string]$City = "Miami",
    [string]$State = "FL",
    [int]$MaxRecords = 100,
    [switch]$IncludeScoring = $true,
    [switch]$GitCommit = $true,
    [switch]$Verbose = $false
)

# Weekly Lead Generation Automation Script (PowerShell)
# More advanced than the batch version with better error handling

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "   Universal Lead Generation Automation" -ForegroundColor Cyan
Write-Host "   Started: $(Get-Date)" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# Change to project directory
$ProjectPath = "C:\Code\bar-directory-recon"
if (!(Test-Path $ProjectPath)) {
    Write-Error "Project directory not found: $ProjectPath"
    exit 1
}

Set-Location $ProjectPath

# Check virtual environment
$VenvPath = ".\.venv\Scripts\Activate.ps1"
if (!(Test-Path $VenvPath)) {
    Write-Error "Virtual environment not found! Please run: python -m venv .venv"
    exit 1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& $VenvPath

# Display configuration
Write-Host "`nConfiguration:" -ForegroundColor Green
Write-Host "  Target City: $City" -ForegroundColor White
Write-Host "  Target State: $State" -ForegroundColor White
Write-Host "  Max Records: $MaxRecords" -ForegroundColor White
Write-Host "  Include Scoring: $IncludeScoring" -ForegroundColor White
Write-Host "  Git Commit: $GitCommit" -ForegroundColor White
Write-Host ""

# Create logs directory
New-Item -ItemType Directory -Path "logs" -Force | Out-Null

# Start logging
$LogFile = "logs\weekly_automation_$(Get-Date -Format 'yyyy-MM-dd_HH-mm').log"
Start-Transcript -Path $LogFile -Append

try {
    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Starting lead generation..." -ForegroundColor Green

    # Build unified CLI command
    $Command = "python unified_scraper.py scrape --config-dir config --max-records $MaxRecords"
    if ($Verbose) {
        $Command += " --verbose"
    }
    else {
        $Command += " --quiet"
    }

    # Run lead generation for lawyers
    Write-Host "Executing (Lawyers): $Command lawyer_directory" -ForegroundColor Gray
    $LawyerResult = Invoke-Expression "$Command lawyer_directory"

    if ($LASTEXITCODE -ne 0) {
        throw "Lawyer directory scraping failed with exit code $LASTEXITCODE"
    }

    # Run lead generation for realtors
    Write-Host "Executing (Realtors): $Command realtor_directory" -ForegroundColor Gray
    $RealtorResult = Invoke-Expression "$Command realtor_directory"

    if ($LASTEXITCODE -ne 0) {
        throw "Realtor directory scraping failed with exit code $LASTEXITCODE"
    }

    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Lead generation completed successfully!" -ForegroundColor Green

    # Score leads if requested
    if ($IncludeScoring) {
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Starting lead scoring..." -ForegroundColor Green

        $ScoringCommand = "python score_leads.py outputs\ --output priority_leads.csv --top 20"
        Write-Host "Executing: $ScoringCommand" -ForegroundColor Gray

        $ScoringResult = Invoke-Expression $ScoringCommand

        if ($LASTEXITCODE -eq 0) {
            Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Lead scoring completed successfully!" -ForegroundColor Green
        }
        else {
            Write-Warning "Lead scoring failed, but continuing..."
        }
    }

    # Git operations if requested
    if ($GitCommit) {
        Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Committing results to git..." -ForegroundColor Green

        # Check for changes
        $GitStatus = git status --porcelain
        if ($GitStatus) {
            git add .
            $CommitMessage = "Weekly automated lead generation - $(Get-Date -Format 'yyyy-MM-dd')"
            git commit -m $CommitMessage

            if ($LASTEXITCODE -eq 0) {
                Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Git commit successful!" -ForegroundColor Green

                # Try to push
                git push
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "[$(Get-Date -Format 'HH:mm:ss')] Git push successful!" -ForegroundColor Green
                }
                else {
                    Write-Warning "Git push failed - check remote repository"
                }
            }
            else {
                Write-Warning "Git commit failed"
            }
        }
        else {
            Write-Host "No changes detected for git commit" -ForegroundColor Yellow
        }
    }

    Write-Host ""
    Write-Host "============================================" -ForegroundColor Cyan
    Write-Host "   Automation completed successfully!" -ForegroundColor Cyan
    Write-Host "   Finished: $(Get-Date)" -ForegroundColor Cyan
    Write-Host "============================================" -ForegroundColor Cyan

    # Generate summary report
    $SummaryFile = "weekly_summary_$(Get-Date -Format 'yyyy-MM-dd').txt"
    $Summary = @"
Weekly Automation Summary
========================
Date: $(Get-Date)
Target: $City, $State
Max Records: $MaxRecords
Include Scoring: $IncludeScoring
Git Commit: $GitCommit

Output Summary:
"@

    # Count output files by industry
    Get-ChildItem "outputs" -Directory | ForEach-Object {
        $IndustryPath = $_.FullName
        $CsvCount = (Get-ChildItem "$IndustryPath" -Recurse -Filter "*.csv" -ErrorAction SilentlyContinue).Count
        $Summary += "`nIndustry $($_.Name): $CsvCount files"
    }

    $Summary += "`n`nDetailed logs: $LogFile"
    $Summary | Out-File $SummaryFile -Encoding UTF8

    Write-Host "`nSummary saved to: $SummaryFile" -ForegroundColor Green

}
catch {
    Write-Host ""
    Write-Host "============================================" -ForegroundColor Red
    Write-Host "   Automation FAILED!" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   Check logs: $LogFile" -ForegroundColor Red
    Write-Host "============================================" -ForegroundColor Red

    Stop-Transcript
    exit 1
}
finally {
    Stop-Transcript
}

# Optional: Send email notification (requires configuration)
# Send-EmailNotification -Subject "Lead Generation Complete" -Body $Summary
