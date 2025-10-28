set -uo pipefail
# prep
bash .devcontainer/setup.sh || true
pip install -r requirements-dev.txt -q || true
pip install -e .[dev] -q || true
# switch to PR head
set +e
git fetch origin 'fix-line-endings' --depth=1 2>/dev/null
git checkout 'fix-line-endings' 2>/dev/null || git checkout -B pr-by-sha '1d6df4f199b22418d9cc227bb968f7ba7c6c0cef'  # pragma: allowlist secret
# smoke (no cacheprovider, no inherited addopts)
pytest -p no:cacheprovider -o addopts="" -q --maxfail=1 universal_recon/tests tests -k "not slow and not e2e and not integration" > /tmp/pytest_smoke.txt 2>&1
code=$?
set -e
tail -n 20 /tmp/pytest_smoke.txt || true
echo "RUN_EXIT=$code"
