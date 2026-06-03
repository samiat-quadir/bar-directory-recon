# CLAUDE.md — bar-directory-recon

Python 3.11 web scraping and data pipeline for extracting lawyer/realtor contact data from state bar and directory sites.

## Quick orientation

```
src/                    Core pipeline modules (orchestrator, extractors, PDF processor, etc.)
universal_recon/        Plugin-based multi-site scraping framework
  main.py               CLI entry point for the plugin framework
  plugins/              20+ site plugins (lawyer_directory, realtor_directory, angi, houzz, etc.)
  core/                 Config manager, snapshot archiver, batch runner
config/                 JSON configs (scraper targets, device profiles)
scripts/                Operational scripts (activate venv, format code, etc.)
plugins/                Root-level plugin adapters (collab_divorce)
tests/                  See src/tests/ and universal_recon/tests/
```

## Entry points

### 1. Unified scraper CLI (`unified_scraper.py`)
Wraps `src.orchestrator` for general scraping runs.
```bash
python unified_scraper.py --help
python unified_scraper.py --config config/lawyer_directory.json
```

### 2. Universal recon framework (`universal_recon/main.py`)
Plugin-based multi-site runner with schema validation and drift reporting.
```bash
python -m universal_recon.main --site lawyer_directory --full-report
python -m universal_recon.main --site realtor_directory --schema-collect --verbose
python -m universal_recon.main --site angi --plugin-diff --score-drift
```

## Running tests

```bash
# Full test suite with coverage
pytest src/tests universal_recon/tests

# Quick smoke (no coverage)
pytest src/tests universal_recon/tests --no-cov -q

# Single file
pytest src/tests/test_core_modules.py -v
```

Coverage gate is 20% (set in `pyproject.toml` → `--cov-fail-under=20`).

## Venv setup (Windows)

```bat
.venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

**Missing packages** (not yet installed as of 2026-06-02 — install manually):
```
pip install aiofiles==24.1.0 loguru==0.7.2 watchdog==6.0.0
```

## Key architectural notes

- **`src/` imports are relative** — scripts in `src/` use bare imports (`from config_loader import ...`). The root `conftest.py` adds `src/` to `sys.path` for pytest. When running a script directly from outside `src/`, you may need `PYTHONPATH=src python unified_scraper.py`.

- **`src/driver_setup.py`** is the Selenium WebDriver manager (renamed from `webdriver_manager.py` to avoid shadowing the `webdriver-manager` pip package). The old name is kept as a shim. Import from `driver_setup` going forward.

- **Plugin system**: plugins in `universal_recon/plugins/` implement `base.BasePlugin`. `plugin_loader.py` discovers and loads them. Add new sites by creating a new `*_plugin.py` following `example_plugin.py`.

- **Config loading**: `src/config_loader.py` reads YAML or JSON. Active site configs are in `config/lawyer_directory.json` and `config/realtor_directory.json`.

- **Notifications**: `src/notification_agent.py` sends email/SMS on pipeline completion. Credentials via `.env` (see `.env.example`).

- **Google Sheets integration**: `google_sheets_integration.py` (root) and `universal_recon/plugins/google_sheets_utils.py`. OAuth credentials must be provided via `.env` — **never commit credential JSON files**.

## Environment variables

Copy `.env.example` to `.env` and fill in:
- `GMAIL_CREDENTIALS_PATH` — path to Google OAuth credentials JSON (outside repo)
- `GMAIL_TOKEN_PATH` — OAuth token cache path
- `CHROMEDRIVER_PATH` — path to chromedriver.exe (or leave blank to use webdriver-manager auto-download)
- `GOOGLE_SHEETS_CREDENTIALS_PATH` — service account key (outside repo)

## Security notes

- `client_secret_*.json` and `service_account*.json` are gitignored — never commit them
- The OAuth client secret was previously committed in git history — rotate it at console.cloud.google.com before using in production
- Run `bandit -r src/ universal_recon/` to check for new issues

## Common tasks

| Task | Command |
|------|---------|
| Lint | `ruff check src/ universal_recon/` |
| Format | `black src/ universal_recon/` |
| Type check | `mypy src/ universal_recon/` |
| Security scan | `bandit -r src/ universal_recon/` |
| Pre-commit | `pre-commit run --all-files` |
