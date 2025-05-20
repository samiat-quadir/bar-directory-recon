@echo off
REM SALESREP VS Code Launcher
REM This script opens VS Code optimized for the SALESREP device

echo Opening VS Code for SALESREP device...

REM Set project root path
set "PROJECT_ROOT=%~dp0"
if %PROJECT_ROOT:~-1%==\ set "PROJECT_ROOT=%PROJECT_ROOT:~0,-1%"

REM Check if device_path_resolver has been fixed
python "%PROJECT_ROOT%\tools\device_path_resolver.py" > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Warning: device_path_resolver.py seems to have issues.
    echo Running fix script first...
    call "%PROJECT_ROOT%\FixPathResolverForSALESREP.bat"
)

REM Open VS Code with proper setup
start "" code "%PROJECT_ROOT%"

echo.
echo VS Code is opening...
echo.
echo IMPORTANT REMINDER:
echo ---------------------
echo When using GitHub Copilot Agent, mention that you are on
echo the SALESREP device with username "samq" to ensure proper
echo path handling in generated code.
echo.

REM Exit after 5 seconds
timeout /t 5 > nul
