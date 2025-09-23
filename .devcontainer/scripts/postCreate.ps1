$ErrorActionPreference = "Stop"
Write-Host "== postCreate starting =="
python --version
python -m pip install -U pip
pip install -e .[dev]
pre-commit install
pre-commit run -a || $true
Write-Host "== postCreate complete =="