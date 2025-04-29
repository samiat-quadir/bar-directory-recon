@echo off
setlocal
set date=%date:~10,4%-%date:~4,2%-%date:~7,2%
set backup_dir=backups
set zip_name=backup_%date%.zip

if not exist %backup_dir% mkdir %backup_dir%
powershell Compress-Archive -Path universal_recon -DestinationPath %backup_dir%\%zip_name%
echo ✅ Backup created: %backup_dir%\%zip_name%
endlocal
