# Import Copilot Agent Helper module when VS Code is opened
# This script provides shortcuts for common tasks using Copilot Agent automation

$workspaceRoot = $PSScriptRoot | Split-Path -Parent
$copilotHelperModule = Join-Path $workspaceRoot "tools\CopilotAgentHelper.psm1"

# Log function for Copilot Agent interactions
function Write-CopilotLog {
    param (
        [string]$Message,
        [string]$Type = "INFO"
    )
    
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logDir = Join-Path $workspaceRoot "logs"
    $logFile = Join-Path $logDir "copilot_agent.log"
    
    if (!(Test-Path $logDir)) {
        New-Item -ItemType Directory -Path $logDir -Force | Out-Null
    }
    
    Add-Content -Path $logFile -Value "[$timestamp] [$Type] $Message"
}

# Import the module if it exists
if (Test-Path $copilotHelperModule) {
    Import-Module $copilotHelperModule -Force
    Write-Host "✅ Copilot Agent Helper module loaded. Use Invoke-CopilotTask to automate tasks." -ForegroundColor Green
    Write-CopilotLog "Copilot Agent Helper module loaded successfully"

    # Define functions for task shortcuts
    function fixgit { Invoke-CopilotTask -TaskName "FixGitRepository" }
    function validate { Invoke-CopilotTask -TaskName "ValidateEnvironment" }
    function scanpaths { Invoke-CopilotTask -TaskName "ScanPaths" }
    function fixpaths { Invoke-CopilotTask -TaskName "ScanPaths" -Parameters @("--fix") }
    function crosstest { Invoke-CopilotTask -TaskName "RunCrossDeviceTest" }

    Write-Host "Task shortcuts: fixgit, validate, scanpaths, fixpaths, crosstest" -ForegroundColor Cyan
}
else {
    Write-Host "⚠️ Copilot Agent Helper module not found at: $copilotHelperModule" -ForegroundColor Yellow
    Write-CopilotLog "Copilot Agent Helper module not found at: $copilotHelperModule" -Type "WARNING"
}
