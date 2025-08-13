Param()
$ErrorActionPreference = 'Stop'
$sshDir = Join-Path $env:USERPROFILE '.ssh'
if (-not (Test-Path $sshDir)) { New-Item -ItemType Directory -Path $sshDir | Out-Null }
$configPath = Join-Path $sshDir 'config'
if (-not (Test-Path $configPath)) { New-Item -ItemType File -Path $configPath | Out-Null }
$blocks = @(
    @"
Host mothership
  HostName 100.124.245.90
  User alex
  IdentitiesOnly yes
  ServerAliveInterval 30
  ServerAliveCountMax 4
  ConnectTimeout 10
  Compression yes
"@,
    @"
Host rog-lucci
  HostName 100.89.12.61
  User alex
  IdentitiesOnly yes
  ServerAliveInterval 30
  ServerAliveCountMax 4
  ConnectTimeout 10
  Compression yes
"@
)
$existing = Get-Content $configPath -Raw
$added = $false
foreach ($b in $blocks) {
    $hostName = ($b -split "`n" | Where-Object { $_ -match '^Host ' }) -replace '^Host\s+', ''
    if ($existing -notmatch "(?m)^Host\s+$hostName(\s|$)") {
        Add-Content -Path $configPath -Value ("`n" + $b.TrimEnd())
        $added = $true
    }
}
if ($added) { Write-Host 'SSH config updated.' } else { Write-Host 'SSH config already contained host entries.' }
Write-Host '--- Extracted host blocks ---'
Select-String -Path $configPath -Pattern '^Host ' -Context 0, 8 | ForEach-Object { $_.Line; $_.Context.PostContext }
