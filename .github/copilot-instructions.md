# Copilot Instructions for `bar-directory-recon`

## Commands

### Environment setup
```powershell
.venv\Scripts\activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### Main entry points
```powershell
# Classic config-driven scraper
python unified_scraper.py --config config\lawyer_directory.json

# Plugin/analytics runner
python -m universal_recon.main --site lawyer_directory --full-report
python -m universal_recon.main --site realtor_directory --schema-collect --verbose
```

### Tests
```powershell
# Main coverage-bearing suites
pytest src/tests universal_recon/tests

# Quick smoke without coverage overhead
pytest src/tests universal_recon/tests --no-cov -q

# Top-level tests suite (this is what pytest.ini points at by default)
pytest tests -q

# Single file
pytest src/tests/test_core_modules.py -v
pytest universal_recon/tests/targeted/test_plugin_loader.py -q
pytest tests/plugins/test_plugin_discovery.py -q

# Single test
pytest src/tests/test_core_modules.py::TestConfigLoader::test_load_config_from_json_file -q
```

### Lint / format / type check / security
```powershell
ruff check src universal_recon
ruff format src universal_recon
mypy src universal_recon
bandit -r src universal_recon
pre-commit run --all-files
```

### MCP
This repository includes a repo-scoped Playwright MCP server in `.vscode\mcp.json`. Use it for browser-driven debugging, DOM inspection, and test scaffolding when a task requires interacting with real pages; keep the production scraping code on its existing Selenium/config-driven path unless the task explicitly changes runtime automation.

## High-level architecture

This repository has **two main execution paths**:

1. **Config-driven scraper pipeline in `src/`**
   - `unified_scraper.py` is the user-facing CLI for the classic scraper flow.
   - `src/orchestrator.py` coordinates the run: it loads a site config, initializes the webdriver/pagination/extraction components, runs a **listing phase -> detail phase** crawl when enabled, then cleans, validates, and exports records.
   - `src/config_loader.py` defines the required config shape. Active site configs such as `config\lawyer_directory.json` and `config\realtor_directory.json` describe selectors, pagination behavior, required fields, output settings, and runtime options.

2. **Plugin/analytics framework in `universal_recon/`**
   - `python -m universal_recon.main --site <site>` is the CLI entry point for plugin-driven analytics and reporting.
   - `universal_recon\main.py` dispatches flags for schema collection, drift/risk analysis, full reports, and a special realtor-directory scrape path.
   - `universal_recon\plugin_loader.py` reads normalized records from `output\fieldmap\<site>_fieldmap.json`.
   - `universal_recon\plugin_aggregator.py`, `universal_recon\core\multisite_config_manager.py`, and `universal_recon\core\snapshot_manager.py` assemble reports and archive schema-matrix snapshots under `output\reports` and `output\archive`.

## Key conventions

- **`src/` uses bare imports on purpose.** Modules there import siblings like `from config_loader import ...` rather than `from src.config_loader import ...`. Test bootstrap relies on `conftest.py` adding `src` to `sys.path`.

- **Use `driver_setup`, not `webdriver_manager`, for new imports.** `src\webdriver_manager.py` is a compatibility shim; `src\driver_setup.py` is the real module name.

- **Scraper configs are schema-shaped, not ad hoc dicts.** New configs should preserve the existing top-level sections:
  `name`, `description`, `base_url`, `listing_phase`, `detail_phase`, `pagination`, `data_extraction`, `output`, and `options`.

- **Universal Recon plugins are discovery-driven.** Add new plugins under `universal_recon\plugins`. Dynamic loading comes from `universal_recon\plugins\loader.py`, while registry-driven flows consult `plugin_registry.json`. Keep plugin modules import-safe; tests exercise plugin discovery without requiring heavy runtime dependencies.

- **Pytest behavior depends on which config you are following.**
  - `pyproject.toml` defines coverage-oriented runs for `src/tests` and `universal_recon/tests`.
  - `pytest.ini` points default `pytest` execution at top-level `tests` and excludes `slow`, `e2e`, and `integration`.
  When you need a specific suite, pass explicit paths instead of relying on bare `pytest`.

- **Follow the repo's contribution workflow conventions.** Branches are expected to use `feat/*`, `fix/*`, or `chore/*`. PRs are expected to open as Draft, include a one-line `SUMMARY >> ...`, and keep CI green.

- **Tests should stay deterministic and offline.** `CONTRIBUTING.md` explicitly prefers unit-level seams, no network dependency in tests, and cleanup of temporary files/artifacts.

- **Environment loading is device-aware.** Prefer `env_loader.py` when touching runtime setup. It selects from `.env`, `.env.work`, `.env.asus`, `.env.alienware`, and related variants based on the machine profile.

- **Playwright MCP is for Copilot assistance, not the scraper runtime.** The repository now exposes Playwright as an MCP tool through `.vscode\mcp.json`, but the scraper implementation itself still centers on `src\driver_setup.py`, Selenium-style flows, and config-driven extraction.

- **Keep credentials outside the repository.** Google OAuth and service-account paths are expected to come from environment variables such as `GMAIL_CREDENTIALS_PATH` and `GOOGLE_SHEETS_CREDENTIALS_PATH`; do not add credential JSON files to the repo.
