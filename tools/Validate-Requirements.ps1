#!/usr/bin/env powershell
<#
.SYNOPSIS
    Validate requirements files to prevent known dependency issues.

.DESCRIPTION
    This script validates requirements files and can automatically fix known issues:
    - Corrects watchdog version constraints
    - Removes non-existent packages like smtplib-ssl
    - Prevents other known problematic dependencies

.PARAMETER Fix
    Automatically fix known issues in requirements files.

.PARAMETER Files
    Specific files to check. Defaults to all requirements*.txt files.

.EXAMPLE
    .\Validate-Requirements.ps1
    Validates all requirements files.

.EXAMPLE
    .\Validate-Requirements.ps1 -Fix
    Validates and automatically fixes issues in requirements files.
#>

param(
    [Parameter()]
    [switch]$Fix,

    [Parameter()]
    [string[]]$Files
)

$ErrorActionPreference = "Stop"

# Known problematic dependencies and their fixes
$DependencyFixes = @{
    "requirements-core.txt" = @{
        "watchdog>=3.0.0" = "watchdog>=6.0.0,<7.0.0"
        "watchdog==3.0.0" = "watchdog>=6.0.0,<7.0.0"
        "watchdog>3.0.0" = "watchdog>=6.0.0,<7.0.0"
    }
    "requirements-optional.txt" = @{
        "smtplib-ssl" = $null  # Remove entirely
    }
}

# Dependencies that should never be present
$ForbiddenDependencies = @(
    "smtplib-ssl"  # Non-existent package
)

function Test-RequirementsFile {
    param(
        [Parameter(Mandatory)]
        [string]$FilePath
    )

    $issues = @()

    if (-not (Test-Path $FilePath)) {
        return @(@{
            LineNumber = "N/A"
            Issue = "File not found: $FilePath"
            Fix = "Create the file"
        })
    }

    try {
        $lines = Get-Content $FilePath -ErrorAction Stop
    } catch {
        return @(@{
            LineNumber = "N/A"
            Issue = "Error reading $FilePath`: $_"
            Fix = "Fix file permissions"
        })
    }

    $fileName = Split-Path $FilePath -Leaf
    $fileFixes = $DependencyFixes[$fileName]

    for ($i = 0; $i -lt $lines.Count; $i++) {
        $lineNum = $i + 1
        $line = $lines[$i].Trim()

        # Skip comments and empty lines
        if (-not $line -or $line.StartsWith('#')) {
            continue
        }

        # Check for forbidden dependencies
        foreach ($forbidden in $ForbiddenDependencies) {
            if ($line -like "*$forbidden*") {
                $issues += @{
                    LineNumber = $lineNum
                    Issue = "Forbidden dependency found: $forbidden"
                    Fix = "Remove this line entirely"
                }
            }
        }

        # Check for specific fixes needed
        if ($fileFixes) {
            foreach ($oldDep in $fileFixes.Keys) {
                if ($line -like "*$oldDep*") {
                    $newDep = $fileFixes[$oldDep]
                    $fixMsg = if ($null -eq $newDep) {
                        "Remove this line entirely"
                    } else {
                        "Change to: $newDep"
                    }

                    $issues += @{
                        LineNumber = $lineNum
                        Issue = "Outdated dependency: $oldDep"
                        Fix = $fixMsg
                    }
                }
            }
        }
    }

    return $issues
}

function Repair-RequirementsFile {
    param(
        [Parameter(Mandatory)]
        [string]$FilePath
    )

    if (-not (Test-Path $FilePath)) {
        Write-Host "❌ File not found: $FilePath" -ForegroundColor Red
        return $false
    }

    try {
        $content = Get-Content $FilePath -Raw -ErrorAction Stop
    } catch {
        Write-Host "❌ Error reading $FilePath`: $_" -ForegroundColor Red
        return $false
    }

    $originalContent = $content
    $fileName = Split-Path $FilePath -Leaf
    $fileFixes = $DependencyFixes[$fileName]

    # Apply specific dependency fixes
    if ($fileFixes) {
        foreach ($oldDep in $fileFixes.Keys) {
            $newDep = $fileFixes[$oldDep]
            if ($content -like "*$oldDep*") {
                if ($null -eq $newDep) {
                    # Remove the entire line containing this dependency
                    $lines = $content -split "`n"
                    $filteredLines = @()
                    foreach ($line in $lines) {
                        if ($line -notlike "*$oldDep*") {
                            $filteredLines += $line
                        } else {
                            Write-Host "🔧 Removing line: $($line.Trim())" -ForegroundColor Yellow
                        }
                    }
                    $content = $filteredLines -join "`n"
                } else {
                    Write-Host "🔧 Replacing $oldDep with $newDep" -ForegroundColor Yellow
                    $content = $content -replace [regex]::Escape($oldDep), $newDep
                }
            }
        }
    }

    # Remove forbidden dependencies
    foreach ($forbidden in $ForbiddenDependencies) {
        $lines = $content -split "`n"
        $filteredLines = @()
        foreach ($line in $lines) {
            if ($line -notlike "*$forbidden*" -or $line.Trim().StartsWith('#')) {
                $filteredLines += $line
            } else {
                Write-Host "🔧 Removing forbidden dependency: $($line.Trim())" -ForegroundColor Yellow
            }
        }
        $content = $filteredLines -join "`n"
    }

    # Only write if changes were made
    if ($content -ne $originalContent) {
        try {
            Set-Content -Path $FilePath -Value $content -ErrorAction Stop
            Write-Host "✅ Fixed $FilePath" -ForegroundColor Green
            return $true
        } catch {
            Write-Host "❌ Error writing $FilePath`: $_" -ForegroundColor Red
            return $false
        }
    }

    return $false
}

# Main execution
try {
    # Get project root (assuming script is in tools/)
    if ($PSScriptRoot -like "*tools*") {
        $projectRoot = Split-Path $PSScriptRoot -Parent
    } else {
        $projectRoot = $PSScriptRoot
    }

    # Default files to check
    if ($Files) {
        $filesToCheck = $Files
    } else {
        $filesToCheck = @(
            "$projectRoot\requirements-core.txt",
            "$projectRoot\requirements-optional.txt",
            "$projectRoot\requirements.txt"
        )
        # Only check files that exist
        $filesToCheck = $filesToCheck | Where-Object { Test-Path $_ }
    }

    Write-Host "🔍 Validating requirements files..." -ForegroundColor Blue
    Write-Host "📁 Project root: $projectRoot"
    Write-Host ""

    $totalIssues = 0
    $filesFixed = 0

    foreach ($filePath in $filesToCheck) {
        $fileName = Split-Path $filePath -Leaf
        Write-Host "📋 Checking $fileName..." -ForegroundColor Blue

        $issues = Test-RequirementsFile -FilePath $filePath

        if ($issues.Count -eq 0) {
            Write-Host "✅ $fileName`: No issues found" -ForegroundColor Green
        } else {
            Write-Host "⚠️  $fileName`: $($issues.Count) issue(s) found:" -ForegroundColor Yellow
            foreach ($issue in $issues) {
                Write-Host "   Line $($issue.LineNumber): $($issue.Issue)" -ForegroundColor Red
                Write-Host "   Suggested fix: $($issue.Fix)" -ForegroundColor Yellow
            }

            $totalIssues += $issues.Count

            if ($Fix) {
                if (Repair-RequirementsFile -FilePath $filePath) {
                    $filesFixed++
                    # Re-validate after fixing
                    $remainingIssues = Test-RequirementsFile -FilePath $filePath
                    if ($remainingIssues.Count -gt 0) {
                        Write-Host "⚠️  $($remainingIssues.Count) issue(s) remain after auto-fix" -ForegroundColor Yellow
                    } else {
                        Write-Host "✅ All issues in $fileName have been fixed" -ForegroundColor Green
                    }
                }
            }
        }

        Write-Host ""
    }

    # Summary
    Write-Host "📊 Summary:" -ForegroundColor Blue
    Write-Host "   Files checked: $($filesToCheck.Count)"
    Write-Host "   Total issues found: $totalIssues"

    if ($Fix) {
        Write-Host "   Files fixed: $filesFixed"
        if ($totalIssues -gt 0 -and $filesFixed -gt 0) {
            Write-Host "`n🎉 Requirements files have been automatically fixed!" -ForegroundColor Green
            Write-Host "💡 Tip: Run this script regularly to catch issues early." -ForegroundColor Cyan
        } elseif ($totalIssues -gt 0) {
            Write-Host "`n⚠️  Some issues could not be automatically fixed." -ForegroundColor Yellow
            Write-Host "   Please review the suggestions above and fix manually."
        }
    } else {
        if ($totalIssues -gt 0) {
            Write-Host "`n💡 Run with -Fix to automatically fix $totalIssues issue(s)" -ForegroundColor Cyan
        } else {
            Write-Host "`n🎉 All requirements files are valid!" -ForegroundColor Green
        }
    }

    # Exit with error code if issues remain
    if (-not $Fix -and $totalIssues -gt 0) {
        exit 1
    } elseif ($Fix) {
        # Check if any issues remain after fixing
        $remainingTotal = 0
        foreach ($filePath in $filesToCheck) {
            $remainingTotal += (Test-RequirementsFile -FilePath $filePath).Count
        }
        if ($remainingTotal -gt 0) {
            exit 1
        }
    }

} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
    Write-Host "Stack trace: $($_.ScriptStackTrace)" -ForegroundColor Red
    exit 1
}
