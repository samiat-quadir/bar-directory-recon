#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Alienware Device Bootstrap Script for bar-directory-recon Project

.DESCRIPTION
    This script brings an Alienware device into exact parity with the ASUS "golden image" environment.
    It sets up the complete development environment from scratch, including:
    - Repository cloning at v2.0 tag
    - Python 3.13 virtual environment setup
    - All required dependencies installation
    - Device-specific configuration
    - Environment validation

.PARAMETER WorkspaceRoot
    Root directory where the project will be cloned (default: C:\Code)

.PARAMETER SkipValidation
    Skip the final validation step

.EXAMPLE
    .\bootstrap_alienware.ps1
    .\bootstrap_alienware.ps1 -WorkspaceRoot "D:\Development"
#>

param(
    [string]$WorkspaceRoot = "C:\Code",
    [switch]$SkipValidation = $false
)

# Script configuration
$ErrorActionPreference = "Stop"
$ProgressPreference = "Continue"
$ProjectName = "bar-directory-recon"
$RepositoryUrl = "https://github.com/samiat-quadir/bar-directory-recon.git"
$RequiredPythonVersion = "3.13"
$TagVersion = "v2.0"

# Colors for output
$Colors = @{
    Success = "Green"
    Warning = "Yellow"
    Error   = "Red"
    Info    = "Cyan"
    Header  = "Magenta"
}

function Write-StatusMessage {
    param(
        [string]$Message,
        [string]$Type = "Info"
    )

    $prefix = switch ($Type) {
        "Success" { "" }
        "Warning" { " " }
        "Error" { "" }
        "Info" { "" }
        "Header" { "" }
        default { " " }
    }

    Write-Host "$prefix $Message" -ForegroundColor $Colors[$Type]
}

function Test-Prerequisites {
    Write-StatusMessage "Checking system prerequisites..." "Header"

    $issues = @()

    # Check if running as Administrator
    $currentUser = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentUser)
    $isAdmin = $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

    if (-not $isAdmin) {
        $issues += "Script must be run as Administrator for proper system setup"
    }

    # Check Git installation
    try {
        $gitVersion = git --version
        Write-StatusMessage "Git found: $gitVersion" "Success"
    }
    catch {
        $issues += "Git is not installed or not in PATH"
    }

    # Check Python 3.13 installation
    try {
        $pythonVersion = py --version 2>&1
        if ($pythonVersion -match "Python 3\.13") {
            Write-StatusMessage "Python found: $pythonVersion" "Success"
        }
        else {
            $issues += "Python 3.13 is required, found: $pythonVersion"
        }
    }
    catch {
        $issues += "Python 3.13 is not installed or not in PATH"
    }

    # Check available disk space (minimum 5GB)
    $drive = Get-WmiObject -Class Win32_LogicalDisk | Where-Object { $_.DeviceID -eq ($WorkspaceRoot.Substring(0, 2)) }
    $freeSpaceGB = [math]::Round($drive.FreeSpace / 1GB, 2)

    if ($freeSpaceGB -lt 5) {
        $issues += "Insufficient disk space: $freeSpaceGB GB available, 5GB required"
    }
    else {
        Write-StatusMessage "Disk space: $freeSpaceGB GB available" "Success"
    }

    if ($issues.Count -gt 0) {
        Write-StatusMessage "Prerequisites check failed!" "Error"
        foreach ($issue in $issues) {
            Write-StatusMessage $issue "Error"
        }
        throw "Prerequisites not met"
    }

    Write-StatusMessage "All prerequisites satisfied" "Success"
}

function Initialize-Workspace {
    Write-StatusMessage "Setting up workspace directory..." "Header"

    $projectPath = Join-Path $WorkspaceRoot $ProjectName

    # Create workspace root if it doesn't exist
    if (-not (Test-Path $WorkspaceRoot)) {
        Write-StatusMessage "Creating workspace root: $WorkspaceRoot" "Info"
        New-Item -Path $WorkspaceRoot -ItemType Directory -Force | Out-Null
    }

    # Remove existing project directory if it exists
    if (Test-Path $projectPath) {
        Write-StatusMessage "Removing existing project directory..." "Warning"
        Remove-Item -Path $projectPath -Recurse -Force
    }

    # Clone repository at specific tag
    Write-StatusMessage "Cloning repository at tag $TagVersion..." "Info"
    Set-Location $WorkspaceRoot

    git clone --branch $TagVersion --single-branch $RepositoryUrl $ProjectName

    if (-not (Test-Path $projectPath)) {
        throw "Failed to clone repository"
    }

    Set-Location $projectPath
    Write-StatusMessage "Repository cloned successfully to: $projectPath" "Success"

    return $projectPath
}

function Setup-PythonEnvironment {
    param([string]$ProjectPath)

    Write-StatusMessage "Setting up Python virtual environment..." "Header"

    $venvPath = Join-Path $ProjectPath ".venv"

    # Create virtual environment
    Write-StatusMessage "Creating virtual environment..." "Info"
    py -m venv $venvPath

    if (-not (Test-Path $venvPath)) {
        throw "Failed to create virtual environment"
    }

    # Activate virtual environment
    $activateScript = Join-Path $venvPath "Scripts\Activate.ps1"
    Write-StatusMessage "Activating virtual environment..." "Info"
    & $activateScript

    # Upgrade pip
    Write-StatusMessage "Upgrading pip..." "Info"
    py -m pip install --upgrade pip

    Write-StatusMessage "Python virtual environment created successfully" "Success"
}

function Install-Dependencies {
    param([string]$ProjectPath)

    Write-StatusMessage "Installing Python dependencies..." "Header"

    Set-Location $ProjectPath

    # Install core requirements
    $coreReqFile = "requirements-core.txt"
    if (Test-Path $coreReqFile) {
        Write-StatusMessage "Installing core requirements..." "Info"
        py -m pip install -r $coreReqFile
    }
    else {
        Write-StatusMessage "Core requirements file not found: $coreReqFile" "Warning"
    }

    # Install optional requirements
    $optionalReqFile = "requirements-optional.txt"
    if (Test-Path $optionalReqFile) {
        Write-StatusMessage "Installing optional requirements..." "Info"
        py -m pip install -r $optionalReqFile
    }
    else {
        Write-StatusMessage "Optional requirements file not found: $optionalReqFile" "Warning"
    }

    # Install main requirements if core/optional don't exist
    $mainReqFile = "requirements.txt"
    if (Test-Path $mainReqFile -and -not (Test-Path $coreReqFile)) {
        Write-StatusMessage "Installing main requirements..." "Info"
        py -m pip install -r $mainReqFile
    }

    Write-StatusMessage "Dependencies installed successfully" "Success"
}

function Setup-Configuration {
    param([string]$ProjectPath)

    Write-StatusMessage "Setting up configuration files..." "Header"

    Set-Location $ProjectPath

    # Create .env file from template
    $envTemplate = ".env.template"
    $envFile = ".env"

    if (Test-Path $envTemplate) {
        if (-not (Test-Path $envFile)) {
            Copy-Item $envTemplate $envFile
            Write-StatusMessage "Created .env file from template" "Success"
            Write-StatusMessage "Please edit .env file to add your secrets and configuration" "Warning"
        }
        else {
            Write-StatusMessage ".env file already exists" "Info"
        }
    }
    else {
        Write-StatusMessage "No .env.template found, creating basic .env..." "Info"
        @"
# Alienware Device Configuration
# Generated by bootstrap_alienware.ps1

# Device identification
DEVICE_NAME=ALIENWARE
DEVICE_TYPE=development

# Project paths
PROJECT_ROOT=$ProjectPath
WORKSPACE_ROOT=$WorkspaceRoot

# Python configuration
PYTHON_VERSION=3.13

# Add your secrets and API keys below:
# OPENAI_API_KEY=your_openai_key_here
# GOOGLE_SHEETS_CREDENTIALS_PATH=path_to_credentials
# Other configuration as needed...
"@ | Out-File -FilePath $envFile -Encoding UTF8
    }

    # Create device-specific profile
    $deviceName = $env:COMPUTERNAME
    $userName = $env:USERNAME
    $userHome = $env:USERPROFILE
    $pythonPath = (Get-Command py).Source
    $oneDrivePath = Join-Path $userHome "OneDrive"

    # Try to find OneDrive path variations
    $oneDriveVariations = @(
        "$userHome\OneDrive",
        "$userHome\OneDrive - Digital Age Marketing Group",
        "$userHome\OneDrive - Personal"
    )

    foreach ($path in $oneDriveVariations) {
        if (Test-Path $path) {
            $oneDrivePath = $path
            break
        }
    }

    $deviceProfile = @{
        device        = $deviceName
        username      = $userName
        user_home     = $userHome.Replace('\', '/')
        timestamp     = (Get-Date).ToString("yyyy-MM-ddTHH:mm:ss.ffffffK")
        python_path   = $pythonPath.Replace('\', '/')
        onedrive_path = $oneDrivePath.Replace('\', '/')
        project_root  = $ProjectPath.Replace('\', '/')
        virtual_env   = (Join-Path $ProjectPath ".venv").Replace('\', '/')
    }

    $configDir = Join-Path $ProjectPath "config"
    if (-not (Test-Path $configDir)) {
        New-Item -Path $configDir -ItemType Directory -Force | Out-Null
    }

    $deviceProfilePath = Join-Path $configDir "device_profile-$deviceName.json"
    $deviceProfile | ConvertTo-Json -Depth 10 | Out-File -FilePath $deviceProfilePath -Encoding UTF8

    Write-StatusMessage "Created device profile: $deviceProfilePath" "Success"

    # Create required directories
    $requiredDirs = @(
        "logs",
        "logs\automation",
        "logs\device_logs",
        "output",
        "input",
        "automation",
        "tools",
        "scripts"
    )

    foreach ($dir in $requiredDirs) {
        $dirPath = Join-Path $ProjectPath $dir
        if (-not (Test-Path $dirPath)) {
            New-Item -Path $dirPath -ItemType Directory -Force | Out-Null
            Write-StatusMessage "Created directory: $dir" "Success"
        }
    }
}

function Install-ExternalTools {
    Write-StatusMessage "Installing external tools..." "Header"

    # Install pre-commit
    try {
        py -m pip install pre-commit
        Write-StatusMessage "Pre-commit installed successfully" "Success"
    }
    catch {
        Write-StatusMessage "Failed to install pre-commit" "Warning"
    }

    # Check for Chrome installation
    $chromePaths = @(
        "${env:ProgramFiles}\Google\Chrome\Application\chrome.exe",
        "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe"
    )

    $chromeFound = $false
    foreach ($path in $chromePaths) {
        if (Test-Path $path) {
            $chromeFound = $true
            Write-StatusMessage "Chrome found at: $path" "Success"
            break
        }
    }

    if (-not $chromeFound) {
        Write-StatusMessage "Chrome not found. Please install Google Chrome for web automation features." "Warning"
    }
}

function Invoke-EnvironmentValidation {
    param([string]$ProjectPath)

    if ($SkipValidation) {
        Write-StatusMessage "Skipping validation as requested" "Warning"
        return
    }

    Write-StatusMessage "Running environment validation..." "Header"

    Set-Location $ProjectPath

    # Run validation script
    $validationScript = "validate_env_state.py"
    $alienwareValidationScript = "validate_alienware_bootstrap.py"

    if (Test-Path $validationScript) {
        try {
            $validationOutput = py $validationScript 2>&1

            # Also run Alienware-specific validation if available
            $alienwareValidationOutput = ""
            if (Test-Path $alienwareValidationScript) {
                $alienwareValidationOutput = py $alienwareValidationScript 2>&1
            }

            # Create validation report
            $reportPath = "alienware_validation_report.md"
            $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

            @"
# Alienware Device Bootstrap Validation Report

**Generated**: $timestamp
**Device**: $env:COMPUTERNAME
**User**: $env:USERNAME
**Bootstrap Script**: bootstrap_alienware.ps1

## Standard Environment Validation

``````
$validationOutput
``````

## Alienware-Specific Validation

``````
$alienwareValidationOutput
``````

## Bootstrap Summary

-  Repository cloned at tag $TagVersion
-  Python $RequiredPythonVersion virtual environment created
-  Dependencies installed from requirements files
-  Device-specific configuration created
-  Required directories created
-  External tools installed
-  Environment validation completed
-  Alienware-specific validation completed

## Next Steps

1. Review and update the `.env` file with your specific configuration
2. Test the automation scripts to ensure everything works correctly
3. Run the full test suite: `python -m pytest -v`
4. Verify cross-device compatibility

---
*Generated by Alienware Bootstrap Script v1.0*
"@ | Out-File -FilePath $reportPath -Encoding UTF8

            Write-StatusMessage "Validation report created: $reportPath" "Success"

            # Check if validation passed
            if ($LASTEXITCODE -eq 0) {
                Write-StatusMessage "Environment validation PASSED" "Success"
            }
            else {
                Write-StatusMessage "Environment validation found issues - check the report" "Warning"
            }
        }
        catch {
            Write-StatusMessage "Validation script failed: $_" "Error"
        }
    }
    else {
        Write-StatusMessage "Validation script not found: $validationScript" "Warning"

        # Create basic validation report
        $reportPath = "alienware_validation_report.md"
        @"
# Alienware Device Bootstrap Validation Report

**Generated**: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
**Device**: $env:COMPUTERNAME
**Status**:  Validation script not found

## Bootstrap Summary

-  Repository cloned at tag $TagVersion
-  Python $RequiredPythonVersion virtual environment created
-  Dependencies installed
-  Configuration files created
-  Environment validation script not available

## Manual Verification Required

Please manually verify:
1. All Python packages are installed correctly
2. Configuration files are properly set up
3. All required directories exist
4. External tools are available

Run `py -c "import sys; print(sys.version)"` to verify Python installation.
"@ | Out-File -FilePath $reportPath -Encoding UTF8

        Write-StatusMessage "Basic validation report created: $reportPath" "Success"
    }
}

function Main {
    try {
        Write-StatusMessage "Starting Alienware Device Bootstrap..." "Header"
        Write-StatusMessage "Target workspace: $WorkspaceRoot" "Info"
        Write-StatusMessage "Repository: $RepositoryUrl at $TagVersion" "Info"

        # Step 1: Check prerequisites
        Test-Prerequisites

        # Step 2: Initialize workspace
        $projectPath = Initialize-Workspace

        # Step 3: Setup Python environment
        Setup-PythonEnvironment -ProjectPath $projectPath

        # Step 4: Install dependencies
        Install-Dependencies -ProjectPath $projectPath

        # Step 5: Setup configuration
        Setup-Configuration -ProjectPath $projectPath

        # Step 6: Install external tools
        Install-ExternalTools

        # Step 7: Run validation
        Invoke-EnvironmentValidation -ProjectPath $projectPath

        Write-StatusMessage "Alienware device bootstrap completed successfully!" "Success"
        Write-StatusMessage "Project location: $projectPath" "Info"
        Write-StatusMessage "Next steps:" "Info"
        Write-StatusMessage "1. Review and update .env file with your secrets" "Info"
        Write-StatusMessage "2. Test the automation scripts" "Info"
        Write-StatusMessage "3. Run 'py -m pytest -v' to verify installation" "Info"

        return $true
    }
    catch {
        Write-StatusMessage "Bootstrap failed: $_" "Error"
        Write-StatusMessage "Check the error message above and retry" "Error"
        return $false
    }
}

# Execute main function
$success = Main
exit $(if ($success) { 0 } else { 1 })

