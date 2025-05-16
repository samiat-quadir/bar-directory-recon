@echo off
REM ====================================================================
REM Cross-Device Project Launcher
REM This script detects the correct paths regardless of which device you're on
REM ====================================================================

echo ===================================================
echo   Cross-Device Project Launcher
echo ===================================================
echo.

REM Store the current directory (where this script is located)
set PROJECT_ROOT=%~dp0

REM Remove trailing backslash
if %PROJECT_ROOT:~-1%==\ set PROJECT_ROOT=%PROJECT_ROOT:~0,-1%

REM Output device information
echo Current device: %COMPUTERNAME%
echo Current user: %USERNAME%
echo Project root: %PROJECT_ROOT%
echo.

REM Check if PowerShell is available
where powershell >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo PowerShell is not available on this system.
    echo This script requires PowerShell to run.
    goto :end
)

echo Detecting OneDrive path...
for /f "tokens=*" %%i in ('powershell -NoProfile -ExecutionPolicy Bypass -Command "& {. '%PROJECT_ROOT%\tools\DevicePathResolver.ps1'; Get-OneDrivePath}"') do set ONEDRIVE_PATH=%%i

echo OneDrive path: %ONEDRIVE_PATH%
echo.

:menu
echo ===================================================
echo   Main Menu
echo ===================================================
echo.
echo  1. Run OneDrive Automation
echo  2. Run OneDrive Cleanup
echo  3. Activate Python Virtual Environment
echo  4. Start PowerShell Development Environment
echo  5. Fix Virtual Environment Activation
echo  6. Install Dependencies
echo  7. Register This Device
echo  0. Exit
echo.
echo ===================================================
echo.

set /p choice="Enter your choice (0-7): "

if "%choice%"=="1" (
    echo Running OneDrive Automation...
    powershell -NoProfile -ExecutionPolicy Bypass -File "%PROJECT_ROOT%\OneDriveAutomation.ps1"
    goto menu
)
if "%choice%"=="2" (
    echo Running OneDrive Cleanup...
    powershell -NoProfile -ExecutionPolicy Bypass -File "%PROJECT_ROOT%\OneDriveCleanup.ps1"
    goto menu
)
if "%choice%"=="3" (
    echo Activating Python Virtual Environment...
    call "%PROJECT_ROOT%\activate_venv.bat"
    goto menu
)
if "%choice%"=="4" (
    echo Starting PowerShell Development Environment...
    start "" powershell -NoExit -NoProfile -ExecutionPolicy Bypass -Command "& '%PROJECT_ROOT%\ActivateVenv.ps1'"
    goto menu
)
if "%choice%"=="5" (
    echo Fixing Virtual Environment Activation...
    call "%PROJECT_ROOT%\fix_venv_activation.bat"
    goto menu
)
if "%choice%"=="6" (
    echo Installing Dependencies...
    call "%PROJECT_ROOT%\InstallDependencies.bat"
    goto menu
)
if "%choice%"=="7" (
    echo Registering device...
    powershell -NoProfile -ExecutionPolicy Bypass -Command "& {. '%PROJECT_ROOT%\tools\DevicePathResolver.ps1'; Register-CurrentDevice -Force}"
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
echo Goodbye!
exit /b 0
