@echo off
REM Run OneDrive Automation with Administrator Privileges
REM This script elevates to admin rights and runs the automation

echo OneDrive Automation - Admin Tasks
echo -------------------------------
echo.

REM Check for admin rights
net session >nul 2>&1
if %errorLevel% == 0 (
    echo Running with administrator privileges...
) else (
    echo Requesting administrator privileges...

    REM Relaunch as admin
    powershell -Command "Start-Process '%~dpnx0' -Verb RunAs"
    exit /b
)

echo.
echo Available administrative tasks:
echo 1. Setup scheduled tasks
echo 2. Run all tasks with admin rights
echo 3. Exit
echo.

set /p choice=Enter your choice (1-3):

IF "%choice%"=="1" (
    powershell -ExecutionPolicy Bypass -File "%~dp0OneDriveAutomation.ps1" -Tasks ScheduleTasks
) ELSE IF "%choice%"=="2" (
    powershell -ExecutionPolicy Bypass -File "%~dp0OneDriveAutomation.ps1" -Tasks All
) ELSE IF "%choice%"=="3" (
    echo Exiting...
    exit /b 0
) ELSE (
    echo Invalid choice. Please run again and select a number between 1-3.
    exit /b 1
)

echo.
echo Task completed. Press any key to exit.
pause >nul
