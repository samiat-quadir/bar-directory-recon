# Import Copilot Agent Helper module when VS Code is opened
# Put this in the correct PowerShell profile location

$workspaceRoot = $PSScriptRoot | Split-Path -Parent
$copilotHelperModule = Join-Path $workspaceRoot "tools\CopilotAgentHelper.psm1"

# Import the module if it exists
# ...existing code...

if (Test-Path $copilotHelperModule) {
    Import-Module $copilotHelperModule -Force
    Write-Host "✅ Copilot Agent Helper module loaded. Use Invoke-CopilotTask to automate tasks." -ForegroundColor Green

    # Define functions for task shortcuts
    function fixgit { Invoke-CopilotTask -TaskName "FixGitRepository" }
    function validate { Invoke-CopilotTask -TaskName "ValidateEnvironment" }
    function scanpaths { Invoke-CopilotTask -TaskName "ScanPaths" }
    function fixpaths { Invoke-CopilotTask -TaskName "ScanPaths" -Parameters @("--fix") }
    function crosstest { Invoke-CopilotTask -TaskName "RunCrossDeviceTest" }

    Write-Host "Task shortcuts: fixgit, validate, scanpaths, fixpaths, crosstest" -ForegroundColor Cyan
}
# ...existing code...
