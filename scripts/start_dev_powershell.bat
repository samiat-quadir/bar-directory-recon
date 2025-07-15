@echo off
REM ====================================================================
REM OneDrive Development Environment PowerShell Launcher
REM This script launches a PowerShell session with the virtual environment activated
REM ====================================================================

echo ===================================================
echo   Starting PowerShell Development Environment
echo ===================================================
echo.

REM Start PowerShell with the activation script
powershell -NoExit -ExecutionPolicy Bypass -Command "& '%~dp0ActivateVenv.ps1'"
