<#
Prepares local Windows OpenSSH server for key-based self or remote admin access.
Adds id_ed25519_clear.pub to administrators_authorized_keys with secure ACLs.
#>
param(
    [string]$PublicKeyPath = "$env:USERPROFILE/.ssh/id_ed25519_clear.pub",
    [string]$AdminAuthKeys = "C:/ProgramData/ssh/administrators_authorized_keys"
)

if (-not (Test-Path $PublicKeyPath)) {
    Write-Host "[ERROR] Public key not found: $PublicKeyPath" -ForegroundColor Red
    exit 1
}

$key = Get-Content $PublicKeyPath -Raw
if (-not (Test-Path $AdminAuthKeys)) {
    New-Item -ItemType File -Path $AdminAuthKeys -Force | Out-Null
}

$current = Get-Content $AdminAuthKeys -Raw
if ($current -notmatch [regex]::Escape($key.Trim())) {
    Add-Content -Path $AdminAuthKeys -Value ($key.Trim() + "`n")
    Write-Host "[OK] Key appended"
}
else {
    Write-Host "[INFO] Key already present"
}

# Normalize encoding to ASCII (no BOM)
$tmp = Get-Content $AdminAuthKeys -Raw
Set-Content -Path $AdminAuthKeys -Value $tmp -Encoding ascii -NoNewline

# Secure permissions
icacls $AdminAuthKeys /inheritance:r | Out-Null
icacls $AdminAuthKeys /grant:r "Administrators:F" "SYSTEM:F" | Out-Null
Write-Host "[OK] Permissions set"

# Ensure sshd service up
Set-Service sshd -StartupType Automatic
Start-Service sshd
Get-Service sshd | Select-Object Status, Name, DisplayName
