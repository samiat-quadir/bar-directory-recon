@echo off
REM Install and Configure OneDrive Automation
REM This batch file helps with initial setup of the OneDrive Automation tool

echo OneDrive Automation - Setup Helper
echo ---------------------------------
echo.

REM Get current script directory
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"

echo Current script location: %SCRIPT_DIR%
echo.

REM Set OneDrive path
set "DEFAULT_ONEDRIVE_PATH=C:\Users\samq\OneDrive - Digital Age Marketing Group"

echo Enter the path to your OneDrive folder
echo [Default: %DEFAULT_ONEDRIVE_PATH%]
set /p ONEDRIVE_PATH="OneDrive path: "

if "%ONEDRIVE_PATH%"=="" set "ONEDRIVE_PATH=%DEFAULT_ONEDRIVE_PATH%"

REM Check if the path exists
if not exist "%ONEDRIVE_PATH%" (
    echo.
    echo ERROR: The specified OneDrive path does not exist.
    echo Please check the path and try again.
    echo.
    pause
    exit /b 1
)

echo.
echo Selected OneDrive path: %ONEDRIVE_PATH%
echo.

REM Set primary repository path
echo Enter the path to your primary Git repository
echo [Default: %SCRIPT_DIR%]
set /p PRIMARY_REPO_PATH="Primary repo path: "

if "%PRIMARY_REPO_PATH%"=="" set "PRIMARY_REPO_PATH=%SCRIPT_DIR%"

REM Check if the path exists
if not exist "%PRIMARY_REPO_PATH%" (
    echo.
    echo ERROR: The specified repository path does not exist.
    echo Please check the path and try again.
    echo.
    pause
    exit /b 1
)

echo.
echo Selected primary repository path: %PRIMARY_REPO_PATH%
echo.

REM Update the command in RunOneDriveAutomation.bat
echo Updating RunOneDriveAutomation.bat with your settings...

REM Read the file content
set "tempFile=%TEMP%\temp_run_onedrive_automation.bat"
type "%SCRIPT_DIR%\RunOneDriveAutomation.bat" > "%tempFile%"

REM Replace the path parameters in the file
powershell -Command "(Get-Content '%tempFile%') | ForEach-Object { $_ -replace 'powershell -ExecutionPolicy Bypass -File \"%~dp0OneDriveAutomation.ps1\" -Tasks All', 'powershell -ExecutionPolicy Bypass -File \"%~dp0OneDriveAutomation.ps1\" -Tasks All -OneDrivePath \"%ONEDRIVE_PATH%\" -PrimaryRepoPath \"%PRIMARY_REPO_PATH%\"' } | Set-Content '%SCRIPT_DIR%\RunOneDriveAutomation.bat'"

REM Run initial setup
echo.
echo Running initial setup with preview (no changes)...
echo.

powershell -ExecutionPolicy Bypass -File "%SCRIPT_DIR%\OneDriveAutomation.ps1" -Tasks All -OneDrivePath "%ONEDRIVE_PATH%" -PrimaryRepoPath "%PRIMARY_REPO_PATH%" -WhatIf

echo.
echo Setup completed. You can now run the automation using:
echo RunOneDriveAutomation.bat
echo.
echo Press any key to exit...
pause > nul
