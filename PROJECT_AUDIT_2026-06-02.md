# bar-directory-recon — Project Audit
**Date:** 2026-06-02  
**Python target:** 3.11.9 | **pip:** 26.1.2 | **Package version:** 0.1.3.dev0

---

## 1. Project Health Check

### Structure overview

| Area | Status |
|------|--------|
| `src/` — core pipeline modules | ✅ Present, organized |
| `universal_recon/` — plugin/scraper framework | ✅ Present, organized |
| `tests/` (in `src/tests/` and `universal_recon/tests/`) | ✅ Present |
| `config/` | ✅ Present |
| `scripts/` | ⚠️ 70+ scripts, mostly ops/SSH/Codespaces cruft |
| Root directory | 🔴 **Severely bloated** — 150+ loose files |
| `plugins/` at root | ⚠️ Only contains `collab_divorce/` adapter; real plugins live in `universal_recon/plugins/` |

### Root directory problem
The repo root has accumulated ~150+ files that don't belong there: phase-completion reports (`PHASE29_COMPLETION_SUMMARY.md`, etc.), Alienware/ASUS SSH diagnostics, device sync logs (`onedrive_check.txt`, `pip_freeze.txt`), personal PDFs, `.ps1` PowerShell scripts, and dozens of one-off Python scripts (`verify_bootstrap_bundle.py`, `create_tree.py`, etc.). This makes the actual project nearly invisible at a glance.

### Missing CLAUDE.md
No `CLAUDE.md` exists. Given the complexity of the codebase, this would be valuable for orienting future AI-assisted work.

---

## 2. Venv & Dependencies

### Venv health
The `.venv` is a Windows venv (Python 3.11.9) and cannot be directly interrogated from Linux, but `pip_freeze.txt` (committed to the repo) gives a full picture. The venv has **185 packages** installed.

### Requirements gaps
Five packages in `requirements.txt` are **missing from the installed venv** (based on pip_freeze.txt):

| Package | Status |
|---------|--------|
| `aiofiles==24.1.0` | Not installed |
| `jinja2==3.1.5` | Installed as `Jinja2==3.1.6` (case + minor version mismatch) |
| `loguru==0.7.2` | Not installed |
| `pyyaml==6.0.2` | Installed as `PyYAML==6.0.2` (case only — functionally fine) |
| `watchdog==6.0.0` | Not installed |

`aiofiles` and `loguru` are imported by core `src/` modules — their absence will cause `ImportError` at runtime. Run:
```
.venv\Scripts\pip install aiofiles==24.1.0 loguru==0.7.2 watchdog==6.0.0
```

### device_profile.json python_path mismatch (FIXED)
`config/device_profile.json` pointed to `Python313` — corrected to `Python311` to match the active venv.

### requirements-dev.txt duplicate (FIXED)
`watchdog`/`watchfiles` conditional markers were duplicated (lines 7–8 and 29–30). Removed the duplicate block.

---

## 3. Code Inventory

### `src/` — Core pipeline modules (ACTIVE)

| File | Purpose |
|------|---------|
| `orchestrator.py` | Main scraping orchestrator — coordinates all scraping ops |
| `config_loader.py` | Loads YAML/JSON config, dataclass-based |
| `data_extractor.py` | BS4 + Selenium DOM extraction |
| `data_hunter.py` | Automated property list discovery from municipal sites |
| `hallandale_pipeline.py` | Full Hallandale PDF → enrichment pipeline |
| `hallandale_pipeline_fixed.py` | Patched version of above (duplicate — should be merged or deleted) |
| `pdf_processor.py` | PDF parsing for property data |
| `property_enrichment.py` | Enriches extracted records |
| `property_validation.py` | Validates enriched records |
| `pagination_manager.py` | Handles paginated scraping |
| `webdriver_manager.py` | Selenium WebDriver setup (local, shadows the pip package name) |
| `unified_schema.py` | Canonical field schema / mapper |
| `logger.py` | Structured logging wrapper |
| `notification_agent.py` | Email/SMS notification dispatching |
| `security_manager.py` | Credential/secret handling |
| `security_audit.py` | Bandit-based audit helpers |
| `ut_bar.py` | Utility functions for bar directory scraping |
| `refactored_scraping_orchestrator.py` | Appears to be a WIP refactor of orchestrator — unclear if active |

### `universal_recon/` — Plugin framework (ACTIVE)

| Area | Purpose |
|------|---------|
| `main.py` | CLI entry point — `--site`, `--schema-collect`, `--full-report`, etc. |
| `core/` | Config manager, snapshot archiver, batch runner, report printer |
| `plugin_loader.py` | Loads normalized records from plugins |
| `plugin_aggregator.py` | Aggregates multi-plugin results |
| `scrapers/realtor_directory_scraper.py` | Realtor-specific scraper |
| `plugins/` | 20+ site plugins: `lawyer_directory_plugin.py`, `realtor_directory_plugin.py`, `angi_plugin.py`, `homeadvisor_plugin.py`, `houzz_plugin.py`, `thumbtack_plugin.py`, etc. |

### `unified_scraper.py` (root) — ACTIVE CLI entry point
Wraps `src.orchestrator` and provides the main command-line interface for the scraping framework.

### Root-level Python scripts — MOSTLY STALE/EXPERIMENTAL

These do not belong at the root and should be archived or deleted:

| Category | Examples |
|----------|---------|
| Device bootstrap/validation | `validate_alienware_bootstrap.py`, `verify_bootstrap_bundle.py`, `create_bootstrap_bundle*.py` |
| One-off demos | `async_pipeline_demo.py`, `automation_demo.py`, `usage_demo.py`, `demo_google_sheets.py` |
| Duplicate pipeline runners | `final_hallandale_pipeline.py`, `local_test_hallandale_pipeline.py`, `simple_enhanced_processing.py` |
| Verification/check scripts | `complete_installation_check.py`, `finalize_verification.py`, `setup_check.py`, `verify_dependencies.py` |
| Git/notifier helpers | `auto_git_commit.py`, `git_commit_and_notify_asus.py`, `notify_agent.alienware.py`, `notify_agent.asus.py` |
| Potentially useful | `score_leads.py`, `lead_enrichment_plugin.py`, `realtor_automation.py`, `google_sheets_integration.py` |

---

## 4. Issues Fixed This Session

| Issue | Fix Applied |
|-------|------------|
| `config/device_profile.json` pointed to Python 3.13 | Updated `python_path` to `Python311` |
| `requirements-dev.txt` had duplicate watchdog/watchfiles lines | Removed duplicate block |
| `client_secret*.json` not in `.gitignore` (OAuth credential committed to git) | Added `client_secret*.json`, `service_account*.json`, `*credentials*.json`, `token.json` to `.gitignore` |

---

## 5. Outstanding Issues (Not Auto-Fixed)

### 🔴 Critical

**OAuth credential in git history**  
`client_secret_1020100796152-...json` is tracked in git and has been committed in at least 5 previous commits. The file is now gitignored but it's still in history. You should rotate this credential in Google Cloud Console immediately, then optionally scrub history with `git filter-repo`.

**`authorized_keys.seed` committed to git**  
SSH public keys shouldn't be in the repo. Add to `.gitignore` and remove from tracking.

**`aiofiles` and `loguru` not installed**  
These are imported by core `src/` modules. Will cause `ImportError` on first run. Install them:
```
.venv\Scripts\pip install aiofiles==24.1.0 loguru==0.7.2 watchdog==6.0.0
```

### 🟡 Important

**`src/webdriver_manager.py` shadows the pip package**  
The local `src/webdriver_manager.py` has the same name as the `webdriver-manager` PyPI package. The orchestrator handles this with a defensive try/except but it's fragile. Rename the local module (e.g., `src/driver_setup.py`).

**`src/hallandale_pipeline_fixed.py` is a duplicate**  
It's nearly identical to `hallandale_pipeline.py`. Either merge the fix into the original and delete `_fixed`, or rename it clearly.

**`refactored_scraping_orchestrator.py` in `src/` — unclear status**  
No tests reference it. Determine if it replaces `orchestrator.py` or is abandoned.

**`config/device_profile.json` has `python_path` hardcoded**  
Even after fixing `313 → 311`, this assumes a specific Windows install path. The `config_loader.py` should use `sys.executable` or fall back gracefully.

**Root-level clutter prevents clean `git status`**  
~50+ diagnostic/report markdown files and one-off scripts at root make the repo very hard to navigate. These should be moved to `archive/` or deleted.

**`.env` contains hardcoded paths**  
`GMAIL_CREDENTIALS_PATH`, `CHROMEDRIVER_PATH`, etc. point to absolute Windows paths. These should be relative or use `~` expansion.

### 🟢 Low priority

- `requirements-dev.txt` pins `black==23.9.1` and `flake8==6.1.0` but `pip_freeze.txt` shows newer versions. Align or loosen pins.
- `.pytest_tmp/` test artifacts are tracked in git — add to `.gitignore`.
- `copilot_context.json` and several `sync_data_*.txt` files are committed but are clearly machine-generated state.
- 1,086 tracked files is high for this project scope; a targeted cleanup pass would reduce noise significantly.

---

## 6. Recommended Next Steps (Prioritized)

### P0 — Do immediately
1. **Rotate the Google OAuth client secret** in Google Cloud Console — the current one is in git history and must be considered compromised. Download a new one and store it outside the repo.
2. **Install missing packages**: `pip install aiofiles==24.1.0 loguru==0.7.2 watchdog==6.0.0`

### P1 — Before next commit
3. **Remove tracked sensitive files**: `git rm --cached client_secret_*.json authorized_keys.seed` then commit.
4. **Rename `src/webdriver_manager.py`** to `src/driver_setup.py` and update imports in `orchestrator.py`.
5. **Delete or merge `src/hallandale_pipeline_fixed.py`** into the original.

### P2 — Clean up
6. **Archive root clutter**: Move all `PHASE*`, `ALIENWARE_*`, `ASUS_*`, `ALI_*`, `SSH_*`, `BOOTSTRAP_*` markdown files and one-off `.py` scripts to `archive/` or delete them.
7. **Add `CLAUDE.md`** documenting the two main entry points (`unified_scraper.py` CLI and `universal_recon/main.py`), the plugin system, and how to run tests.
8. **Add missing items to `.gitignore`**: `.pytest_tmp/`, `pip_freeze.txt`, `venv_*.txt`, `*_tree_*.txt`, `diagnostic_*.txt`, `copilot_context.json`, `sync_data_*.txt`.

### P3 — Code quality
9. **Run `pytest`** and confirm the 20% coverage gate passes cleanly.
10. **Resolve `refactored_scraping_orchestrator.py`** — integrate or delete.
11. **Parameterize hardcoded paths** in `.env` using `pathlib.Path.home()` expansion.
