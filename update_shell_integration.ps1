# PowerShell script to update VS Code Insiders user settings with shell integration
$userSettingsPath = "$env:APPDATA\Code - Insiders\User\settings.json"

if (Test-Path $userSettingsPath) {
    $settings = Get-Content $userSettingsPath -Raw | ConvertFrom-Json
}
else {
    $settings = @{}
}

# Add shell integration settings
$settings | Add-Member -Type NoteProperty -Name "terminal.integrated.shellIntegration.enabled" -Value $true -Force
$settings | Add-Member -Type NoteProperty -Name "terminal.integrated.shellIntegration.decorationsEnabled" -Value "both" -Force
$settings | Add-Member -Type NoteProperty -Name "terminal.integrated.shellIntegration.history" -Value 100 -Force
$settings | Add-Member -Type NoteProperty -Name "terminal.integrated.shellIntegration.suggestEnabled" -Value $true -Force

# Ensure assistant identity is still there
if (-not $settings."assistant.identity") {
    $settings | Add-Member -Type NoteProperty -Name "assistant.identity" -Value @{
        "agentName" = "Ace"
        "device"    = "ROG-LUCCI"
    } -Force
}

# Convert back to JSON and save
$settings | ConvertTo-Json -Depth 10 | Set-Content $userSettingsPath -Encoding UTF8

Write-Host "Updated user settings with shell integration and assistant identity"
