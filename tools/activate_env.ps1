# tools\activate_env.ps1

Write-Host "🔧 Checking Execution Policy..."
$currentPolicy = Get-ExecutionPolicy -Scope CurrentUser
if ($currentPolicy -ne "RemoteSigned") {
    Write-Host "🔐 Current policy is '$currentPolicy'. Setting to 'RemoteSigned'..."
    Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser -Force
    Write-Host "✅ Execution policy updated."
}
else {
    Write-Host "✅ Execution policy already set to 'RemoteSigned'."
}

$activateScript = ".venv311\Scripts\Activate.ps1"
if (Test-Path $activateScript) {
    Write-Host "⚡ Activating .venv311..."
    & $activateScript
}
else {
    Write-Host "❌ Activation script not found at $activateScript"
}
