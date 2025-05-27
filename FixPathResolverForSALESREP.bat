@echo off
REM This batch file fixes the device_path_resolver.py file to ensure it works correctly on the SALESREP device

echo ===================================================
echo     Fix Device Path Resolver for SALESREP
echo ===================================================
echo.

REM Set project root path
set "PROJECT_ROOT=%~dp0"
if %PROJECT_ROOT:~-1%==\ set "PROJECT_ROOT=%PROJECT_ROOT:~0,-1%"

REM Activate virtual environment if it exists
if exist "%PROJECT_ROOT%\.venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call "%PROJECT_ROOT%\.venv\Scripts\activate.bat"
) else (
    echo Virtual environment not found at .venv
    echo Will use system Python instead
)

REM Run the fix script
echo.
echo Running fix_path_resolver.py...
echo.
python "%PROJECT_ROOT%\tools\fix_path_resolver.py"

REM Check if the script succeeded
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ===================================================
    echo     Device Path Resolver Fixed Successfully
    echo ===================================================
    echo.
    echo The device_path_resolver.py has been fixed and configured for the SALESREP device.
    echo.
    echo Next steps:
    echo 1. Run Test-CrossDevicePaths.ps1 to verify paths are working
    echo 2. Run ScanPaths.bat --fix to fix any remaining hardcoded paths
    echo.
) else (
    echo.
    echo ===================================================
    echo     Error: Failed to Fix Device Path Resolver
    echo ===================================================
    echo.
    echo Please check the error messages above and try again.
    echo You may need to manually edit the device_path_resolver.py file.
    echo.
)

pause
