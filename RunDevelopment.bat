@echo off
REM ====================================================================
REM OneDrive Development Environment Launcher
REM This script activates the Python virtual environment for the project
REM and provides options for running various features
REM ====================================================================

echo ===================================================
echo   OneDrive Development Environment Launcher
echo ===================================================
echo.

REM Store the current directory
set PROJECT_ROOT=%~dp0
cd /d "%PROJECT_ROOT%"

REM Activate the virtual environment
echo Activating Python virtual environment...
call .venv\Scripts\activate.bat

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to activate virtual environment.
    echo        Please run fix_venv_activation.bat first.
    goto :end
)

:menu
echo.
echo ===================================================
echo   Main Menu
echo ===================================================
echo.
echo  1. Run OneDrive Automation
echo  2. Run OneDrive Cleanup
echo  3. Run Git Repository Cleanup
echo  4. Run Secrets Scanner
echo  5. Run Environment File Consolidation
echo  6. Run All Tests
echo  7. Open Python Shell in Virtual Environment
echo  0. Exit
echo.
echo ===================================================
echo.

set /p choice="Enter your choice (0-7): "

if "%choice%"=="1" (
    echo Running OneDrive Automation...
    python OneDriveAutomation.ps1
    goto menu
)
if "%choice%"=="2" (
    echo Running OneDrive Cleanup...
    python OneDriveCleanup.ps1
    goto menu
)
if "%choice%"=="3" (
    echo Running Git Repository Cleanup...
    python tools\git_repo_cleanup.ps1
    goto menu
)
if "%choice%"=="4" (
    echo Running Secrets Scanner...
    python tools\secrets_scan.py
    goto menu
)
if "%choice%"=="5" (
    echo Running Environment File Consolidation...
    python tools\consolidate_env_files.ps1
    goto menu
)
if "%choice%"=="6" (
    echo Running All Tests...
    pytest
    goto menu
)
if "%choice%"=="7" (
    echo Opening Python Shell...
    python
    goto menu
)
if "%choice%"=="0" (
    goto end
) else (
    echo Invalid choice! Please try again.
    goto menu
)

:end
echo.
echo Deactivating virtual environment...
call deactivate
echo Goodbye!
exit /b 0
