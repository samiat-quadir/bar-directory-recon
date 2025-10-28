# file: scripts/testpypi_local_build.ps1
Set-StrictMode -Version Latest
$ErrorActionPreference='Stop'
python -m pip install -U pip build twine
if(Test-Path dist){ Remove-Item -Recurse -Force dist }
python -m build
Write-Host "Built artifacts in dist/. To publish in CI, add TESTPYPI_API_TOKEN secret and dispatch the workflow."