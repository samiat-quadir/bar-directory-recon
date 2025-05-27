@echo off
REM ==========================================================================
REM safe_commit_push.bat
REM A wrapper for the safe_commit_push.py script that makes it easier to run
REM ==========================================================================

echo ===================================================
echo     Safe Commit and Push Tool
echo ===================================================
echo.

setlocal

set "PROJECT_ROOT=%~dp0"
if %PROJECT_ROOT:~-1%==\ set "PROJECT_ROOT=%PROJECT_ROOT:~0,-1%"

if "%1"=="--help" (
    echo Usage:
    echo   safe_commit_push.bat [options]
    echo.
    echo Options:
    echo   --dry-run    Run checks without committing or pushing
    echo   --message    Specify a commit message
    echo   --help       Display this help message
    goto :end
)

set MSG="Updated files from ROG-Lucci"
set DRY_RUN=

:parse_args
if "%1"=="" goto run
if "%1"=="--dry-run" (
    set DRY_RUN=--dry-run
    shift
    goto parse_args
)
if "%1"=="--message" (
    if not "%2"=="" (
        set MSG=%2
        shift
        shift
        goto parse_args
    ) else (
        echo Error: --message requires a value
        goto :end
    )
)

:run
if exist "%PROJECT_ROOT%\tools\safe_commit_push.py" (
    echo Running safe commit and push checks...
    echo.

    if defined DRY_RUN (
        echo DRY RUN MODE: Will not commit or push changes
        python "%PROJECT_ROOT%\tools\safe_commit_push.py" %DRY_RUN% --message %MSG%
    ) else (
        python "%PROJECT_ROOT%\tools\safe_commit_push.py" --message %MSG%
    )
) else (
    echo Error: safe_commit_push.py not found at expected location:
    echo %PROJECT_ROOT%\tools\safe_commit_push.py
)

:end
echo.
endlocal
