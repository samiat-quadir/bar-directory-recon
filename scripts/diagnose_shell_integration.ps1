<#
Diagnose why VS Code still prompts for shell integration.
Outputs environment details and checks for injected variables.
#>
Write-Host "[ShellDiag] Terminal Process Info" -ForegroundColor Cyan
Write-Host "COMSPEC=$env:COMSPEC"
Write-Host "WT_SESSION=$env:WT_SESSION"
Write-Host "TERM_PROGRAM=$env:TERM_PROGRAM"
Write-Host "PROMPT=$env:PROMPT"
Write-Host "VSCODE_SHELL_INTEGRATION=$env:VSCODE_SHELL_INTEGRATION"
Write-Host "VSCODE_CWD=$env:VSCODE_CWD"

Write-Host "`n[ShellDiag] PROMPT Snippet Preview" -ForegroundColor Cyan
$promptLine = (Get-Item function:prompt -ErrorAction SilentlyContinue)
if ($promptLine) { $promptLine | Format-List }
else { Write-Host "No custom prompt function." }

Write-Host "`n[ShellDiag] Shell & Profile Details" -ForegroundColor Cyan
$shell = if ($PSVersionTable) { "PowerShell $($PSVersionTable.PSVersion)" } else { "cmd/other" }
Write-Host "Shell Detected: $shell"
if ($shell -like "PowerShell*") {
    Write-Host "PowerShell Profiles: ($PROFILE is per-host):" -ForegroundColor Yellow
    $profilePaths = @(
        $PROFILE.AllUsersAllHosts,
        $PROFILE.AllUsersCurrentHost,
        $PROFILE.CurrentUserAllHosts,
        $PROFILE.CurrentUserCurrentHost
    ) | Select-Object -Unique
    foreach ($p in $profilePaths) {
        $exists = Test-Path $p
        Write-Host " - $p : $(if($exists){'Present'}else{'Missing'})"
        if ($exists) {
            $content = Get-Content $p -Raw
            if ($content -match 'VSCODE_SHELL_INTEGRATION') {
                Write-Host "   * Contains VSCODE_SHELL_INTEGRATION reference" -ForegroundColor Yellow
            }
            if ($content -match 'function\s+prompt') {
                Write-Host "   * Overrides prompt function" -ForegroundColor Yellow
            }
        }
    }
}

Write-Host "`n[ShellDiag] Checking for injection script markers" -ForegroundColor Cyan
$historyPath = Join-Path $env:USERPROFILE "AppData\Roaming\Code\User\History" # heuristic
if (Test-Path $historyPath) {
    Write-Host "History dir exists: $historyPath"
}
else { Write-Host "History dir missing (may be okay)" }

Write-Host "`n[ShellDiag] Suggested Remediations" -ForegroundColor Cyan
Write-Host "1. Ensure settings: terminal.integrated.shellIntegration.enabled = true (already set)."
Write-Host "2. Try disabling and re-enabling: set enabled false, reload, then true, reload."
Write-Host "3. Confirm you're not launching an external (detached) terminal (should be integrated)."
Write-Host "4. For cmd.exe: verify no PROMPT overrides removing injected sequence."
Write-Host "5. For PowerShell: ensure profile does not clear $env:VSCODE_SHELL_INTEGRATION."
Write-Host "6. Check Extensions: a shell customization extension might reset prompt."
Write-Host "7. Open a brand new integrated terminal AFTER settings changes (old terminals don't retrofit)."
Write-Host "8. Temporarily move your PowerShell profile(s) aside to test: ren profile.ps1 profile.ps1.bak then reopen."
Write-Host "9. Run: echo $env:TERM_PROGRAM ; echo $env:VSCODE_SHELL_INTEGRATION inside new terminal to confirm injection."
Write-Host "10. If still blank, update VS Code to latest Stable or Insiders (older builds had injection issues)."
