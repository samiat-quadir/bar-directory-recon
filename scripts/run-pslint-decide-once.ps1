Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
Set-Location 'C:\Code\bar-directory-recon'
$log = "artifacts\pslint\decide_20251021-173800.log"
pwsh -NoProfile -ExecutionPolicy Bypass -File 'scripts\pslint_promotion_decide.ps1' -Execute *>&1 | Tee-Object -FilePath $log