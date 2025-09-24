# VSCode-Insiders-Terminal-Audit.ps1
<#
Purpose: Read-only diagnostics to explain why multiple terminals/scripts auto-start in VS Code Insiders.
It **does not** modify anything. It gathers and summarizes:
 - VS Code (Insiders) User settings affecting terminals/restore
 - Workspace .vscode/{settings,tasks,launch}.json
 - PowerShell profiles that may auto-run activation scripts
 - Bash profile scripts (if present) that may spawn terminals
 - Evidence of auto-run (“runOn":"folderOpen”, preLaunchTask, startupCommands, persistent sessions, defaultProfile)

Output: .vscode_audit/VSCode_Terminal_Audit_<timestamp>.md in the current folder.
Usage (from repo folder):
  pwsh -NoProfile -ExecutionPolicy Bypass -File .\VSCode-Insiders-Terminal-Audit.ps1
#>

param()

$ErrorActionPreference = 'SilentlyContinue'

function Read-JsonFile {
  param($Path)
  if (Test-Path $Path) {
    try {
      return Get-Content $Path -Raw | ConvertFrom-Json -Depth 100
    }
    catch {
      return @{ "__parse_error__" = $_.Exception.Message; "__raw__" = (Get-Content $Path -Raw) }
    }
  }
  return $null
}

function Read-TextFile {
  param($Path)
  if (Test-Path $Path) { return Get-Content $Path -Raw }
  return $null
}

# Paths
$repoRoot = (Get-Location).Path
$wsVscode = Join-Path $repoRoot ".vscode"
$userSettings = Join-Path $env:APPDATA "Code - Insiders\User\settings.json"
$tasksJson = Join-Path $wsVscode "tasks.json"
$launchJson = Join-Path $wsVscode "launch.json"
$workspaceSettings = Join-Path $wsVscode "settings.json"

# Profiles
## Resolve PROFILE path strings (use the specific properties which are file paths)
$pwProfile = $PROFILE.CurrentUserCurrentHost
$pwAllHosts = $PROFILE.AllUsersAllHosts
$pwAllUsers = $PROFILE.AllUsersCurrentHost
$pwCurrentUserAllHosts = $PROFILE.CurrentUserAllHosts

$bashProfileCandidates = @("$HOME\.bashrc", "$HOME\.bash_profile", "$HOME\.profile")

# Read files
$userSet = Read-JsonFile $userSettings
$wsSet = Read-JsonFile $workspaceSettings
$tasks = Read-JsonFile $tasksJson
$launch = Read-JsonFile $launchJson

$pwProfileText = Read-TextFile $pwProfile
$pwAllHostsText = Read-TextFile $pwAllHosts
$pwAllUsersText = Read-TextFile $pwAllUsers
$pwAllUsersAllHostsText = Read-TextFile $pwCurrentUserAllHosts

$bashProfiles = foreach ($p in $bashProfileCandidates) {
  if (Test-Path $p) { [pscustomobject]@{ path = $p; text = Read-TextFile $p } }
}

# Heuristics
function Find-Keys {
  param($obj, [string[]]$keys)
  $hits = @()
  if ($null -eq $obj) { return $hits }
  foreach ($k in $keys) {
    if ($obj.PSObject.Properties.Name -contains $k) {
      $hits += [pscustomobject]@{ key = $k; value = ($obj.$k | ConvertTo-Json -Depth 100) }
    }
  }
  return $hits
}

$keysToCheck = @(
  'terminal.integrated.enablePersistentSessions',
  'terminal.integrated.persistentSessionReviveProcess',
  'terminal.integrated.defaultProfile.windows',
  'terminal.integrated.startupCommands',
  'python.terminal.activateEnvironment',
  'window.restoreWindows'
)

$userKeyHits = Find-Keys $userSet $keysToCheck
$wsKeyHits = Find-Keys $wsSet $keysToCheck

# Task/launch heuristics
$autoTasks = @()
if ($tasks) {
  foreach ($t in @($tasks.tasks)) {
    $o = [pscustomobject]@{
      label   = $t.label
      runOn   = $t.runOn
      type    = $t.type
      command = $t.command
    }
    $autoTasks += $o
  }
}

$preLaunchTasks = @()
if ($launch) {
  foreach ($cfg in @($launch.configurations)) {
    $preLaunchTasks += [pscustomobject]@{
      name          = $cfg.name
      preLaunchTask = $cfg.preLaunchTask
      request       = $cfg.request
      type          = $cfg.type
    }
  }
}

# Detect suspicious lines in PowerShell profiles
function Find-Suspicious {
  param($text)
  if (-not $text) { return @() }
  $lines = $text -split "`r?`n"
  $sus = $lines | Where-Object {
    $_ -match 'Activate\.ps1' -or
    $_ -match 'conda activate' -or
    $_ -match 'pipenv shell' -or
    $_ -match 'python.*-m venv'
  }
  return ($sus | ForEach-Object { $_.Trim() })
}

$pwProfileSus = Find-Suspicious $pwProfileText
$pwAllHostsSus = Find-Suspicious $pwAllHostsText
$pwAllUsersSus = Find-Suspicious $pwAllUsersText
$pwCUAllHostsSus = Find-Suspicious $pwAllUsersAllHostsText

# Output folder
$outDir = Join-Path $repoRoot ".vscode_audit"
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
$stamp = (Get-Date).ToString("yyyy-MM-dd_HH-mm-ss")
$outFile = Join-Path $outDir ("VSCode_Terminal_Audit_{0}.md" -f $stamp)

# Build markdown
$md = @()
$md += "# VS Code Insiders — Terminal Startup Audit (Read-only)"
$md += ""
$md += ('Repo: `{0}`' -f $repoRoot)
$md += "Generated: $stamp"
$md += ""
$md += "## Summary"
$md += "* User settings hits: $($userKeyHits.Count)"
$md += "* Workspace settings hits: $($wsKeyHits.Count)"
$taskCount = 0
if ($tasks -and $tasks.tasks) { $taskCount = $tasks.tasks.Count }
$launchCount = 0
if ($launch -and $launch.configurations) { $launchCount = $launch.configurations.Count }
$md += "* Tasks found: $taskCount"
$md += "* Launch configs: $launchCount"
$md += "* PowerShell profile suspicious lines (any): " + ($( @($pwProfileSus + $pwAllHostsSus + $pwAllUsersSus + $pwCUAllHostsSus).Count ))
$md += ""

Set-Content -Path $outFile -Value ($md -join "`r`n") -Encoding UTF8
Write-Host "Audit complete."
Write-Host "Report: $outFile"
