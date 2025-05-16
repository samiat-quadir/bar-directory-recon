@echo off
REM ====================================================================
REM Fix-VirtualEnvPath.bat
REM This script fixes VS Code terminal activation error by updating terminal settings
REM ====================================================================

echo ===================================================
echo   Fixing Virtual Environment Path for VS Code
echo ===================================================
echo.

setlocal enabledelayedexpansion

set "PROJECT_ROOT=%~dp0"
if %PROJECT_ROOT:~-1%==\ set PROJECT_ROOT=%PROJECT_ROOT:~0,-1%

REM Check if .venv exists
if not exist "%PROJECT_ROOT%\.venv" (
    echo Virtual environment not found at: %PROJECT_ROOT%\.venv
    echo Please create a virtual environment first.
    goto END
)

REM Check if this is a Python virtual environment
if not exist "%PROJECT_ROOT%\.venv\Scripts\python.exe" (
    echo This doesn't appear to be a valid Python virtual environment.
    echo Missing: %PROJECT_ROOT%\.venv\Scripts\python.exe
    goto END
)

echo Found Python virtual environment at: %PROJECT_ROOT%\.venv
echo.

REM Create a PowerShell script to update the VS Code settings properly
echo $settingsPath = "%PROJECT_ROOT%\.vscode\settings.json" > "%TEMP%\fix_vscode_env.ps1"
echo if (Test-Path $settingsPath) { >> "%TEMP%\fix_vscode_env.ps1"
echo     $settings = Get-Content -Raw $settingsPath ^| ConvertFrom-Json >> "%TEMP%\fix_vscode_env.ps1"
echo     $settings ^| Add-Member -NotePropertyName "python.defaultInterpreterPath" -NotePropertyValue "${workspaceFolder}\.venv\Scripts\python.exe" -Force >> "%TEMP%\fix_vscode_env.ps1"
echo     $settings ^| Add-Member -NotePropertyName "python.terminal.activateEnvironment" -NotePropertyValue $true -Force >> "%TEMP%\fix_vscode_env.ps1"
echo     $settings ^| ConvertTo-Json -Depth 10 ^| Set-Content $settingsPath >> "%TEMP%\fix_vscode_env.ps1"
echo     Write-Host "Updated VS Code settings to use the correct Python environment" -ForegroundColor Green >> "%TEMP%\fix_vscode_env.ps1"
echo } else { >> "%TEMP%\fix_vscode_env.ps1"
echo     Write-Host "VS Code settings file not found. Please open VS Code and try again." -ForegroundColor Red >> "%TEMP%\fix_vscode_env.ps1"
echo } >> "%TEMP%\fix_vscode_env.ps1"

REM Run the PowerShell script
powershell -ExecutionPolicy Bypass -NoProfile -File "%TEMP%\fix_vscode_env.ps1"

REM Create a better activate.ps1 script
echo # This activation script is designed to work across devices > "%PROJECT_ROOT%\.venv\Scripts\activate.ps1"
echo # and prevent path-related issues > "%PROJECT_ROOT%\.venv\Scripts\activate.ps1"
echo. >> "%PROJECT_ROOT%\.venv\Scripts\activate.ps1"
echo $scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path >> "%PROJECT_ROOT%\.venv\Scripts\activate.ps1"
echo $env:VIRTUAL_ENV = (Split-Path -Parent $scriptPath) >> "%PROJECT_ROOT%\.venv\Scripts\activate.ps1"
echo. >> "%PROJECT_ROOT%\.venv\Scripts\activate.ps1"
echo # Store the old path to restore it later >> "%PROJECT_ROOT%\.venv\Scripts\activate.ps1"
echo if (Test-Path Env:_OLD_VIRTUAL_PATH) { >> "%PROJECT_ROOT%\.venv\Scripts\activate.ps1"
echo     $env:PATH = $env:_OLD_VIRTUAL_PATH >> "%PROJECT_ROOT%\.venv\Scripts\activate.ps1"
echo } >> "%PROJECT_ROOT%\.venv\Scripts\activate.ps1"
echo $env:_OLD_VIRTUAL_PATH = $env:PATH >> "%PROJECT_ROOT%\.venv\Scripts\activate.ps1"
echo. >> "%PROJECT_ROOT%\.venv\Scripts\activate.ps1"
echo # Add the venv to the PATH >> "%PROJECT_ROOT%\.venv\Scripts\activate.ps1"
echo $env:PATH = "$env:VIRTUAL_ENV\Scripts;$env:PATH" >> "%PROJECT_ROOT%\.venv\Scripts\activate.ps1"
echo. >> "%PROJECT_ROOT%\.venv\Scripts\activate.ps1"
echo # Set prompt >> "%PROJECT_ROOT%\.venv\Scripts\activate.ps1"
echo function global:prompt { >> "%PROJECT_ROOT%\.venv\Scripts\activate.ps1"
echo     Write-Host "(venv) " -NoNewline -ForegroundColor Green >> "%PROJECT_ROOT%\.venv\Scripts\activate.ps1"
echo     _OLD_VIRTUAL_PROMPT >> "%PROJECT_ROOT%\.venv\Scripts\activate.ps1"
echo } >> "%PROJECT_ROOT%\.venv\Scripts\activate.ps1"
echo. >> "%PROJECT_ROOT%\.venv\Scripts\activate.ps1"
echo function global:_OLD_VIRTUAL_PROMPT { >> "%PROJECT_ROOT%\.venv\Scripts\activate.ps1"
echo     if ("" -ne $function:prompt) { >> "%PROJECT_ROOT%\.venv\Scripts\activate.ps1"
echo         $previous_prompt_value = & $function:prompt >> "%PROJECT_ROOT%\.venv\Scripts\activate.ps1"
echo     } >> "%PROJECT_ROOT%\.venv\Scripts\activate.ps1"
echo     Write-Host $previous_prompt_value -NoNewline >> "%PROJECT_ROOT%\.venv\Scripts\activate.ps1"
echo } >> "%PROJECT_ROOT%\.venv\Scripts\activate.ps1"
echo $function:prompt = $function:_OLD_VIRTUAL_PROMPT >> "%PROJECT_ROOT%\.venv\Scripts\activate.ps1"
echo. >> "%PROJECT_ROOT%\.venv\Scripts\activate.ps1"
echo Write-Host "Activated cross-device compatible virtual environment" -ForegroundColor Green >> "%PROJECT_ROOT%\.venv\Scripts\activate.ps1"

echo Updated Python virtual environment activation scripts.
echo.

REM Create a VS Code terminal startup script that doesn't try to auto-activate a specific path
echo # VSCode-PowerShell integration startup script > "%PROJECT_ROOT%\.vscode\startup.ps1"
echo # This script is loaded when PowerShell starts in VS Code >> "%PROJECT_ROOT%\.vscode\startup.ps1"
echo. >> "%PROJECT_ROOT%\.vscode\startup.ps1"
echo # Load device path resolver >> "%PROJECT_ROOT%\.vscode\startup.ps1"
echo $pathResolverScript = Join-Path -Path $PSScriptRoot -ChildPath "..\tools\DevicePathResolver.ps1" >> "%PROJECT_ROOT%\.vscode\startup.ps1"
echo if (Test-Path $pathResolverScript) { >> "%PROJECT_ROOT%\.vscode\startup.ps1"
echo     . $pathResolverScript >> "%PROJECT_ROOT%\.vscode\startup.ps1"
echo     Write-Host "Device path resolver loaded." -ForegroundColor Green >> "%PROJECT_ROOT%\.vscode\startup.ps1"
echo } >> "%PROJECT_ROOT%\.vscode\startup.ps1"
echo. >> "%PROJECT_ROOT%\.vscode\startup.ps1"
echo # Activate the virtual environment if it exists >> "%PROJECT_ROOT%\.vscode\startup.ps1"
echo $venvPath = Join-Path -Path (Split-Path -Parent $PSScriptRoot) -ChildPath ".venv\Scripts\activate.ps1" >> "%PROJECT_ROOT%\.vscode\startup.ps1"
echo if (Test-Path $venvPath) { >> "%PROJECT_ROOT%\.vscode\startup.ps1"
echo     try { >> "%PROJECT_ROOT%\.vscode\startup.ps1"
echo         . $venvPath >> "%PROJECT_ROOT%\.vscode\startup.ps1"
echo     } catch { >> "%PROJECT_ROOT%\.vscode\startup.ps1"
echo         Write-Host "Failed to activate virtual environment: $_" -ForegroundColor Yellow >> "%PROJECT_ROOT%\.vscode\startup.ps1"
echo         Write-Host "You can manually activate it with: .\.venv\Scripts\activate.ps1" -ForegroundColor Yellow >> "%PROJECT_ROOT%\.vscode\startup.ps1"
echo     } >> "%PROJECT_ROOT%\.vscode\startup.ps1"
echo } else { >> "%PROJECT_ROOT%\.vscode\startup.ps1"
echo     Write-Host "Virtual environment not found. Run 'python -m venv .venv' to create one." -ForegroundColor Yellow >> "%PROJECT_ROOT%\.vscode\startup.ps1"
echo } >> "%PROJECT_ROOT%\.vscode\startup.ps1"

echo Created VS Code terminal startup script.
echo.

REM Update VS Code settings.json to use our startup script
powershell -ExecutionPolicy Bypass -NoProfile -Command "& {
    $settingsPath = '%PROJECT_ROOT%\.vscode\settings.json'
    if (Test-Path $settingsPath) {
        $settings = Get-Content -Raw $settingsPath | ConvertFrom-Json
        $settings.terminal.integrated.profiles.windows.PowerShell.args = @(
            '-NoLogo',
            '-NoExit',
            '-ExecutionPolicy',
            'Bypass',
            '-Command',
            '& \"${workspaceFolder}\.vscode\startup.ps1\"'
        )
        $settings | ConvertTo-Json -Depth 10 | Set-Content $settingsPath
        Write-Host 'Updated VS Code terminal settings.' -ForegroundColor Green
    } else {
        Write-Host 'VS Code settings file not found.' -ForegroundColor Red
    }
}"

echo VS Code terminal settings updated.
echo.
echo ===================================================
echo   Fix Complete - Actions Taken:
echo ===================================================
echo 1. Updated VS Code Python interpreter settings
echo 2. Created cross-device compatible activate.ps1
echo 3. Created VS Code terminal startup script
echo 4. Updated VS Code terminal settings
echo.
echo Please restart VS Code for changes to take effect.
echo.
echo If you still encounter issues, run:
echo   .\UpdateVenvCrossDevice.bat
echo.

:END
echo.
pause
