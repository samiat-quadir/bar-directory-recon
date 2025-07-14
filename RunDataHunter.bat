@echo off
REM Data Hunter - Automated Property List Discovery
REM Windows Batch Script for Easy Execution

echo.
echo ================================================================
echo                     DATA HUNTER - PROPERTY DISCOVERY
echo ================================================================
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv .venv
    echo Then: .venv\Scripts\activate.bat
    echo And: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Activate virtual environment
call .venv\Scripts\activate.bat

REM Check command line arguments
if "%1"=="test" (
    echo Running Data Hunter test...
    python test_data_hunter.py
    goto :end
)

if "%1"=="once" (
    echo Running single discovery scan...
    python src\data_hunter.py --run-once
    goto :end
)

if "%1"=="schedule" (
    echo Starting scheduled discovery (runs daily)...
    echo Press Ctrl+C to stop
    python src\data_hunter.py --schedule
    goto :end
)

if "%1"=="config" (
    echo Opening configuration file...
    if exist "config\data_hunter_config.json" (
        notepad config\data_hunter_config.json
    ) else (
        echo Config file not found. Run 'RunDataHunter.bat test' first to create it.
    )
    goto :end
)

REM Default - show menu
echo Choose an option:
echo.
echo 1. Test Data Hunter (test configuration and run discovery)
echo 2. Run discovery once (manual scan)
echo 3. Start scheduled discovery (daily automation)
echo 4. Edit configuration file
echo 5. View logs
echo 6. Exit
echo.
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" (
    echo Running Data Hunter test...
    python test_data_hunter.py
) else if "%choice%"=="2" (
    echo Running single discovery scan...
    python src\data_hunter.py --run-once
) else if "%choice%"=="3" (
    echo Starting scheduled discovery...
    echo Press Ctrl+C to stop
    python src\data_hunter.py --schedule
) else if "%choice%"=="4" (
    echo Opening configuration file...
    if exist "config\data_hunter_config.json" (
        notepad config\data_hunter_config.json
    ) else (
        echo Config file not found. Running test first...
        python test_data_hunter.py
        notepad config\data_hunter_config.json
    )
) else if "%choice%"=="5" (
    echo Recent discovery logs:
    echo.
    if exist "logs\auto_discovery.log" (
        echo Last 20 lines of auto_discovery.log:
        echo ----------------------------------------
        powershell "Get-Content logs\auto_discovery.log -Tail 20"
    ) else (
        echo No discovery logs found yet.
    )
    echo.
    if exist "logs\downloaded_files.json" (
        echo Downloaded files tracking:
        echo ----------------------------------------
        type logs\downloaded_files.json
    ) else (
        echo No downloaded files yet.
    )
    echo.
    pause
) else if "%choice%"=="6" (
    echo Exiting...
    goto :end
) else (
    echo Invalid choice. Please try again.
    pause
    goto :end
)

:end
echo.
echo ================================================================
echo Data Hunter execution completed.
echo ================================================================
pause
