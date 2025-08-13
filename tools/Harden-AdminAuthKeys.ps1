[CmdletBinding()]
param(
    [string]$PubKeyPath = "$env:USERPROFILE\.ssh\id_ed25519_clear.pub"
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$ak = 'C:\ProgramData\ssh\administrators_authorized_keys'

if (-not (Test-Path $PubKeyPath)) { Write-Error "Pub key not found: $PubKeyPath"; exit 1 }
if (-not (Test-Path $ak)) { New-Item -ItemType File -Path $ak -Force | Out-Null }

$raw = Get-Content $PubKeyPath -Raw
if (-not (Select-String -Path $ak -SimpleMatch $raw -Quiet)) {
    Add-Content -Path $ak -Value $raw
}
# Re-write ASCII (no BOM)
$tmp = Get-Content $ak -Raw
Set-Content -Path $ak -Value $tmp -Encoding ascii -NoNewline

# Lock ACLs to Administrators + SYSTEM
icacls $ak /inheritance:r | Out-Null
icacls $ak /grant:r "Administrators:F" "SYSTEM:F" | Out-Null
Write-Host "administrators_authorized_keys OK"
