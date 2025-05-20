@echo off
REM ====================================================================
REM ValidateCrossDeviceSetup.bat
REM Tests cross-device path resolution and compatibility
REM ====================================================================

echo ===================================================
echo   Cross-Device Setup Validation Tool
echo ===================================================
echo.

REM Store the current directory
set PROJECT_ROOT=%~dp0
if %PROJECT_ROOT:~-1%==\ set PROJECT_ROOT=%PROJECT_ROOT:~0,-1%

REM Check if PowerShell is available
where powershell >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: PowerShell is not available on this system.
    echo This script requires PowerShell to run.
    exit /b 1
)

REM Check if Python is available
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not available on this system.
    echo This script requires Python to run.
    exit /b 1
)

REM PHASE 1: Check for required files
echo.
echo PHASE 1: Checking for required files...
set MISSING_FILES=0

if not exist "%PROJECT_ROOT%\tools\DevicePathResolver.ps1" (
    echo ERROR: Missing DevicePathResolver.ps1
    set /a MISSING_FILES+=1
)

if not exist "%PROJECT_ROOT%\tools\device_path_resolver.py" (
    echo ERROR: Missing device_path_resolver.py
    set /a MISSING_FILES+=1
)

if not exist "%PROJECT_ROOT%\CrossDeviceLauncher.bat" (
    echo ERROR: Missing CrossDeviceLauncher.bat
    set /a MISSING_FILES+=1
)

if %MISSING_FILES% GTR 0 (
    echo.
    echo ERROR: Required files are missing. Please restore them before continuing.
    exit /b 1
) else (
    echo All required files are present.
)

REM PHASE 2: Test PowerShell path resolver
echo.
echo PHASE 2: Testing PowerShell path resolver...
echo.
echo Running PowerShell path resolver...
powershell -NoProfile -ExecutionPolicy Bypass -Command "& {. '%PROJECT_ROOT%\tools\DevicePathResolver.ps1'; $onedrivePath = Get-OneDrivePath; Write-Host 'Detected OneDrive path:' $onedrivePath; $projectRoot = Get-ProjectRootPath; Write-Host 'Detected project root:' $projectRoot; Write-Host 'Current device:' $env:COMPUTERNAME; }"

REM PHASE 3: Test Python path resolver
echo.
echo PHASE 3: Testing Python path resolver...
echo.
echo Running Python path resolver...
python "%PROJECT_ROOT%\tools\device_path_resolver.py"

REM PHASE 4: Verify environment consistency
echo.
echo PHASE 4: Verifying environment consistency...
echo.
echo Checking configuration directory...
if not exist "%PROJECT_ROOT%\config" (
    echo Creating config directory...
    mkdir "%PROJECT_ROOT%\config"
)

echo.
echo Registering current device...
powershell -NoProfile -ExecutionPolicy Bypass -Command "& {. '%PROJECT_ROOT%\tools\DevicePathResolver.ps1'; Register-CurrentDevice -Force; }"

echo.
echo Validation complete!
echo If any issues were reported, please check the CROSS_DEVICE_GUIDE.md file.
echo.
echo You can now use either of these launchers:
echo  - CrossDeviceLauncher.bat - For general access to all features
echo  - UpdateVenvCrossDevice.bat - To update virtual environment activation scripts
echo.
echo Happy developing!
exit /b 0
