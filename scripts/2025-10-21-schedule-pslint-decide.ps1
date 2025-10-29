[CmdletBinding()]
param(
  [datetime]$RunAtLocal = (Get-Date -Date '2025-10-23T09:10:00'),
  [string]$RepoPath = 'C:\Code\bar-directory-recon',
  [switch]$DryRun
)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
function Say($m){ Write-Host "==> $m" }

Set-Location $RepoPath
Say "Working in: $(Get-Location)"

# Run preview
if(Test-Path 'scripts\pslint_promotion_preview.ps1'){
  if(-not $DryRun){ 
    Say "Running preview..."
    pwsh -NoProfile -ExecutionPolicy Bypass -File 'scripts\pslint_promotion_preview.ps1' 
  }
}

# Create wrapper
if(-not (Test-Path 'artifacts\pslint')){ New-Item -ItemType Directory -Path 'artifacts\pslint' | Out-Null }
$wrap = @"
Set-StrictMode -Version Latest
`$ErrorActionPreference='Stop'
Set-Location '$RepoPath'
`$log = "artifacts\pslint\decide_$(Get-Date -Format 'yyyyMMdd-HHmmss').log"
pwsh -NoProfile -ExecutionPolicy Bypass -File 'scripts\pslint_promotion_decide.ps1' -Execute *>&1 | Tee-Object -FilePath `$log
"@
[IO.File]::WriteAllText('scripts\run-pslint-decide-once.ps1', $wrap, [Text.UTF8Encoding]::new($false))
Say "Wrapper created"

# Register task
$taskName = 'BDR-pslint-promote-2025-10-23-0910ET'
if(-not $DryRun){
  $exe = (Get-Command pwsh).Source
  $arg = "-NoProfile -ExecutionPolicy Bypass -File `"$RepoPath\scripts\run-pslint-decide-once.ps1`""
  $action = New-ScheduledTaskAction -Execute $exe -Argument $arg -WorkingDirectory $RepoPath
  $trigger = New-ScheduledTaskTrigger -Once -At $RunAtLocal
  $principal = New-ScheduledTaskPrincipal -UserId "$env:USERNAME" -RunLevel Highest
  $existing = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
  if($existing){
    Set-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal | Out-Null
    Say "Updated task: $taskName"
  } else {
    Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Principal $principal | Out-Null
    Say "Registered task: $taskName"
  }
  Say "Scheduled for: $($RunAtLocal.ToString('yyyy-MM-dd HH:mm:ss'))"
}
$status = if($DryRun){ 'preview-only' } else { 'queued' }
Write-Host "RELAY >> task=pslint_decide_schedule status=$status when_local=$($RunAtLocal.ToString('yyyy-MM-dd HH:mm'))"