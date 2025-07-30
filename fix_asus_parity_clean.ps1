#!/usr/bin/env powershell
#Requires -Version 5.1

<#
.SYNOPSIS
    Fix ASUS system parity issues before re-running parity checks.

.DESCRIPTION
    This script implements the complete fix sequence for ASUS system parity:
    1. Reset git repository to clean state
    2. Fix requirements files
    3. Install correct packages with winget
    4. Clean up old audit files
    5. Set up Python virtual environment
    6. Install dependencies
    7. Run system parity implementation

.PARAMETER WhatIf
    Show what would be done without actually executing the changes.

.PARAMETER SkipGitReset
    Skip the git reset steps (use if you want to preserve local changes).

.PARAMETER SkipWinget
    Skip winget package installations.

.EXAMPLE
    .\fix_asus_parity.ps1 -WhatIf
    Shows what would be done without making changes.

.EXAMPLE
    .\fix_asus_parity.ps1
    Executes the complete parity fix sequence.
#>

[CmdletBinding(SupportsShouldProcess)]
param(
    [Parameter()]
    [switch]$WhatIf,

    [Parameter()]
    [switch]$SkipGitReset,

    [Parameter()]
    [switch]$SkipWinget
)

# Set error action preference
$ErrorActionPreference = "Stop"

# Colors for output
$Red = "`e[31m"
$Green = "`e[32m"
$Yellow = "`e[33m"
$Blue = "`e[34m"
$Reset = "`e[0m"

function Write-ColorOutput {
    param([string]$Message, [string]$Color = $Reset)
    Write-Host "$Color$Message$Reset"
}

function Write-Step {
    param([string]$Message)
    Write-ColorOutput "==> $Message" $Blue
}

function Write-Success {
    param([string]$Message)
    Write-ColorOutput "✓ $Message" $Green
}

function Write-Warning {
    param([string]$Message)
    Write-ColorOutput "⚠ $Message" $Yellow
}

function Write-Error {
    param([string]$Message)
    Write-ColorOutput "✗ $Message" $Red
}

# Ensure we're in the correct directory
$ProjectRoot = "C:\Code\bar-directory-recon"
if (-not (Test-Path $ProjectRoot)) {
    Write-Error "Project directory not found: $ProjectRoot"
    exit 1
}

Set-Location $ProjectRoot
Write-Step "Working in directory: $(Get-Location)"

try {
    # Step 1: Git repository cleanup and reset (unless skipped)
    if (-not $SkipGitReset) {
        Write-Step "Step 1: Cleaning and resetting Git repository"

        if ($WhatIf) {
            Write-ColorOutput "Would execute: git stash" $Yellow
            Write-ColorOutput "Would execute: git reset --hard origin/main" $Yellow
            Write-ColorOutput "Would execute: git clean -fd tools/" $Yellow
            Write-ColorOutput "Would execute: git fetch origin v2.0" $Yellow
            Write-ColorOutput "Would execute: git checkout v2.0" $Yellow
        } else {
            # Stash any local changes
            Write-ColorOutput "Stashing local changes..."
            git stash push -m "ASUS parity fix - auto stash $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" 2>$null

            # Reset to clean state
            Write-ColorOutput "Resetting to origin/main..."
            git reset --hard origin/main

            # Clean untracked files in tools directory (be careful!)
            Write-ColorOutput "Cleaning untracked files in tools directory..."
            git clean -fd tools/

            # Fetch and checkout v2.0 branch
            Write-ColorOutput "Fetching and checking out v2.0 branch..."
            git fetch origin v2.0
            git checkout v2.0

            Write-Success "Git repository reset complete"
        }
    } else {
        Write-Warning "Skipping Git reset as requested"
    }

    # Step 2: Fix requirements files (already done by previous edits, but verify)
    Write-Step "Step 2: Verifying requirements files are correct"

    $coreRequirements = Get-Content "requirements-core.txt" -Raw
    $optionalRequirements = Get-Content "requirements-optional.txt" -Raw

    if ($coreRequirements -like "*watchdog>=6.0.0*") {
        Write-Success "requirements-core.txt: watchdog version is correct"
    } else {
        Write-Error "requirements-core.txt: watchdog version needs fixing"
    }

    if ($optionalRequirements -notmatch "smtplib-ssl") {
        Write-Success "requirements-optional.txt: bogus SMTP dependency removed"
    } else {
        Write-Error "requirements-optional.txt: still contains smtplib-ssl dependency"
    }

    # Step 3: Install correct packages with winget (unless skipped)
    if (-not $SkipWinget) {
        Write-Step "Step 3: Installing packages with winget"

        $wingetPackages = @(
            @{Id = "Git.Git"; Name = "Git" },
            @{Id = "pre-commit.pre-commit"; Name = "pre-commit" },
            @{Id = "Google.Chrome"; Name = "Google Chrome" }
        )

        foreach ($package in $wingetPackages) {
            if ($WhatIf) {
                Write-ColorOutput "Would install: $($package.Name) (ID: $($package.Id))" $Yellow
            } else {
                Write-ColorOutput "Installing $($package.Name)..."
                try {
                    winget install --id=$($package.Id) -e --accept-package-agreements --silent
                    Write-Success "$($package.Name) installed successfully"
                } catch {
                    Write-Warning "Failed to install $($package.Name): $($_.Exception.Message)"
                }
            }
        }
    } else {
        Write-Warning "Skipping winget installations as requested"
    }

    # Step 4: Clean up old firewall exports
    Write-Step "Step 4: Cleaning up old audit files"

    $auditPath = "C:\Temp\bar-recon-audit"
    if (Test-Path $auditPath) {
        if ($WhatIf) {
            Write-ColorOutput "Would remove: $auditPath\*.wfw" $Yellow
        } else {
            Remove-Item "$auditPath\*.wfw" -ErrorAction SilentlyContinue
            Write-Success "Old firewall exports cleaned up"
        }
    } else {
        Write-ColorOutput "Audit directory doesn't exist yet: $auditPath"
    }

    # Step 5: Set up Python virtual environment
    Write-Step "Step 5: Setting up Python virtual environment"

    if ($WhatIf) {
        Write-ColorOutput "Would create virtual environment with: py -3.13 -m venv .venv" $Yellow
        Write-ColorOutput "Would activate virtual environment" $Yellow
        Write-ColorOutput "Would upgrade pip" $Yellow
        Write-ColorOutput "Would install requirements-core.txt" $Yellow
        Write-ColorOutput "Would install requirements-optional.txt" $Yellow
    } else {
        # Remove existing .venv if it exists
        if (Test-Path ".venv") {
            Write-ColorOutput "Removing existing virtual environment..."
            Remove-Item ".venv" -Recurse -Force
        }

        # Create new virtual environment
        Write-ColorOutput "Creating Python virtual environment..."
        py -3.13 -m venv .venv

        # Activate virtual environment
        Write-ColorOutput "Activating virtual environment..."
        & ".venv\Scripts\Activate.ps1"

        # Upgrade pip
        Write-ColorOutput "Upgrading pip..."
        python -m pip install --upgrade pip

        # Install core requirements
        Write-ColorOutput "Installing core requirements..."
        pip install -r requirements-core.txt

        # Install optional requirements
        Write-ColorOutput "Installing optional requirements..."
        pip install -r requirements-optional.txt

        Write-Success "Python environment setup complete"
    }

    # Step 6: Check for required parity scripts
    Write-Step "Step 6: Checking for required parity scripts"

    $requiredScripts = @(
        "tools\implement_system_parity.ps1",
        "tools\run_nightly_checks.ps1"
    )

    $missingScripts = @()
    foreach ($script in $requiredScripts) {
        if (-not (Test-Path $script)) {
            $missingScripts += $script
            Write-Warning "Missing required script: $script"
        } else {
            Write-Success "Found required script: $script"
        }
    }

    if ($missingScripts.Count -gt 0) {
        Write-Error "Missing required scripts. Please ensure these exist before running parity:"
        $missingScripts | ForEach-Object { Write-Error "  - $_" }
        Write-ColorOutput "You may need to copy them from your repository or regenerate them." $Yellow
    }

    # Step 7: Prepare to run parity (show commands)
    Write-Step "Step 7: Ready to run system parity"

    Write-ColorOutput ""
    Write-ColorOutput "ASUS Parity Fix Complete!" $Green
    Write-ColorOutput ""
    Write-ColorOutput "Next steps to run system parity:"
    Write-ColorOutput ""
    Write-ColorOutput "1. Ensure you're in an elevated PowerShell session"
    Write-ColorOutput "2. Navigate to the tools directory:"
    Write-ColorOutput "   cd C:\Code\bar-directory-recon\tools"
    Write-ColorOutput ""
    Write-ColorOutput "3. Run parity check in WhatIf mode first:"
    Write-ColorOutput "   powershell -NoProfile -File .\implement_system_parity.ps1 -WhatIf"
    Write-ColorOutput ""
    Write-ColorOutput "4. If the output looks good, run the actual parity:"
    Write-ColorOutput "   powershell -NoProfile -File .\implement_system_parity.ps1"
    Write-ColorOutput ""

    if (-not $WhatIf -and (Test-Path "tools\implement_system_parity.ps1")) {
        $runParity = Read-Host "Do you want to run the system parity check now? (y/N)"
        if ($runParity -eq 'y' -or $runParity -eq 'Y') {
            Write-Step "Running system parity implementation..."
            Set-Location "tools"
            powershell -NoProfile -File .\implement_system_parity.ps1 -WhatIf

            $confirmRun = Read-Host "Run the actual parity implementation? (y/N)"
            if ($confirmRun -eq 'y' -or $confirmRun -eq 'Y') {
                powershell -NoProfile -File .\implement_system_parity.ps1
            }
        }
    }

} catch {
    Write-Error "An error occurred during the parity fix process:"
    Write-Error $_.Exception.Message
    Write-Error "Stack Trace: $($_.ScriptStackTrace)"
    exit 1
}

Write-Success "ASUS parity fix process completed successfully!"
