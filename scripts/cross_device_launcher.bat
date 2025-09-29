@echo off
REM Cross Device Launcher - simplified
setlocal

set "PROJECT_ROOT=%~dp0"
if %PROJECT_ROOT:~-1%==\ set "PROJECT_ROOT=%PROJECT_ROOT:~0,-1%"

REM Launch automation tasks
if "%~1"=="--run" (
    echo Running cross-device task launcher...
    powershell -ExecutionPolicy Bypass -NoProfile -File "%PROJECT_ROOT%\Run-CrossDeviceTask.ps1"
    exit /b
)

echo Usage: cross_device_launcher.bat --run
endlocal
exit /b
