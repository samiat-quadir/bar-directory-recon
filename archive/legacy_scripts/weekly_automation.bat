@echo off
setlocal EnableDelayedExpansion

rem Weekly Lead Generation Automation Script
rem Run this script weekly to automatically generate leads across all industries

echo ============================================
echo    Universal Lead Generation Automation
echo    Started: %date% %time%
echo ============================================

cd /d "C:\Code\bar-directory-recon"

rem Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv .venv
    exit /b 1
)

rem Activate virtual environment
call .venv\Scripts\activate.bat

rem Set default values
set "CITY=Miami"
set "STATE=FL"
set "MAX_RECORDS=100"

rem Allow command line overrides
if not "%1"=="" set "CITY=%1"
if not "%2"=="" set "STATE=%2"
if not "%3"=="" set "MAX_RECORDS=%3"

echo Target City: %CITY%
echo Target State: %STATE%
echo Max Records: %MAX_RECORDS%
echo.

rem Create logs directory
if not exist "logs" mkdir logs

rem Run multi-industry lead generation
echo [%time%] Starting lead generation...
python universal_automation.py --industry all --city "%CITY%" --state "%STATE%" --max-records %MAX_RECORDS% >> logs/weekly_automation.log 2>&1

if errorlevel 1 (
    echo ERROR: Lead generation failed!
    goto :error
)

echo [%time%] Lead generation completed successfully!

rem Score and prioritize leads
echo [%time%] Starting lead scoring...
python score_leads.py outputs/ --output priority_leads.csv --top 20 >> logs/weekly_automation.log 2>&1

if errorlevel 1 (
    echo WARNING: Lead scoring failed, but continuing...
) else (
    echo [%time%] Lead scoring completed successfully!
)

rem Optional: Git commit and push results
echo [%time%] Committing results to git...
git add . >> logs/weekly_automation.log 2>&1
git commit -m "Weekly automated lead generation - %date%" >> logs/weekly_automation.log 2>&1

if errorlevel 1 (
    echo NOTE: Git commit failed (possibly no changes)
) else (
    echo [%time%] Git commit successful!

    rem Push to remote (optional)
    git push >> logs/weekly_automation.log 2>&1
    if errorlevel 1 (
        echo WARNING: Git push failed
    ) else (
        echo [%time%] Git push successful!
    )
)

echo.
echo ============================================
echo    Automation completed successfully!
echo    Finished: %date% %time%
echo ============================================

rem Generate summary report
echo Weekly Automation Summary > weekly_summary.txt
echo Date: %date% %time% >> weekly_summary.txt
echo Target: %CITY%, %STATE% >> weekly_summary.txt
echo Max Records: %MAX_RECORDS% >> weekly_summary.txt
echo. >> weekly_summary.txt

rem Count output files
for /d %%D in (outputs\*) do (
    for /f %%F in ('dir /b "%%D\*\*.csv" 2^>nul ^| find /c /v ""') do (
        echo Industry %%~nxD: %%F files >> weekly_summary.txt
    )
)

echo. >> weekly_summary.txt
echo Check logs/weekly_automation.log for detailed output >> weekly_summary.txt

goto :end

:error
echo.
echo ============================================
echo    Automation FAILED!
echo    Check logs/weekly_automation.log
echo ============================================
exit /b 1

:end
endlocal
