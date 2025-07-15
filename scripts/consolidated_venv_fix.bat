@echo off
REM Consolidated Virtual Environment Fix Script
REM Combines functionality from Fix-VenvPath.bat, Fix-VirtualEnvPath.bat, and fix_venv_activation.bat

echo Starting virtual environment fix process...

REM Check if virtual environment exists
if not exist ".venv" (
    echo Virtual environment not found. Creating new one...
    python -m venv .venv
    if errorlevel 1 (
        echo Failed to create virtual environment
        exit /b 1
    )
)

REM Activate virtual environment
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo Failed to activate virtual environment
    exit /b 1
)

REM Update pip and install requirements
python -m pip install --upgrade pip
if exist requirements.txt (
    pip install -r requirements.txt
    if errorlevel 1 (
        echo Warning: Some packages failed to install
    )
)

REM Fix common path issues for cross-device compatibility
python -c "
import sys
import os
from pathlib import Path

# Fix pyvenv.cfg for cross-device compatibility
venv_path = Path('.venv')
pyvenv_cfg = venv_path / 'pyvenv.cfg'

if pyvenv_cfg.exists():
    print('Updating pyvenv.cfg for cross-device compatibility...')
    with open(pyvenv_cfg, 'r') as f:
        content = f.read()
    
    # Update home path to current Python installation
    import sys
    python_home = str(Path(sys.executable).parent)
    
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if line.startswith('home = '):
            lines[i] = f'home = {python_home}'
            break
    
    with open(pyvenv_cfg, 'w') as f:
        f.write('\n'.join(lines))
    
    print('pyvenv.cfg updated successfully')
"

echo Virtual environment fix completed successfully!
echo Virtual environment is now activated and ready to use.
