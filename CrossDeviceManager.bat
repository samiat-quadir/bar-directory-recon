@echo off
REM ====================================================================
REM CrossDeviceManager.bat
REM Comprehensive cross-device management tool for OneDrive development
REM ====================================================================

setlocal enabledelayedexpansion

REM Set project root path
set "PROJECT_ROOT=%~dp0"
if %PROJECT_ROOT:~-1%==\ set "PROJECT_ROOT=%PROJECT_ROOT:~0,-1%"

REM Banner
echo ===================================================
echo     OneDrive Cross-Device Management System
echo ===================================================
echo.

REM Detect the current device
for /f "tokens=*" %%a in ('powershell -ExecutionPolicy Bypass -NoProfile -Command "$env:COMPUTERNAME"') do set CURRENT_DEVICE=%%a
for /f "tokens=*" %%a in ('powershell -ExecutionPolicy Bypass -NoProfile -Command "$env:USERNAME"') do set CURRENT_USER=%%a

echo Current device: %CURRENT_DEVICE%
echo Current user: %CURRENT_USER%
echo.

REM Display menu
:MENU
echo Choose an action:
echo.
echo  [1] Check device compatibility status
echo  [2] Fix virtual environment paths
echo  [3] Scan for hardcoded paths
echo  [4] Fix hardcoded paths (automatic)
echo  [5] Switch to another device
echo  [6] Run full system check
echo  [7] Update VS Code configuration
echo  [8] Run OneDrive automation
echo  [9] Exit
echo.
set /p CHOICE=Enter your choice (1-9):

if "%CHOICE%"=="1" goto CHECK_STATUS
if "%CHOICE%"=="2" goto FIX_VENV
if "%CHOICE%"=="3" goto SCAN_PATHS
if "%CHOICE%"=="4" goto FIX_PATHS
if "%CHOICE%"=="5" goto SWITCH_DEVICE
if "%CHOICE%"=="6" goto FULL_CHECK
if "%CHOICE%"=="7" goto UPDATE_VSCODE
if "%CHOICE%"=="8" goto RUN_ONEDRIVE
if "%CHOICE%"=="9" goto EXIT
echo Invalid choice. Please try again.
goto MENU

:CHECK_STATUS
echo.
echo ===================================================
echo     Checking Device Compatibility Status
echo ===================================================
echo.
powershell -ExecutionPolicy Bypass -NoProfile -File "%PROJECT_ROOT%\Test-CrossDevicePaths.ps1" -Verbose
pause
goto MENU

:FIX_VENV
echo.
echo ===================================================
echo     Fixing Virtual Environment Paths
echo ===================================================
echo.
call "%PROJECT_ROOT%\Fix-VenvPath.bat"
goto MENU

:SCAN_PATHS
echo.
echo ===================================================
echo     Scanning for Hardcoded Paths
echo ===================================================
echo.
call "%PROJECT_ROOT%\ScanPaths.bat"
goto MENU

:FIX_PATHS
echo.
echo ===================================================
echo     Fixing Hardcoded Paths (Automatic)
echo ===================================================
echo.
call "%PROJECT_ROOT%\ScanPaths.bat" --fix
goto MENU

:SWITCH_DEVICE
echo.
echo ===================================================
echo     Switching to Another Device
echo ===================================================
echo.
call "%PROJECT_ROOT%\SwitchToDevice.bat"
goto MENU

:FULL_CHECK
echo.
echo ===================================================
echo     Running Full System Check
echo ===================================================
echo.
echo Step 1: Testing cross-device paths...
powershell -ExecutionPolicy Bypass -NoProfile -File "%PROJECT_ROOT%\Test-CrossDevicePaths.ps1" -Verbose
echo.
echo Step 2: Checking for hardcoded paths...
call "%PROJECT_ROOT%\ScanPaths.bat"
echo.
echo Step 3: Verifying virtual environment...
call "%PROJECT_ROOT%\Fix-VenvPath.bat"
echo.
echo Step 4: Checking VS Code configuration...
powershell -ExecutionPolicy Bypass -NoProfile -Command "& { . '%PROJECT_ROOT%\tools\AutoDeviceSetup.ps1' }"
echo.
echo Full system check complete.
pause
goto MENU

:UPDATE_VSCODE
echo.
echo ===================================================
echo     Updating VS Code Configuration
echo ===================================================
echo.
powershell -ExecutionPolicy Bypass -NoProfile -Command "& { . '%PROJECT_ROOT%\tools\AutoDeviceSetup.ps1' }"
echo.
echo VS Code configuration updated.
pause
goto MENU

:RUN_ONEDRIVE
echo.
echo ===================================================
echo     Running OneDrive Automation
echo ===================================================
echo.
powershell -ExecutionPolicy Bypass -NoProfile -File "%PROJECT_ROOT%\OneDriveAutomation.ps1"
pause
goto MENU

:EXIT
echo.
echo Exiting Cross-Device Manager...
endlocal
exit /b
