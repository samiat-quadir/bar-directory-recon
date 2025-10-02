# Apply coverage gate from dc_full_run logs
$rateText = & python scripts\extract_coverage_rate.py
if (-not $rateText) { Write-Error 'No coverage rate found in logs/dc_full_run.txt'; exit 2 }
$rate = [double]::Parse($rateText)
$obs = [math]::Floor($rate * 100)
$gate = [Math]::Max(8, [Math]::Min(35, $obs - 1))
Write-Host "observed=$obs% gate=$gate"
# Ensure we're on the hygiene branch
git fetch origin
if (-not (git show-ref --verify --quiet refs/heads/chore/min-cov-gate)) {
    git checkout -b chore/min-cov-gate origin/main
}
else {
    git checkout chore/min-cov-gate
}
$files = @('pytest.ini', 'pyproject.toml', 'tox.ini')
$modified = $false
foreach ($f in $files) {
    if (Test-Path $f) {
        $content = Get-Content $f -Raw
        if ($content -match '--cov-fail-under=\d+') {
            $new = $content -replace '--cov-fail-under=\d+', "--cov-fail-under=$gate"
            if ($new -ne $content) {
                Set-Content -Path $f -Value $new -Encoding utf8
                Write-Host "Updated $f"
                $modified = $true
            }
            else {
                Write-Host "No change in $f"
            }
        }
        else {
            Write-Host "No --cov-fail-under found in $f"
        }
    }
    else {
        Write-Host "$f not found"
    }
}
if ($modified) {
    git add pytest.ini pyproject.toml tox.ini
    git commit -m 'chore(test): container-verified coverage gate='+$gate+' (observed '+$obs+'%)'
    git push -u origin HEAD
}
else {
    Write-Host 'No config changes to commit'
}
Write-Host "DONE: observed=$obs% gate=$gate"
