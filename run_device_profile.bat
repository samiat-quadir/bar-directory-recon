@echo off
REM Run resolve_device_profile.py with explicit path to Python in virtual environment
set PYTHON_PATH=%~dp0.venv311\Scripts\python.exe
echo Using Python: %PYTHON_PATH%
"%PYTHON_PATH%" %~dp0tools\resolve_device_profile.py
pause
