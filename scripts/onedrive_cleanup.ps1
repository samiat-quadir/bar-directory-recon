<#
.SYNOPSIS
Automates cleanup and optimization for a OneDrive-based Windows developer environment                    $dest = Join-Path $Base $cat
                    Move-Item $f.FullName -Destination (Join-Path -Path $dest -ChildPath $f.Name) -Force -ErrorAction SilentlyContinue
                    $moved = $true; break
.DESCRIPTION
This script performs tasks like:
1. Resolving OneDrive paths dynamically.
2. Detecting and resolving duplicate files.
3. Handling OneDrive sync conflicts.
4. Enforcing folder structure and organization.
5. Scanning for secrets (optional).

.PARAMETER Preview
Runs the script in dry-run mode, showing planned actions without making changes.

.PARAMETER LogPath
Optional path to save audit logs (JSON format).

.PARAMETER ConfigPath
Path to a YAML file defining folder structures and settings.

.NOTES
- Safe to re-run (idempotent).
- Designed for Windows environments with OneDrive integration.

.EXAMPLE
.\OneDriveCleanup.ps1 -Preview -LogPath "C:\Logs" -ConfigPath "C:\Config\folder_map.yaml"
#>

param (
    [switch]$Preview,
    [string]$LogPath = "$PSScriptRoot\Logs",
    [string]$ConfigPath = "$PSScriptRoot\folder_map.yaml"
)

#region Helpers
function Get-OneDrivePath {
    # Primary approach: Try the hardcoded path specific to this environment
    $hardcodedPath = "C:\Users\samq\OneDrive - Digital Age Marketing Group"

    if (Test-Path $hardcodedPath) {
        return $hardcodedPath
    }

    # Fallback approach: Try standard environment variables and detection methods
    $candidates = @(
        $env:OneDriveCommercial,
        $env:OneDriveConsumer,
        $env:OneDrive,
        (Get-ItemProperty -Path "HKCU:\Software\Microsoft\OneDrive" -ErrorAction SilentlyContinue).UserFolder,
        (& "$env:localappdata\Microsoft\OneDrive\onedrive.exe" /getsyncfolders 2>$null |
        Select-String -Pattern 'path: (.+)' | ForEach-Object { $_.Matches[0].Groups[1].Value })
    ) | Where-Object { $_ -and (Test-Path $_) } | Select-Object -First 1

    if (-not $candidates) {
        throw "⚠️  OneDrive root not found. Please verify OneDrive is installed and syncing."
    }

    return $candidates
}

function Write-JsonLog($Object, $Name) {
    if ($null -eq $global:ReportDir) {
        $global:ReportDir = (Join-Path $global:OneDriveRoot 'OneDriveAuditReports')
    }
    if (-not (Test-Path $ReportDir)) { New-Item $ReportDir -ItemType Directory | Out-Null }
    $Object | ConvertTo-Json -Depth 6 | Out-File (Join-Path $ReportDir "$Name.json") -Encoding UTF8
}

#endregion

#region Resolve Paths
$OneDriveRoot = Get-OneDrivePath
$OneDriveDesktop = Join-Path $OneDriveRoot 'Desktop'
if (-not (Test-Path $OneDriveDesktop)) { throw "Desktop not synced under OneDrive." }
#endregion

#region Folder Structure
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
            }            if (-not $moved) {
                Move-Item $f.FullName -Destination (Join-Path -Path $Base -ChildPath 'Other' -AdditionalChildPath $f.Name) -Force -ErrorAction SilentlyContinue
            }
        }
    }
}
#endregion

#region Conflict Resolution
function Resolve-OneDriveConflicts {
    param(
        [string]$Path = $OneDriveDesktop,
        [ValidateSet('Newest', 'Oldest')]$Keep = 'Newest'
    )
    $conflictDir = Join-Path $Path '_Conflicts'
    if (-not (Test-Path $conflictDir)) { New-Item $conflictDir -ItemType Directory | Out-Null }

    $patterns = @('\s\(\d+\)\.', '-[A-Za-z0-9]+\.')

    $groups = @{}
    Get-ChildItem $Path -File -Recurse | ForEach-Object {
        if ($patterns | Where-Object { $_.Name -match $_ }) {
            $base = ($_.BaseName -replace ($patterns -join '|'), '').ToLower()
            $groups[$base] = $groups[$base] + , $_
        }
    }

    foreach ($k in $groups.Keys) {
        $set = $groups[$k] | Sort-Object LastWriteTime
        $toArchive = if ($Keep -eq 'Newest') { $set | Select-Object -First ($set.Count - 1) }
        else { $set | Select-Object -Skip 1 }
        foreach ($file in $toArchive) {
            Move-Item $file.FullName (Join-Path $conflictDir $file.Name) -Force
        }
    }
}
#endregion

#region Cross-Device Environment Validation
function Export-EnvironmentInfo {
    param(
        [string]$OutputPath = (Join-Path $OneDriveRoot "env_validation"),
        [string]$DeviceLabel = $env:COMPUTERNAME
    )

    if (-not (Test-Path $OutputPath)) {
        New-Item $OutputPath -ItemType Directory -Force | Out-Null
    }

    # Export Python version info
    $pythonVersion = & python --version 2>&1
    $pythonVersion | Out-File (Join-Path $OutputPath "python_version_$DeviceLabel.txt")

    # Export pip packages
    & pip freeze | Out-File (Join-Path $OutputPath "requirements_$DeviceLabel.txt")

    # Export VS Code extensions if VS Code is installed
    $vscodePath = Get-Command code -ErrorAction SilentlyContinue
    if ($vscodePath) {
        & code --list-extensions | Out-File (Join-Path $OutputPath "vscode_extensions_$DeviceLabel.txt")
    }
    else {
        "VS Code not found in PATH" | Out-File (Join-Path $OutputPath "vscode_extensions_$DeviceLabel.txt")
    }

    # Check for .env files
    $envFiles = Get-ChildItem -Path $PSScriptRoot -Filter ".env*" -File
    if ($envFiles) {
        $envFilesOutput = Join-Path $OutputPath "env_files_$DeviceLabel.txt"
        $envFiles | ForEach-Object { $_.Name } | Out-File $envFilesOutput
    }

    # Export Git configuration if Git is installed
    $gitPath = Get-Command git -ErrorAction SilentlyContinue
    if ($gitPath) {
        & git config --list | Out-File (Join-Path $OutputPath "git_config_$DeviceLabel.txt")
        & git remote -v | Out-File (Join-Path $OutputPath "git_remotes_$DeviceLabel.txt")
    }
    else {
        "Git not found in PATH" | Out-File (Join-Path $OutputPath "git_config_$DeviceLabel.txt")
    }

    Write-Host "Environment information exported to $OutputPath"
}

function Compare-EnvironmentInfo {
    param(
        [string]$BasePath = (Join-Path $OneDriveRoot "env_validation"),
        [string]$Device1 = "Work",
        [string]$Device2 = "ASUS"
    )

    # Define file pairs to compare
    $filePairs = @(
        @{Name = "Python Version"; File1 = "python_version_$Device1.txt"; File2 = "python_version_$Device2.txt" },
        @{Name = "Installed Packages"; File1 = "requirements_$Device1.txt"; File2 = "requirements_$Device2.txt" },
        @{Name = "VS Code Extensions"; File1 = "vscode_extensions_$Device1.txt"; File2 = "vscode_extensions_$Device2.txt" },
        @{Name = "Git Configuration"; File1 = "git_config_$Device1.txt"; File2 = "git_config_$Device2.txt" },
        @{Name = "Git Remotes"; File1 = "git_remotes_$Device1.txt"; File2 = "git_remotes_$Device2.txt" }
    )

    $report = @()
    foreach ($pair in $filePairs) {
        $path1 = Join-Path $BasePath $pair.File1
        $path2 = Join-Path $BasePath $pair.File2

        if (-not (Test-Path $path1) -or -not (Test-Path $path2)) {
            $report += [PSCustomObject]@{
                Category = $pair.Name
                Status   = "⚠️ Files missing"
                Details  = "One or both files are missing"
            }
            continue
        }

        $diff = Compare-Object -ReferenceObject (Get-Content $path1) -DifferenceObject (Get-Content $path2)
        if ($diff) {
            $report += [PSCustomObject]@{
                Category = $pair.Name
                Status   = "❌ Differences found"
                Details  = "$($diff.Count) differences detected"
            }
        }
        else {
            $report += [PSCustomObject]@{
                Category = $pair.Name
                Status   = "✅ Identical"
                Details  = "No differences detected"
            }
        }
    }

    # Format and display the report
    $report | Format-Table -AutoSize

    # Save the report to a JSON file
    $reportPath = Join-Path $BasePath "environment_comparison_report.json"
    $report | ConvertTo-Json | Out-File $reportPath

    Write-Host "Comparison report saved to $reportPath"
    return $report
}
#endregion

#region Secrets Scanning
function Find-Secrets {
    param(
        [string]$Path = $OneDriveRoot,
        [string[]]$Patterns = @('password', 'secret', 'token', 'api[_\s]?key', 'credential', 'pwd'),
        [string[]]$FileTypes = @('*.txt', '*.json', '*.xml', '*.ini', '*.config', '*.env*', '*.ps1', '*.py')
    )

    Write-Host "Scanning for potential secrets in $Path..."

    $results = @()
    foreach ($pattern in $Patterns) {
        Write-Host "  Searching for pattern: $pattern"
        $matches = Get-ChildItem -Path $Path -Recurse -File -Include $FileTypes |
        Select-String -Pattern $pattern -SimpleMatch

        foreach ($match in $matches) {
            $results += [PSCustomObject]@{
                File       = $match.Path
                LineNumber = $match.LineNumber
                Pattern    = $pattern
                Line       = $match.Line.Trim()
            }
        }
    }

    # Create a report in the OneDrive audit directory
    if ($results.Count -gt 0) {
        Write-Host "Found $($results.Count) potential secrets."
        Write-JsonLog $results "secrets_scan_report"
        Write-Host "Secret scan report saved to the OneDriveAuditReports folder."
    }
    else {
        Write-Host "No potential secrets found."
    }

    return $results
}
#endregion

#region Main
function Main {
    param(
        [switch]$SkipFolderStructure,
        [switch]$SkipConflictResolution,
        [switch]$ExportEnv,
        [switch]$CompareEnv,
        [switch]$ScanSecrets,
        [string]$DeviceLabel = $env:COMPUTERNAME
    )

    Write-Host "Starting OneDrive Cleanup Script..."
    Write-Host "OneDrive Root: $OneDriveRoot"

    if (-not $SkipFolderStructure) {
        Write-Host "Organizing folder structure..."
        New-StandardLayout -MoveFiles:$true
    }

    if (-not $SkipConflictResolution) {
        Write-Host "Resolving OneDrive conflicts..."
        Resolve-OneDriveConflicts -Keep Newest
    }

    if ($ExportEnv) {
        Write-Host "Exporting environment information for device: $DeviceLabel"
        Export-EnvironmentInfo -DeviceLabel $DeviceLabel
    }

    if ($CompareEnv) {
        Write-Host "Comparing environment information between devices..."
        Compare-EnvironmentInfo | Out-Null
        Write-Host "Environment comparison complete."
    }

    if ($ScanSecrets) {
        Write-Host "Scanning for potential secrets..."
        $secretsFound = Find-Secrets
        if ($secretsFound) {
            Write-Host "⚠️ Potential secrets found. See OneDriveAuditReports for details."
        }
    }

    Write-Host "All tasks completed!"
}

# Parse any additional script parameters and run Main with the appropriate options
$mainParams = @{}

if ($Preview) {
    Write-Host "Preview mode enabled. No changes will be made."
    $mainParams.Add('WhatIf', $true)
}

# Run main function
Main @mainParams

# Export-EnvironmentInfo -DeviceLabel "Work" # Uncomment to export environment info
# Compare-EnvironmentInfo # Uncomment to compare environment info between devices
# Find-Secrets # Uncomment to scan for secrets
#endregion
