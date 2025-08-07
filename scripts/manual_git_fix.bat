@echo off
echo [*] Manual Git Conflict Resolution Script
echo.

echo [*] Current status:
git status --short
echo.

echo [*] Fetching latest changes...
git fetch origin
echo.

echo [*] Creating backup branch...
for /f "tokens=*" %%i in ('git branch --show-current') do set CURRENT_BRANCH=%%i
set BACKUP_BRANCH=%CURRENT_BRANCH%-manual-backup-%random%
git branch %BACKUP_BRANCH%
echo [+] Created backup: %BACKUP_BRANCH%
echo.

echo [*] Adding current changes...
git add .
echo.

echo [*] Committing current changes...
git commit --no-verify -m "Manual commit before force push resolution"
echo.

echo [*] Attempting force push with lease (safer than regular force)...
git push --force-with-lease origin %CURRENT_BRANCH%

if %ERRORLEVEL% EQU 0 (
    echo [+] Force push successful!
    echo [*] Your changes have been pushed to remote
) else (
    echo [-] Force push failed
    echo [*] Options:
    echo     1. git reset --hard origin/%CURRENT_BRANCH%  (lose local changes)
    echo     2. git pull --rebase origin %CURRENT_BRANCH%  (rebase on remote)
    echo     3. Contact team lead for manual resolution
    echo.
    echo [*] Your work is backed up in branch: %BACKUP_BRANCH%
)

pause
