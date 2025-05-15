<#
.SYNOPSIS
OneDriveAutomation.ps1 - Comprehensive management script for OneDrive-based development environments.

.DESCRIPTION
This script automates and standardizes development environments across multiple devices by:
1. Resolving OneDrive paths correctly for the current device
2. Creating and maintaining standard folder structures
3. Ensuring cross-device environment parity (Python packages, VS Code extensions, .env files)
4. Managing Git repositories and resolving conflicts
5. Scanning for and securing sensitive information
6. Setting up scheduled automation tasks

.PARAMETER Tasks
An array of tasks to run. Valid options: All, ResolvePath, StandardizeFolders,
SyncEnvironment, GitCleanup, ScanSecrets, ScheduleTasks

.PARAMETER OneDrivePath
The path to your OneDrive folder. If not specified, will use a hardcoded path.

.PARAMETER PrimaryRepoPath
The path to your primary Git repository outside of OneDrive.

.PARAMETER DeviceId
An identifier for the current device (e.g., "Work", "ASUS").

.PARAMETER WhatIf
Run in preview mode without making changes.

.NOTES
Created: May 15, 2025
Author: GitHub Copilot
Requirements: PowerShell 5.1+, Administrative privileges for scheduled tasks

.EXAMPLE
.\OneDriveAutomation.ps1 -Tasks All
Runs all automation tasks with default settings.

.EXAMPLE
.\OneDriveAutomation.ps1 -Tasks ResolvePath,SyncEnvironment -DeviceId "ASUS" -WhatIf
Previews path resolution and environment sync for the ASUS device without making changes.
#>

param (
    [Parameter(Mandatory = $false)]
    [ValidateSet("All", "ResolvePath", "StandardizeFolders", "SyncEnvironment", "GitCleanup", "ScanSecrets", "ScheduleTasks")]
    [string[]]$Tasks = @("All"),

    [Parameter(Mandatory = $false)]
    [string]$OneDrivePath = "C:\Users\samq\OneDrive - Digital Age Marketing Group",

    [Parameter(Mandatory = $false)]
    [string]$PrimaryRepoPath = "C:\bar-directory-recon",

    [Parameter(Mandatory = $false)]
    [string]$DeviceId = $env:COMPUTERNAME,

    [Parameter(Mandatory = $false)]
    [switch]$WhatIf
)

#region Setup & Utility Functions

# Set up logging
$script:LogFile = Join-Path $PSScriptRoot "OneDriveAutomation_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
$script:ErrorFile = Join-Path $PSScriptRoot "OneDriveAutomation_$(Get-Date -Format 'yyyyMMdd_HHmmss')_errors.log"
$script:ReportFolder = $null
$script:WhatIfEnabled = $WhatIf

function Write-Log {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Message,

        [Parameter(Mandatory = $false)]
        [ValidateSet("INFO", "WARNING", "ERROR", "SUCCESS")]
        [string]$Level = "INFO"
    )

    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $logEntry = "[$timestamp] [$Level] $Message"

    # Output to console with optional colors
    switch ($Level) {
        "WARNING" { Write-Host $logEntry -ForegroundColor Yellow }
        "ERROR" { Write-Host $logEntry -ForegroundColor Red }
        "SUCCESS" { Write-Host $logEntry -ForegroundColor Green }
        default { Write-Host $logEntry }
    }

    # Write to log file
    $logEntry | Out-File -FilePath $script:LogFile -Append

    # Also log errors to dedicated error file
    if ($Level -eq "ERROR") {
        $logEntry | Out-File -FilePath $script:ErrorFile -Append
    }
}

function Invoke-WithErrorHandling {
    param(
        [Parameter(Mandatory = $true)]
        [scriptblock]$ScriptBlock,

        [Parameter(Mandatory = $true)]
        [string]$ErrorMessage
    )

    try {
        if ($script:WhatIfEnabled) {
            Write-Log "PREVIEW MODE: Would execute $ErrorMessage" -Level "INFO"
            return $true
        }
        else {
            return & $ScriptBlock
        }
    }
    catch {
        Write-Log "$ErrorMessage failed: $_" -Level "ERROR"
        return $false
    }
}

function Export-ToJson {
    param(
        [Parameter(Mandatory = $true)]
        [object]$Data,

        [Parameter(Mandatory = $true)]
        [string]$FileName
    )

    if ($null -eq $script:ReportFolder) {
        $script:ReportFolder = Join-Path $OneDrivePath "OneDriveAuditReports"

        if (-not (Test-Path $script:ReportFolder) -and -not $script:WhatIfEnabled) {
            New-Item -Path $script:ReportFolder -ItemType Directory -Force | Out-Null
        }
    }

    $filePath = Join-Path $script:ReportFolder $FileName

    if ($script:WhatIfEnabled) {
        Write-Log "PREVIEW MODE: Would export data to $filePath" -Level "INFO"
    }
    else {
        $Data | ConvertTo-Json -Depth 10 | Out-File -FilePath $filePath -Encoding utf8
        Write-Log "Exported data to $filePath" -Level "SUCCESS"
    }
}

#endregion

#region Task 1: Resolve OneDrive Path
function Resolve-OneDrivePath {
    Write-Log "Starting OneDrive path resolution..." -Level "INFO"

    # Verify the OneDrive path exists
    if (-not (Test-Path $OneDrivePath)) {
        Write-Log "The specified OneDrive path does not exist: $OneDrivePath" -Level "ERROR"
        return $false
    }

    # Verify the Desktop folder exists in OneDrive
    $desktopPath = Join-Path $OneDrivePath "Desktop"
    if (-not (Test-Path $desktopPath)) {
        Write-Log "Desktop folder not found in OneDrive at: $desktopPath" -Level "WARNING"
    }

    # Get OneDrive configuration details for validation
    try {
        $odConfig = $null
        $odRegistry = Get-ItemProperty -Path "HKCU:\Software\Microsoft\OneDrive" -ErrorAction SilentlyContinue

        if ($odRegistry) {
            Write-Log "Found OneDrive in registry" -Level "INFO"
            if ($odRegistry.UserFolder) {
                Write-Log "Registry path matches: $($odRegistry.UserFolder -eq $OneDrivePath)" -Level "INFO"
            }
        }

        # Try to use OneDrive executable to verify paths
        $oneDriveExe = "$env:localappdata\Microsoft\OneDrive\onedrive.exe"
        if (Test-Path $oneDriveExe) {
            Write-Log "OneDrive executable found at: $oneDriveExe" -Level "INFO"
            $syncFolders = & $oneDriveExe /getsyncfolders 2>$null
            if ($syncFolders) {
                Write-Log "Retrieved sync folders from OneDrive executable" -Level "INFO"
                $foundPath = $syncFolders | Select-String -Pattern 'path: (.+)' |
                ForEach-Object { $_.Matches[0].Groups[1].Value }

                if ($foundPath -contains $OneDrivePath) {
                    Write-Log "Confirmed path is a valid OneDrive sync folder" -Level "SUCCESS"
                }
            }
        }
    }
    catch {
        Write-Log "Error while validating OneDrive configuration: $_" -Level "WARNING"
    }

    Write-Log "Using OneDrive path: $OneDrivePath" -Level "SUCCESS"
    return $true
}
#endregion

#region Task 2: Standardize Folder Structure
function New-StandardFolderLayout {
    Write-Log "Creating standard folder layout in OneDrive..." -Level "INFO"

    # Define the standard folders structure
    $standardFolders = @("Scripts", "Logs", "Configs", "Docs", "Projects", "Images", "Archives", "Other")

    # Create standard folders
    foreach ($folder in $standardFolders) {
        $folderPath = Join-Path $OneDrivePath $folder

        if (-not (Test-Path $folderPath)) {
            if ($script:WhatIfEnabled) {
                Write-Log "PREVIEW MODE: Would create folder: $folderPath" -Level "INFO"
            }
            else {
                New-Item -Path $folderPath -ItemType Directory -Force | Out-Null
                Write-Log "Created folder: $folderPath" -Level "SUCCESS"
            }
        }
        else {
            Write-Log "Folder already exists: $folderPath" -Level "INFO"
        }
    }

    # Define file extension mappings
    $fileTypeMap = @{
        "Scripts" = @("*.ps1", "*.py", "*.js", "*.bat", "*.sh", "*.cmd")
        "Logs"    = @("*.log", "*.txt")
        "Configs" = @("*.json", "*.yaml", "*.yml", "*.xml", "*.ini", "*.env", "*.config", "*.toml")
        "Docs"    = @("*.md", "*.pdf", "*.docx", "*.xlsx", "*.pptx", "*.rtf", "*.csv")
        "Images"  = @("*.png", "*.jpg", "*.jpeg", "*.gif", "*.bmp", "*.svg", "*.ico")
    }

    # Get all top-level files in OneDrive
    $files = Get-ChildItem -Path $OneDrivePath -File -Recurse:$false
    $moveReport = @()

    foreach ($file in $files) {
        $destinationFolder = $null

        # Determine target folder based on file extension
        foreach ($folderType in $fileTypeMap.Keys) {
            foreach ($extension in $fileTypeMap[$folderType]) {
                if ($file.Name -like $extension) {
                    $destinationFolder = $folderType
                    break
                }
            }
            if ($destinationFolder) { break }
        }

        # If no matching folder found, use "Other"
        if (-not $destinationFolder) {
            $destinationFolder = "Other"
        }

        $destPath = Join-Path $OneDrivePath $destinationFolder
        $destFilePath = Join-Path $destPath $file.Name

        # Check if file already exists in destination
        if (Test-Path $destFilePath) {
            $destFilePath = Join-Path $destPath "$($file.BaseName)_$(Get-Date -Format 'yyyyMMdd_HHmmss')$($file.Extension)"
        }

        # Move file to appropriate folder
        if ($script:WhatIfEnabled) {
            Write-Log "PREVIEW MODE: Would move file $($file.FullName) to $destFilePath" -Level "INFO"
        }
        else {
            try {
                Move-Item -Path $file.FullName -Destination $destFilePath -Force
                Write-Log "Moved file $($file.Name) to $destinationFolder folder" -Level "SUCCESS"

                $moveReport += [PSCustomObject]@{
                    FileName        = $file.Name
                    SourcePath      = $file.FullName
                    DestinationPath = $destFilePath
                    Category        = $destinationFolder
                    Timestamp       = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
                }
            }
            catch {
                Write-Log "Failed to move file $($file.Name): $_" -Level "ERROR"
            }
        }
    }

    # Export move report
    if ($moveReport.Count -gt 0 -and -not $script:WhatIfEnabled) {
        Export-ToJson -Data $moveReport -FileName "file_organization_report.json"
    }

    Write-Log "Folder structure standardization completed" -Level "SUCCESS"
}
#endregion

#region Task 3: Cross-Device Environment Sync
function Sync-DeviceEnvironment {
    Write-Log "Starting cross-device environment synchronization for device: $DeviceId" -Level "INFO"

    # Ensure the Configs directory exists first
    $configsDir = Join-Path $OneDrivePath "Configs"
    if (-not (Test-Path $configsDir) -and -not $script:WhatIfEnabled) {
        New-Item -Path $configsDir -ItemType Directory -Force | Out-Null
        Write-Log "Created configs directory: $configsDir" -Level "INFO"
    }
    elseif ($script:WhatIfEnabled) {
        Write-Log "PREVIEW MODE: Would create configs directory: $configsDir" -Level "INFO"
    }

    # Then ensure the Environment subdirectory exists
    $envDir = Join-Path $configsDir "Environment"
    if (-not (Test-Path $envDir) -and -not $script:WhatIfEnabled) {
        New-Item -Path $envDir -ItemType Directory -Force | Out-Null
        Write-Log "Created environment directory: $envDir" -Level "INFO"
    }
    elseif ($script:WhatIfEnabled) {
        Write-Log "PREVIEW MODE: Would create environment directory: $envDir" -Level "INFO"
    }

    # 1. Export Python packages
    Write-Log "Exporting Python package list..." -Level "INFO"
    $pipRequirementsFile = Join-Path $envDir "requirements_$DeviceId.txt"

    if ($script:WhatIfEnabled) {
        Write-Log "PREVIEW MODE: Would export pip packages to $pipRequirementsFile" -Level "INFO"
    }
    else {
        try {
            $pipCommand = Get-Command pip -ErrorAction SilentlyContinue
            if ($pipCommand) {
                & pip freeze | Out-File -FilePath $pipRequirementsFile -Encoding utf8
                Write-Log "Exported Python packages to $pipRequirementsFile" -Level "SUCCESS"
            }
            else {
                Write-Log "pip command not found in PATH" -Level "WARNING"
            }
        }
        catch {
            Write-Log "Failed to export Python packages: $_" -Level "ERROR"
        }
    }

    # 2. Export VS Code extensions
    Write-Log "Exporting VS Code extensions..." -Level "INFO"
    $vscodeExtensionsFile = Join-Path $envDir "vscode_extensions_$DeviceId.txt"

    if ($script:WhatIfEnabled) {
        Write-Log "PREVIEW MODE: Would export VS Code extensions to $vscodeExtensionsFile" -Level "INFO"
    }
    else {
        try {
            $codeCommand = Get-Command code -ErrorAction SilentlyContinue
            if ($codeCommand) {
                & code --list-extensions | Out-File -FilePath $vscodeExtensionsFile -Encoding utf8
                Write-Log "Exported VS Code extensions to $vscodeExtensionsFile" -Level "SUCCESS"
            }
            else {
                Write-Log "VS Code command not found in PATH" -Level "WARNING"
            }
        }
        catch {
            Write-Log "Failed to export VS Code extensions: $_" -Level "ERROR"
        }
    }

    # 3. Check for and try to consolidate .env files
    Write-Log "Checking for .env files to consolidate..." -Level "INFO"
    $envFilesDir = Join-Path $OneDrivePath "Configs"
    $envFiles = @(
        (Join-Path $envFilesDir ".env.asus"),
        (Join-Path $envFilesDir ".env.work")
    )

    $validEnvFiles = $envFiles | Where-Object { Test-Path $_ }

    if ($validEnvFiles.Count -gt 0) {
        Write-Log "Found $($validEnvFiles.Count) .env files" -Level "INFO"
        $consolidatedEnvFile = Join-Path $envFilesDir ".env"

        if ($script:WhatIfEnabled) {
            Write-Log "PREVIEW MODE: Would consolidate .env files into $consolidatedEnvFile" -Level "INFO"
        }
        else {
            try {
                # Create a simple environment variable parser
                $envVariables = @{}

                foreach ($envFile in $validEnvFiles) {
                    Write-Log "Processing .env file: $envFile" -Level "INFO"
                    $fileContent = Get-Content -Path $envFile -ErrorAction SilentlyContinue

                    foreach ($line in $fileContent) {
                        # Skip empty lines and comments
                        if ([string]::IsNullOrWhiteSpace($line) -or $line.TrimStart().StartsWith('#')) {
                            continue
                        }

                        if ($line -match '^\s*([^=]+?)\s*=\s*(.*)$') {
                            $key = $matches[1]
                            $value = $matches[2]

                            # If key already exists, check if files came from different devices
                            if ($envVariables.ContainsKey($key) -and $envVariables[$key] -ne $value) {
                                $deviceName = if ($envFile -match '\.env\.(.+)$') { $matches[1] } else { "unknown" }
                                Write-Log "Conflict for key '$key': Using value from $deviceName device" -Level "WARNING"
                            }

                            $envVariables[$key] = $value
                        }
                    }
                }

                # Write consolidated .env file
                $consolidatedContent = @()
                foreach ($key in $envVariables.Keys | Sort-Object) {
                    $consolidatedContent += "$key=$($envVariables[$key])"
                }

                $consolidatedContent | Out-File -FilePath $consolidatedEnvFile -Encoding utf8
                Write-Log "Created consolidated .env file at $consolidatedEnvFile" -Level "SUCCESS"
            }
            catch {
                Write-Log "Failed to consolidate .env files: $_" -Level "ERROR"
            }
        }
    }
    else {
        Write-Log "No .env files found to consolidate" -Level "INFO"
    }

    # 4. Compare environment with other devices (if available)
    Write-Log "Checking for environment differences between devices..." -Level "INFO"
    $otherDevices = Get-ChildItem -Path $envDir -Filter "requirements_*.txt" |
    ForEach-Object { if ($_.Name -notmatch "requirements_$DeviceId\.txt") {
            $_.Name -replace 'requirements_(.+)\.txt', '$1'
        } }

    if ($otherDevices) {
        Write-Log "Found other device environments: $($otherDevices -join ', ')" -Level "INFO"
        $envDiff = @{}

        foreach ($device in $otherDevices) {
            $otherDeviceReqs = Join-Path $envDir "requirements_$device.txt"
            $currentDeviceReqs = Join-Path $envDir "requirements_$DeviceId.txt"

            if (Test-Path $otherDeviceReqs -and Test-Path $currentDeviceReqs) {
                try {
                    $otherPackages = Get-Content $otherDeviceReqs
                    $currentPackages = Get-Content $currentDeviceReqs

                    $diff = Compare-Object -ReferenceObject $otherPackages -DifferenceObject $currentPackages

                    if ($diff) {
                        $packagesOnlyInOther = $diff | Where-Object { $_.SideIndicator -eq '<=' } | Select-Object -ExpandProperty InputObject
                        $packagesOnlyInCurrent = $diff | Where-Object { $_.SideIndicator -eq '=>' } | Select-Object -ExpandProperty InputObject

                        $envDiff[$device] = @{
                            MissingPackages = $packagesOnlyInOther
                            ExtraPackages   = $packagesOnlyInCurrent
                        }

                        Write-Log "Found environment differences with device $device" -Level "WARNING"
                    }
                    else {
                        Write-Log "Environments for $DeviceId and $device are identical" -Level "SUCCESS"
                    }
                }
                catch {
                    Write-Log "Error comparing environments: $_" -Level "ERROR"
                }
            }
        }

        if ($envDiff.Count -gt 0 -and -not $script:WhatIfEnabled) {
            Export-ToJson -Data $envDiff -FileName "environment_diff_report.json"

            # Offer to install missing packages
            foreach ($device in $envDiff.Keys) {
                $missingPackages = $envDiff[$device].MissingPackages
                if ($missingPackages -and $missingPackages.Count -gt 0) {
                    Write-Log "Found $($missingPackages.Count) packages in $device that are missing from $DeviceId" -Level "WARNING"
                    Write-Log "You might want to install them using: pip install $($missingPackages -join ' ')" -Level "INFO"
                }
            }
        }
    }
    else {
        Write-Log "No other device environments found for comparison" -Level "INFO"
    }

    Write-Log "Environment synchronization completed" -Level "SUCCESS"
}
#endregion

#region Task 4: Git Repository Cleanup
function Clean-GitRepositories {
    Write-Log "Starting Git repository cleanup..." -Level "INFO"

    # Adjust the primary repository path to the current workspace location if not found
    if (-not (Test-Path $PrimaryRepoPath)) {
        $scriptDir = Split-Path -Parent $PSCommandPath
        $PrimaryRepoPath = $scriptDir
        Write-Log "Primary repository path not found, using script directory instead: $PrimaryRepoPath" -Level "WARNING"
    }

    # 1. Check if OneDrive contains a stale Git repository
    $repoName = Split-Path -Leaf $PrimaryRepoPath
    $oneDriveRepo = Join-Path $OneDrivePath $repoName

    if (Test-Path $oneDriveRepo) {
        Write-Log "Found potential stale Git repository in OneDrive: $oneDriveRepo" -Level "WARNING"

        # Verify it's actually a Git repository
        $gitDir = Join-Path $oneDriveRepo ".git"
        if (Test-Path $gitDir) {
            Write-Log "Confirmed $oneDriveRepo is a Git repository" -Level "INFO"

            # Archive the repository before removing if needed
            $archiveDir = Join-Path $OneDrivePath "Archives\git_repos"
            $archiveName = "bar-directory-recon_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
            $archivePath = Join-Path $archiveDir $archiveName

            if ($script:WhatIfEnabled) {
                Write-Log "PREVIEW MODE: Would archive repository to $archivePath and then remove it" -Level "INFO"
            }
            else {
                try {
                    # Create archive directory if it doesn't exist
                    if (-not (Test-Path $archiveDir)) {
                        New-Item -Path $archiveDir -ItemType Directory -Force | Out-Null
                    }

                    # Archive repository
                    New-Item -Path $archivePath -ItemType Directory -Force | Out-Null
                    Copy-Item -Path "$oneDriveRepo\*" -Destination $archivePath -Recurse -Force
                    Write-Log "Archived repository to $archivePath" -Level "SUCCESS"

                    # Remove stale repository
                    Remove-Item -Path $oneDriveRepo -Recurse -Force
                    Write-Log "Removed stale repository from OneDrive: $oneDriveRepo" -Level "SUCCESS"
                }
                catch {
                    Write-Log "Failed to clean up stale repository: $_" -Level "ERROR"
                }
            }
        }
    }
    else {
        Write-Log "No stale Git repository found in OneDrive" -Level "INFO"
    }

    # 2. Verify and synchronize primary Git repository
    if (-not (Test-Path $PrimaryRepoPath)) {
        Write-Log "Primary Git repository not found at: $PrimaryRepoPath" -Level "ERROR"
        return
    }

    $primaryGitDir = Join-Path $PrimaryRepoPath ".git"
    if (-not (Test-Path $primaryGitDir)) {
        Write-Log "The specified primary repository is not a Git repository: $PrimaryRepoPath" -Level "ERROR"
        return
    }

    # Synchronize with remote repository
    Write-Log "Synchronizing primary Git repository at $PrimaryRepoPath with remotes" -Level "INFO"

    if ($script:WhatIfEnabled) {
        Write-Log "PREVIEW MODE: Would synchronize Git repository at $PrimaryRepoPath" -Level "INFO"
    }
    else {
        try {
            # Save current location
            $currentLocation = Get-Location
            Set-Location $PrimaryRepoPath

            # Check remote
            $remotes = & git remote -v
            if ($remotes) {
                Write-Log "Repository remotes: $remotes" -Level "INFO"
            }
            else {
                Write-Log "No remotes configured for repository" -Level "WARNING"
                Set-Location $currentLocation
                return
            }

            # Fetch updates
            Write-Log "Fetching updates from remote..." -Level "INFO"
            & git fetch --all

            # Check branch and status
            $currentBranch = & git branch --show-current
            $status = & git status --porcelain

            if ($status) {
                Write-Log "Repository has uncommitted changes. Please commit or stash before pulling." -Level "WARNING"
            }
            else {
                # Pull updates
                Write-Log "Pulling updates from remote for branch: $currentBranch" -Level "INFO"
                $pullResult = & git pull
                Write-Log "Pull result: $pullResult" -Level "SUCCESS"

                # Push any local commits
                Write-Log "Pushing local commits to remote..." -Level "INFO"
                $pushResult = & git push
                Write-Log "Push result: $pushResult" -Level "SUCCESS"
            }

            # Restore location
            Set-Location $currentLocation
        }
        catch {
            Write-Log "Error synchronizing Git repository: $_" -Level "ERROR"
            # Ensure we restore location even on error
            Set-Location $currentLocation
        }
    }

    Write-Log "Git repository cleanup completed" -Level "SUCCESS"
}
#endregion

#region Task 5: Secrets Scanning
function Scan-ForSecrets {
    Write-Log "Starting scan for sensitive information..." -Level "INFO"

    # Define patterns for sensitive information
    $secretPatterns = @(
        @{Name = "Password"; Pattern = "password|pwd|pass=" }
        @{Name = "API Key"; Pattern = "api[_\s]?key|apikey" }
        @{Name = "Token"; Pattern = "token|jwt|bearer" }
        @{Name = "Secret"; Pattern = "secret|private[_\s]?key" }
        @{Name = "Connection String"; Pattern = "connection[_\s]?string|connstr|conn=" }
        @{Name = "Credential"; Pattern = "credential|auth|login" }
    )

    # Define file types to scan
    $fileTypes = @("*.txt", "*.env", "*.config", "*.ini", "*.json", "*.yaml", "*.yml", "*.ps1", "*.py", "*.js")

    # Define directories to exclude
    $excludeDirs = @(".git", ".venv", "venv", "node_modules", "obj", "bin", ".vs", ".vscode")

    # Initialize results
    $scanResults = @()

    # Function to check if path should be excluded
    function ShouldExclude {
        param($Path)
        foreach ($excludeDir in $excludeDirs) {
            if ($Path -match "[\\/]$excludeDir([\\/]|$)") {
                return $true
            }
        }
        return $false
    }

    # Get all files matching the extensions
    Write-Log "Scanning for sensitive information in files..." -Level "INFO"

    if ($script:WhatIfEnabled) {
        Write-Log "PREVIEW MODE: Would scan $OneDrivePath for sensitive information" -Level "INFO"
    }
    else {
        try {
            $files = Get-ChildItem -Path $OneDrivePath -Include $fileTypes -Recurse -File -ErrorAction SilentlyContinue |
            Where-Object { -not (ShouldExclude $_.FullName) }

            Write-Log "Found $($files.Count) files to scan" -Level "INFO"

            foreach ($file in $files) {
                $relativePath = $file.FullName.Substring($OneDrivePath.Length)
                Write-Log "Scanning file: $relativePath" -Level "INFO" -Verbose

                $fileResults = @()
                $content = Get-Content -Path $file.FullName -Raw -ErrorAction SilentlyContinue

                if ($content) {
                    foreach ($pattern in $secretPatterns) {
                        if ($content -match $pattern.Pattern) {
                            $lines = Get-Content -Path $file.FullName -ErrorAction SilentlyContinue
                            $lineNumber = 1

                            foreach ($line in $lines) {
                                if ($line -match $pattern.Pattern) {
                                    $fileResults += [PSCustomObject]@{
                                        LineNumber     = $lineNumber
                                        PatternType    = $pattern.Name
                                        MatchedPattern = $pattern.Pattern
                                        LineContent    = ($line -replace $pattern.Pattern, "***$($pattern.Name)***")
                                    }
                                }
                                $lineNumber++
                            }
                        }
                    }
                }

                if ($fileResults.Count -gt 0) {
                    $scanResults += [PSCustomObject]@{
                        FilePath     = $file.FullName
                        RelativePath = $relativePath
                        Matches      = $fileResults
                        MatchCount   = $fileResults.Count
                        FileType     = $file.Extension
                        LastModified = $file.LastWriteTime
                    }
                }
            }

            # Generate report
            if ($scanResults.Count -gt 0) {
                Write-Log "Found $($scanResults.Count) files containing potential sensitive information" -Level "WARNING"
                Export-ToJson -Data $scanResults -FileName "secrets_scan_report.json"

                # Provide remediation advice
                Write-Log "Recommend reviewing secrets_scan_report.json and securing sensitive information" -Level "WARNING"
                Write-Log "Consider using Windows Credential Manager or Azure Key Vault instead of plaintext" -Level "INFO"
            }
            else {
                Write-Log "No sensitive information found in scanned files" -Level "SUCCESS"
            }
        }
        catch {
            Write-Log "Error during secrets scanning: $_" -Level "ERROR"
        }
    }

    Write-Log "Secrets scanning completed" -Level "SUCCESS"
}
#endregion

#region Task 6: Schedule Automation Tasks
function Register-AutomationTasks {
    Write-Log "Setting up scheduled tasks for automation..." -Level "INFO"

    # Check if running with administrator rights
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

    if (-not $isAdmin) {
        Write-Log "Administrator privileges required to create scheduled tasks" -Level "ERROR"
        Write-Log "Please run this script as Administrator to set up scheduled tasks" -Level "ERROR"
        return
    }

    # Define task for git_commit_and_notify.py
    $gitCommitScript = Join-Path $PrimaryRepoPath "git_commit_and_notify.py"

    if (-not (Test-Path $gitCommitScript)) {
        Write-Log "Git commit script not found at: $gitCommitScript" -Level "ERROR"
        return
    }

    # Define task parameters
    $taskName = "DailyGitCommit"
    $taskDescription = "Automatically commits changes and sends notifications"
    $pythonPath = "python.exe"  # Assuming Python is in the PATH

    # Create task action
    $taskAction = New-ScheduledTaskAction -Execute $pythonPath -Argument $gitCommitScript -WorkingDirectory $PrimaryRepoPath

    # Create task trigger (daily at 9:30 AM)
    $taskTrigger = New-ScheduledTaskTrigger -Daily -At "9:30 AM"

    # Create task settings
    $taskSettings = New-ScheduledTaskSettingsSet -StartWhenAvailable -DontStopOnIdleEnd -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

    # Get current user for task principal
    $currentUser = [System.Security.Principal.WindowsIdentity]::GetCurrent().Name
    $taskPrincipal = New-ScheduledTaskPrincipal -UserId $currentUser -LogonType S4U -RunLevel Highest

    if ($script:WhatIfEnabled) {
        Write-Log "PREVIEW MODE: Would create scheduled task '$taskName' to run '$gitCommitScript' daily at 9:30 AM" -Level "INFO"
    }
    else {
        try {
            # Register the task
            $existingTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue

            if ($existingTask) {
                Write-Log "Task '$taskName' already exists. Unregistering existing task." -Level "WARNING"
                Unregister-ScheduledTask -TaskName $taskName -Confirm:$false
            }

            Register-ScheduledTask -TaskName $taskName -Action $taskAction -Trigger $taskTrigger -Settings $taskSettings -Principal $taskPrincipal -Description $taskDescription
            Write-Log "Successfully registered scheduled task: $taskName" -Level "SUCCESS"

            # Verify task was created
            $createdTask = Get-ScheduledTask -TaskName $taskName -ErrorAction SilentlyContinue
            if ($createdTask) {
                Write-Log "Verified task creation. Next run time: $($createdTask.NextRunTime)" -Level "SUCCESS"
            }
        }
        catch {
            Write-Log "Failed to create scheduled task: $_" -Level "ERROR"
        }
    }

    Write-Log "Scheduled task setup completed" -Level "SUCCESS"
}
#endregion

#region Main Execution
function Start-Main {
    Write-Log "=== Starting OneDriveAutomation.ps1 ===" -Level "INFO"
    Write-Log "Device ID: $DeviceId" -Level "INFO"
    Write-Log "OneDrive Path: $OneDrivePath" -Level "INFO"
    Write-Log "Primary Repo Path: $PrimaryRepoPath" -Level "INFO"

    if ($script:WhatIfEnabled) {
        Write-Log "Running in PREVIEW mode (WhatIf)" -Level "WARNING"
    }

    # Execute tasks
    $executeAll = $Tasks -contains "All"

    # 1. Resolve OneDrive Path
    if ($executeAll -or $Tasks -contains "ResolvePath") {
        $pathResolved = Resolve-OneDrivePath
        if (-not $pathResolved) {
            Write-Log "Failed to resolve OneDrive path. Cannot proceed." -Level "ERROR"
            return
        }
    }

    # 2. Standardize Folder Structure
    if ($executeAll -or $Tasks -contains "StandardizeFolders") {
        New-StandardFolderLayout
    }

    # 3. Cross-Device Environment Sync
    if ($executeAll -or $Tasks -contains "SyncEnvironment") {
        Sync-DeviceEnvironment
    }

    # 4. Git Repository Cleanup
    if ($executeAll -or $Tasks -contains "GitCleanup") {
        Clean-GitRepositories
    }

    # 5. Secrets Scanning
    if ($executeAll -or $Tasks -contains "ScanSecrets") {
        Scan-ForSecrets
    }

    # 6. Schedule Automation Tasks
    if ($executeAll -or $Tasks -contains "ScheduleTasks") {
        Register-AutomationTasks
    }

    Write-Log "=== OneDriveAutomation.ps1 Completed ===" -Level "SUCCESS"
    Write-Log "Log file: $script:LogFile" -Level "INFO"

    if (Test-Path $script:ErrorFile) {
        $errorCount = (Get-Content $script:ErrorFile).Count
        if ($errorCount -gt 0) {
            Write-Log "Errors encountered during execution. See: $script:ErrorFile" -Level "WARNING"
        }
    }
}

# Start execution
Start-Main
#endregion
