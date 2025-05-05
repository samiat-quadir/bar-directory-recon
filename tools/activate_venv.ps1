# tools/activate_venv.ps1
param (
    [string]$VenvPath = ".venv311"
)

$ActivateScript = Join-Path -Path $PSScriptRoot -ChildPath "..\$VenvPath\Scripts\Activate.ps1"

Write-Host "`nChecking Execution Policy..."
$currentPolicy = Get-ExecutionPolicy -Scope CurrentUser

if ($currentPolicy -ne "RemoteSigned" -and $currentPolicy -ne "Bypass") {
    Write-Host "Current policy is '$currentPolicy'. Attempting to set to RemoteSigned..."
    try {
        Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
        Write-Host "Execution policy updated successfully."
    }
    catch {
        Write-Error "Failed to set execution policy. Try running VS Code as Administrator."
        exit 1
    }
}
else {
    Write-Host "Execution policy is already $currentPolicy."
}

Write-Host "`nActivating virtual environment at '$ActivateScript'..."
& $ActivateScript
