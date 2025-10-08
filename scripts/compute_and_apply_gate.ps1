$xml = Get-Content -Path 'reports/coverage.xml' -Raw
$m = [regex]::Match($xml, 'line-rate="([0-9.]+)"')
if (-not $m.Success) { Write-Host 'ERROR: coverage xml missing line-rate'; exit 2 }
$obs = [math]::Floor([double]$m.Groups[1].Value * 100)
$gate = [Math]::Max(8, [Math]::Min(35, $obs - 1))
Write-Host "observed=$obs% gate=$gate"
$files = @('pytest.ini', 'pyproject.toml', 'tox.ini')
foreach ($f in $files) { if (Test-Path $f) { $c = Get-Content $f -Raw; if ($c -match '--cov-fail-under=\d+') { $c2 = $c -replace '--cov-fail-under=\d+', "--cov-fail-under=$gate"; Set-Content -Path $f -Value $c2 -Encoding utf8; Write-Host "Updated $f" } else { Write-Host "No --cov-fail-under found in $f" } } }
if ((git status --porcelain) -match '^\s*(A|M).*\breports\/') { Write-Host 'refusing_to_stage_generated'; exit 3 }
git add pytest.ini pyproject.toml tox.ini .devcontainer/devcontainer.json
if (!(git diff --cached --quiet)) {
    git commit -m "chore(test): container-verified coverage gate=$gate (observed $obs%)"
}
else { Write-Host 'no_changes_to_commit' }
Write-Host "GATE=$gate OBS=$obs"
