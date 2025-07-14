@echo off
REM Realtor Directory Automation - Batch Runner
REM Quick execution script for Windows

setlocal enabledelayedexpansion

echo.
echo ========================================
echo   Realtor Directory Lead Extractor
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ and try again
    pause
    exit /b 1
)

REM Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    echo 📦 Activating virtual environment...
    call .venv\Scripts\activate.bat
)

REM Create required directories
if not exist "outputs" mkdir outputs
if not exist "logs" mkdir logs

REM Ask user for execution mode
echo Select execution mode:
echo 1. Run once (single scrape)
echo 2. Interactive mode (custom parameters)
echo 3. Start scheduler (weekly automation)
echo.
set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" (
    echo.
    echo 🚀 Running single scrape...
    python realtor_automation.py --mode once
) else if "%choice%"=="2" (
    echo.
    echo 🔧 Starting interactive mode...
    python realtor_automation.py --mode interactive
) else if "%choice%"=="3" (
    echo.
    echo ⏰ Starting weekly scheduler...
    echo This will run continuously and execute every Monday at 8:00 AM
    echo Press Ctrl+C to stop the scheduler
    python realtor_automation.py --mode schedule
) else (
    echo ❌ Invalid choice. Please run the script again.
    goto end
)

:end
echo.
echo 📋 Check the 'outputs' folder for CSV files
echo 📋 Check the 'logs' folder for execution logs
echo.
pause
