@echo off
REM ScanPaths.bat
REM This script runs both PowerShell and Python path scanners to check for hardcoded paths

echo =====================================================
echo   Cross-Device Path Compatibility Scanner
echo =====================================================
echo.

setlocal enabledelayedexpansion

set "PROJECT_ROOT=%~dp0"
set "PROJECT_ROOT=%PROJECT_ROOT:~0,-1%"

REM Check for command-line arguments
set FIX_MODE=
if "%1"=="--fix" (
    set FIX_MODE=--fix
    echo Running in FIX mode - will attempt to fix issues automatically
    echo.
)

REM Run PowerShell scanner
echo Running PowerShell path scanner...
echo.
powershell -ExecutionPolicy Bypass -NoProfile -Command ^
    "& { . '%PROJECT_ROOT%\tools\Scan_For_Hardcoded_Paths.ps1' %FIX_MODE% }"

echo.
echo =====================================================
echo.

REM Check if Python virtual environment exists
if exist "%PROJECT_ROOT%\.venv\Scripts\python.exe" (
    echo Running Python path scanner...
    echo.

    "%PROJECT_ROOT%\.venv\Scripts\python.exe" "%PROJECT_ROOT%\tools\scan_hardcoded_paths.py" %FIX_MODE%
) else (
    echo Virtual environment not found at "%PROJECT_ROOT%\.venv"
    echo Cannot run Python path scanner.
)

echo.
echo =====================================================
echo Path scanning completed.
echo See results above for any necessary actions.
echo =====================================================

pause
