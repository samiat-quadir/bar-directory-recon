@echo off
REM OpenInVSCode.bat
REM This script opens the project in VS Code with cross-device compatibility enabled

echo ===================================================
echo   Opening Project in VS Code
echo ===================================================
echo.

setlocal

REM Store the current directory
set PROJECT_ROOT=%~dp0
if %PROJECT_ROOT:~-1%==\ set PROJECT_ROOT=%PROJECT_ROOT:~0,-1%

REM Echo device info
echo Current device: %COMPUTERNAME%
echo Current user: %USERNAME%

REM Check if VS Code is installed and available in PATH
where code >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: VS Code not found in PATH.
    echo Please ensure VS Code is installed and added to your PATH.
    echo Alternatively, you can open VS Code manually and then open this folder.
    goto END
)

REM Setup the .vscode directory if it doesn't exist
if not exist "%PROJECT_ROOT%\.vscode" (
    echo Creating .vscode directory...
    mkdir "%PROJECT_ROOT%\.vscode"
)

REM Ensure the required VS Code files exist
if not exist "%PROJECT_ROOT%\.vscode\tasks.json" (
    echo Creating VS Code tasks.json...
    echo { > "%PROJECT_ROOT%\.vscode\tasks.json"
    echo     "version": "2.0.0", >> "%PROJECT_ROOT%\.vscode\tasks.json"
    echo     "tasks": [ >> "%PROJECT_ROOT%\.vscode\tasks.json"
    echo         { >> "%PROJECT_ROOT%\.vscode\tasks.json"
    echo             "label": "Detect and Configure Device", >> "%PROJECT_ROOT%\.vscode\tasks.json"
    echo             "type": "shell", >> "%PROJECT_ROOT%\.vscode\tasks.json"
    echo             "command": "powershell", >> "%PROJECT_ROOT%\.vscode\tasks.json"
    echo             "args": [ >> "%PROJECT_ROOT%\.vscode\tasks.json"
    echo                 "-ExecutionPolicy", >> "%PROJECT_ROOT%\.vscode\tasks.json"
    echo                 "Bypass", >> "%PROJECT_ROOT%\.vscode\tasks.json"
    echo                 "-NoProfile", >> "%PROJECT_ROOT%\.vscode\tasks.json"
    echo                 "-File", >> "%PROJECT_ROOT%\.vscode\tasks.json"
    echo                 "${workspaceFolder}\\tools\\AutoDeviceSetup.ps1" >> "%PROJECT_ROOT%\.vscode\tasks.json"
    echo             ], >> "%PROJECT_ROOT%\.vscode\tasks.json"
    echo             "presentation": { >> "%PROJECT_ROOT%\.vscode\tasks.json"
    echo                 "reveal": "silent", >> "%PROJECT_ROOT%\.vscode\tasks.json"
    echo                 "panel": "dedicated", >> "%PROJECT_ROOT%\.vscode\tasks.json"
    echo                 "clear": true >> "%PROJECT_ROOT%\.vscode\tasks.json"
    echo             }, >> "%PROJECT_ROOT%\.vscode\tasks.json"
    echo             "problemMatcher": [], >> "%PROJECT_ROOT%\.vscode\tasks.json"
    echo             "runOptions": { >> "%PROJECT_ROOT%\.vscode\tasks.json"
    echo                 "runOn": "folderOpen" >> "%PROJECT_ROOT%\.vscode\tasks.json"
    echo             } >> "%PROJECT_ROOT%\.vscode\tasks.json"
    echo         } >> "%PROJECT_ROOT%\.vscode\tasks.json"
    echo     ] >> "%PROJECT_ROOT%\.vscode\tasks.json"
    echo } >> "%PROJECT_ROOT%\.vscode\tasks.json"
)

REM Check if AutoDeviceSetup.ps1 exists
if not exist "%PROJECT_ROOT%\tools\AutoDeviceSetup.ps1" (
    echo ERROR: AutoDeviceSetup.ps1 not found.
    echo Please ensure the tools directory is properly set up.
    goto END
)

REM Open the project in VS Code
echo Opening project in VS Code...
start code "%PROJECT_ROOT%"

echo.
echo Project opened in VS Code.
echo The cross-device configuration will run automatically when VS Code opens.

:END
endlocal
echo.
echo Press any key to exit...
pause >nul
