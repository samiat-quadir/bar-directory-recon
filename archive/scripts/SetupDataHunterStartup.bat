@echo off
REM Setup Data Hunter Windows Task Scheduler
REM Run this as Administrator to set up automatic startup

echo.
echo ================================================================
echo          DATA HUNTER - WINDOWS TASK SCHEDULER SETUP
echo ================================================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: This script must be run as Administrator!
    echo Right-click and select "Run as administrator"
    pause
    exit /b 1
)

echo Setting up Windows Task Scheduler for Data Hunter...

REM Create scheduled task to run Data Hunter at startup
schtasks /create /tn "DataHunter-AutoStart" /tr "c:\Code\bar-directory-recon\StartDataHunterScheduled.bat" /sc onstart /ru SYSTEM /f

if %errorlevel% equ 0 (
    echo ✅ Task created successfully!
    echo.
    echo Task Name: DataHunter-AutoStart
    echo Trigger: At system startup
    echo Action: Start Data Hunter in scheduled mode
    echo.
    echo To manage this task:
    echo - Open Task Scheduler (taskschd.msc)
    echo - Look for "DataHunter-AutoStart" in Task Scheduler Library
    echo.
    echo To remove the task:
    echo schtasks /delete /tn "DataHunter-AutoStart" /f
) else (
    echo ❌ Failed to create scheduled task
    echo Please check permissions and try again
)

echo.
echo Alternative method - Startup folder:
echo You can also copy StartDataHunterScheduled.bat to:
echo %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\
echo.

pause
