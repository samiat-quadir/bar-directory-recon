# Scan_For_Hardcoded_Paths.ps1
# This script scans project files for hardcoded paths that might cause cross-device compatibility issues

<#
.SYNOPSIS
    Scans for hardcoded paths in project files.

.DESCRIPTION
    This utility script scans PowerShell, Python, batch, and text files for
    hardcoded paths that might cause cross-device compatibility issues.
    It identifies potential issues like desktop-specific paths and suggests
    replacements with device-agnostic paths.

.PARAMETER Fix
    If specified, attempts to automatically fix detected issues by replacing
    hardcoded paths with device-agnostic alternatives.

.EXAMPLE
    .\Scan_For_Hardcoded_Paths.ps1
    # Scans project files and reports issues

.EXAMPLE
    .\Scan_For_Hardcoded_Paths.ps1 -Fix
    # Scans project files and attempts to fix detected issues
#>

param (
    [switch]$Fix
)

# Import device path resolver
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
$pathResolverScript = Join-Path -Path $projectRoot -ChildPath "tools\DevicePathResolver.ps1"

if (-not (Test-Path $pathResolverScript)) {
    Write-Host "ERROR: DevicePathResolver.ps1 not found at expected location." -ForegroundColor Red
    Write-Host "Expected at: $pathResolverScript" -ForegroundColor Red
    exit 1
}

. $pathResolverScript

# File patterns to scan
$filePatterns = @(
    "*.ps1",
    "*.py",
    "*.bat",
    "*.cmd",
    "*.md",
    "*.txt"
)

# Paths to exclude from scanning
$excludePaths = @(
    ".git",
    ".venv",
    "archive",
    "temp_backup",
    "temp_broken_code"
)

# Patterns to look for
$pathPatterns = @(
    "C:\\Users\\samq\\OneDrive",
    "C:\\Users\\samqu\\OneDrive",
    "C:\\Users\\samq\\OneDrive - Digital Age Marketing Group",
    "C:\\Users\\samqu\\OneDrive - Digital Age Marketing Group",
    "$(Get-OneDrivePath)",
    "$(Get-OneDrivePath)",
    "$(Get-OneDrivePath)",
    "$(Get-OneDrivePath)",
    "samq\\OneDrive",
    "samqu\\OneDrive"
)

# Add VS Code settings and virtual environment paths to check
$venvPatterns = @(
    '.venv\\Scripts\\python.exe',
    '\\.venv\\\\Scripts\\\\python.exe',
    '/.venv/Scripts/python.exe',
    "C:\\Users\\samq\\.venv",
    "C:\\Users\\samqu\\.venv",
    "C:/Users/samq/.venv",
    "C:/Users/samqu/.venv"
)

$pathPatterns += $venvPatterns

function Get-ScriptFilesToProcess {
    $allFiles = @()

    foreach ($pattern in $filePatterns) {
        $files = Get-ChildItem -Path $projectRoot -Filter $pattern -Recurse |
        Where-Object {
            $include = $true
            foreach ($excludePath in $excludePaths) {
                if ($_.FullName -like "*\$excludePath\*") {
                    $include = $false
                    break
                }
            }
            $include
        }
        $allFiles += $files
    }

    return $allFiles
}

function Write-ColorHighlightedLine {
    param (
        [string]$Line,
        [string]$Highlight,
        [string]$Color = "Red"
    )

    $parts = $Line -split [regex]::Escape($Highlight)

    for ($i = 0; $i -lt $parts.Length; $i++) {
        Write-Host $parts[$i] -NoNewline
        if ($i -lt $parts.Length - 1) {
            Write-Host $Highlight -NoNewline -ForegroundColor $Color
        }
    }
    Write-Host ""
}

function Search-HardcodedPaths {
    param (
        [switch]$Fix
    )

    $files = Get-ScriptFilesToProcess
    $totalIssues = 0
    $filesWithIssues = @()

    Write-Host "Scanning for hardcoded paths in $($files.Count) files..." -ForegroundColor Cyan
    Write-Host ""

    foreach ($file in $files) {
        $fileContent = Get-Content -Path $file.FullName -Raw
        $fileIssues = 0
        $issueLines = @()

        foreach ($pattern in $pathPatterns) {
            if ($fileContent -match [regex]::Escape($pattern)) {
                $fileIssues++
                $totalIssues++

                # Get the line numbers with the issue
                $lineNum = 1
                foreach ($line in (Get-Content -Path $file.FullName)) {
                    if ($line -match [regex]::Escape($pattern)) {
                        $issueLines += @{
                            LineNumber = $lineNum
                            Line       = $line
                            Pattern    = $pattern
                        }
                    }
                    $lineNum++
                }
            }
        }

        if ($fileIssues -gt 0) {
            $filesWithIssues += $file.FullName

            Write-Host "File: $($file.FullName)" -ForegroundColor Yellow
            Write-Host "Issues found: $fileIssues" -ForegroundColor Yellow
            Write-Host ""

            foreach ($issueLine in $issueLines) {
                Write-Host "Line $($issueLine.LineNumber): " -NoNewline
                Write-ColorHighlightedLine -Line $issueLine.Line -Highlight $issueLine.Pattern

                # Suggest a fix
                $extension = $file.Extension.ToLower()

                if ($Fix) {
                    if ($extension -eq ".ps1") {
                        # For PowerShell files
                        $dynamicPath = "`$OneDrivePath = Get-OneDrivePath"
                        $relativePath = ConvertTo-ProjectRelativePath -Path $issueLine.Pattern -ProjectRoot $projectRoot
                        $suggestedFix = "`$projectRoot = Get-ProjectRootPath; Join-Path -Path `$projectRoot -ChildPath `"$relativePath`""
                    }
                    elseif ($extension -eq ".py") {
                        # For Python files
                        $dynamicPath = "onedrive_path = $(Get-OneDrivePath)"
                        $relativePath = ConvertTo-ProjectRelativePath -Path $issueLine.Pattern -ProjectRoot $projectRoot
                        $suggestedFix = "project_root = get_project_root_path(); os.path.join(project_root, '$relativePath')"
                    }
                    elseif ($extension -eq ".bat" -or $extension -eq ".cmd") {
                        # For batch files
                        $dynamicPath = "for /f \"tokens=*\" %%i in ('powershell -NoProfile -ExecutionPolicy Bypass -Command \"& { . ' % ~dp0tools\\DevicePathResolver.ps1'; Get-OneDrivePath }\"') do set ONEDRIVE_PATH=%%i"
                        $relativePath = ConvertTo-ProjectRelativePath -Path $issueLine.Pattern -ProjectRoot $projectRoot
                        $suggestedFix = "%ONEDRIVE_PATH%\\$relativePath"
                    }
                    else {
                        # For other files
                        Write-Host "  Could not automatically fix this file type." -ForegroundColor Yellow
                    }

                    if ($suggestedFix) {
                        try {
                            $updatedContent = $fileContent.Replace($issueLine.Pattern, $suggestedFix)
                            Set-Content -Path $file.FullName -Value $updatedContent
                            Write-Host "  Fixed: Replaced with $suggestedFix" -ForegroundColor Green
                        }
                        catch {
                            Write-Host "  Failed to fix: $_" -ForegroundColor Red
                        }
                    }
                }
                else {
                    Write-Host "  Consider using device-agnostic paths instead of hardcoded paths." -ForegroundColor Cyan
                    Write-Host "  Use Get-OneDrivePath / $(Get-OneDrivePath) to get the correct path for the current device." -ForegroundColor Cyan
                }

                Write-Host ""
            }

            Write-Host ("=" * 80) -ForegroundColor DarkGray
            Write-Host ""
        }
    }

    Write-Host "Scan completed." -ForegroundColor Cyan
    Write-Host "Total issues found: $totalIssues in $($filesWithIssues.Count) files." -ForegroundColor $(if ($totalIssues -gt 0) { "Yellow" } else { "Green" })

    if ($totalIssues -gt 0 -and -not $Fix) {
        Write-Host "Run with -Fix parameter to attempt automatic fixes." -ForegroundColor Cyan
    }
    elseif ($Fix -and $totalIssues -gt 0) {
        Write-Host "Attempted to fix all issues. Please review the changes carefully." -ForegroundColor Yellow
    }
}

function ConvertTo-ProjectRelativePath {
    param (
        [string]$Path,
        [string]$ProjectRoot
    )

    # Try to convert OneDrive paths
    $onedrivePath = Get-OneDrivePath
    if ($Path -like "$onedrivePath*") {
        $relativePath = $Path.Substring($onedrivePath.Length).TrimStart('\', '/')
        return $relativePath
    }

    # Try to match username paths
    $knownUsernames = @("samq", "samqu")
    foreach ($username in $knownUsernames) {
        if ($Path -match "C:\\Users\\$username\\OneDrive") {
            $match = [regex]::Match($Path, "C:\\Users\\$username\\OneDrive.*?\\(.*)")
            if ($match.Success) {
                return $match.Groups[1].Value
            }
        }
        if ($Path -match "C:/Users/$username/OneDrive") {
            $match = [regex]::Match($Path, "C:/Users/$username/OneDrive.*?/(.*)")
            if ($match.Success) {
                return $match.Groups[1].Value
            }
        }
    }

    # Default case: just return the path if we couldn't convert it
    return $Path
}

# Run the scan
Search-HardcodedPaths -Fix:$Fix
