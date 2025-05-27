# CopilotAgentHelper.psm1
# Helper functions for Copilot Agent automation

# Function to perform common tasks without requiring user confirmation
function Invoke-CopilotTask {
    [CmdletBinding()]
    param (
        [Parameter(Mandatory = $true)]
        [string]$TaskName,

        [Parameter(Mandatory = $false)]
        [string[]]$Parameters = @()
    )

    $workspaceRoot = $PSScriptRoot | Split-Path -Parent
    $logFile = Join-Path $workspaceRoot "logs\copilot_agent_automation.log"

    # Ensure logs directory exists
    $logsDir = Join-Path $workspaceRoot "logs"
    if (!(Test-Path $logsDir)) {
        New-Item -ItemType Directory -Path $logsDir -Force | Out-Null
    }

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logMessage = "$timestamp - Executing task: $TaskName"
    Add-Content -Path $logFile -Value $logMessage

    try {
        switch ($TaskName) {
            "FixGitRepository" {
                Write-Host "Attempting to fix Git repository..." -ForegroundColor Yellow

                # Run Git repair commands
                git fsck --full
                git gc --aggressive

                # Check if fix worked
                $gitStatus = git rev-parse --verify HEAD 2>&1
                if ($LASTEXITCODE -eq 0) {
                    Write-Host "Git repository fixed successfully!" -ForegroundColor Green
                    Add-Content -Path $logFile -Value "$timestamp - SUCCESS: Git repository fixed"
                }
                else {
                    Write-Host "Git repository could not be fixed automatically." -ForegroundColor Red
                    Add-Content -Path $logFile -Value "$timestamp - ERROR: Git repository fix failed: $gitStatus"
                }
            }

            "ValidateEnvironment" {
                Write-Host "Validating Python environment..." -ForegroundColor Yellow

                # Activate virtual environment if not already active
                if (-not $env:VIRTUAL_ENV) {
                    $activateScript = Join-Path $workspaceRoot ".venv\Scripts\Activate.ps1"
                    if (Test-Path $activateScript) {
                        & $activateScript
                    }
                }

                # Run environment validation
                python (Join-Path $workspaceRoot "test_cross_device_env.py")

                Add-Content -Path $logFile -Value "$timestamp - INFO: Environment validation completed"
            }

            "ScanPaths" {
                Write-Host "Scanning for hardcoded paths..." -ForegroundColor Yellow
                $scanPathsBat = Join-Path $workspaceRoot "ScanPaths.bat"

                if ($Parameters -contains "--fix") {
                    & $scanPathsBat --fix
                    Add-Content -Path $logFile -Value "$timestamp - INFO: Ran ScanPaths with --fix option"
                }
                else {
                    & $scanPathsBat
                    Add-Content -Path $logFile -Value "$timestamp - INFO: Ran ScanPaths without options"
                }
            }

            "RunCrossDeviceTest" {
                Write-Host "Running cross-device path test..." -ForegroundColor Yellow
                $testScript = Join-Path $workspaceRoot "Test-CrossDevicePaths.ps1"

                & powershell -ExecutionPolicy Bypass -NoProfile -File $testScript
                Add-Content -Path $logFile -Value "$timestamp - INFO: Ran cross-device path test"
            }

            default {
                Write-Host "Unknown task: $TaskName" -ForegroundColor Red
                Add-Content -Path $logFile -Value "$timestamp - ERROR: Unknown task requested: $TaskName"
            }
        }
    }
    catch {
        $errorMessage = $_.Exception.Message
        Write-Host "Error executing task $TaskName`: $errorMessage" -ForegroundColor Red
        Add-Content -Path $logFile -Value "$timestamp - ERROR: Task $TaskName failed: $errorMessage"
    }
}

# Export functions
Export-ModuleMember -Function Invoke-CopilotTask
