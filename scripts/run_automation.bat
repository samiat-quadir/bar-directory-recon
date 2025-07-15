@echo off
REM Universal Project Runner - Phase 3 Automation Initiative
REM =========================================================
REM 
REM This batch script provides easy access to all automation features.
REM Run without arguments to see the menu, or use specific commands.

setlocal EnableDelayedExpansion

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0
set PROJECT_ROOT=%SCRIPT_DIR%

REM Check if virtual environment exists and activate it
if exist "%PROJECT_ROOT%.venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call "%PROJECT_ROOT%.venv\Scripts\activate.bat"
) else (
    echo Warning: Virtual environment not found. Using system Python.
)

REM Change to project directory
cd /d "%PROJECT_ROOT%"

REM Create logs directory if it doesn't exist
if not exist "logs\automation" mkdir "logs\automation"

REM Parse command line arguments
set COMMAND=%1
shift

if "%COMMAND%"=="" goto :show_menu
if "%COMMAND%"=="help" goto :show_help
if "%COMMAND%"=="menu" goto :show_menu

REM Execute specific commands
if "%COMMAND%"=="quick" goto :quick_run
if "%COMMAND%"=="full" goto :full_pipeline
if "%COMMAND%"=="monitor" goto :monitor_input
if "%COMMAND%"=="schedule" goto :start_scheduler
if "%COMMAND%"=="status" goto :show_status
if "%COMMAND%"=="dashboard" goto :generate_dashboard
if "%COMMAND%"=="test" goto :test_notifications
if "%COMMAND%"=="validate" goto :validate_system
if "%COMMAND%"=="setup" goto :setup_environment
if "%COMMAND%"=="install" goto :install_dependencies
if "%COMMAND%"=="discovery" goto :run_discovery
if "%COMMAND%"=="list-config" goto :configure_list_discovery

echo Unknown command: %COMMAND%
echo Run "%~n0 help" for available commands.
goto :end

:show_menu
echo.
echo ================================================================
echo         🔍 UNIVERSAL PROJECT RUNNER - PHASE 3 AUTOMATION
echo ================================================================
echo.
echo   Bar Directory Reconnaissance - Automation Control Panel
echo.
echo   Available Commands:
echo   [1] quick ^<site^>     - Quick pipeline run for a single site
echo   [2] full             - Run full pipeline for all configured sites
echo   [3] monitor          - Start input directory monitoring
echo   [4] schedule         - Start automation scheduler
echo   [5] status           - Show current system status
echo   [6] dashboard        - Generate status dashboard
echo   [7] test             - Test notification systems
echo   [8] validate         - Validate system health
echo   [9] setup            - Setup automation environment
echo   [10] install         - Install required dependencies
echo   [11] discovery       - Run List Discovery Agent (check for new files)
echo   [12] list-config     - Configure List Discovery URLs
echo.
echo   Usage Examples:
echo     %~n0 quick example-bar.com
echo     %~n0 full
echo     %~n0 monitor
echo     %~n0 dashboard
echo.
echo ================================================================
echo.
set /p choice="Enter command number or name (or 'exit' to quit): "

if "%choice%"=="exit" goto :end
if "%choice%"=="1" goto :prompt_quick
if "%choice%"=="2" goto :full_pipeline
if "%choice%"=="3" goto :monitor_input
if "%choice%"=="4" goto :start_scheduler
if "%choice%"=="5" goto :show_status
if "%choice%"=="6" goto :generate_dashboard
if "%choice%"=="7" goto :test_notifications
if "%choice%"=="8" goto :validate_system
if "%choice%"=="9" goto :setup_environment
if "%choice%"=="10" goto :install_dependencies
if "%choice%"=="11" goto :run_discovery
if "%choice%"=="12" goto :configure_list_discovery

REM Direct command execution
set COMMAND=%choice%
if "%COMMAND%"=="quick" goto :prompt_quick
if "%COMMAND%"=="full" goto :full_pipeline
if "%COMMAND%"=="monitor" goto :monitor_input
if "%COMMAND%"=="schedule" goto :start_scheduler
if "%COMMAND%"=="status" goto :show_status
if "%COMMAND%"=="dashboard" goto :generate_dashboard
if "%COMMAND%"=="test" goto :test_notifications
if "%COMMAND%"=="validate" goto :validate_system
if "%COMMAND%"=="setup" goto :setup_environment
if "%COMMAND%"=="install" goto :install_dependencies
if "%COMMAND%"=="discovery" goto :run_discovery
if "%COMMAND%"=="list-config" goto :configure_list_discovery

echo Invalid choice: %choice%
goto :show_menu

:prompt_quick
set /p site="Enter site URL to process: "
if "%site%"=="" (
    echo Error: Site URL is required
    goto :show_menu
)
goto :quick_run_with_site

:quick_run
set site=%1
if "%site%"=="" (
    echo Error: Site argument required for quick run
    echo Usage: %~n0 quick ^<site^>
    goto :end
)
:quick_run_with_site
echo.
echo 🚀 Running quick pipeline for: %site%
python automation\cli_shortcuts.py quick "%site%"
goto :end

:full_pipeline
echo.
echo 🔄 Running full pipeline for all configured sites...
python automation\cli_shortcuts.py full
goto :end

:monitor_input
echo.
echo 👀 Starting input directory monitoring...
echo Press Ctrl+C to stop monitoring
python automation\cli_shortcuts.py monitor
goto :end

:start_scheduler
echo.
echo ⏰ Starting automation scheduler...
echo Press Ctrl+C to stop scheduler
python automation\cli_shortcuts.py schedule
goto :end

:show_status
echo.
echo 📊 Current System Status:
python automation\cli_shortcuts.py status
goto :end

:generate_dashboard
echo.
echo 📈 Generating status dashboard...
python automation\cli_shortcuts.py dashboard
if exist "output\dashboard.html" (
    echo ✅ Dashboard generated: output\dashboard.html
    set /p open="Open dashboard in browser? (y/n): "
    if /i "!open!"=="y" start "" "output\dashboard.html"
) else (
    echo ❌ Failed to generate dashboard
)
goto :end

:test_notifications
echo.
echo 📧 Testing notification systems...
python automation\cli_shortcuts.py test
goto :end

:validate_system
echo.
echo 🔍 Validating system health...
python automation\cli_shortcuts.py validate
goto :end

:setup_environment
echo.
echo 🛠️ Setting up automation environment...
echo.

REM Create necessary directories
echo Creating directory structure...
if not exist "input" mkdir "input"
if not exist "output" mkdir "output"

REM Check configuration
if not exist "automation\config.yaml" (
    echo ⚠️ Configuration file not found. Creating default config...
    (
        echo # Default configuration for automation
        echo sites:
        echo   - example-bar.com
        echo notifications:
        echo   discord: ""
        echo   email: ""
        echo schedule:
        echo   daily: true
        echo dashboard:
        echo   enabled: true
    ) > "automation\config.yaml"
    echo Default config created at automation\config.yaml. Please edit this file to configure your settings.
)

REM Check Python dependencies
echo Checking Python dependencies...
python -m pip check
if errorlevel 1 (
    echo ❌ Some dependencies are missing or incompatible
    echo Run "%~n0 install" to install or fix dependencies
) else (
    echo ✅ All Python dependencies are satisfied
)

echo.
echo ✅ Environment setup complete!
echo Next steps:
echo   1. Edit automation\config.yaml with your settings
echo   2. Run "%~n0 validate" to check system health
echo   3. Run "%~n0 dashboard" to generate status dashboard
goto :end

:install_dependencies
echo.
echo 📦 Installing required dependencies...
echo.

REM Install Python packages
echo Installing Python packages from requirements.txt...
python -m pip install -r requirements.txt

if %errorlevel%==0 (
    echo ✅ Dependencies installed successfully
) else (
    echo ❌ Failed to install some dependencies
    echo Please check the error messages above
)
goto :end

:run_discovery
echo.
echo 🔍 Running List Discovery Agent...
python automation\cli_shortcuts.py discovery
goto :end

:configure_list_discovery
echo.
echo ⚙️ Configuring List Discovery URLs...
python automation\cli_shortcuts.py configure_list_discovery
goto :end

:show_help
echo.
echo Universal Project Runner - Command Reference
echo ==========================================
echo.
echo Commands:
echo   quick ^<site^>    - Quick pipeline run for a specific site
echo   full            - Run full pipeline for all configured sites  
echo   monitor         - Start monitoring input directories for new files
echo   schedule        - Start the automation scheduler (daily/weekly tasks)
echo   status          - Show current system status and recent activity
echo   dashboard       - Generate and display status dashboard
echo   test            - Test notification systems (Discord/Email)
echo   validate        - Run system health checks and validation
echo   setup           - Setup automation environment and directories
echo   install         - Install required Python dependencies
echo   discovery       - Run List Discovery Agent (check for new files)
echo   list-config     - Configure List Discovery URLs
echo   help            - Show this help message
echo   menu            - Show interactive menu
echo.
echo Examples:
echo   %~n0 quick example-bar.com
echo   %~n0 full --sites site1.com site2.com
echo   %~n0 monitor
echo   %~n0 dashboard ^&^& start output\dashboard.html
echo.
echo Configuration:
echo   Edit automation\config.yaml to configure:
echo   - Sites to monitor
echo   - Notification settings (Discord/Email)
echo   - Schedule timings
echo   - Dashboard preferences
echo.
goto :end

:end
echo.
echo Press any key to exit...
pause >nul
