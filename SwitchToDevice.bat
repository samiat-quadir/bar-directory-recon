@echo off
REM SwitchToDevice.bat
REM This script facilitates switching between devices by performing necessary checks and updates

echo ===================================================
echo   Device Transition Assistant
echo ===================================================
echo.

setlocal enabledelayedexpansion

set "PROJECT_ROOT=%~dp0"
if %PROJECT_ROOT:~-1%==\ set PROJECT_ROOT=%PROJECT_ROOT:~0,-1%

REM Determine which action to take
if "%1"=="" goto MENU
if /i "%1"=="desktop" goto DESKTOP
if /i "%1"=="laptop" goto LAPTOP
if /i "%1"=="test" goto TEST
if /i "%1"=="checklist" goto CHECKLIST
goto MENU

:MENU
echo Choose the device you're switching to:
echo.
echo  [1] Work Desktop (samq)
echo  [2] Laptop (samqu)
echo  [3] Run Device Compatibility Test
echo  [4] Show Cross-Device Checklist
echo  [5] Exit
echo.
set /p CHOICE=Enter your choice (1-5):

if "%CHOICE%"=="1" goto DESKTOP
if "%CHOICE%"=="2" goto LAPTOP
if "%CHOICE%"=="3" goto TEST
if "%CHOICE%"=="4" goto CHECKLIST
if "%CHOICE%"=="5" goto END
echo Invalid choice. Please try again.
goto MENU

:DESKTOP
echo.
echo Preparing for transition to WORK DESKTOP (samq)...
echo.

REM Run path scan
echo Running path scan...
call "%PROJECT_ROOT%\ScanPaths.bat"

REM Check virtual environment
echo Checking virtual environment...
call "%PROJECT_ROOT%\UpdateVenvCrossDevice.bat"

REM Show Git instructions
echo.
echo === Git Instructions ===
echo Before leaving this device:
echo   1. Commit your changes:
echo      git add .
echo      git commit -m "Pre-transition checkpoint"
echo   2. Push your changes:
echo      git push
echo.
echo On the desktop (samq):
echo   1. Pull the latest changes:
echo      git pull
echo   2. Run the device detection:
echo      .\CrossDeviceLauncher.bat
echo.

type "%PROJECT_ROOT%\DEVICE_TRANSITION_GUIDE.md"

goto END

:LAPTOP
echo.
echo Preparing for transition to LAPTOP (samqu)...
echo.

REM Run path scan
echo Running path scan...
call "%PROJECT_ROOT%\ScanPaths.bat"

REM Check virtual environment
echo Checking virtual environment...
call "%PROJECT_ROOT%\UpdateVenvCrossDevice.bat"

REM Show Git instructions
echo.
echo === Git Instructions ===
echo Before leaving this device:
echo   1. Commit your changes:
echo      git add .
echo      git commit -m "Pre-transition checkpoint"
echo   2. Push your changes:
echo      git push
echo.
echo On the laptop (samqu):
echo   1. Pull the latest changes:
echo      git pull
echo   2. Run the device detection:
echo      .\CrossDeviceLauncher.bat
echo.

type "%PROJECT_ROOT%\DEVICE_TRANSITION_GUIDE.md"

goto END

:TEST
echo.
echo Running device compatibility test...
echo.

powershell -ExecutionPolicy Bypass -NoProfile -File "%PROJECT_ROOT%\Test-CrossDevicePaths.ps1" -Verbose

goto END

:CHECKLIST
echo.
echo === Cross-Device Development Checklist ===
echo.

type "%PROJECT_ROOT%\CROSS_DEVICE_CHECKLIST.md"

goto END

:END
echo.
echo Press any key to exit...
pause >nul
