# PowerShell script to update VS Code Insiders user settings
$userSettingsPath = "$env:APPDATA\Code - Insiders\User\settings.json"

if (Test-Path $userSettingsPath) {
    $settings = Get-Content $userSettingsPath -Raw | ConvertFrom-Json
} else {
    $settings = @{}
}

# Add assistant identity
$settings | Add-Member -Type NoteProperty -Name "assistant.identity" -Value @{
    "agentName" = "Ace"
    "device" = "ROG-LUCCI"
} -Force

# Convert back to JSON and save
$settings | ConvertTo-Json -Depth 10 | Set-Content $userSettingsPath -Encoding UTF8

Write-Host "Updated user settings with assistant identity"
