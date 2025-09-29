# Finalize attic: ensure venv and run fast tests; write rc to rc_finalize.txt
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
# Run pre-commit (do not fail the script if hooks return non-zero)
try { .\.venv\Scripts\python -m pre_commit run -a } catch { Write-Output "pre-commit returned non-zero" }
# Run quick pytest suite
& .\.venv\Scripts\python -m pytest -q -m "not slow and not e2e and not integration"
$rc = $LASTEXITCODE
Set-Content -Path rc_finalize.txt -Value $rc -Encoding utf8
Write-Output "TEST_RC=$rc"
exit $rc
