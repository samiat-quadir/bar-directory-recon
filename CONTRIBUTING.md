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

## Devcontainer
- Opening in devcontainer installs deps and hooks automatically (postCreate).
