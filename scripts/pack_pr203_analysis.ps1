Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$SRC = 'artifacts\pr203_analysis'
$ZIP = 'artifacts\pr203_analysis.zip'

if (-not (Test-Path $SRC)) { Write-Host "Source folder not found: $SRC"; exit 1 }
if (Test-Path $ZIP) { Remove-Item $ZIP -Force }

Get-ChildItem $SRC | Format-Table Name, Length | Out-String | Write-Host
Compress-Archive -Path "$SRC\*" -DestinationPath $ZIP -Force
Write-Host "SUMMARY >> task=pack_pr203_analysis status=ok zip=$ZIP note='ready to upload'"
