@echo off
REM This batch file creates a launcher for activating the Python virtual environment

REM Store the current directory
set ORIGINAL_DIR=%CD%

REM Navigate to the script's directory
cd /d "%~dp0"

REM Create the activate.bat file in the Scripts directory
echo @echo off > .venv\Scripts\activate.bat
echo REM This script activates the virtual environment >> .venv\Scripts\activate.bat
echo set "VIRTUAL_ENV=%CD%\.venv" >> .venv\Scripts\activate.bat
echo if defined _OLD_VIRTUAL_PROMPT (>> .venv\Scripts\activate.bat
echo     set "PROMPT=%%_OLD_VIRTUAL_PROMPT%%" >> .venv\Scripts\activate.bat
echo ) else (>> .venv\Scripts\activate.bat
echo     if not defined PROMPT (>> .venv\Scripts\activate.bat
echo         set "PROMPT=$P$G" >> .venv\Scripts\activate.bat
echo     )>> .venv\Scripts\activate.bat
echo     set "_OLD_VIRTUAL_PROMPT=%%PROMPT%%" >> .venv\Scripts\activate.bat
echo     set "PROMPT=(venv) %%PROMPT%%" >> .venv\Scripts\activate.bat
echo )>> .venv\Scripts\activate.bat
echo set "_OLD_VIRTUAL_PYTHONHOME=%%PYTHONHOME%%" >> .venv\Scripts\activate.bat
echo set PYTHONHOME= >> .venv\Scripts\activate.bat
echo if defined _OLD_VIRTUAL_PATH (>> .venv\Scripts\activate.bat
echo     set "PATH=%%_OLD_VIRTUAL_PATH%%" >> .venv\Scripts\activate.bat
echo ) else (>> .venv\Scripts\activate.bat
echo     set "_OLD_VIRTUAL_PATH=%%PATH%%" >> .venv\Scripts\activate.bat
echo )>> .venv\Scripts\activate.bat
echo set "PATH=%%VIRTUAL_ENV%%\Scripts;%%PATH%%" >> .venv\Scripts\activate.bat
echo echo Virtual environment activated successfully >> .venv\Scripts\activate.bat

REM Return to the original directory
cd /d "%ORIGINAL_DIR%"

echo Created activate.bat file for the virtual environment
echo You can now activate the virtual environment using:
echo .venv\Scripts\activate.bat
