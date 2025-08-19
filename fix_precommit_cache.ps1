# Fix Pre-commit Cache Corruption Script
# This script resolves Windows permission issues with pre-commit cache

param(
    [switch]$Force = $false
)

Write-Host "🔧 Pre-commit Cache Fix Utility" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan

$cacheDir = "$env:USERPROFILE\.cache\pre-commit"

if (-not (Test-Path $cacheDir)) {
    Write-Host "✅ No pre-commit cache found - nothing to fix" -ForegroundColor Green
    exit 0
}

Write-Host "📁 Found pre-commit cache at: $cacheDir" -ForegroundColor Yellow

if (-not $Force) {
    $response = Read-Host "Clear corrupted pre-commit cache? (y/N)"
    if ($response -ne 'y' -and $response -ne 'Y') {
        Write-Host "❌ Operation cancelled by user" -ForegroundColor Red
        exit 1
    }
}

Write-Host "🔓 Taking ownership of cache files..." -ForegroundColor Yellow
try {
    & takeown /f $cacheDir /r /d y 2>$null | Out-Null
    Write-Host "✅ Ownership acquired" -ForegroundColor Green
}
catch {
    Write-Host "⚠️ Takeown had issues, continuing..." -ForegroundColor Yellow
}

Write-Host "🔑 Setting full permissions..." -ForegroundColor Yellow
try {
    & icacls $cacheDir /grant "$env:USERNAME`:F" /t 2>$null | Out-Null
    Write-Host "✅ Permissions updated" -ForegroundColor Green
}
catch {

    Write-Host "⚠️ Permission update had issues, continuing..." -ForegroundColor Yellow
}

Write-Host "🗑️ Removing corrupted cache..." -ForegroundColor Yellow
try {
    Remove-Item $cacheDir -Recurse -Force -ErrorAction SilentlyContinue
    if (-not (Test-Path $cacheDir)) {
        Write-Host "✅ Cache successfully cleared" -ForegroundColor Green
    }
    else {
        Write-Host "⚠️ Some files may still remain (this is usually OK)" -ForegroundColor Yellow
    }
}
catch {

    Write-Host "⚠️ Removal had issues, but cache should be cleared" -ForegroundColor Yellow
}

Write-Host "🔄 Re-initializing pre-commit..." -ForegroundColor Yellow
try {
    if (Get-Command "pre-commit" -ErrorAction SilentlyContinue) {
        & pre-commit install 2>$null
        Write-Host "✅ Pre-commit re-installed" -ForegroundColor Green
    }
    else {
        Write-Host "⚠️ Pre-commit command not found - install manually if needed" -ForegroundColor Yellow
    }
}
catch {

    Write-Host "⚠️ Pre-commit install had issues - may need manual reinstall" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "🎉 Pre-commit cache fix complete!" -ForegroundColor Green
Write-Host "You can now run git commits normally" -ForegroundColor White
Write-Host ""
Write-Host "If issues persist, run: git commit --no-verify" -ForegroundColor Cyan

