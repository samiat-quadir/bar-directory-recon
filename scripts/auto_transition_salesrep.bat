@echo off
REM ====================================================================
REM AutoTransitionToSALESREP.bat
REM Automates the transition process to the SALESREP device
REM ====================================================================

setlocal enabledelayedexpansion

REM Set project root path
set "PROJECT_ROOT=%~dp0"
if %PROJECT_ROOT:~-1%==\ set "PROJECT_ROOT=%PROJECT_ROOT:~0,-1%"

echo ===================================================
echo     Automated Transition to SALESREP Device
echo ===================================================
echo.

REM Step 1: Fix path resolver
echo Step 1: Fixing device_path_resolver.py for SALESREP...
call "%PROJECT_ROOT%\FixPathResolverForSALESREP.bat"
if %ERRORLEVEL% NEQ 0 (
    echo Failed to fix path resolver. Please fix manually and try again.
    pause
    exit /b 1
)
echo.

REM Step 2: Scan and fix hardcoded paths
echo Step 2: Scanning and fixing hardcoded paths...
call "%PROJECT_ROOT%\ScanPaths.bat" --fix
echo.

REM Step 3: Fix virtual environment paths
echo Step 3: Fixing virtual environment paths...
call "%PROJECT_ROOT%\Fix-VenvPath.bat"
echo.

REM Step 4: Create device profile
echo Step 4: Creating SALESREP device profile...
python "%PROJECT_ROOT%\tools\create_device_profile.py" --device SALESREP
if %ERRORLEVEL% NEQ 0 (
    echo Failed to create device profile. Continuing anyway...
)
echo.

REM Step 5: Run full system check
echo Step 5: Running full system check...
powershell -ExecutionPolicy Bypass -NoProfile -File "%PROJECT_ROOT%\Test-CrossDevicePaths.ps1" -Verbose
echo.

REM Step 6: Create summary report
echo Step 6: Creating transition summary...
echo # SALESREP Transition Summary > "%PROJECT_ROOT%\logs\SALESREP_TRANSITION_REPORT.md"
echo. >> "%PROJECT_ROOT%\logs\SALESREP_TRANSITION_REPORT.md"
echo **Date:** %date% >> "%PROJECT_ROOT%\logs\SALESREP_TRANSITION_REPORT.md"
echo **Time:** %time% >> "%PROJECT_ROOT%\logs\SALESREP_TRANSITION_REPORT.md"
echo. >> "%PROJECT_ROOT%\logs\SALESREP_TRANSITION_REPORT.md"
echo ## Transition Steps Completed >> "%PROJECT_ROOT%\logs\SALESREP_TRANSITION_REPORT.md"
echo. >> "%PROJECT_ROOT%\logs\SALESREP_TRANSITION_REPORT.md"
echo - Fixed device_path_resolver.py for SALESREP >> "%PROJECT_ROOT%\logs\SALESREP_TRANSITION_REPORT.md"
echo - Scanned and fixed hardcoded paths >> "%PROJECT_ROOT%\logs\SALESREP_TRANSITION_REPORT.md"
echo - Fixed virtual environment paths >> "%PROJECT_ROOT%\logs\SALESREP_TRANSITION_REPORT.md"
echo - Created SALESREP device profile >> "%PROJECT_ROOT%\logs\SALESREP_TRANSITION_REPORT.md"
echo - Ran full system check >> "%PROJECT_ROOT%\logs\SALESREP_TRANSITION_REPORT.md"
echo. >> "%PROJECT_ROOT%\logs\SALESREP_TRANSITION_REPORT.md"
echo ## Next Steps >> "%PROJECT_ROOT%\logs\SALESREP_TRANSITION_REPORT.md"
echo. >> "%PROJECT_ROOT%\logs\SALESREP_TRANSITION_REPORT.md"
echo 1. Open VS Code with OpenInVSCode.bat >> "%PROJECT_ROOT%\logs\SALESREP_TRANSITION_REPORT.md"
echo 2. Verify GitHub Copilot integration >> "%PROJECT_ROOT%\logs\SALESREP_TRANSITION_REPORT.md"
echo 3. Review SALESREP_TRANSITION_GUIDE.md for detailed instructions >> "%PROJECT_ROOT%\logs\SALESREP_TRANSITION_REPORT.md"
echo. >> "%PROJECT_ROOT%\logs\SALESREP_TRANSITION_REPORT.md"

echo ===================================================
echo     Transition to SALESREP Complete
echo ===================================================
echo.
echo All transition steps have been completed.
echo A transition report has been created at:
echo %PROJECT_ROOT%\logs\SALESREP_TRANSITION_REPORT.md
echo.
echo Next steps:
echo 1. Open the project in VS Code with OpenInVSCode.bat
echo 2. Verify GitHub Copilot integration
echo 3. Review SALESREP_TRANSITION_GUIDE.md for detailed instructions
echo.
echo For any issues, refer to the troubleshooting section
echo in the SALESREP_TRANSITION_GUIDE.md file.
echo.

pause
