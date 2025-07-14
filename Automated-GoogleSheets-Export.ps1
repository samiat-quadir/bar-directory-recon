# Universal Lead Generation Automation - Scheduled Google Sheets Export
# PowerShell script for unattended operation with Google Sheets integration

param(
    [string]$Industry = "all",
    [string]$City = "",
    [string]$State = "",
    [int]$MaxRecords = 50,
    [string]$GoogleSheetId = "",
    [string]$CredentialsPath = "",
    [switch]$TestMode,
    [switch]$Verbose
)

# Configuration
$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$LogsDir = Join-Path $ProjectRoot "logs"
$OutputsDir = Join-Path $ProjectRoot "outputs"
$Timestamp = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$LogFile = Join-Path $LogsDir "automation_$Timestamp.log"

# Ensure directories exist
if (-not (Test-Path $LogsDir)) {
    New-Item -ItemType Directory -Path $LogsDir -Force | Out-Null
}
if (-not (Test-Path $OutputsDir)) {
    New-Item -ItemType Directory -Path $OutputsDir -Force | Out-Null
}

# Logging function
function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $LogMessage = "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') [$Level] $Message"
    Write-Host $LogMessage
    Add-Content -Path $LogFile -Value $LogMessage
}

Write-Log "Starting Universal Lead Generation Automation" "INFO"
Write-Log "Project Root: $ProjectRoot" "INFO"
Write-Log "Logs Directory: $LogsDir" "INFO"

# Environment variables for Google Sheets
if ($GoogleSheetId) {
    $env:DEFAULT_GOOGLE_SHEET_ID = $GoogleSheetId
    Write-Log "Set Google Sheet ID: $GoogleSheetId" "INFO"
}

if ($CredentialsPath) {
    $env:GOOGLE_CREDENTIALS_PATH = $CredentialsPath
    Write-Log "Set credentials path: $CredentialsPath" "INFO"
}
else {
    # Look for OAuth credentials file in project root
    $DefaultCredentials = Get-ChildItem -Path $ProjectRoot -Filter "client_secret_*.json" | Select-Object -First 1
    if ($DefaultCredentials) {
        $env:GOOGLE_CREDENTIALS_PATH = $DefaultCredentials.FullName
        Write-Log "Found credentials file: $($DefaultCredentials.FullName)" "INFO"
    }
}

# Build unified CLI command arguments
$PythonArgs = @()
$PythonArgs += "unified_scraper.py", "scrape", "--config-dir", "config"

if ($MaxRecords -gt 0) {
    $PythonArgs += "--max-records", $MaxRecords
}
if ($TestMode) {
    $PythonArgs += "--test"
}
if ($Verbose) {
    $PythonArgs += "--verbose"
}
else {
    $PythonArgs += "--quiet"
}

# Add configuration names based on industry
if ($Industry -eq "all" -or $Industry -eq "lawyers") {
    $LawyerArgs = $PythonArgs + @("lawyer_directory")
    Write-Log "Lawyer scraping command: python $($LawyerArgs -join ' ')" "INFO"
}
if ($Industry -eq "all" -or $Industry -eq "realtors") {
    $RealtorArgs = $PythonArgs + @("realtor_directory")
    Write-Log "Realtor scraping command: python $($RealtorArgs -join ' ')" "INFO"
}

try {
    # Change to project directory
    Set-Location $ProjectRoot

    # Run the automation for each configured industry
    Write-Log "Executing lead generation automation..." "INFO"

    $SuccessCount = 0
    $TotalCount = 0

    # Execute lawyer scraping if applicable
    if ($Industry -eq "all" -or $Industry -eq "lawyers") {
        $TotalCount++
        Write-Log "Starting lawyer directory scraping..." "INFO"

        $LawyerArgs = $PythonArgs + @("lawyer_directory")
        $Process = Start-Process -FilePath "python" -ArgumentList $LawyerArgs -PassThru -Wait -NoNewWindow -RedirectStandardOutput "$LogsDir\lawyers_output_$Timestamp.log" -RedirectStandardError "$LogsDir\lawyers_error_$Timestamp.log"

        if ($Process.ExitCode -eq 0) {
            Write-Log "Lawyer directory scraping completed successfully!" "SUCCESS"
            $SuccessCount++
        }
        else {
            Write-Log "Lawyer directory scraping failed with exit code: $($Process.ExitCode)" "ERROR"
        }
    }

    # Execute realtor scraping if applicable
    if ($Industry -eq "all" -or $Industry -eq "realtors") {
        $TotalCount++
        Write-Log "Starting realtor directory scraping..." "INFO"

        $RealtorArgs = $PythonArgs + @("realtor_directory")
        $Process = Start-Process -FilePath "python" -ArgumentList $RealtorArgs -PassThru -Wait -NoNewWindow -RedirectStandardOutput "$LogsDir\realtors_output_$Timestamp.log" -RedirectStandardError "$LogsDir\realtors_error_$Timestamp.log"

        if ($Process.ExitCode -eq 0) {
            Write-Log "Realtor directory scraping completed successfully!" "SUCCESS"
            $SuccessCount++
        }
        else {
            Write-Log "Realtor directory scraping failed with exit code: $($Process.ExitCode)" "ERROR"
        }
    }

    # Summary
    Write-Log "Automation Summary: $SuccessCount/$TotalCount processes completed successfully" "INFO"

    if ($SuccessCount -eq $TotalCount) {
        Write-Log "All automation processes completed successfully!" "SUCCESS"

        # Check for new output files
        $RecentFiles = Get-ChildItem -Path $OutputsDir -Recurse -File | Where-Object { $_.LastWriteTime -gt (Get-Date).AddMinutes(-10) }
        if ($RecentFiles) {
            Write-Log "Recent output files created:" "INFO"
            $RecentFiles | ForEach-Object { Write-Log "  - $($_.FullName)" "INFO" }
        }

        # Check for Google Sheets link in output
        if ($PythonOutput -and ($PythonOutput | Where-Object { $_ -match "https://docs.google.com/spreadsheets" })) {
            $SheetLinks = $PythonOutput | Where-Object { $_ -match "https://docs.google.com/spreadsheets" }
            Write-Log "Google Sheets links:" "SUCCESS"
            $SheetLinks | ForEach-Object { Write-Log "  - $_" "SUCCESS" }
        }

    }
    else {
        Write-Log "Automation failed with exit code: $ExitCode" "ERROR"
        exit $ExitCode
    }

}
catch {
    Write-Log "Error executing automation: $($_.Exception.Message)" "ERROR"
    Write-Log "Stack trace: $($_.Exception.StackTrace)" "ERROR"
    exit 1
}

# Cleanup old log files (keep last 30 days)
try {
    $OldLogs = Get-ChildItem -Path $LogsDir -Filter "*.log" | Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) }
    if ($OldLogs) {
        Write-Log "Cleaning up $($OldLogs.Count) old log files" "INFO"
        $OldLogs | Remove-Item -Force
    }
}
catch {
    Write-Log "Warning: Could not clean up old logs: $($_.Exception.Message)" "WARNING"
}

Write-Log "Automation script completed" "INFO"
Write-Log "Log file: $LogFile" "INFO"

# Return success
exit 0
