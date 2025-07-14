@echo off
REM Google Sheets Integration Test Batch File

echo Testing Google Sheets Integration...
echo =====================================

REM Activate virtual environment
call ".venv\Scripts\activate.bat"

REM Install required packages
echo Installing Google API dependencies...
pip install google-api-python-client google-auth-oauthlib google-auth-httplib2

REM Test CLI arguments
echo Testing CLI arguments...
python universal_automation.py --help

REM Test Google Sheets integration
echo Testing Google Sheets integration...
python -c "from google_sheets_integration import GoogleSheetsIntegration; print('Google Sheets integration imported successfully')"

echo.
echo Test complete!
pause
