# VirtualEnvHelper.ps1
# PowerShell script to help with virtual environment management

# Function to check if we're currently in a virtual environment
function Test-VirtualEnvironment {
    if ($env:VIRTUAL_ENV) {
        Write-Host "Currently in virtual environment: $env:VIRTUAL_ENV" -ForegroundColor Green
        return $true
    }
    else {
        Write-Host "Not currently in a virtual environment" -ForegroundColor Yellow
        return $false
    }
}

# Function to activate the virtual environment
function Enter-VirtualEnvironment {
    param (
        [string]$VenvPath = ".venv"
    )

    $activateScript = Join-Path (Resolve-Path $VenvPath) "Scripts\activate.ps1"

    if (Test-Path $activateScript) {
        Write-Host "Activating virtual environment at: $VenvPath" -ForegroundColor Green
        & $activateScript
    }
    else {
        Write-Host "Virtual environment activation script not found at: $activateScript" -ForegroundColor Red
        Write-Host "Creating PS1 activation script..." -ForegroundColor Yellow

        # Create the PowerShell activation script
        $content = @"
# This file must be dot sourced from PoSh; you cannot run it directly
`$script:THIS_PATH = `$myinvocation.mycommand.path
`$script:BASE_DIR = Split-Path (Resolve-Path "`$THIS_PATH/..") -Parent

function global:deactivate([switch]`$NonDestructive) {
    if (Test-Path variable:_OLD_VIRTUAL_PATH) {
        `$env:PATH = `$_OLD_VIRTUAL_PATH
        Remove-Variable "_OLD_VIRTUAL_PATH" -Scope global
    }

    if (Test-Path variable:_OLD_VIRTUAL_PYTHONHOME) {
        `$env:PYTHONHOME = `$_OLD_VIRTUAL_PYTHONHOME
        Remove-Variable "_OLD_VIRTUAL_PYTHONHOME" -Scope global
    }

    if (Test-Path variable:_OLD_VIRTUAL_PROMPT) {
        `$env:PROMPT = `$_OLD_VIRTUAL_PROMPT
        Remove-Variable "_OLD_VIRTUAL_PROMPT" -Scope global
    }

    if (`$env:VIRTUAL_ENV) {
        Remove-Item env:VIRTUAL_ENV
    }

    if (!`$NonDestructive) {
        # Self destruct!
        Remove-Item function:deactivate
    }
}

deactivate -nondestructive

`$env:VIRTUAL_ENV = "`$BASE_DIR"
`$env:_OLD_VIRTUAL_PATH = `$env:PATH
`$env:PATH = "`$env:VIRTUAL_ENV\Scripts;" + `$env:PATH

# Set the prompt to show that we're in a virtual environment
function global:prompt {
    Write-Host "(venv) " -nonewline -ForegroundColor Green
    `$_OLD_VIRTUAL_PROMPT
}
`$env:_OLD_VIRTUAL_PROMPT = `$function:prompt

if (Test-Path env:PYTHONHOME) {
    `$env:_OLD_VIRTUAL_PYTHONHOME = `$env:PYTHONHOME
    Remove-Item env:PYTHONHOME
}

# SIG # Begin signature block
# SIG # End signature block
"@

        $activateDir = Split-Path $activateScript
        if (-not (Test-Path $activateDir)) {
            New-Item -ItemType Directory -Path $activateDir -Force | Out-Null
        }

        $content | Out-File -FilePath $activateScript -Encoding utf8
        Write-Host "Created PowerShell activation script at: $activateScript" -ForegroundColor Green
        Write-Host "To activate the environment, run: . $activateScript" -ForegroundColor Cyan
    }
}

# Function to create/update the virtual environment
function Update-VirtualEnvironment {
    param (
        [string]$PythonPath = "python",
        [string]$VenvPath = ".venv",
        [switch]$ForceRecreate
    )

    if ($ForceRecreate -and (Test-Path $VenvPath)) {
        Write-Host "Removing existing virtual environment at: $VenvPath" -ForegroundColor Yellow
        Remove-Item -Path $VenvPath -Recurse -Force
    }

    if (-not (Test-Path $VenvPath)) {
        Write-Host "Creating new virtual environment at: $VenvPath" -ForegroundColor Green
        & $PythonPath -m venv $VenvPath
    }
    else {
        Write-Host "Virtual environment already exists at: $VenvPath" -ForegroundColor Cyan
    }

    # Create activate.bat if it doesn't exist
    $activateBat = Join-Path $VenvPath "Scripts\activate.bat"
    if (-not (Test-Path $activateBat)) {
        Write-Host "Creating activate.bat script..." -ForegroundColor Yellow
        $content = @"
@echo off
REM This script activates the virtual environment
set "VIRTUAL_ENV=$((Resolve-Path $VenvPath).Path)"
if defined _OLD_VIRTUAL_PROMPT (
    set "PROMPT=%_OLD_VIRTUAL_PROMPT%"
) else (
    if not defined PROMPT (
        set "PROMPT=`$P`$G"
    )
    set "_OLD_VIRTUAL_PROMPT=%PROMPT%"
    set "PROMPT=(venv) %PROMPT%"
)
set "_OLD_VIRTUAL_PYTHONHOME=%PYTHONHOME%"
set PYTHONHOME=
if defined _OLD_VIRTUAL_PATH (
    set "PATH=%_OLD_VIRTUAL_PATH%"
) else (
    set "_OLD_VIRTUAL_PATH=%PATH%"
)
set "PATH=%VIRTUAL_ENV%\Scripts;%PATH%"
echo Virtual environment activated successfully
"@
        $content | Out-File -FilePath $activateBat -Encoding ASCII
        Write-Host "Created activate.bat at: $activateBat" -ForegroundColor Green
    }

    # Activate the environment and install requirements
    Enter-VirtualEnvironment -VenvPath $VenvPath

    if (Test-Path "requirements.txt") {
        Write-Host "Installing packages from requirements.txt..." -ForegroundColor Green
        & pip install -r requirements.txt
    }
    else {
        Write-Host "No requirements.txt file found" -ForegroundColor Yellow
    }

    if (Test-Path "pyproject.toml") {
        Write-Host "Installing project in development mode..." -ForegroundColor Green
        & pip install -e .
    }
}

# Check if we're in a virtual environment when this script is sourced
$isInVenv = Test-VirtualEnvironment

# Export the functions if we're in a module context
if ($MyInvocation.Line -match 'Import-Module') {
    Export-ModuleMember -Function Test-VirtualEnvironment, Enter-VirtualEnvironment, Update-VirtualEnvironment
}
