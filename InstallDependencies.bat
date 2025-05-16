@echo off
REM ====================================================================
REM Install Project Dependencies
REM This script ensures all project dependencies are installed
REM ====================================================================

echo ===================================================
echo   Installing Project Dependencies
echo ===================================================
echo.

REM Store the current directory
set PROJECT_ROOT=%~dp0
cd /d "%PROJECT_ROOT%"

REM Activate the virtual environment
echo Activating Python virtual environment...
call .venv\Scripts\activate.bat

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to activate virtual environment.
    echo        Please run fix_venv_activation.bat first.
    goto :end
)

echo Installing dependencies...

REM Install development dependencies
echo Installing development tools and testing dependencies...
pip install -e ".[dev]" pytest pytest-cov black isort flake8 mypy bandit pre-commit

REM Install project dependencies
echo Installing project dependencies...
pip install -r requirements.txt

echo.
echo All dependencies have been installed successfully!
echo You can now run the project using RunDevelopment.bat

:end
call deactivate
exit /b 0
