#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Launch Suite for Bar Directory Recon - PowerShell Version

.DESCRIPTION
    This script provides a complete launch suite for the bar directory reconnaissance
    automation system. It handles environment activation, configuration loading,
    and starts all required services.

.PARAMETER Mode
    Launch mode: 'full' (default), 'dashboard', 'demo', 'env-check'

.PARAMETER Sites
    Comma-separated list of sites to process

.EXAMPLE
    .\launch_suite.ps1
    .\launch_suite.ps1 -Mode dashboard
    .\launch_suite.ps1 -Mode demo -Sites "example1.com,example2.com"

.NOTES
    Author: Bar Directory Recon Team
    Version: 2.0
    Last Modified: July 25, 2025
#>

param(
    [ValidateSet('full', 'dashboard', 'demo', 'env-check', 'async-demo')]
    [string]$Mode = 'full',

    [string]$Sites = '',

    [switch]$Help,

    [switch]$Verbose
)

# Enable verbose output if requested
if ($Verbose) {
    $VerbosePreference = 'Continue'
}

# Display help and exit
if ($Help) {
    Get-Help $MyInvocation.MyCommand.Path -Full
    exit 0
}

# Get script directory and project root
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = $ScriptDir

Write-Host "🚀 Bar Directory Recon - Launch Suite (PowerShell)" -ForegroundColor Cyan
Write-Host "=" * 60 -ForegroundColor Gray
Write-Host "📁 Project Root: $ProjectRoot" -ForegroundColor Yellow
Write-Host "🎯 Launch Mode: $Mode" -ForegroundColor Green

# Step 1: Activate Virtual Environment
Write-Host "`n🔧 Step 1: Activating Python Virtual Environment..." -ForegroundColor Blue

$VenvPath = Join-Path $ProjectRoot ".venv"
$VenvActivate = Join-Path $VenvPath "Scripts\Activate.ps1"

if (Test-Path $VenvActivate) {
    Write-Verbose "Found virtual environment at: $VenvPath"
    & $VenvActivate

    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Virtual environment activated successfully" -ForegroundColor Green
    }
    else {
        Write-Host "❌ Failed to activate virtual environment" -ForegroundColor Red
        exit 1
    }
}
else {
    Write-Host "⚠️ Virtual environment not found at: $VenvPath" -ForegroundColor Yellow
    Write-Host "   Creating virtual environment..." -ForegroundColor Yellow

    # Create virtual environment
    python -m venv $VenvPath
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Virtual environment created" -ForegroundColor Green
        & $VenvActivate
    }
    else {
        Write-Host "❌ Failed to create virtual environment" -ForegroundColor Red
        exit 1
    }
}

# Verify Python is available
$PythonVersion = python --version 2>&1
Write-Host "🐍 Python Version: $PythonVersion" -ForegroundColor Cyan

# Step 2: Load Environment Configuration
Write-Host "`n🔧 Step 2: Loading Environment Configuration..." -ForegroundColor Blue

$EnvLoaderPath = Join-Path $ProjectRoot "env_loader.py"
if (Test-Path $EnvLoaderPath) {
    Write-Verbose "Running environment loader: $EnvLoaderPath"
    python $EnvLoaderPath

    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Environment configuration loaded successfully" -ForegroundColor Green
    }
    else {
        Write-Host "⚠️ Environment loader completed with warnings" -ForegroundColor Yellow
    }
}
else {
    Write-Host "⚠️ Environment loader not found, using system environment" -ForegroundColor Yellow
}

# Step 3: Execute based on mode
Write-Host "`n🎯 Step 3: Executing Launch Mode: $Mode" -ForegroundColor Blue

switch ($Mode) {
    'full' {
        Write-Host "🚀 Starting Full Launch Suite..." -ForegroundColor Green

        # Start async pipeline demo
        Write-Host "`n📊 Starting Async Pipeline Demo..." -ForegroundColor Cyan
        $AsyncDemoPath = Join-Path $ProjectRoot "async_pipeline_demo.py"
        if (Test-Path $AsyncDemoPath) {
            if ($Sites) {
                $SiteList = $Sites -split ','
                python $AsyncDemoPath --sites $SiteList
            }
            else {
                python $AsyncDemoPath --demo-mode
            }
        }
        else {
            Write-Host "⚠️ Async pipeline demo not found" -ForegroundColor Yellow
        }

        # Start dashboard server
        Write-Host "`n🖥️ Starting Dashboard Server..." -ForegroundColor Cyan
        $DashboardPath = Join-Path $ProjectRoot "automation\dashboard.py"
        if (Test-Path $DashboardPath) {
            Start-Process -NoNewWindow python -ArgumentList $DashboardPath
            Write-Host "✅ Dashboard server started" -ForegroundColor Green
        }
        else {
            Write-Host "⚠️ Dashboard server not found" -ForegroundColor Yellow
        }
    }

    'dashboard' {
        Write-Host "🖥️ Starting Dashboard Only..." -ForegroundColor Green

        $DashboardPath = Join-Path $ProjectRoot "automation\dashboard.py"
        if (Test-Path $DashboardPath) {
            python $DashboardPath
        }
        else {
            Write-Host "❌ Dashboard not found at: $DashboardPath" -ForegroundColor Red
            exit 1
        }
    }

    'demo' {
        Write-Host "🎬 Starting Demo Mode..." -ForegroundColor Green

        $DemoPath = Join-Path $ProjectRoot "automation_demo.py"
        if (Test-Path $DemoPath) {
            python $DemoPath
        }
        else {
            Write-Host "❌ Demo script not found at: $DemoPath" -ForegroundColor Red
            exit 1
        }
    }

    'async-demo' {
        Write-Host "⚡ Starting Async Pipeline Demo..." -ForegroundColor Green

        $AsyncDemoPath = Join-Path $ProjectRoot "async_pipeline_demo.py"
        if (Test-Path $AsyncDemoPath) {
            if ($Sites) {
                $SiteList = $Sites -split ','
                python $AsyncDemoPath --sites $SiteList --sync-vs-async
            }
            else {
                python $AsyncDemoPath --sync-vs-async
            }
        }
        else {
            Write-Host "❌ Async demo not found at: $AsyncDemoPath" -ForegroundColor Red
            exit 1
        }
    }

    'env-check' {
        Write-Host "🔍 Environment Check Mode..." -ForegroundColor Green

        # Check Python environment
        Write-Host "`n🐍 Python Environment:" -ForegroundColor Cyan
        python -c "import sys; print(f'Python: {sys.version}'); print(f'Executable: {sys.executable}')"

        # Check virtual environment
        if ($env:VIRTUAL_ENV) {
            Write-Host "✅ Virtual Environment: $env:VIRTUAL_ENV" -ForegroundColor Green
        }
        else {
            Write-Host "⚠️ No virtual environment detected" -ForegroundColor Yellow
        }

        # Check key modules
        Write-Host "`n📦 Module Check:" -ForegroundColor Cyan
        $Modules = @('requests', 'selenium', 'pandas', 'pydantic', 'yaml')
        foreach ($Module in $Modules) {
            python -c "import $Module; print('✅ $Module: Available')" 2>$null
            if ($LASTEXITCODE -ne 0) {
                Write-Host "❌ $Module: Not available" -ForegroundColor Red
            }
        }

        # Check project structure
        Write-Host "`n📁 Project Structure:" -ForegroundColor Cyan
        $RequiredDirs = @('automation', 'tools', 'scripts', 'config', 'logs')
        foreach ($Dir in $RequiredDirs) {
            $DirPath = Join-Path $ProjectRoot $Dir
            if (Test-Path $DirPath) {
                Write-Host "✅ $Dir/: Present" -ForegroundColor Green
            }
            else {
                Write-Host "❌ $Dir/: Missing" -ForegroundColor Red
            }
        }
    }
}

# Step 4: Launch Summary
Write-Host "`n📊 Launch Summary:" -ForegroundColor Blue
Write-Host "  Mode: $Mode" -ForegroundColor White
Write-Host "  Project Root: $ProjectRoot" -ForegroundColor White
if ($Sites) {
    Write-Host "  Sites: $Sites" -ForegroundColor White
}
Write-Host "  Status: Launch completed" -ForegroundColor Green

Write-Host "`n🎉 Launch Suite execution completed!" -ForegroundColor Green
Write-Host "💡 Use 'launch_suite.ps1 -Help' for more options" -ForegroundColor Cyan
