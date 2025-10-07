# Contributing

## Quickstart (Windows)
1. Clone: `git clone https://github.com/samiat-quadir/bar-directory-recon C:\Code\bar-directory-recon`
2. Create venv: `py -3.11 -m venv .venv` (or use the local junction if set)
3. Install dev deps: `.\.venv\Scripts\pip install -e .[dev]`
4. Lint/format: `.\.venv\Scripts\pre-commit run -a`
5. Fast tests: `.\.venv\Scripts\pytest -p no:cacheprovider -o addopts="" -k "not slow and not e2e and not integration" -q`

## Branch & PR

- Use small, reviewable branches; squash-merge.
- Keep secrets in env vars; never commit them.

## CI Workflow Guard Policy

### Short-Circuit Allow-List

CI workflows use guard logic to skip expensive checks on **workflow-only** changes.
Changes affecting **only** the following paths trigger a short-circuit (tests skipped):

- `.github/workflows/**`
- `.github/dependabot.yml`

All other changes run the full test suite.

### Required Status Checks

Branch protection enforces exactly **three** required checks:

1. `audit` - pip-audit security scan
2. `fast-tests (ubuntu-latest)` - Fast test suite on Ubuntu
3. `fast-tests (windows-latest)` - Fast test suite on Windows

Do **not** rename these jobs without updating branch protection settings.

## Devcontainer

- Opening in devcontainer installs deps and hooks automatically (postCreate).
