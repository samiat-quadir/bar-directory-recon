@echo off
REM CrossDeviceLauncher.bat
REM A helper script to automate cross-device workflows with minimal user input
REM Created for samq device setup

echo ===================================================
echo  CrossDeviceLauncher - Automated Setup Assistant
echo ===================================================
echo.

REM Store the current directory
set PROJECT_ROOT=%~dp0
if %PROJECT_ROOT:~-1%==\ set PROJECT_ROOT=%PROJECT_ROOT:~0,-1%

REM Determine current device
for /f "tokens=*" %%a in ('hostname') do set DEVICE_NAME=%%a
echo Device detected: %DEVICE_NAME%
echo.

REM Activate virtual environment
call "%PROJECT_ROOT%\activate_venv.bat"

REM Check if Git repository needs fixing
git rev-parse --verify HEAD >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: Git repository issue detected
    echo Running Git repository repair...
    git fsck --full
    git gc --aggressive

    REM Check if fix worked
    git rev-parse --verify HEAD >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        echo ERROR: Git repository could not be fixed automatically.
        echo Consider recreating the repository with:
        echo   1. Backup your changes
        echo   2. Delete this folder and clone a fresh copy
        pause
        exit /b 1
    ) else (
        echo Git repository fixed successfully!
    )
)

REM Create or update device profile
echo Checking device profile...
if not exist "%PROJECT_ROOT%\config\device_profile-%DEVICE_NAME%.json" (
    echo Creating device profile for %DEVICE_NAME%...
    powershell -ExecutionPolicy Bypass -NoProfile -Command "& '%PROJECT_ROOT%\tools\CreateDeviceProfile.ps1' -DeviceName '%DEVICE_NAME%'"
)

REM Run cross-device path test
echo Running cross-device path test...
powershell -ExecutionPolicy Bypass -NoProfile -File "%PROJECT_ROOT%\Test-CrossDevicePaths.ps1"

REM Validate environment
echo Validating Python environment...
python "%PROJECT_ROOT%\test_cross_device_env.py"

echo.
echo ===================================================
echo  Setup complete! Environment is ready for use.
echo ===================================================

REM Keep terminal open
cmd /k
