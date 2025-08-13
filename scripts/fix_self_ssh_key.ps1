# Ensure local public key is present for administrative SSH and correct ACL
$pub = "$env:USERPROFILE/.ssh/id_ed25519_clear.pub"
$ak = 'C:/ProgramData/ssh/administrators_authorized_keys'
if (!(Test-Path $pub)) { Write-Error "Public key not found: $pub"; exit 1 }
$keyData = Get-Content $pub -Raw
if (!(Test-Path $ak)) { New-Item -ItemType File -Path $ak -Force | Out-Null }
$existing = Get-Content $ak -Raw
if ($existing -notmatch [Regex]::Escape($keyData.Trim())) {
    Add-Content -Path $ak -Value $keyData.Trim()
    # Normalize file to single newline separated entries
    (Get-Content $ak) | Where-Object { $_.Trim() } | Set-Content -Path $ak -Encoding ascii
    icacls $ak /inheritance:r | Out-Null
    icacls $ak /grant:r "Administrators:F" "SYSTEM:F" | Out-Null
    Write-Host "[UPDATED] administrators_authorized_keys updated."
}
else {
    Write-Host "[OK] Key already present in administrators_authorized_keys."
}
Set-Service sshd -StartupType Automatic
Start-Service sshd
Write-Host "[OK] sshd service ensured running."
