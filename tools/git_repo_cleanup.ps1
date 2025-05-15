# Script: git_repo_cleanup.ps1
# Description: Detects and cleans up stale or conflicting Git repositories in OneDrive folders
# Usage: ./git_repo_cleanup.ps1 -OneDrivePath "C:\Users\username\OneDrive" -PrimaryRepoPath "C:\Repository" -WhatIf

param (
    [string]$OneDrivePath = "C:\Users\samq\OneDrive - Digital Age Marketing Group",
    [string]$PrimaryRepoPath = "C:\bar-directory-recon",
    [switch]$ArchiveRepos = $true,
    [switch]$WhatIf = $false
)

# Set up logging
function Write-Log {
    param (
        [string]$Message,
        [ValidateSet("INFO", "WARNING", "ERROR", "SUCCESS")]
        [string]$Level = "INFO"
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $formattedMessage = "[$timestamp] [$Level] $Message"

    # Color-code console output
    switch ($Level) {
        "INFO" { Write-Host $formattedMessage }
        "WARNING" { Write-Host $formattedMessage -ForegroundColor Yellow }
        "ERROR" { Write-Host $formattedMessage -ForegroundColor Red }
        "SUCCESS" { Write-Host $formattedMessage -ForegroundColor Green }
    }

    # Also log to file
    $logDir = Join-Path $PSScriptRoot "..\Logs"
    if (-not (Test-Path $logDir)) {
        New-Item -Path $logDir -ItemType Directory -Force | Out-Null
    }

    $logFile = Join-Path $logDir "git_cleanup_$(Get-Date -Format 'yyyyMMdd').log"
    $formattedMessage | Out-File -FilePath $logFile -Append
}

# Function to check if a path is a Git repository
function Test-GitRepository {
    param (
        [string]$Path
    )

    $gitDir = Join-Path $Path ".git"
    return (Test-Path $gitDir)
}

# Function to get Git information
function Get-GitInfo {
    param (
        [string]$RepoPath
    )

    if (-not (Test-GitRepository $RepoPath)) {
        return $null
    }

    try {
        $currentLocation = Get-Location
        Set-Location $RepoPath

        $info = @{
            Remote       = $(git remote -v 2>$null)
            Branch       = $(git branch --show-current 2>$null)
            Status       = $(git status --porcelain 2>$null)
            LastCommit   = $(git log -1 --format="%h %cd %s" 2>$null)
            LastActivity = $(git log -1 --format="%at" 2>$null)
        }

        Set-Location $currentLocation
        return $info
    }
    catch {
        Set-Location $currentLocation
        Write-Log "Error getting Git info from $RepoPath: $_" -Level "ERROR"
        return $null
    }
}

# Function to archive a Git repository
function Backup-GitRepository {
    param (
        [string]$RepoPath,
        [string]$ArchivePath
    )

    if ($WhatIf) {
        Write-Log "PREVIEW: Would archive repository $RepoPath to $ArchivePath" -Level "WARNING"
        return $true
    }

    try {
        # Create archive directory if it doesn't exist
        if (-not (Test-Path $ArchivePath)) {
            New-Item -Path $ArchivePath -ItemType Directory -Force | Out-Null
        }

        $repoName = Split-Path $RepoPath -Leaf
        $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
        $zipName = "${repoName}_${timestamp}.zip"
        $zipPath = Join-Path $ArchivePath $zipName

        Write-Log "Archiving $RepoPath to $zipPath..." -Level "INFO"

        # Create a ZIP archive of the repository
        Compress-Archive -Path "$RepoPath\*" -DestinationPath $zipPath -Force

        Write-Log "Repository archived successfully" -Level "SUCCESS"
        return $true
    }
    catch {
        Write-Log "Failed to archive repository: $_" -Level "ERROR"
        return $false
    }
}

# Function to find and clean up Git repositories
function Find-CleanGitRepositories {
    param (
        [string]$ScanPath,
        [switch]$Recursive = $true
    )

    Write-Log "Scanning for Git repositories in $ScanPath..." -Level "INFO"

    # Find all Git repositories in the scan path
    $gitFolders = @()

    if ($Recursive) {
        # Find all .git directories
        $gitDirs = Get-ChildItem -Path $ScanPath -Filter ".git" -Directory -Recurse -Depth 4 -ErrorAction SilentlyContinue
        foreach ($dir in $gitDirs) {
            $gitFolders += $dir.Parent.FullName
        }
    }
    else {
        # Just check immediate subdirectories
        $dirs = Get-ChildItem -Path $ScanPath -Directory
        foreach ($dir in $dirs) {
            if (Test-GitRepository $dir.FullName) {
                $gitFolders += $dir.FullName
            }
        }
    }

    Write-Log "Found $($gitFolders.Count) Git repositories" -Level "INFO"

    # Process each repository
    $results = @{
        ActiveRepos   = @()
        StaleRepos    = @()
        ArchivedRepos = @()
        FailedRepos   = @()
    }

    foreach ($repo in $gitFolders) {
        Write-Log "Processing repository: $repo" -Level "INFO"

        $gitInfo = Get-GitInfo -RepoPath $repo
        if (-not $gitInfo) {
            Write-Log "Could not get Git information for $repo" -Level "ERROR"
            $results.FailedRepos += $repo
            continue
        }

        # Check if this repository is stale (no commits in the last 30 days)
        $isStale = $false
        if ($gitInfo.LastActivity) {
            $lastCommitTime = [datetime]::new(1970, 1, 1, 0, 0, 0, [DateTimeKind]::Utc).AddSeconds($gitInfo.LastActivity)
            $daysSinceLastCommit = (Get-Date) - $lastCommitTime
            if ($daysSinceLastCommit.TotalDays -gt 30) {
                $isStale = $true
                Write-Log "Repository is stale: No commits in $($daysSinceLastCommit.TotalDays.ToString('F0')) days" -Level "WARNING"
            }
        }

        # Check if the repository is in OneDrive
        $isInOneDrive = $repo.StartsWith($OneDrivePath)

        # If it's stale and in OneDrive, it's a candidate for cleanup
        if ($isStale -and $isInOneDrive) {
            Write-Log "Repository is stale and in OneDrive - candidate for cleanup" -Level "WARNING"
            $results.StaleRepos += $repo

            if ($ArchiveRepos) {
                $archivePath = Join-Path $OneDrivePath "Archives\GitRepos"
                $archived = Backup-GitRepository -RepoPath $repo -ArchivePath $archivePath

                if ($archived -and -not $WhatIf) {
                    Write-Log "Removing repository after archiving: $repo" -Level "WARNING"
                    Remove-Item -Path $repo -Recurse -Force
                    $results.ArchivedRepos += $repo
                }
                elseif ($WhatIf) {
                    Write-Log "PREVIEW: Would remove repository after archiving: $repo" -Level "WARNING"
                    $results.ArchivedRepos += $repo
                }
            }
        }
        else {
            Write-Log "Repository is active or not in OneDrive - keeping" -Level "SUCCESS"
            $results.ActiveRepos += $repo
        }
    }

    # Summary
    Write-Log "Git Repository Cleanup Summary:" -Level "INFO"
    Write-Log "  Active repositories: $($results.ActiveRepos.Count)" -Level "SUCCESS"
    Write-Log "  Stale repositories found: $($results.StaleRepos.Count)" -Level "WARNING"
    Write-Log "  Repositories archived: $($results.ArchivedRepos.Count)" -Level "SUCCESS"
    Write-Log "  Failed to process: $($results.FailedRepos.Count)" -Level "ERROR"

    return $results
}

# Function to synchronize a Git repository
function Sync-GitRepository {
    param (
        [string]$RepoPath
    )

    if (-not (Test-Path $RepoPath)) {
        Write-Log "Repository path not found: $RepoPath" -Level "ERROR"
        return $false
    }

    if (-not (Test-GitRepository $RepoPath)) {
        Write-Log "Not a Git repository: $RepoPath" -Level "ERROR"
        return $false
    }

    try {
        $currentLocation = Get-Location
        Set-Location $RepoPath

        # Check if there are any remotes
        $remotes = git remote -v
        if (-not $remotes) {
            Write-Log "No remotes configured for repository: $RepoPath" -Level "WARNING"
            Set-Location $currentLocation
            return $false
        }

        if ($WhatIf) {
            Write-Log "PREVIEW: Would synchronize repository: $RepoPath" -Level "WARNING"
            Set-Location $currentLocation
            return $true
        }

        # Fetch changes
        Write-Log "Fetching changes from remote..." -Level "INFO"
        git fetch --all

        # Check status
        $status = git status --porcelain
        if ($status) {
            Write-Log "Repository has uncommitted changes. Cannot pull." -Level "WARNING"
            Set-Location $currentLocation
            return $false
        }

        # Pull changes
        Write-Log "Pulling changes from remote..." -Level "INFO"
        $pullResult = git pull

        # Push any local changes
        Write-Log "Pushing local changes to remote..." -Level "INFO"
        $pushResult = git push

        Write-Log "Repository synchronized successfully" -Level "SUCCESS"
        Set-Location $currentLocation
        return $true
    }
    catch {
        Write-Log "Error synchronizing repository: $_" -Level "ERROR"
        Set-Location $currentLocation
        return $false
    }
}

# Main execution
if (-not (Test-Path $OneDrivePath)) {
    Write-Log "OneDrive path not found: $OneDrivePath" -Level "ERROR"
    exit 1
}

# Print execution mode
if ($WhatIf) {
    Write-Log "Running in PREVIEW mode. No changes will be made." -Level "WARNING"
}

# Scan OneDrive for Git repositories
Find-CleanGitRepositories -ScanPath $OneDrivePath

# Sync the primary repository if specified
if ($PrimaryRepoPath -and (Test-Path $PrimaryRepoPath)) {
    Write-Log "Syncing primary repository: $PrimaryRepoPath" -Level "INFO"
    Sync-GitRepository -RepoPath $PrimaryRepoPath
}
else {
    Write-Log "Primary repository path not specified or not found. Skipping sync." -Level "WARNING"
}
