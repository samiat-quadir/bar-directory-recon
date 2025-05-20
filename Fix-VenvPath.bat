@echo off
REM ====================================================================
REM Fix-VenvPath.bat
REM Fixes Python virtual environment paths for VS Code
REM ====================================================================

echo ===================================================
echo   Fixing Python Virtual Environment Path
echo ===================================================
echo.

REM Store the current directory (where this script is located)
set PROJECT_ROOT=%~dp0
if %PROJECT_ROOT:~-1%==\ set PROJECT_ROOT=%PROJECT_ROOT:~0,-1%

echo Project root: %PROJECT_ROOT%
echo.

REM Check if virtual environment exists
if not exist "%PROJECT_ROOT%\.venv" (
    echo ERROR: Virtual environment not found at %PROJECT_ROOT%\.venv
    echo Please create a virtual environment first.
    goto END
)

echo Found virtual environment at: %PROJECT_ROOT%\.venv
echo.

REM Create activation script for PowerShell
echo Creating cross-device compatible PowerShell activation script...
powershell -ExecutionPolicy Bypass -NoProfile -Command "Set-Content -Path '%PROJECT_ROOT%\.venv\Scripts\activate.ps1' -Value @'
# Cross-device compatible activate.ps1
# This script activates the Python virtual environment with device-agnostic paths

# Get the current script directory using the invocation info
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$venvRoot = Split-Path -Parent $scriptDir

# Store the old path to restore when deactivating
if (Test-Path Env:_OLD_VIRTUAL_PATH) {
    $env:PATH = $env:_OLD_VIRTUAL_PATH
    Remove-Item Env:_OLD_VIRTUAL_PATH
}
$env:_OLD_VIRTUAL_PATH = $env:PATH

# Store the old PYTHONHOME to restore when deactivating
if (Test-Path Env:_OLD_VIRTUAL_PYTHONHOME) {
    $env:PYTHONHOME = $env:_OLD_VIRTUAL_PYTHONHOME
    Remove-Item Env:_OLD_VIRTUAL_PYTHONHOME
}
if (Test-Path Env:PYTHONHOME) {
    $env:_OLD_VIRTUAL_PYTHONHOME = $env:PYTHONHOME
    Remove-Item Env:PYTHONHOME
}

# Set VIRTUAL_ENV environment variable
$env:VIRTUAL_ENV = $venvRoot

# Add Scripts directory to PATH
$env:PATH = \"$venvRoot\Scripts;$env:PATH\"

# Set prompt to indicate active virtual environment
function global:prompt {
    Write-Host \"(venv) \" -NoNewline -ForegroundColor Green
    _OLD_VIRTUAL_PROMPT
}

# Backup original prompt function
function global:_OLD_VIRTUAL_PROMPT {
    # Show the current path in the prompt
    Write-Host \"$($executionContext.SessionState.Path.CurrentLocation)> \" -NoNewline
}

# Update the prompt
$function:prompt = $function:prompt

# Output success message
Write-Host \"Activated cross-device compatible virtual environment at: $venvRoot\" -ForegroundColor Green
'@"

REM Create activation script for CMD (bat)
echo Creating cross-device compatible batch activation script...
echo @echo off > "%PROJECT_ROOT%\.venv\Scripts\activate.bat"
echo REM Cross-device compatible activate.bat >> "%PROJECT_ROOT%\.venv\Scripts\activate.bat"
echo REM This script activates the Python virtual environment with device-agnostic paths >> "%PROJECT_ROOT%\.venv\Scripts\activate.bat"
echo. >> "%PROJECT_ROOT%\.venv\Scripts\activate.bat"
echo REM Get the script directory without trailing backslash >> "%PROJECT_ROOT%\.venv\Scripts\activate.bat"
echo set "SCRIPT_DIR=%%~dp0" >> "%PROJECT_ROOT%\.venv\Scripts\activate.bat"
echo if "%%SCRIPT_DIR:~-1%%" == "\" set "SCRIPT_DIR=%%SCRIPT_DIR:~0,-1%%" >> "%PROJECT_ROOT%\.venv\Scripts\activate.bat"
echo. >> "%PROJECT_ROOT%\.venv\Scripts\activate.bat"
echo REM Get the virtual environment root directory >> "%PROJECT_ROOT%\.venv\Scripts\activate.bat"
echo set "VIRTUAL_ENV=%%SCRIPT_DIR%%.." >> "%PROJECT_ROOT%\.venv\Scripts\activate.bat"
echo if "%%VIRTUAL_ENV:~-2%%" == ".." set "VIRTUAL_ENV=%%VIRTUAL_ENV:~0,-2%%" >> "%PROJECT_ROOT%\.venv\Scripts\activate.bat"
echo. >> "%PROJECT_ROOT%\.venv\Scripts\activate.bat"
echo REM Store old PATH to restore when deactivated >> "%PROJECT_ROOT%\.venv\Scripts\activate.bat"
echo if defined _OLD_VIRTUAL_PATH ( >> "%PROJECT_ROOT%\.venv\Scripts\activate.bat"
echo     set "PATH=%%_OLD_VIRTUAL_PATH%%" >> "%PROJECT_ROOT%\.venv\Scripts\activate.bat"
echo ) else ( >> "%PROJECT_ROOT%\.venv\Scripts\activate.bat"
echo     set "_OLD_VIRTUAL_PATH=%%PATH%%" >> "%PROJECT_ROOT%\.venv\Scripts\activate.bat"
echo ) >> "%PROJECT_ROOT%\.venv\Scripts\activate.bat"
echo. >> "%PROJECT_ROOT%\.venv\Scripts\activate.bat"
echo REM Add the virtual environment's Scripts directory to the PATH >> "%PROJECT_ROOT%\.venv\Scripts\activate.bat"
echo set "PATH=%%VIRTUAL_ENV%%\Scripts;%%PATH%%" >> "%PROJECT_ROOT%\.venv\Scripts\activate.bat"
echo. >> "%PROJECT_ROOT%\.venv\Scripts\activate.bat"
echo REM Update the prompt >> "%PROJECT_ROOT%\.venv\Scripts\activate.bat"
echo if defined _OLD_VIRTUAL_PROMPT ( >> "%PROJECT_ROOT%\.venv\Scripts\activate.bat"
echo     set "PROMPT=%%_OLD_VIRTUAL_PROMPT%%" >> "%PROJECT_ROOT%\.venv\Scripts\activate.bat"
echo ) else ( >> "%PROJECT_ROOT%\.venv\Scripts\activate.bat"
echo     set "_OLD_VIRTUAL_PROMPT=%%PROMPT%%" >> "%PROJECT_ROOT%\.venv\Scripts\activate.bat"
echo ) >> "%PROJECT_ROOT%\.venv\Scripts\activate.bat"
echo set "PROMPT=(venv) %%PROMPT%%" >> "%PROJECT_ROOT%\.venv\Scripts\activate.bat"
echo. >> "%PROJECT_ROOT%\.venv\Scripts\activate.bat"
echo echo Virtual environment activated successfully. >> "%PROJECT_ROOT%\.venv\Scripts\activate.bat"
echo echo VIRTUAL_ENV=%%VIRTUAL_ENV%% >> "%PROJECT_ROOT%\.venv\Scripts\activate.bat"

REM Create a settings.json file for VS Code
echo Creating VS Code settings for Python integration...
powershell -ExecutionPolicy Bypass -NoProfile -Command "Set-Content -Path '%PROJECT_ROOT%\.vscode\python-settings.json' -Value @'
{
    \"python.defaultInterpreterPath\": \"${workspaceFolder}\\.venv\\Scripts\\python.exe\",
    \"python.terminal.activateEnvironment\": true
}
'@"

REM Update VS Code settings
echo Updating VS Code settings...
powershell -ExecutionPolicy Bypass -NoProfile -Command "
try {
    # Read existing settings
    $settingsPath = '%PROJECT_ROOT%\.vscode\settings.json'
    $settings = Get-Content $settingsPath -Raw | ConvertFrom-Json

    # Add or update Python settings
    $settings | Add-Member -NotePropertyName 'python.defaultInterpreterPath' -NotePropertyValue '${workspaceFolder}\.venv\Scripts\python.exe' -Force

    # Save updated settings
    $settings | ConvertTo-Json -Depth 10 | Set-Content $settingsPath
    Write-Host 'Updated VS Code settings successfully' -ForegroundColor Green
} catch {
    Write-Host 'Error updating VS Code settings: $_' -ForegroundColor Red
}
"

echo Virtual environment activation scripts updated successfully.
echo.
echo To activate the environment:
echo   - In PowerShell: .\.venv\Scripts\activate.ps1
echo   - In CMD: .\.venv\Scripts\activate.bat
echo.
echo VS Code will now use the correct Python interpreter.

:END
echo.
pause
