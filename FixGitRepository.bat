@echo off
REM FixGitRepository.bat
REM Attempts to fix common Git repository issues

echo ===================================================
echo   Git Repository Repair Tool
echo ===================================================
echo.

REM Store the current directory
set PROJECT_ROOT=%~dp0
if %PROJECT_ROOT:~-1%==\ set PROJECT_ROOT=%PROJECT_ROOT:~0,-1%

echo Current directory: %PROJECT_ROOT%
echo.

echo Step 1: Checking if .git directory exists...
if not exist "%PROJECT_ROOT%\.git" (
    echo ERROR: This is not a Git repository ^(.git directory not found^)
    echo Please run this script in a valid Git repository.
    pause
    exit /b 1
)

echo Step 2: Running git fsck to check for corruption...
git fsck --full
echo.

echo Step 3: Running git gc to clean up and optimize...
git gc --aggressive
echo.

echo Step 4: Running git reflog to verify history...
git reflog expire --expire=now --all
echo.

echo Step 5: Testing HEAD reference...
git rev-parse --verify HEAD >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo WARNING: HEAD reference is invalid
    echo Attempting to fix HEAD reference...

    echo Listing available branches:
    git branch -a
    echo.

    set /p BRANCH_NAME=Enter a valid branch name to reset HEAD to (or press Enter to use 'main'):
    if "%BRANCH_NAME%"=="" set BRANCH_NAME=main

    echo Attempting to set HEAD to %BRANCH_NAME%...
    git symbolic-ref HEAD refs/heads/%BRANCH_NAME% 2>nul
    if %ERRORLEVEL% NEQ 0 (
        echo Failed to set HEAD to %BRANCH_NAME%, trying 'master'...
        git symbolic-ref HEAD refs/heads/master 2>nul
        if %ERRORLEVEL% NEQ 0 (
            echo ERROR: Could not set HEAD to a valid branch.
            echo.
            echo You may need to recreate this repository by:
            echo 1. Backing up your current files
            echo 2. Cloning a fresh copy of the repository
            echo 3. Copying your changes back
            pause
            exit /b 1
        ) else (
            echo Successfully reset HEAD to 'master'!
        )
    ) else (
        echo Successfully reset HEAD to '%BRANCH_NAME%'!
    )
)

echo Step 6: Final verification...
git status
echo.

echo ===================================================
echo  Git Repository Repair Complete
echo ===================================================
echo.
echo If you still see errors, please consider recreating
echo the repository from a fresh clone.
echo.

pause
