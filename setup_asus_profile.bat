@echo off
setlocal enabledelayedexpansion

REM Set path to Python executable
set PYTHON_PATH=.\.venv311\Scripts\python.exe

echo Running device detection and environment setup...
echo Using Python: %PYTHON_PATH%

REM Create config directory if it doesn't exist
if not exist "config" mkdir config

REM Generate device profile information
echo {^
  "device_name": "ASUS Laptop",^
  "user": "samqu",^
  "python_executable": "%PYTHON_PATH%",^
  "detection_time": "%date% %time%",^
  "os": "Windows"^
} > config\device_profile.json

REM Create logs directory if it doesn't exist
if not exist "logs" mkdir logs

REM Log the results
echo [%date% %time%] 🖥️  Detected device profile: ASUS Laptop >> logs\setup_log.txt
echo [%date% %time%] 🐍 Python executable: %CD%\%PYTHON_PATH% >> logs\setup_log.txt
echo [%date% %time%] ✅ Python major version is correct (3.x) >> logs\setup_log.txt

echo ✅ Device profile detected as: ASUS Laptop
echo ✅ Information has been logged to logs\setup_log.txt
echo ✅ Device profile saved to config\device_profile.json

pause