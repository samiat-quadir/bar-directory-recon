@echo off
REM List Discovery Agent CLI Interface
REM Phase 4 - Quick access to web monitoring commands

setlocal enabledelayedexpansion

echo.
echo ===============================================
echo 📋 LIST DISCOVERY AGENT - PHASE 4
echo ===============================================
echo.

if "%1"=="" goto :show_menu

REM Handle command line arguments
if "%1"=="check" goto :run_check
if "%1"=="monitor" goto :run_monitor
if "%1"=="status" goto :run_status
if "%1"=="setup" goto :run_setup
if "%1"=="add" goto :run_add
if "%1"=="remove" goto :run_remove
if "%1"=="list" goto :run_list
if "%1"=="install" goto :run_install
if "%1"=="help" goto :show_help

echo ❌ Unknown command: %1
goto :show_help

:show_menu
echo Select an option:
echo.
echo 1. 🔍 Check for new files (single run)
echo 2. 👀 Start continuous monitoring
echo 3. 📊 Show status and statistics
echo 4. ⚙️  Setup configuration
echo 5. ➕ Add URL to monitor
echo 6. ➖ Remove URL from monitoring
echo 7. 📝 List configured URLs
echo 8. 📦 Install dependencies
echo 9. ❓ Show help
echo 0. 🚪 Exit
echo.
set /p choice="Enter your choice (0-9): "

if "%choice%"=="1" goto :run_check
if "%choice%"=="2" goto :run_monitor
if "%choice%"=="3" goto :run_status
if "%choice%"=="4" goto :run_setup
if "%choice%"=="5" goto :run_add
if "%choice%"=="6" goto :run_remove
if "%choice%"=="7" goto :run_list
if "%choice%"=="8" goto :run_install
if "%choice%"=="9" goto :show_help
if "%choice%"=="0" goto :exit

echo ❌ Invalid choice. Please try again.
echo.
goto :show_menu

:run_check
echo 🔍 Checking for new files...
python list_discovery/agent.py check
echo.
if not "%1"=="" goto :exit
goto :show_menu

:run_monitor
echo 👀 Starting continuous monitoring...
echo Press Ctrl+C to stop monitoring
python list_discovery/agent.py monitor
echo.
if not "%1"=="" goto :exit
goto :show_menu

:run_status
echo 📊 Getting status...
python list_discovery/agent.py status
echo.
if not "%1"=="" goto :exit
goto :show_menu

:run_setup
echo ⚙️ Setting up configuration...
python list_discovery/agent.py setup
echo.
if not "%1"=="" goto :exit
goto :show_menu

:run_add
if not "%2"=="" (
    if not "%3"=="" (
        echo ➕ Adding URL: %2 with name: %3
        python list_discovery/agent.py add "%2" --name "%3"
    ) else (
        echo ➕ Adding URL: %2
        python list_discovery/agent.py add "%2"
    )
) else (
    set /p url="Enter URL to monitor: "
    set /p name="Enter display name (optional): "
    if "!name!"=="" (
        python list_discovery/agent.py add "!url!"
    ) else (
        python list_discovery/agent.py add "!url!" --name "!name!"
    )
)
echo.
if not "%1"=="" goto :exit
goto :show_menu

:run_remove
if not "%2"=="" (
    echo ➖ Removing URL: %2
    python list_discovery/agent.py remove "%2"
) else (
    echo Current URLs:
    python list_discovery/agent.py list
    echo.
    set /p target="Enter URL or index number to remove: "
    python list_discovery/agent.py remove "!target!"
)
echo.
if not "%1"=="" goto :exit
goto :show_menu

:run_list
echo 📝 Configured URLs:
python list_discovery/agent.py list
echo.
if not "%1"=="" goto :exit
goto :show_menu

:run_install
echo 📦 Installing List Discovery Agent dependencies...
echo.
echo Installing core requirements...
pip install aiohttp aiofiles beautifulsoup4 PyYAML lxml html5lib
echo.
echo Installing optional requirements...
pip install selenium playwright PyPDF2 pdfplumber openpyxl pandas
echo.
echo ✅ Installation complete!
echo.
if not "%1"=="" goto :exit
goto :show_menu

:show_help
echo.
echo 📖 LIST DISCOVERY AGENT HELP
echo ===============================================
echo.
echo COMMANDS:
echo   check      - Run single check for new files
echo   monitor    - Start continuous monitoring
echo   status     - Show current status and statistics
echo   setup      - Setup initial configuration
echo   add URL    - Add URL to monitor
echo   remove ID  - Remove URL from monitoring
echo   list       - List all configured URLs
echo   install    - Install required dependencies
echo   help       - Show this help message
echo.
echo EXAMPLES:
echo   RunListDiscovery.bat check
echo   RunListDiscovery.bat add "https://county.gov/licenses" "County Licenses"
echo   RunListDiscovery.bat remove 1
echo.
echo CONFIGURATION:
echo   Edit list_discovery/config.yaml to configure:
echo   - URLs to monitor
echo   - Download directory
echo   - Check intervals
echo   - Notification settings
echo.
echo INTEGRATION:
echo   The List Discovery Agent integrates with the Universal
echo   Project Runner. Downloaded files are automatically
echo   processed by the main pipeline.
echo.
if not "%1"=="" goto :exit
goto :show_menu

:exit
echo.
echo 👋 Goodbye!
echo.
pause
exit /b 0
