@echo off
REM Fix self-SSH authentication by updating administrators_authorized_keys with the correct key
echo Fixing self-SSH authentication...

set PUBLIC_KEY=%USERPROFILE%\.ssh\id_ed25519_clear.pub
set AUTH_KEYS=C:\ProgramData\ssh\administrators_authorized_keys

if not exist "%PUBLIC_KEY%" (
    echo ERROR: Public key not found at %PUBLIC_KEY%
    exit /b 1
)

echo Updating administrators_authorized_keys with correct key...
copy "%PUBLIC_KEY%" "%AUTH_KEYS%" >nul 2>&1

if %ERRORLEVEL% neq 0 (
    echo ERROR: Failed to update administrators_authorized_keys. Running as administrator...
    powershell -Command "Start-Process cmd -ArgumentList '/c copy \"%PUBLIC_KEY%\" \"%AUTH_KEYS%\"' -Verb RunAs"
    echo Please run this script as administrator or manually copy the key.
    exit /b 1
)

echo Setting proper permissions on administrators_authorized_keys...
icacls "%AUTH_KEYS%" /inheritance:r >nul 2>&1
icacls "%AUTH_KEYS%" /grant:r "Administrators:F" "SYSTEM:F" >nul 2>&1

echo Testing self-SSH connection...
ssh -o IdentitiesOnly=yes -o ConnectTimeout=5 rog-lucci "echo Self-SSH working"

if %ERRORLEVEL% equ 0 (
    echo SUCCESS: Self-SSH authentication fixed!
) else (
    echo WARNING: Self-SSH still not working. Check SSH service and key configuration.
)
