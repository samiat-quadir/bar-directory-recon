@echo off
REM Launch Suite for Bar Directory Recon - Windows Batch Version
REM Usage: launch_suite.bat [mode]
REM Modes: full, dashboard, demo, env-check, async-demo

setlocal enabledelayedexpansion

REM Colors for output
set "GREEN=[32m"
set "RED=[31m"
set "YELLOW=[33m"
set "BLUE=[34m"
set "CYAN=[36m"
set "RESET=[0m"

set "mode=%1"
if "%mode%"=="" set "mode=full"

echo %CYAN%🚀 Bar Directory Recon Launch Suite%RESET%
echo %BLUE%=================================================%RESET%
echo Mode: %YELLOW%!mode!%RESET%
echo Timestamp: %DATE% %TIME%
echo.

REM Validate mode
if /i "!mode!"=="full" goto :valid_mode
if /i "!mode!"=="dashboard" goto :valid_mode
if /i "!mode!"=="demo" goto :valid_mode
if /i "!mode!"=="env-check" goto :valid_mode
if /i "!mode!"=="async-demo" goto :valid_mode

echo %RED%❌ Invalid mode: !mode!%RESET%
echo Valid modes: full, dashboard, demo, env-check, async-demo
exit /b 1

:valid_mode

REM Check virtual environment
echo %BLUE%🔍 Checking virtual environment...%RESET%
if exist ".venv\Scripts\python.exe" (
    echo %GREEN%✅ Virtual environment found%RESET%
    set "PYTHON_CMD=.venv\Scripts\python.exe"
) else (
    echo %YELLOW%⚠️  Virtual environment not found, using system Python%RESET%
    set "PYTHON_CMD=python"
)

REM Load environment
echo %BLUE%🔧 Loading environment configuration...%RESET%
%PYTHON_CMD% env_loader.py
if !errorlevel! neq 0 (
    echo %YELLOW%⚠️  Environment loading completed with warnings%RESET%
) else (
    echo %GREEN%✅ Environment loaded successfully%RESET%
)

echo.

REM Execute based on mode
if /i "!mode!"=="env-check" (
    echo %GREEN%✅ Environment check completed%RESET%
    goto :end
)

if /i "!mode!"=="async-demo" (
    echo %BLUE%🔄 Running AsyncPipelineExecutor demo...%RESET%
    %PYTHON_CMD% async_pipeline_demo.py
    goto :end
)

if /i "!mode!"=="demo" (
    echo %BLUE%🎯 Running automation demo...%RESET%
    if exist "automation_demo.py" (
        %PYTHON_CMD% automation_demo.py
    ) else (
        echo %YELLOW%⚠️  automation_demo.py not found%RESET%
    )
    goto :end
)

if /i "!mode!"=="dashboard" (
    echo %BLUE%📊 Starting dashboard server...%RESET%
    if exist "automation\dashboard.py" (
        %PYTHON_CMD% automation\dashboard.py
    ) else (
        echo %YELLOW%⚠️  automation\dashboard.py not found%RESET%
    )
    goto :end
)

if /i "!mode!"=="full" (
    echo %BLUE%🚀 Running full automation suite...%RESET%

    REM Run async demo first
    echo %CYAN%Step 1: AsyncPipelineExecutor Demo%RESET%
    %PYTHON_CMD% async_pipeline_demo.py

    echo.
    echo %CYAN%Step 2: Starting Dashboard Server%RESET%
    if exist "automation\dashboard.py" (
        echo %BLUE%📊 Starting dashboard server in background...%RESET%
        start /b %PYTHON_CMD% automation\dashboard.py
        echo %GREEN%✅ Dashboard server started%RESET%
    ) else (
        echo %YELLOW%⚠️  automation\dashboard.py not found%RESET%
    )

    goto :end
)

:end
echo.
echo %GREEN%🎯 Launch suite execution completed%RESET%
echo %BLUE%=================================================%RESET%
endlocal
