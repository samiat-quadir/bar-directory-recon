# PowerShell script to move stray automation files to the repo
$repo = "C:\Code\bar-directory-recon"
$names = @("automation", "cross_device_tasks.yaml", "run_cross_device_task.py")

Write-Host "Searching for stray automation files outside of $repo..."

foreach ($name in $names) {
    try {
        $strays = Get-ChildItem -Path C:\ -Name $name -Recurse -ErrorAction SilentlyContinue |
        Where-Object { -not $_.StartsWith("$repo\") }

        foreach ($stray in $strays) {
            $fullPath = "C:\$stray"
            Write-Host "Found stray file: $fullPath"

            if ($name -eq "automation" -and (Test-Path $fullPath -PathType Container)) {
                $targetPath = "$repo\automation"
                Write-Host "Moving automation directory from $fullPath to $targetPath"
                if (Test-Path $targetPath) {
                    Remove-Item $targetPath -Recurse -Force
                }
                Move-Item -Path $fullPath -Destination $targetPath -Force
            }
            elseif ($name -eq "cross_device_tasks.yaml") {
                New-Item -ItemType Directory -Force -Path "$repo\automation" | Out-Null
                $targetPath = "$repo\automation\cross_device_tasks.yaml"
                Write-Host "Moving $fullPath to $targetPath"
                Move-Item -Path $fullPath -Destination $targetPath -Force
            }
            elseif ($name -eq "run_cross_device_task.py") {
                $targetPath = "$repo\run_cross_device_task.py"
                Write-Host "Moving $fullPath to $targetPath"
                Move-Item -Path $fullPath -Destination $targetPath -Force
            }
        }
    }
    catch {
        Write-Host "Error searching for $name : $_"
    }
}

# Ensure automation directory exists
if (-not (Test-Path "$repo\automation")) {
    New-Item -ItemType Directory -Force -Path "$repo\automation" | Out-Null
    Write-Host "Created automation directory"
}

Write-Host "Stray file cleanup complete"
