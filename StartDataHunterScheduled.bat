@echo off
REM Data Hunter - Automated Startup Script
REM This script starts the Data Hunter in scheduled mode at Windows startup

echo Starting Data Hunter in scheduled mode...
echo Timestamp: %date% %time%

REM Change to project directory
cd /d "c:\Code\bar-directory-recon"

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run InstallDependencies.bat first
    pause
    exit /b 1
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Start Data Hunter in scheduled mode
echo Starting Data Hunter scheduler...
python src\data_hunter.py --schedule

REM If we get here, the scheduler stopped unexpectedly
echo Data Hunter scheduler stopped at %date% %time%
echo Restarting in 60 seconds...
timeout /t 60
goto :start
