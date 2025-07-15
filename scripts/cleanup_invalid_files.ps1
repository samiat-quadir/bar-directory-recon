# Cleanup Invalid Files Script
# Addresses critical filename issues identified in audit report

Write-Host "Starting cleanup of invalid filenames..." -ForegroundColor Green

$rootPath = Split-Path -Parent $PSScriptRoot

# Define problematic files and their actions
$cleanupActions = @(
    @{
        Original = "correct and try again_"
        Action   = "DELETE"
        Reason   = "Invalid filename with trailing underscore"
    },
    @{
        Original = "erssamqOneDrive - Digital Age Marketing GroupDesktopLocal PyWork Projectsbar-directory-recon-new && git status"
        Action   = "DELETE"
        Reason   = "Filename contains shell command and is corrupted path"
    },
    @{
        Original = "erssamquOneDrive - Digital Age Marketing GroupDesktopLocal PyWork Projectsbar-directory-recon"
        Action   = "DELETE"
        Reason   = "Filename is corrupted path"
    },
    @{
        Original = "git"
        Action   = "DELETE"
        Reason   = "Single word filename, likely temporary"
    },
    @{
        Original = "python"
        Action   = "DELETE"
        Reason   = "Single word filename, likely temporary"
    },
    @{
        Original = "t --limit 5"
        Action   = "DELETE"
        Reason   = "Command fragment as filename"
    },
    @{
        Original = "tatus"
        Action   = "DELETE"
        Reason   = "Truncated word, likely temporary"
    },
    @{
        Original = "the name of a cmdlet, function, script file, or operable program. Check the spelling of the name, or if a path was included, verify that the"
        Action   = "DELETE"
        Reason   = "Error message as filename"
    },
    @{
        Original = "_--date=relative"
        Action   = "DELETE"
        Reason   = "Command argument as filename"
    }
)

# Execute cleanup actions
foreach ($action in $cleanupActions) {
    $filePath = Join-Path $rootPath $action.Original
    
    if (Test-Path $filePath) {
        Write-Host "Processing: $($action.Original)" -ForegroundColor Yellow
        Write-Host "  Reason: $($action.Reason)" -ForegroundColor Cyan
        Write-Host "  Action: $($action.Action)" -ForegroundColor Red
        
        try {
            if ($action.Action -eq "DELETE") {
                Remove-Item $filePath -Force -Recurse -ErrorAction Stop
                Write-Host "  Success: Deleted successfully" -ForegroundColor Green
            }
        }
        catch {
            Write-Host "  Error: $($_.Exception.Message)" -ForegroundColor Red
        }
    }
    else {
        Write-Host "File not found (may already be cleaned): $($action.Original)" -ForegroundColor Gray
    }
}

Write-Host ""
Write-Host "Cleanup completed!" -ForegroundColor Green
