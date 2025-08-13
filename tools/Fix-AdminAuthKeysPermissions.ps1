# Fix-AdminAuthKeysPermissions.ps1 - Fix ACL permissions and add Ali's key
# Resolves: Access to the path 'C:\ProgramData\ssh\administrators_authorized_keys' is denied.

[CmdletBinding()]
param(
    [string]$AliKeyPath = "C:\Users\samqu\OneDrive - Digital Age Marketing Group\ssh\ali_id_ed25519_clear.pub"
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
    Write-Log "Starting ACL fix and key addition for administrators_authorized_keys..."

    # Check if running as administrator
    if (-not (Test-IsAdministrator)) {
        throw "This script must be run as Administrator to modify SSH key permissions"
    }

    # Define paths
    $authKeysFile = "C:\ProgramData\ssh\administrators_authorized_keys"

    # Verify the file exists
    if (-not (Test-Path $authKeysFile)) {
        throw "administrators_authorized_keys file not found: $authKeysFile"
    }

    # Verify Ali's key file exists
    if (-not (Test-Path $AliKeyPath)) {
        throw "Ali's key file not found: $AliKeyPath"
    }

    # Read Ali's key content
    $aliKeyContent = Get-Content $AliKeyPath -Raw -ErrorAction Stop
    $aliKeyContent = $aliKeyContent.Trim()
    Write-Log "Loaded Ali's key content (length: $($aliKeyContent.Length))"

    # Check if key already exists to avoid duplicates
    $existingContent = Get-Content $authKeysFile -Raw -ErrorAction SilentlyContinue
    if ($existingContent -and $existingContent.Contains($aliKeyContent.Trim())) {
        Write-Log "Ali's key already exists in authorized_keys file"
        exit 0
    }

    Write-Log "Taking ownership of administrators_authorized_keys file..."

    # Take ownership of the file
    takeown /f $authKeysFile /a

    Write-Log "Granting full control to Administrators group..."

    # Grant full control to Administrators group
    icacls $authKeysFile /grant "Administrators:(F)" /inheritance:r

    Write-Log "Adding Ali's key to administrators_authorized_keys..."

    # Add Ali's key to the file
    Add-Content -Path $authKeysFile -Value $aliKeyContent -Encoding UTF8

    Write-Log "Ali's key added successfully"

    # Restore proper restrictive permissions
    Write-Log "Restoring restrictive permissions..."

    # Remove inheritance and set proper permissions
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

    # Apply the restrictive ACL
    Set-Acl -Path $authKeysFile -AclObject $acl

    Write-Log "Restrictive permissions restored"

    # Verify the key was added
    $finalContent = Get-Content $authKeysFile -Raw
    if ($finalContent.Contains("ALI-clear")) {
        Write-Log "SUCCESS: Ali's key verified in administrators_authorized_keys" -Level "SUCCESS"

        # Show key count
        $keyCount = (Get-Content $authKeysFile | Where-Object { $_.Trim() -ne "" }).Count
        Write-Log "Total authorized keys: $keyCount"

        # Show keys with their comments
        Write-Log "Authorized keys:"
        Get-Content $authKeysFile | Where-Object { $_.Trim() -ne "" } | ForEach-Object {
            $parts = $_ -split '\s+'
            if ($parts.Length -ge 3) {
                Write-Log "  - $($parts[2])"
            }
        }

    }
    else {
        throw "Key addition verification failed - ALI-clear pattern not found"
    }

    Write-Log "ACL fix and key addition completed successfully" -Level "SUCCESS"
    exit 0

}
catch {
    Write-Log "Error: $($_.Exception.Message)" -Level "ERROR"
    Write-Log "Full error details: $($_ | Out-String)" -Level "ERROR"
    exit 1
}
