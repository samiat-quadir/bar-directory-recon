# VS Code Copilot Agent Auto-Confirm Configuration

This document explains how to configure VS Code to automatically confirm trusted Copilot Agent commands, enabling full automation without manual approvals.

## Auto-Confirm Configuration

### Option 1: Global Settings (Recommended)

Add to your VS Code global settings file (`settings.json`):

```json
{
    "github.copilot.chat.experimental.agentCommands.enabled": true,
    "github.copilot.chat.experimental.agentCommands.autoConfirm": true,
    "github.copilot.chat.experimental.agentCommands.trustedCommands": [
        "python",
        "pip",
        "git",
        "npm",
        "node",
        "cmd",
        "powershell"
    ],
    "github.copilot.chat.experimental.agentCommands.dangerousCommandsRequireConfirmation": true,
    "github.copilot.chat.experimental.agentCommands.allowAutomation": true
}
```

### Option 2: Workspace Settings (Project-Specific)

Create/edit `.vscode/settings.json` in your project root:

```json
{
    "github.copilot.chat.experimental.agentCommands.enabled": true,
    "github.copilot.chat.experimental.agentCommands.autoConfirm": true,
    "github.copilot.chat.experimental.agentCommands.trustedCommands": [
        "python",
        "python universal_automation.py",
        "python score_leads.py",
        "git add",
        "git commit",
        "git push"
    ],
    "github.copilot.chat.experimental.agentCommands.allowAutomation": true,
    "github.copilot.chat.experimental.agentCommands.trustedDirectories": [
        "${workspaceFolder}",
        "${workspaceFolder}/universal_recon",
        "${workspaceFolder}/tools"
    ]
}
```

## Security Configuration

### Trusted Commands

Only these commands will auto-execute without confirmation:

- Basic Python script execution
- Lead generation automation
- Git version control commands
- File operations within the project

### Dangerous Commands

These will always require manual confirmation:

- System administration commands
- File deletion operations
- Network configuration changes
- Package installations outside virtual environment

## Weekly Automation Setup

### Windows Task Scheduler Configuration

1. **Create the Automation Script** (`weekly_automation.bat`):

```batch
@echo off
cd /d "C:\Code\bar-directory-recon"
call .venv\Scripts\activate.bat

rem Run multi-industry lead generation
python universal_automation.py --industry all --city "Miami" --state "FL" --max-records 100

rem Score and prioritize leads
python score_leads.py outputs/ --output priority_leads.csv --top 20

rem Git commit and push results
git add .
git commit -m "Weekly automated lead generation - %date%"
git push

echo Weekly automation completed at %date% %time%
```

2. **PowerShell Alternative** (`weekly_automation.ps1`):

```powershell
param(
    [string]$City = "Miami",
    [string]$State = "FL",
    [int]$MaxRecords = 100,
    [switch]$IncludeScoring = $true
)

Set-Location "C:\Code\bar-directory-recon"

# Activate virtual environment
& ".\.venv\Scripts\Activate.ps1"

try {
    Write-Host "Starting weekly lead generation automation..." -ForegroundColor Green

    # Run lead generation for all industries
    python universal_automation.py --industry all --city $City --state $State --max-records $MaxRecords

    if ($IncludeScoring) {
        # Score and prioritize leads
        python score_leads.py outputs/ --output priority_leads.csv --top 20
    }

    # Commit results
    git add .
    git commit -m "Weekly automated lead generation - $(Get-Date -Format 'yyyy-MM-dd')"
    git push

    Write-Host "Weekly automation completed successfully!" -ForegroundColor Green
}
catch {
    Write-Error "Automation failed: $_"
    exit 1
}
```

3. **Schedule the Task**:

```powershell
# Run as Administrator
$action = New-ScheduledTaskAction -Execute "PowerShell.exe" -Argument "-ExecutionPolicy Bypass -File C:\Code\bar-directory-recon\weekly_automation.ps1"
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 6:00AM
$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -StartWhenAvailable
$principal = New-ScheduledTaskPrincipal -UserId "$env:USERDOMAIN\$env:USERNAME" -LogonType Interactive

Register-ScheduledTask -TaskName "Universal Lead Generation" -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Description "Weekly automated lead generation and scoring"
```

## Testing Auto-Confirm

### Test Commands

1. **Safe Command Test**:

```
@copilot run python --version
```

2. **Automation Test**:

```
@copilot run python universal_automation.py --industry home_services --city Phoenix --test
```

3. **Lead Scoring Test**:

```
@copilot run python score_leads.py outputs/pool_contractors/tampa/ --top 10
```

### Expected Behavior

- ✅ **Auto-Confirm**: Trusted commands execute immediately
- ⚠️ **Manual Confirm**: Dangerous operations require approval
- 🔒 **Blocked**: Unauthorized commands are rejected

## Troubleshooting

### Common Issues

1. **Commands Still Require Confirmation**:
   - Check VS Code version (requires latest Copilot extension)
   - Verify settings are in correct location
   - Restart VS Code after configuration changes

2. **Automation Script Fails**:
   - Ensure virtual environment is properly activated
   - Check file paths are absolute and correct
   - Verify Python scripts have execution permissions

3. **Scheduled Task Not Running**:
   - Check task scheduler logs
   - Ensure user has appropriate permissions
   - Test script manually before scheduling

### Logs and Monitoring

- **Automation Logs**: `logs/cross_device_sync.log`
- **Lead Generation Logs**: Console output and CSV files in `outputs/`
- **Task Scheduler Logs**: Windows Event Viewer → Task Scheduler events

## Security Best Practices

1. **Limit Trusted Commands**: Only add commands you fully trust
2. **Use Project-Specific Settings**: Avoid global auto-confirm for all projects
3. **Regular Review**: Periodically review and update trusted command lists
4. **Monitor Logs**: Check automation logs for unexpected behavior
5. **Test in Development**: Always test automation in non-production environment first

## Support and Updates

This configuration is experimental and may change with VS Code/Copilot updates. Always review the latest documentation:

- [VS Code Copilot Documentation](https://code.visualstudio.com/docs/copilot)
- [GitHub Copilot Chat Documentation](https://docs.github.com/en/copilot/github-copilot-chat)
