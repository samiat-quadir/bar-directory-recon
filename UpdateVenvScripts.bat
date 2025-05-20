@echo off
REM ====================================================================
REM Update Virtual Environment Helper Scripts
REM ====================================================================

echo ===================================================
echo   Updating Virtual Environment Helper Scripts
echo ===================================================
echo.

REM Store the current directory
set PROJECT_ROOT=%~dp0
cd /d "%PROJECT_ROOT%"

echo Creating PowerShell Virtual Environment Helper...
powershell -ExecutionPolicy Bypass -Command "$content = Get-Content -Path 'tools\VirtualEnvHelper.ps1.template'; $content -replace 'Activate-VirtualEnvironment', 'Enter-VirtualEnvironment' | Set-Content -Path 'tools\VirtualEnvHelper.ps1' -Force"

echo Updating PowerShell activation script...
powershell -ExecutionPolicy Bypass -Command "$content = Get-Content -Path 'ActivateVenv.ps1'; $content -replace 'Activate-VirtualEnvironment', 'Enter-VirtualEnvironment' | Set-Content -Path 'ActivateVenv.ps1' -Force"

echo Creating virtual environment activation script...
powershell -ExecutionPolicy Bypass -Command ". .\tools\VirtualEnvHelper.ps1; Update-VirtualEnvironment -VenvPath '.venv'"

echo.
echo Virtual environment has been updated and fixed!
echo You can now activate it using:
echo   * activate_venv.bat (for CMD)
echo   * .\ActivateVenv.ps1 (for PowerShell)
echo   * StartDevPowerShell.bat (for a full dev environment)
echo.

pause
