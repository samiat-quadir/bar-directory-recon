Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
Set-Location 'C:\Code\bar-directory-recon'
$wfDir = '.github/workflows'
if (-not (Test-Path $wfDir)) { Write-Output 'NO_WORKFLOW_DIR'; exit 0 }
Get-ChildItem -Path $wfDir -Recurse -File -Include *.yml, *.yaml | ForEach-Object {
    if (Select-String -Path $_.FullName -Pattern 'pull_request' -Quiet) { Write-Output $_.FullName }
}
