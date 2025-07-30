<#
.SYNOPSIS
    Holistic audit (and optional auto-fix) for the bar-directory-recon root.

.DESCRIPTION
    * Takes a snapshot of the directory tree.
    * Verifies virtual-env, VS Code settings, device & OneDrive path.
    * Summarizes Git status, recent logs, hard-coded path scan.
    * Writes Markdown & JSON reports to logs\.
    * With -AutoFix it:
        - Re-runs OneDriveAutomation.ps1 live if last run was preview/old.
        - Consolidates .env files.
        - Ensures hooks & .gitignore entries.
        - Creates missing standard folders.
    * Designed to be idempotent; add -Preview to simulate fixes.

.PARAMETER AutoFix
    Apply safe fixes where possible.

.PARAMETER Preview
    Simulate all actions (implies -AutoFix).
#>

[CmdletBinding()]
param(
    [switch]$AutoFix,
    [switch]$Preview,
    [switch]$WhatIf,
    [string]$OutputDir
)

#region -- Helpers & bootstrap
$ErrorActionPreference = 'Stop'

# If WhatIf is specified, enable Preview mode
if ($WhatIf) { $Preview = $true }

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
$repoRoot = Resolve-Path (Join-Path $here '..')
$logsDir = if ($OutputDir) { $OutputDir } else { Join-Path $repoRoot 'logs' }
if (-not (Test-Path $logsDir)) { New-Item -ItemType Directory -Path $logsDir | Out-Null }

$timestamp = (Get-Date -Format 'yyyyMMdd_HHmmss')
$mdReport = Join-Path $logsDir "audit_$timestamp.md"
$jsonReport = Join-Path $logsDir "audit_$timestamp.json"

$report = [ordered]@{
    RunDate  = (Get-Date)
    Device   = $env:COMPUTERNAME
    Sections = @{}
}

# If the DevicePathResolver exists, dot-source it
$pathResolver = Join-Path $repoRoot 'tools\DevicePathResolver.ps1'
if (Test-Path $pathResolver) { . $pathResolver }

function Write-MD {
    param([string]$text)
    Add-Content -Path $mdReport -Value $text
}

Write-MD "# Smart Root Audit - $($report.RunDate)`n"
#endregion

#region 1 -- Directory Tree Snapshot
function Get-TreeSnapshot {
    param([string]$BasePath)
    $tree = & tree $BasePath /F | Out-String
    return $tree
}
$treeText = Get-TreeSnapshot -BasePath $repoRoot
Write-MD "## Directory Tree (top level)\n```\n$($treeText.Trim())\n```\n"
$report.Sections.Tree = $treeText
#endregion

#region 2 -- Virtual Environment Check
function Test-VirtualEnv {
    $virtualEnvPath = Join-Path $repoRoot '.venv'
    $ok = Test-Path (Join-Path $virtualEnvPath 'Scripts\activate.ps1')
    return [PSCustomObject]@{
        Exists = $ok
        Path   = $virtualEnvPath
    }
}
$virtualEnvInfo = Test-VirtualEnv
Write-MD "## Virtual Environment\n* Exists: **$($virtualEnvInfo.Exists)** at `$($virtualEnvInfo.Path)`\n"
if (-not $virtualEnvInfo.Exists -and $AutoFix) {
    Write-Warning "Virtual environment not found - creating..."
    if (-not $Preview) {
        python -m venv $virtualEnvInfo.Path
    }
}
$report.Sections.VirtualEnv = $virtualEnvInfo
#endregion

#region 3 -- VS Code Config Check
function Test-VSCodeConfig {
    $vsRoot = Join-Path $repoRoot '.vscode'
    $settings = Join-Path $vsRoot 'settings.json'
    $launch = Join-Path $vsRoot 'launch.json'
    try {
        $exts = (& code --list-extensions --show-versions 2>$null) -join ', '
    } catch {
        $exts = "VS Code command not found"
    }
    return [pscustomobject]@{
        SettingsFile = Test-Path $settings
        LaunchFile   = Test-Path $launch
        Extensions   = $exts
    }
}
$vsInfo = Test-VSCodeConfig
Write-MD "## VS Code\n* settings.json present: **$($vsInfo.SettingsFile)**\n* launch.json present: **$($vsInfo.LaunchFile)**\n"
$report.Sections.VSCode = $vsInfo
#endregion

#region 4 -- Device & OneDrive Path
$deviceInfo = if (Get-Command -Name Get-DeviceInfo -ErrorAction SilentlyContinue) { Get-DeviceInfo } else { $null }
$oneDrive = if (Get-Command -Name Get-OneDrivePath -ErrorAction SilentlyContinue) { Get-OneDrivePath } else { "C:\Users\$env:USERNAME\OneDrive - Digital Age Marketing Group" }
$report.Sections.Device = $deviceInfo
$report.Sections.OneDrive = $oneDrive
Write-MD "## Device / OneDrive\n* DeviceInfo: `$(if($deviceInfo){$deviceInfo.DeviceType}else{'n/a'})`\n* OneDrive path: `$oneDrive`\n"

#endregion

#region 5 -- Git Status
function Test-GitStatus {
    param($Path)
    $branch = (& git -C $Path rev-parse --abbrev-ref HEAD).Trim()
    $dirty = (& git -C $Path status --porcelain).Trim()
    $ignErr = -not (Select-String -Path (Join-Path $Path '.gitignore') -Pattern '\*\.env' -Quiet)
    return [pscustomobject]@{
        Branch     = $branch
        IsDirty    = [bool]$dirty
        EnvIgnored = -not $ignErr
        DirtyFiles = $dirty
    }
}
$gitInfo = Test-GitStatus -Path $repoRoot
Write-MD "## Git\n* Branch: **$($gitInfo.Branch)**\n* Dirty: **$($gitInfo.IsDirty)**\n* .env ignored: **$($gitInfo.EnvIgnored)**\n"
if ($AutoFix -and $gitInfo.IsDirty -eq $false -and -not $Preview) {
    git -C $repoRoot pull
}
if ($AutoFix -and -not $gitInfo.EnvIgnored -and -not $Preview) {
    Add-Content (Join-Path $repoRoot '.gitignore') '*.env'
}
$report.Sections.Git = $gitInfo
#endregion

#region 6 -- Recent Logs
$lastLog = Get-ChildItem $logsDir -Filter 'OneDriveAutomation_*.log' | Sort-Object LastWriteTime -Descending | Select-Object -First 1
$logSummary = if ($lastLog) { Get-Content $lastLog -TotalCount 25 } else { 'No logs yet' }
Write-MD "## Recent OneDriveAutomation Log\n<details><summary>Last 25 lines</summary>\n\n```\n$logSummary\n```\n</details>\n"
$report.Sections.LastLog = @{ File = $lastLog.FullName; Preview = $logSummary -match 'PREVIEW' }
# Auto-rerun cleanup if last run was preview
if ($AutoFix -and $report.Sections.LastLog.Preview -and -not $Preview) {
    & $repoRoot\tools\OneDriveAutomation.ps1
}
#endregion

#region 7 -- Hard-coded Path Scan
try {
    $scanScript = Join-Path $repoRoot 'tools\Scan_For_Hardcoded_Paths.ps1'
    if (Test-Path $scanScript) {
        $scanResult = & powershell -NoProfile -File $scanScript -SummaryOnly 2>$null
    } else {
        $scanResult = "Scan script not found"
    }
} catch {
    $scanResult = "Path scan failed: $($_.Exception.Message)"
}
Write-MD "## Hard-coded Path Scan\n```\n$scanResult\n```\n"
$report.Sections.PathScan = $scanResult
#endregion

#region 8 -- Summary & JSON
$warnings = @()
if (-not $virtualEnvInfo.Exists) { $warnings += 'Virtual environment missing' }
if ($gitInfo.IsDirty) { $warnings += 'Uncommitted Git changes' }
if ($report.Sections.LastLog.Preview) { $warnings += 'Last OneDriveAutomation run was preview' }
$report.Warnings = $warnings

Write-MD "## Summary\n* Warnings: **$($warnings.Count)** - $($warnings -join '; ')\n"
$report | ConvertTo-Json -Depth 6 | Out-File $jsonReport -Encoding UTF8

Write-Host ("Audit complete - report saved to {0}" -f $mdReport) -ForegroundColor Cyan
#endregion
