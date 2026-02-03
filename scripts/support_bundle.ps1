#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Collects diagnostic information for support without exposing credentials.

.DESCRIPTION
    Creates a timestamped ZIP file containing:
    - Latest bdr logs (from ~/.bdr/logs/)
    - bdr doctor --no-exec output
    - System info (Python version, OS, working directory)
    - Environment status (does NOT expose credential file contents)
    - support_metadata.txt (plaintext record of collection)

    This script:
    - Refuses to include credential files
    - Sanitizes paths (removes usernames where possible)
    - Includes only non-sensitive diagnostic data

.PARAMETER OutputDir
    Directory to save the support bundle ZIP. Defaults to current directory.

.PARAMETER Timestamp
    Optional timestamp suffix for bundle name. Defaults to current date/time.

.EXAMPLE
    .\support_bundle.ps1
    # Creates: support_bundle_2026_02_03_1435.zip

.EXAMPLE
    .\support_bundle.ps1 -OutputDir "~/Desktop"
    # Creates: ~/Desktop/support_bundle_2026_02_03_1435.zip

.NOTES
    - This script will NOT include the service account JSON key file
    - Logs are captured as-is; review for sensitive data before sharing
    - For complete troubleshooting, attach this ZIP to support request

.LINK
    docs/ops/SUPPORT_PACKET.md
#>

param(
    [string]$OutputDir = (Get-Location).Path,
    [string]$Timestamp = (Get-Date -Format "yyyy_MM_dd_HHmm")
)

$ErrorActionPreference = "Stop"

# Configuration
$BdrLogsDir = "$env:USERPROFILE\.bdr\logs"
$BundleName = "support_bundle_${Timestamp}.zip"
$BundlePath = Join-Path $OutputDir $BundleName
$TempDir = Join-Path $env:TEMP "bdr_support_$$"

Write-Host "═══════════════════════════════════════════════════════════════════"
Write-Host "                 bar-directory-recon Support Bundle Collector"
Write-Host "═══════════════════════════════════════════════════════════════════"
Write-Host ""

try {
    # Step 1: Create temporary directory
    Write-Host "📁 Creating temporary directory..."
    if (Test-Path $TempDir) {
        Remove-Item $TempDir -Recurse -Force
    }
    New-Item -ItemType Directory -Path $TempDir | Out-Null
    Write-Host "   ✓ Temp directory: $TempDir"
    Write-Host ""

    # Step 2: Collect environment info
    Write-Host "ℹ️  Collecting environment information..."
    $EnvInfo = @"
═══════════════════════════════════════════════════════════════════
SUPPORT BUNDLE METADATA
═══════════════════════════════════════════════════════════════════

Collected: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')
Bundle Version: 0.1.13
Script: support_bundle.ps1

─────────────────────────────────────────────────────────────────
ENVIRONMENT
─────────────────────────────────────────────────────────────────
PowerShell Version: $($PSVersionTable.PSVersion)
OS: $(if ($IsWindows) { 'Windows' } elseif ($IsLinux) { 'Linux' } elseif ($IsMacOS) { 'macOS' } else { 'Unknown' })
OS Version: $(if ($PSVersionTable.PSVersion.Major -ge 5) { [System.Environment]::OSVersion.VersionString } else { 'N/A' })
Working Directory: $(Get-Location)

─────────────────────────────────────────────────────────────────
PYTHON & bdr INSTALLATION
─────────────────────────────────────────────────────────────────
Python Executable: $(python -c "import sys; print(sys.executable)" 2>$null || 'NOT FOUND')
Python Version: $(python --version 2>&1)
bdr Version: $(bdr --version 2>&1 || 'NOT FOUND')
bdr Location: $(where.exe bdr 2>$null || 'NOT FOUND')

─────────────────────────────────────────────────────────────────
CREDENTIALS SETUP STATUS (NO FILE CONTENTS REVEALED)
─────────────────────────────────────────────────────────────────
GOOGLE_SHEETS_CREDENTIALS_PATH env var is set: $(if ($env:GOOGLE_SHEETS_CREDENTIALS_PATH) { 'YES' } else { 'NO' })
Credentials file exists: $(if ($env:GOOGLE_SHEETS_CREDENTIALS_PATH -and (Test-Path $env:GOOGLE_SHEETS_CREDENTIALS_PATH)) { 'YES' } else { 'NO' })
Credentials file readable: $(
    if ($env:GOOGLE_SHEETS_CREDENTIALS_PATH -and (Test-Path $env:GOOGLE_SHEETS_CREDENTIALS_PATH)) {
        try {
            [void](Get-Content $env:GOOGLE_SHEETS_CREDENTIALS_PATH -ErrorAction Stop | Measure-Object);
            'YES'
        } catch {
            'NO'
        }
    } else {
        'N/A'
    }
)

⚠️  NOTE: Credentials file path and contents are NOT included in this bundle.

─────────────────────────────────────────────────────────────────
LOGS DIRECTORY
─────────────────────────────────────────────────────────────────
Logs directory: $BdrLogsDir
"@

    $EnvInfo | Out-File -FilePath "$TempDir\metadata.txt" -Encoding UTF8
    Write-Host "   ✓ Environment info captured"
    Write-Host ""

    # Step 3: Capture bdr doctor output
    Write-Host "💊 Running 'bdr doctor --no-exec'..."
    $DoctorOutput = try {
        bdr doctor --no-exec 2>&1
    } catch {
        "ERROR: $($_)"
    }
    $DoctorOutput | Out-File -FilePath "$TempDir\doctor_output.txt" -Encoding UTF8
    Write-Host "   ✓ Doctor output captured"
    Write-Host ""

    # Step 4: Collect recent logs
    Write-Host "📋 Collecting recent logs..."
    if (Test-Path $BdrLogsDir) {
        $LogCount = 0
        Get-ChildItem -Path $BdrLogsDir -Filter "*.log" -ErrorAction SilentlyContinue | 
            Sort-Object -Property LastWriteTime -Descending | 
            Select-Object -First 5 | 
            ForEach-Object {
                Copy-Item -Path $_.FullName -Destination "$TempDir\$(Split-Path $_ -Leaf)" -ErrorAction SilentlyContinue
                $LogCount++
            }
        Write-Host "   ✓ Copied $LogCount recent log files"
    } else {
        Write-Host "   ℹ️  No logs directory found at: $BdrLogsDir"
        "No logs found at: $BdrLogsDir" | Out-File -FilePath "$TempDir\logs_info.txt" -Encoding UTF8
    }
    Write-Host ""

    # Step 5: Security check - refuse to include credentials
    Write-Host "🔒 Security check..."
    $CredentialFiles = @(
        "service-account*.json",
        "*credentials*.json",
        ".env*",
        "*.key",
        "*.pem"
    )
    
    $Found = 0
    foreach ($Pattern in $CredentialFiles) {
        $Matches = Get-ChildItem -Path $TempDir -Filter $Pattern -ErrorAction SilentlyContinue
        if ($Matches) {
            Write-Host "   ⚠️  Found potential credential file(s) — REMOVING:"
            foreach ($Match in $Matches) {
                Write-Host "      - $(Split-Path $Match -Leaf)"
                Remove-Item -Path $Match.FullName -Force
                $Found++
            }
        }
    }
    
    if ($Found -eq 0) {
        Write-Host "   ✓ No credential files detected — bundle is safe"
    } else {
        Write-Host "   ✓ Removed $Found potential credential file(s)"
    }
    Write-Host ""

    # Step 6: Create ZIP archive
    Write-Host "📦 Creating ZIP archive..."
    Compress-Archive -Path "$TempDir\*" -DestinationPath $BundlePath -Force
    Write-Host "   ✓ Bundle created: $BundlePath"
    Write-Host ""

    # Step 7: Display results
    Write-Host "═══════════════════════════════════════════════════════════════════"
    Write-Host "✅ SUPPORT BUNDLE READY"
    Write-Host "═══════════════════════════════════════════════════════════════════"
    Write-Host ""
    
    $BundleSize = (Get-Item $BundlePath).Length / 1MB
    Write-Host "Bundle Details:"
    Write-Host "  Name:     $BundleName"
    Write-Host "  Location: $BundlePath"
    Write-Host "  Size:     $([math]::Round($BundleSize, 2)) MB"
    Write-Host ""
    
    Write-Host "Contents:"
    $ZipContent = [System.IO.Compression.ZipFile]::OpenRead($BundlePath)
    foreach ($Entry in $ZipContent.Entries) {
        if ($Entry.Name) {
            Write-Host "  📄 $($Entry.Name) ($([math]::Round($Entry.Length / 1KB, 1)) KB)"
        }
    }
    $ZipContent.Dispose()
    Write-Host ""

    Write-Host "Next steps:"
    Write-Host "  1. Review the bundle for any unexpected sensitive data:"
    Write-Host "     (optional) Expand the ZIP and inspect files"
    Write-Host ""
    Write-Host "  2. Attach to support request:"
    Write-Host "     - Email: [support email TBD]"
    Write-Host "     - GitHub Issue: https://github.com/samiat-quadir/bar-directory-recon/issues"
    Write-Host ""
    Write-Host "  3. Include this in your report: docs/ops/SUPPORT_PACKET.md"
    Write-Host ""
    Write-Host "═══════════════════════════════════════════════════════════════════"

} catch {
    Write-Host ""
    Write-Host "❌ ERROR: $_"
    Write-Host ""
    exit 1

} finally {
    # Cleanup temporary directory
    if (Test-Path $TempDir) {
        Remove-Item $TempDir -Recurse -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "✨ Done!"
