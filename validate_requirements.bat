@echo off
REM Validate and fix requirements files
REM Usage: validate_requirements.bat [--fix]

echo 🔍 Validating requirements files...

python tools\validate_requirements.py %*

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ❌ Requirements validation failed!
    echo 💡 Run with --fix to automatically fix issues:
    echo    validate_requirements.bat --fix
    exit /b 1
) else (
    echo.
    echo ✅ Requirements validation passed!
)
