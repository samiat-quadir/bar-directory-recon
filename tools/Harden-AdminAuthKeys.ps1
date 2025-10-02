# Harden-AdminAuthKeys.ps1 - Harden administrators_authorized_keys with proper permissions
# Mirrors Ali's implementation for cross-device parity

[CmdletBinding()]
param(
    [switch]$VerboseOutput,
    [string]$KeyContent = $null,
    [string]$PubKeyPath = $null
)

$ErrorActionPreference = "Stop"

function Write-Log {
    param([string]$Message, [string]$Level = "INFO")
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    Write-Host "[$timestamp] [$Level] $Message"
}

function Test-IsAdministrator {
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

try {
    Write-Log "Starting administrators_authorized_keys hardening..."

    # Check if running as administrator
    if (-not (Test-IsAdministrator)) {
        throw "This script must be run as Administrator to modify SSH key permissions"
    }

    # Define paths
    $sshDir = "C:\ProgramData\ssh"
    $authKeysFile = "$sshDir\administrators_authorized_keys"

    # Ensure SSH directory exists
    if (-not (Test-Path $sshDir)) {
        Write-Log "Creating SSH directory: $sshDir"
        New-Item -ItemType Directory -Path $sshDir -Force | Out-Null
    }

    # Create or verify administrators_authorized_keys file
    if (-not (Test-Path $authKeysFile)) {
        Write-Log "Creating administrators_authorized_keys file: $authKeysFile"
        New-Item -ItemType File -Path $authKeysFile -Force | Out-Null
    }
    else {
        Write-Log "administrators_authorized_keys file exists: $authKeysFile"
    }

    # Add key content if provided
    if ($PubKeyPath) {
        if (Test-Path $PubKeyPath) {
            Write-Log "Reading public key from: $PubKeyPath"
            $KeyContent = Get-Content $PubKeyPath -Raw -ErrorAction SilentlyContinue
            $KeyContent = $KeyContent.Trim()
            Write-Log "Loaded key content from file (length: $($KeyContent.Length))"
        }
        else {
            throw "Public key file not found: $PubKeyPath"
        }
    }

    if ($KeyContent) {
        Write-Log "Adding provided key content to authorized_keys"
        # Check if key already exists to avoid duplicates
        $existingContent = Get-Content $authKeysFile -Raw -ErrorAction SilentlyContinue
        if ($existingContent -and $existingContent.Contains($KeyContent.Trim())) {
            Write-Log "Key already exists in authorized_keys file"
        }
        else {
            Add-Content -Path $authKeysFile -Value $KeyContent -Encoding UTF8
            Write-Log "Key added to authorized_keys file"
        }
    }

    # Ensure file is ASCII encoded (no BOM)
    Write-Log "Converting file to ASCII encoding (no BOM)..."
    $content = Get-Content $authKeysFile -Raw -ErrorAction SilentlyContinue
    if ($content) {
        Set-Content -Path $authKeysFile -Value $content -Encoding ASCII -NoNewline
    }

    # Set proper permissions (remove inheritance, grant only to SYSTEM and Administrators)
    Write-Log "Setting restrictive permissions on administrators_authorized_keys..."

    # Remove inheritance
    $acl = Get-Acl $authKeysFile
    $acl.SetAccessRuleProtection($true, $false)  # Disable inheritance, don't copy current rules

    # Clear existing access rules
    $acl.Access | ForEach-Object { $acl.RemoveAccessRule($_) }

    # Add SYSTEM full control
    $systemSid = New-Object System.Security.Principal.SecurityIdentifier([System.Security.Principal.WellKnownSidType]::LocalSystemSid, $null)
    $systemAccess = New-Object System.Security.AccessControl.FileSystemAccessRule(
        $systemSid,
        [System.Security.AccessControl.FileSystemRights]::FullControl,
        [System.Security.AccessControl.AccessControlType]::Allow
    )
    $acl.SetAccessRule($systemAccess)

    # Add Administrators full control
    $adminsSid = New-Object System.Security.Principal.SecurityIdentifier([System.Security.Principal.WellKnownSidType]::BuiltinAdministratorsSid, $null)
    $adminsAccess = New-Object System.Security.AccessControl.FileSystemAccessRule(
        $adminsSid,
        [System.Security.AccessControl.FileSystemRights]::FullControl,
        [System.Security.AccessControl.AccessControlType]::Allow
    )
    $acl.SetAccessRule($adminsAccess)

    # Apply the ACL
    Set-Acl -Path $authKeysFile -AclObject $acl

    Write-Log "Permissions set: SYSTEM and Administrators have full control"

    # Verify permissions
    if ($VerboseOutput) {
        Write-Log "Current permissions on ${authKeysFile}:"
        $currentAcl = Get-Acl $authKeysFile
        $currentAcl.Access | ForEach-Object {
            Write-Log "  $($_.IdentityReference): $($_.FileSystemRights) ($($_.AccessControlType))"
        }
    }

    # Verify file properties
    $fileInfo = Get-Item $authKeysFile
    Write-Log "File size: $($fileInfo.Length) bytes"
    Write-Log "Last modified: $($fileInfo.LastWriteTime)"

    # Check if file contains any keys
    $keyCount = (Get-Content $authKeysFile -ErrorAction SilentlyContinue | Where-Object { $_.Trim() -ne "" }).Count
    Write-Log "Number of authorization keys: $keyCount"

    Write-Log "administrators_authorized_keys hardening completed successfully" -Level "SUCCESS"
    exit 0

}
catch {
    Write-Log "Error hardening administrators_authorized_keys: $($_.Exception.Message)" -Level "ERROR"
    if ($VerboseOutput) {
        Write-Log "Full error details: $($_ | Out-String)" -Level "ERROR"
    }
    exit 1
}
