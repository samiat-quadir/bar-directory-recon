# Setup venv if missing, install dependencies, run pre-commit and pytest with coverage, record rc and pct
Set-Location 'C:\Code\bar-directory-recon'
if(-not (Test-Path .venv)){
  py -3.11 -m venv .venv
}
.\.venv\Scripts\python -m pip install -U pip
if(Test-Path requirements-lock.txt){
  .\.venv\Scripts\python -m pip install -r requirements-lock.txt
  .\.venv\Scripts\python -m pip install -e .[dev] --no-deps
} else {
  .\.venv\Scripts\python -m pip install -e .[dev]
}
# Run pre-commit but don't fail the run if it returns non-zero
try { .\.venv\Scripts\python -m pre_commit run -a } catch { Write-Output "pre-commit failed: $($_)" }
# Run pytest and capture exit code
$pytestCmd = { .\.venv\Scripts\python -m pytest --cov=. --cov-report=xml --cov-report=term -m "not slow and not e2e and not integration" }
& $pytestCmd
$pyExit = $LASTEXITCODE
# record rc
Set-Content -Path rc.txt -Value $pyExit -Encoding utf8
# parse coverage.xml
if(Test-Path 'coverage.xml'){
  $xml = [xml](Get-Content coverage.xml)
  $lineRate = [double]$xml.coverage.'line-rate'
  $pct = [math]::Round($lineRate*100,2)
  Set-Content -Path pct.txt -Value $pct -Encoding utf8
} else {
  Set-Content -Path pct.txt -Value 0 -Encoding utf8
}
exit $pyExit
