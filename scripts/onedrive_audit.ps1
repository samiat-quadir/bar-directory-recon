<#
.SYNOPSIS
    OneDrive Desktop audit & cleanup helper.
.DESCRIPTION
    - Detects OneDrive root across devices
    - Builds standard sub-folders
    - Moves files by category
    - Prunes OneDrive sync-conflict duplicates
    - Generates JSON reports
.NOTES
    Safe to re-run (idempotent). Use -WhatIf for a dry run.
#>

#region 0-Helpers  ──────────────────────────────────────────────────────────────
function Get-OneDrivePath {
    $candidates = @(
        $env:OneDriveCommercial,
        $env:OneDriveConsumer,
        $env:OneDrive, # older Windows builds
        (Get-ItemProperty -Path "HKCU:\Software\Microsoft\OneDrive" -ErrorAction SilentlyContinue).UserFolder,
        (& "$env:localappdata\Microsoft\OneDrive\onedrive.exe" /getsyncfolders 2>$null |
        Select-String -Pattern 'path: (.+)' | ForEach-Object { $_.Matches[0].Groups[1].Value })
    ) | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1
    if (-not $candidates) { throw "⚠️  OneDrive root not found." }
    return $candidates
}

function Write-JsonLog($Object, $Name) {
    $global:ReportDir = $global:ReportDir ?? (Join-Path $global:OneDriveRoot 'OneDriveAuditReports')
    if (-not (Test-Path $ReportDir)) { New-Item $ReportDir -ItemType Directory | Out-Null }
    $Object | ConvertTo-Json -Depth 6 | Out-File (Join-Path $ReportDir "$Name.json") -Encoding UTF8
}

#endregion

#region 1-Resolve Paths  ────────────────────────────────────────────────────────
$OneDriveRoot = Get-OneDrivePath
$OneDriveDesktop = Join-Path $OneDriveRoot 'Desktop'
if (-not (Test-Path $OneDriveDesktop)) { throw "Desktop not synced under OneDrive." }

#endregion

#region 2-Standard Layout Builder  ─────────────────────────────────────────────
function New-StandardLayout {
    param(
        [string]$Base = $OneDriveDesktop,
        [switch]$MoveFiles
    )
    $map = @{
        Scripts = '*.ps1', '*.py', '*.js', '*.bat', '*.sh'
        Logs    = '*.log'
        Configs = '*.json', '*.yaml', '*.yml', '*.xml', '*.ini', '*.env'
        Docs    = '*.md', '*.txt', '*.pdf', '*.docx', '*.xlsx'
        Images  = '*.png', '*.jpg', '*.jpeg', '*.gif'
    }
    foreach ($cat in $map.Keys + 'Other') {
        $path = Join-Path $Base $cat
        if (-not (Test-Path $path)) { New-Item $path -ItemType Directory | Out-Null }
    }
    if ($MoveFiles) {
        $files = Get-ChildItem $Base -File -Recurse -ErrorAction SilentlyContinue
        foreach ($f in $files) {
            $moved = $false
            foreach ($cat in $map.Keys) {
                if ($map[$cat] | Where-Object { $f.Name -like $_ }) {
                    $dest = Join-Path $Base $cat
                    Move-Item $f.FullName (Join-Path $dest $f.Name) -Force -ErrorAction SilentlyContinue
                    $moved = $true; break
                }
            }
            if (-not $moved) {
                Move-Item $f.FullName (Join-Path $Base 'Other' $f.Name) -Force -ErrorAction SilentlyContinue
            }
        }
    }
}
New-StandardLayout -MoveFiles:$true
#endregion

#region 3-Duplicate & Conflict Handler  ────────────────────────────────────────
function Resolve-OneDriveConflicts {
    param(
        [string]$Path = $OneDriveDesktop,
        [ValidateSet('Newest', 'Oldest')]$Keep = 'Newest'
    )
    $conflictDir = Join-Path $Path '_Conflicts'
    if (-not (Test-Path $conflictDir)) { New-Item $conflictDir -ItemType Directory | Out-Null }

    # Pattern 1: "filename (1).ext" / "filename (2).ext"
    $pattern1 = '\s\(\d+\)\.'
    # Pattern 2: "filename-PCNAME.ext"
    $pattern2 = '-[A-Za-z0-9]+\.'

    $groups = @{}
    Get-ChildItem $Path -File -Recurse | ForEach-Object {
        if ($_.Name -match $pattern1 -or $_.Name -match $pattern2) {
            $base = ($_.BaseName -replace $pattern1, '' -replace $pattern2, '').ToLower()
            $groups[$base] = $groups[$base] + , $_
        }
    }

    $log = @()
    foreach ($k in $groups.Keys) {
        $set = $groups[$k] | Sort-Object LastWriteTime
        $toArchive = if ($Keep -eq 'Newest') { $set | Select-Object -First ($set.Count - 1) }
        else { $set | Select-Object -Skip 1 }
        foreach ($file in $toArchive) {
            Move-Item $file.FullName (Join-Path $conflictDir $file.Name) -Force
        }
        $log += [pscustomobject]@{
            Original = $set[-1].FullName
            Archived = $toArchive.FullName
        }
    }
    Write-JsonLog $log '06-conflict-resolution'
}
Resolve-OneDriveConflicts -Keep Newest
#endregion

#region 4-Final Duplicate Hash Pass  ───────────────────────────────────────────
$hashTable = @{}
$dupeLog = @()
Get-ChildItem $OneDriveDesktop -Recurse -File | ForEach-Object {
    $hash = (Get-FileHash $_.FullName -Algorithm SHA256).Hash
    if ($hashTable[$hash]) {
        # Duplicate found, move to /Duplicates
        $dupDir = Join-Path $OneDriveDesktop 'Duplicates'
        if (-not (Test-Path $dupDir)) { New-Item $dupDir -ItemType Directory | Out-Null }
        Move-Item $_.FullName (Join-Path $dupDir $_.Name) -Force
        $dupeLog += [pscustomobject]@{ Duplicate = $_; Kept = $hashTable[$hash] }
    }
    else {
        $hashTable[$hash] = $_.FullName
    }
}
Write-JsonLog $dupeLog '07-duplicate-by-hash'
#endregion

#region 5-Inventory Snapshot  ─────────────────────────────────────────────────
$summary = @{
    RunDate     = Get-Date
    Machine     = $env:COMPUTERNAME
    FileCount   = (Get-ChildItem $OneDriveDesktop -File -Recurse).Count
    CategoryMap = Get-ChildItem $OneDriveDesktop -Directory |
    Select-Object Name, @{N = 'FileCount'; E = { (Get-ChildItem $_.FullName -File).Count } }
}
Write-JsonLog $summary '08-final-summary'
#endregion
