@echo off
REM ====================================================================
REM UpdateVirtualEnvScripts.bat
REM Updates virtual environment activation scripts for cross-device compatibility
REM ====================================================================

echo ===================================================
echo   Updating Virtual Environment Activation Scripts
echo ===================================================
echo.

REM Store the current directory (where this script is located)
set PROJECT_ROOT=%~dp0
set VENV_DIR=%PROJECT_ROOT%.venv

REM Check if virtual environment exists
if not exist "%VENV_DIR%" (
    echo Virtual environment not found at: %VENV_DIR%
    echo Please create a virtual environment first.
    exit /b 1
)

echo Virtual environment found at: %VENV_DIR%

REM Check if device path resolver exists
if not exist "%PROJECT_ROOT%tools\DevicePathResolver.ps1" (
    echo Device path resolver not found. Cannot continue.
    exit /b 1
)

echo.
echo Creating activation scripts with cross-device compatibility...

REM Create activate.bat (for CMD)
echo @echo off > "%VENV_DIR%\Scripts\activate.bat"
echo REM This script activates the virtual environment from any device >> "%VENV_DIR%\Scripts\activate.bat"
echo. >> "%VENV_DIR%\Scripts\activate.bat"
echo set "VIRTUAL_ENV=%%~dp0.." >> "%VENV_DIR%\Scripts\activate.bat"
echo REM Remove trailing backslash if present >> "%VENV_DIR%\Scripts\activate.bat"
echo if "%%VIRTUAL_ENV:~-1%%" == "\" set "VIRTUAL_ENV=%%VIRTUAL_ENV:~0,-1%%" >> "%VENV_DIR%\Scripts\activate.bat"
echo. >> "%VENV_DIR%\Scripts\activate.bat"
echo if defined _OLD_VIRTUAL_PROMPT (>> "%VENV_DIR%\Scripts\activate.bat"
echo     set "PROMPT=%%_OLD_VIRTUAL_PROMPT%%" >> "%VENV_DIR%\Scripts\activate.bat"
echo ) else (>> "%VENV_DIR%\Scripts\activate.bat"
echo     if not defined PROMPT (>> "%VENV_DIR%\Scripts\activate.bat"
echo         set "PROMPT=$P$G" >> "%VENV_DIR%\Scripts\activate.bat"
echo     )>> "%VENV_DIR%\Scripts\activate.bat"
echo     set "_OLD_VIRTUAL_PROMPT=%%PROMPT%%" >> "%VENV_DIR%\Scripts\activate.bat"
echo     set "PROMPT=(venv) %%PROMPT%%" >> "%VENV_DIR%\Scripts\activate.bat"
echo )>> "%VENV_DIR%\Scripts\activate.bat"
echo. >> "%VENV_DIR%\Scripts\activate.bat"
echo set "_OLD_VIRTUAL_PYTHONHOME=%%PYTHONHOME%%" >> "%VENV_DIR%\Scripts\activate.bat"
echo set PYTHONHOME= >> "%VENV_DIR%\Scripts\activate.bat"
echo. >> "%VENV_DIR%\Scripts\activate.bat"
echo if defined _OLD_VIRTUAL_PATH (>> "%VENV_DIR%\Scripts\activate.bat"
echo     set "PATH=%%_OLD_VIRTUAL_PATH%%" >> "%VENV_DIR%\Scripts\activate.bat"
echo ) else (>> "%VENV_DIR%\Scripts\activate.bat"
echo     set "_OLD_VIRTUAL_PATH=%%PATH%%" >> "%VENV_DIR%\Scripts\activate.bat"
echo )>> "%VENV_DIR%\Scripts\activate.bat"
echo. >> "%VENV_DIR%\Scripts\activate.bat"
echo set "PATH=%%VIRTUAL_ENV%%\Scripts;%%PATH%%" >> "%VENV_DIR%\Scripts\activate.bat"
echo. >> "%VENV_DIR%\Scripts\activate.bat"
echo echo Virtual environment activated successfully on device: %%COMPUTERNAME%% >> "%VENV_DIR%\Scripts\activate.bat"
echo echo Python executable: %%VIRTUAL_ENV%%\Scripts\python.exe >> "%VENV_DIR%\Scripts\activate.bat"

REM Create Activate.ps1 (for PowerShell)
echo # This script activates the virtual environment from any device > "%VENV_DIR%\Scripts\Activate.ps1"
echo. >> "%VENV_DIR%\Scripts\Activate.ps1"
echo function global:deactivate ([switch]$NonDestructive) { >> "%VENV_DIR%\Scripts\Activate.ps1"
echo     # Revert to original values >> "%VENV_DIR%\Scripts\Activate.ps1"
echo     if (Test-Path function:_OLD_VIRTUAL_PROMPT) { >> "%VENV_DIR%\Scripts\Activate.ps1"
echo         copy-item function:_OLD_VIRTUAL_PROMPT function:prompt >> "%VENV_DIR%\Scripts\Activate.ps1"
echo         remove-item function:_OLD_VIRTUAL_PROMPT >> "%VENV_DIR%\Scripts\Activate.ps1"
echo     } >> "%VENV_DIR%\Scripts\Activate.ps1"
echo. >> "%VENV_DIR%\Scripts\Activate.ps1"
echo     if (Test-Path env:_OLD_VIRTUAL_PYTHONHOME) { >> "%VENV_DIR%\Scripts\Activate.ps1"
echo         copy-item env:_OLD_VIRTUAL_PYTHONHOME env:PYTHONHOME >> "%VENV_DIR%\Scripts\Activate.ps1"
echo         remove-item env:_OLD_VIRTUAL_PYTHONHOME >> "%VENV_DIR%\Scripts\Activate.ps1"
echo     } >> "%VENV_DIR%\Scripts\Activate.ps1"
echo. >> "%VENV_DIR%\Scripts\Activate.ps1"
echo     if (Test-Path env:_OLD_VIRTUAL_PATH) { >> "%VENV_DIR%\Scripts\Activate.ps1"
echo         copy-item env:_OLD_VIRTUAL_PATH env:PATH >> "%VENV_DIR%\Scripts\Activate.ps1"
echo         remove-item env:_OLD_VIRTUAL_PATH >> "%VENV_DIR%\Scripts\Activate.ps1"
echo     } >> "%VENV_DIR%\Scripts\Activate.ps1"
echo. >> "%VENV_DIR%\Scripts\Activate.ps1"
echo     if (Test-Path env:VIRTUAL_ENV) { >> "%VENV_DIR%\Scripts\Activate.ps1"
echo         remove-item env:VIRTUAL_ENV >> "%VENV_DIR%\Scripts\Activate.ps1"
echo     } >> "%VENV_DIR%\Scripts\Activate.ps1"
echo. >> "%VENV_DIR%\Scripts\Activate.ps1"
echo     if (!$NonDestructive) { >> "%VENV_DIR%\Scripts\Activate.ps1"
echo         # Self destruct! >> "%VENV_DIR%\Scripts\Activate.ps1"
echo         remove-item function:deactivate >> "%VENV_DIR%\Scripts\Activate.ps1"
echo     } >> "%VENV_DIR%\Scripts\Activate.ps1"
echo } >> "%VENV_DIR%\Scripts\Activate.ps1"
echo. >> "%VENV_DIR%\Scripts\Activate.ps1"
echo function global:_OLD_VIRTUAL_PROMPT { "" } >> "%VENV_DIR%\Scripts\Activate.ps1"
echo $function:_OLD_VIRTUAL_PROMPT = $function:prompt >> "%VENV_DIR%\Scripts\Activate.ps1"
echo. >> "%VENV_DIR%\Scripts\Activate.ps1"
echo function global:prompt { >> "%VENV_DIR%\Scripts\Activate.ps1"
echo     # Add a prefix to the current prompt, but don't discard it. >> "%VENV_DIR%\Scripts\Activate.ps1"
echo     Write-Host -NoNewline -ForegroundColor Green "(venv) " >> "%VENV_DIR%\Scripts\Activate.ps1"
echo     _OLD_VIRTUAL_PROMPT >> "%VENV_DIR%\Scripts\Activate.ps1"
echo } >> "%VENV_DIR%\Scripts\Activate.ps1"
echo. >> "%VENV_DIR%\Scripts\Activate.ps1"
echo # Set the prompt to include the env name >> "%VENV_DIR%\Scripts\Activate.ps1"
echo # Make sure _OLD_VIRTUAL_PROMPT is global >> "%VENV_DIR%\Scripts\Activate.ps1"
echo copy-item function:prompt function:_OLD_VIRTUAL_PROMPT >> "%VENV_DIR%\Scripts\Activate.ps1"
echo. >> "%VENV_DIR%\Scripts\Activate.ps1"
echo # Get the parent directory of this script >> "%VENV_DIR%\Scripts\Activate.ps1"
echo $scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path >> "%VENV_DIR%\Scripts\Activate.ps1"
echo $virtualEnvDir = Split-Path -Parent $scriptDir >> "%VENV_DIR%\Scripts\Activate.ps1"
echo. >> "%VENV_DIR%\Scripts\Activate.ps1"
echo # Set VIRTUAL_ENV using script location rather than hardcoded path >> "%VENV_DIR%\Scripts\Activate.ps1"
echo $env:VIRTUAL_ENV = $virtualEnvDir >> "%VENV_DIR%\Scripts\Activate.ps1"
echo. >> "%VENV_DIR%\Scripts\Activate.ps1"
echo if ($env:PYTHONHOME) { >> "%VENV_DIR%\Scripts\Activate.ps1"
echo     copy-item env:PYTHONHOME env:_OLD_VIRTUAL_PYTHONHOME >> "%VENV_DIR%\Scripts\Activate.ps1"
echo     remove-item env:PYTHONHOME >> "%VENV_DIR%\Scripts\Activate.ps1"
echo } >> "%VENV_DIR%\Scripts\Activate.ps1"
echo. >> "%VENV_DIR%\Scripts\Activate.ps1"
echo # Add the venv to the PATH >> "%VENV_DIR%\Scripts\Activate.ps1"
echo copy-item env:PATH env:_OLD_VIRTUAL_PATH >> "%VENV_DIR%\Scripts\Activate.ps1"
echo $env:PATH = "$env:VIRTUAL_ENV\Scripts;$env:PATH" >> "%VENV_DIR%\Scripts\Activate.ps1"
echo. >> "%VENV_DIR%\Scripts\Activate.ps1"
echo Write-Host "Virtual environment activated successfully on device: $env:COMPUTERNAME" -ForegroundColor Green >> "%VENV_DIR%\Scripts\Activate.ps1"
echo Write-Host "Python executable: $env:VIRTUAL_ENV\Scripts\python.exe" -ForegroundColor Green >> "%VENV_DIR%\Scripts\Activate.ps1"

echo.
echo Successfully updated virtual environment activation scripts!
echo.
echo You can now use the following commands to activate the virtual environment:
echo  - From CMD: call .venv\Scripts\activate.bat
echo  - From PowerShell: .\.venv\Scripts\Activate.ps1

exit /b 0
