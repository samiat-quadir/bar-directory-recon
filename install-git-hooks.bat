@echo off
REM ====================================================================
REM install-git-hooks.bat
REM Installs Git hooks for cross-device path validation
REM ====================================================================

echo ===================================================
echo   Installing Git Hooks for Cross-Device Development
echo ===================================================
echo.

setlocal enabledelayedexpansion

set "PROJECT_ROOT=%~dp0"
set "PROJECT_ROOT=%PROJECT_ROOT:~0,-1%"
set "GIT_HOOKS_DIR=%PROJECT_ROOT%\.git\hooks"
set "PRE_COMMIT_HOOK=%GIT_HOOKS_DIR%\pre-commit"
set "PRE_COMMIT_SOURCE=%PROJECT_ROOT%\pre-commit-hooks\check_hardcoded_paths.py"

REM Check if .git directory exists
if not exist "%PROJECT_ROOT%\.git" (
    echo ERROR: No Git repository found at %PROJECT_ROOT%
    echo This script must be run from the root of a Git repository.
    goto END
)

REM Create hooks directory if it doesn't exist
if not exist "%GIT_HOOKS_DIR%" (
    echo Creating Git hooks directory...
    mkdir "%GIT_HOOKS_DIR%"
)

REM Check if pre-commit-hooks directory exists
if not exist "%PROJECT_ROOT%\pre-commit-hooks" (
    echo ERROR: Pre-commit hooks directory not found.
    echo Expected: %PROJECT_ROOT%\pre-commit-hooks
    goto END
)

REM Check if source hook exists
if not exist "%PRE_COMMIT_SOURCE%" (
    echo ERROR: Pre-commit hook source file not found.
    echo Expected: %PRE_COMMIT_SOURCE%
    goto END
)

REM Create pre-commit hook
echo Installing pre-commit hook for hardcoded path checking...
copy "%PRE_COMMIT_SOURCE%" "%PRE_COMMIT_HOOK%" >nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Failed to install pre-commit hook.
    goto END
)

REM Make the hook executable
powershell -Command "& { if (Test-Path '%PRE_COMMIT_HOOK%') { $acl = Get-Acl '%PRE_COMMIT_HOOK%'; $acl.SetAccessRuleProtection($false, $false); Set-Acl '%PRE_COMMIT_HOOK%' $acl } }"

echo.
echo Pre-commit hook successfully installed!
echo This hook will check for hardcoded paths when you commit code.
echo To bypass this check, use: git commit --no-verify

:END
echo.
echo Press any key to exit...
pause >nul
