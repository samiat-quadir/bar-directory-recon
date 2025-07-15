@echo off
REM RecreateVenv.bat
REM This script recreates the virtual environment from scratch

echo ===================================================
echo   Recreating Python Virtual Environment
echo ===================================================
echo.

REM Store the current directory
set PROJECT_ROOT=%~dp0
if %PROJECT_ROOT:~-1%==\ set PROJECT_ROOT=%PROJECT_ROOT:~0,-1%

echo Project root: %PROJECT_ROOT%
echo.

REM Deactivate virtual environment if active
if defined VIRTUAL_ENV (
    echo Deactivating current virtual environment...
    call deactivate
)

REM Backup requirements if exists
if exist "%PROJECT_ROOT%\requirements.txt" (
    echo Backing up requirements.txt...
    copy "%PROJECT_ROOT%\requirements.txt" "%PROJECT_ROOT%\requirements.txt.bak"
)

REM Remove existing virtual environment
if exist "%PROJECT_ROOT%\.venv" (
    echo Removing existing virtual environment...
    rmdir /s /q "%PROJECT_ROOT%\.venv"
)

REM Create new virtual environment
echo Creating new virtual environment...
python -m venv "%PROJECT_ROOT%\.venv"

REM Activate the new environment
echo Activating new virtual environment...
call "%PROJECT_ROOT%\.venv\Scripts\activate.bat"

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install requirements if exists
if exist "%PROJECT_ROOT%\requirements.txt" (
    echo Installing requirements...
    pip install -r "%PROJECT_ROOT%\requirements.txt"
)

REM Install development tools
echo Installing development tools...
pip install black==24.4.0 ruff==0.4.7 autoflake==2.3.1 pre-commit

echo.
echo Virtual environment has been recreated successfully!
echo.

echo You can now activate the virtual environment with:
echo   call .venv\Scripts\activate.bat

pause
