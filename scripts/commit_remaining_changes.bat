@echo off
REM CommitRemainingChanges.bat
REM A simple batch script to commit any remaining changes

echo ===================================================
echo   Committing Remaining Changes
echo ===================================================
echo.

git add -A
git commit -m "Final cross-device compatibility updates for ROG-LUCCI"
git push

echo.
echo Done! All changes have been committed and pushed.
pause
