# realtor_automation_scheduler.ps1
# PowerShell script for Windows Task Scheduler integration

param(
    [switch]$Install,
    [switch]$Uninstall,
    [switch]$Status,
    [string]$Mode = "once",
    [int]$MaxRecords = $null,
    [string]$Output = "",
    [string]$GoogleSheetId = "",
    [string]$PythonPath = "",
    [string]$ScriptPath = "",
    [string]$OutputPath = "outputs\realtor_leads.csv"
)

# Set working directory to script location
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $ScriptDir

# Activate virtual environment if it exists
$VenvPath = Join-Path $ScriptDir ".venv\Scripts\Activate.ps1"
if (Test-Path $VenvPath) {
    Write-Host "📦 Activating virtual environment..."
    & $VenvPath
}

# Ensure required directories exist
$OutputDir = Join-Path $ScriptDir "outputs"
$LogsDir = Join-Path $ScriptDir "logs"

if (-not (Test-Path $OutputDir)) {
    New-Item -ItemType Directory -Path $OutputDir -Force | Out-Null
}

if (-not (Test-Path $LogsDir)) {
    New-Item -ItemType Directory -Path $LogsDir -Force | Out-Null
}

# Build command arguments
$PythonArgs = @("realtor_automation.py", "--mode", $Mode)

if ($MaxRecords -gt 0) {
    $PythonArgs += "--max-records"
    $PythonArgs += $MaxRecords.ToString()
}

if ($Output -ne "") {
    $PythonArgs += "--output"
    $PythonArgs += $Output
}

if ($GoogleSheetId -ne "") {
    $PythonArgs += "--google-sheet-id"
    $PythonArgs += $GoogleSheetId
}

# Log the execution
$LogFile = Join-Path $LogsDir "scheduler.log"
$Timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

Write-Host "🤖 Starting Realtor Directory Automation..."
Write-Host "📅 Timestamp: $Timestamp"
Write-Host "⚙️ Mode: $Mode"

# Add to log
Add-Content -Path $LogFile -Value "[$Timestamp] Starting automation with mode: $Mode"

try {
    # Run the Python script
    $Result = & python $PythonArgs 2>&1

    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Automation completed successfully"
        Add-Content -Path $LogFile -Value "[$Timestamp] SUCCESS: Automation completed"
        Write-Output $Result
    }
    else {
        Write-Host "❌ Automation failed with exit code: $LASTEXITCODE"
        Add-Content -Path $LogFile -Value "[$Timestamp] ERROR: Automation failed with exit code $LASTEXITCODE"
        foreach ($line in $Result) {
            Write-Error "$line"
        }
    }
}
catch {
    Write-Host "❌ PowerShell execution error: $($_.Exception.Message)"
    Add-Content -Path $LogFile -Value "[$Timestamp] POWERSHELL ERROR: $($_.Exception.Message)"
    throw
}

    # Deactivate virtual environment
    if (Get-Command "deactivate" -ErrorAction SilentlyContinue) {
        deactivate
    }

$TaskName = "RealtorDirectoryAutomation"
$TaskDescription = "Weekly automated lead extraction from realtor directory"

function Get-PythonExecutable {
    if ($PythonPath) {
        return $PythonPath
    }

    # Try to find Python in common locations
    $possiblePaths = @(
        (Get-Command python -ErrorAction SilentlyContinue).Path,
        (Get-Command python3 -ErrorAction SilentlyContinue).Path,
        "$env:LOCALAPPDATA\Programs\Python\Python*\python.exe",
        "C:\Python*\python.exe",
        ".venv\Scripts\python.exe"
    )

    foreach ($path in $possiblePaths) {
        if ($path -and (Test-Path $path)) {
            return $path
        }
    }

    throw "Python executable not found. Please specify -PythonPath parameter."
}

function Get-ScriptPath {
    if ($ScriptPath) {
        return $ScriptPath
    }

    $currentDir = Get-Location
    $scriptFile = Join-Path $currentDir "realtor_automation.py"

    if (Test-Path $scriptFile) {
        return $scriptFile
    }

    throw "realtor_automation.py not found. Please specify -ScriptPath parameter."
}

function Install-Task {
    Write-Host "🔧 Setting up Realtor Directory Automation Task..." -ForegroundColor Cyan

    try {
        $pythonExe = Get-PythonExecutable
        $scriptPath = Get-ScriptPath

        Write-Host "Python: $pythonExe" -ForegroundColor Gray
        Write-Host "Script: $scriptPath" -ForegroundColor Gray
        Write-Host "Output: $OutputPath" -ForegroundColor Gray

        # Create the scheduled task action
        $action = New-ScheduledTaskAction -Execute $pythonExe -Argument "`"$scriptPath`" --output `"$OutputPath`" --verbose"

        # Create the trigger (every Monday at 8:00 AM)
        $trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Monday -At "8:00AM"

        # Create the principal (run as current user)
        $principal = New-ScheduledTaskPrincipal -UserId $env:USERNAME -LogonType Interactive

        # Create task settings
        $settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable

        # Register the task
        Register-ScheduledTask -TaskName $TaskName -Action $action -Trigger $trigger -Principal $principal -Settings $settings -Description $TaskDescription -Force

        Write-Host "✅ Task '$TaskName' created successfully!" -ForegroundColor Green
        Write-Host "📅 Scheduled to run every Monday at 8:00 AM" -ForegroundColor Yellow
        Write-Host "📁 Output will be saved to: $OutputPath" -ForegroundColor Yellow

        # Test the task
        Write-Host "`n🧪 Testing task configuration..." -ForegroundColor Cyan
        $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        if ($task) {
            Write-Host "Task found and properly configured." -ForegroundColor Green

            # Ask if user wants to run a test
            $response = Read-Host "Would you like to run a test execution now? (y/N)"
            if ($response -eq 'y' -or $response -eq 'Y') {
                Write-Host "Running test..." -ForegroundColor Cyan
                Start-ScheduledTask -TaskName $TaskName
                Write-Host "Test started. Check the logs directory for results." -ForegroundColor Yellow
            }
        }

    } catch {
        Write-Host "❌ Error creating task: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

function Uninstall-Task {
    Write-Host "🗑️  Removing Realtor Directory Automation Task..." -ForegroundColor Cyan

    try {
        $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        if ($task) {
            Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
            Write-Host "✅ Task '$TaskName' removed successfully!" -ForegroundColor Green
        } else {
            Write-Host "ℹ️  Task '$TaskName' not found." -ForegroundColor Yellow
        }
    } catch {
        Write-Host "❌ Error removing task: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

function Show-TaskStatus {
    Write-Host "📊 Realtor Directory Automation Task Status" -ForegroundColor Cyan
    Write-Host "=" * 50

    try {
        $task = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue
        if ($task) {
            Write-Host "✅ Task Status: $($task.State)" -ForegroundColor Green

            # Get last run info
            $taskInfo = Get-ScheduledTaskInfo -TaskName $TaskName -ErrorAction SilentlyContinue
            if ($taskInfo) {
                Write-Host "⏱️  Last Run: $($taskInfo.LastRunTime)" -ForegroundColor Gray
                Write-Host "🔄 Last Result: $($taskInfo.LastTaskResult)" -ForegroundColor Gray
            }

            # Show recent log entries
            $logFile = "logs\scheduler.log"
            if (Test-Path $logFile) {
                Write-Host "`n📋 Recent Log Entries:" -ForegroundColor Cyan
                Get-Content $logFile -Tail 5 | ForEach-Object {
                    Write-Host "  $_" -ForegroundColor Gray
                }
            }

        } else {
            Write-Host "❌ Task not found. Run with -Install to create it." -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ Error checking task status: $($_.Exception.Message)" -ForegroundColor Red
        exit 1
    }
}

function Show-Help {
    Write-Host "🏠 Realtor Directory Automation - Task Scheduler Setup" -ForegroundColor Cyan
    Write-Host "=" * 60
    Write-Host ""
    Write-Host "Usage:"
    Write-Host "  .\realtor_automation_scheduler.ps1 -Install              # Install weekly automation"
    Write-Host "  .\realtor_automation_scheduler.ps1 -Uninstall           # Remove automation"
    Write-Host "  .\realtor_automation_scheduler.ps1 -Status              # Check task status"
    Write-Host ""
    Write-Host "Optional Parameters:"
    Write-Host "  -PythonPath <path>     # Specify Python executable path"
    Write-Host "  -ScriptPath <path>     # Specify realtor_automation.py path"
    Write-Host "  -OutputPath <path>     # Specify output CSV path"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  .\realtor_automation_scheduler.ps1 -Install -OutputPath 'C:\Data\leads.csv'"
    Write-Host "  .\realtor_automation_scheduler.ps1 -Install -PythonPath '.venv\Scripts\python.exe'"
    Write-Host ""
}

# Handle task management operations first
if ($Install) {
    Install-Task
    exit 0
} elseif ($Uninstall) {
    Uninstall-Task
    exit 0
} elseif ($Status) {
    Show-TaskStatus
    exit 0
} elseif (-not $Mode) {
    Show-Help
    exit 0
}

# Continue with execution mode if no task management switches were used
# ...existing code...

Write-Host "`n📚 For more information, see README_REALTOR_AUTOMATION.md" -ForegroundColor Cyan
