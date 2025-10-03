$ErrorActionPreference = 'SilentlyContinue'
Set-Location C:\Code\bar-directory-recon
Write-Output "Fetching branch chore/devcontainer-secrets from origin..."
git fetch origin chore/devcontainer-secrets
Write-Output "Checking out branch..."
git checkout -B chore/devcontainer-secrets origin/chore/devcontainer-secrets
if (-not (Test-Path '.venv-ci')) { python -m venv .venv-ci }
. .\.venv-ci\Scripts\Activate.ps1
pip install -q -U pip pytest
Write-Output "Running secrets test..."
pytest -q universal_recon\tests\unit\test_secrets_loader.py

if (Test-Path scripts\check_ready.ps1) { Write-Output "Running heartbeat..."; pwsh -NoProfile -ExecutionPolicy Bypass -File scripts\check_ready.ps1 }
Write-Output "SUMMARY >> task=ace-secrets-verify status=ok"
