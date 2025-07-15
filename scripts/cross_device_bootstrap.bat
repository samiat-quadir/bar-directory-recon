@echo off
REM Cross-Device Bootstrap Launcher
REM Timestamp: %date% %time%

echo [BOOTSTRAP] Initializing Cross-Device Environment...

REM Activate Virtual Environment
call ".\.venv\Scripts\activate.bat"
if errorlevel 1 (
    echo [ERROR] Virtual environment activation failed.
    goto END
)
echo [BOOTSTRAP] (.venv) Activated Successfully.

REM Run Cross-Device Compatibility Test
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\tools\Test-CrossDeviceCompatibility.ps1"
if errorlevel 1 (
    echo [ERROR] Compatibility test reported issues. Check logs for details.
    goto END
)

REM Initialize VS Code Environment (if startup.ps1 present)
if exist ".\.vscode\startup.ps1" (
    powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\.vscode\startup.ps1"
    echo [BOOTSTRAP] VS Code environment initialized.
) else (
    echo [WARNING] .vscode\startup.ps1 not found.
)

:END
echo [BOOTSTRAP] Environment setup complete.
pause
