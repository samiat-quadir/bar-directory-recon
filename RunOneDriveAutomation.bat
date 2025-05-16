@echo off
REM OneDriveAutomation Launcher Script
REM This batch file provides quick access to different automation tasks

echo OneDrive Automation Tool
echo ------------------------
echo.
echo Available options:
echo 1. Run all tasks
echo 2. Fix folder structure only
echo 3. Sync environment between devices
echo 4. Cleanup Git repositories
echo 5. Scan for secrets
echo 6. Setup scheduled tasks
echo 7. Run in preview mode (no changes)
echo 8. Exit
echo.

set /p choice=Enter your choice (1-8):

IF "%choice%"=="1" (
    powershell -ExecutionPolicy Bypass -File "%~dp0OneDriveAutomation.ps1" -Tasks All
) ELSE IF "%choice%"=="2" (
    powershell -ExecutionPolicy Bypass -File "%~dp0OneDriveAutomation.ps1" -Tasks StandardizeFolders
) ELSE IF "%choice%"=="3" (
    powershell -ExecutionPolicy Bypass -File "%~dp0OneDriveAutomation.ps1" -Tasks SyncEnvironment
    echo.
    echo NOTE: Run this on both devices to fully synchronize environments
) ELSE IF "%choice%"=="4" (
    powershell -ExecutionPolicy Bypass -File "%~dp0OneDriveAutomation.ps1" -Tasks GitCleanup
) ELSE IF "%choice%"=="5" (
    powershell -ExecutionPolicy Bypass -File "%~dp0OneDriveAutomation.ps1" -Tasks ScanSecrets
) ELSE IF "%choice%"=="6" (
    powershell -ExecutionPolicy Bypass -File "%~dp0OneDriveAutomation.ps1" -Tasks ScheduleTasks
) ELSE IF "%choice%"=="7" (
    powershell -ExecutionPolicy Bypass -File "%~dp0OneDriveAutomation.ps1" -Tasks All -WhatIf
) ELSE IF "%choice%"=="8" (
    echo Exiting...
    exit /b 0
) ELSE (
    echo Invalid choice. Please run again and select a number between 1-8.
    exit /b 1
)

echo.
echo Task completed. Press any key to exit.
pause >nul
