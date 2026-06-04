# Integrations

This document describes integration tiers for Bar Directory Recon.

## Quickstart: Google Sheets Export

Google Sheets is an **optional dependency** — the core library works without it.

### Installation

```bash
# Install with Google Sheets support
pip install .[gsheets]

# Or install dependencies directly
pip install google-api-python-client google-auth google-auth-oauthlib gspread
```

### Configuration

Set the following environment variables:

```bash
# Path to service account JSON credentials
export GOOGLE_SHEETS_CREDENTIALS_PATH=/path/to/service-account.json

# Destination spreadsheet ID (from the URL)
export GOOGLE_SHEETS_SPREADSHEET_ID=1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms
```

### CLI Usage

The exporter can be run as a module:

```bash
# Show help
python -m tools.gsheets_exporter --help

# Check if dependencies are installed
python -m tools.gsheets_exporter --check

# One-command demo: export 1 test row to configured sheet
python -m tools.gsheets_exporter --demo

# Dry-run demo (no network, no credentials required)
python -m tools.gsheets_exporter --demo --dry-run

# Export custom data
python -m tools.gsheets_exporter --worksheet "Sheet1" --data '[["Name", "Email"], ["John", "john@example.com"]]'
```

### CSV Import

Export a local CSV file directly to Google Sheets:

```bash
# Basic CSV import (appends to worksheet)
python -m tools.gsheets_exporter --csv path/to/leads.csv --worksheet "leads"

# Replace mode (clears worksheet first)
python -m tools.gsheets_exporter --csv path/to/leads.csv --worksheet "leads" --mode replace

# Deduplicate by email before importing
python -m tools.gsheets_exporter --csv path/to/leads.csv --worksheet "leads" --dedupe-key email

# Dry-run to preview without writing
python -m tools.gsheets_exporter --csv path/to/leads.csv --worksheet "leads" --dry-run
```

A sample CSV is provided at `docs/examples/sample_leads.csv`:

```csv
name,email,firm,city,state,bar_number
John Doe,john.doe@lawfirm.com,Doe & Associates,New York,NY,NY123456
...
```

### One-Command Demo (PowerShell)

For the fastest setup, use the provided demo script:

```powershell
# 1. Create .env.local with your credentials
# GOOGLE_SHEETS_CREDENTIALS_PATH=C:\path\to\service-account.json
# GOOGLE_SHEETS_SPREADSHEET_ID=your-spreadsheet-id

# 2. Run the demo script (activates venv, loads env, exports demo row)
.\scripts\gsheets-demo.ps1

# Or specify a different worksheet
.\scripts\gsheets-demo.ps1 -Worksheet "Sheet1"

# Dry-run mode (no network calls)
.\scripts\gsheets-demo.ps1 -DryRun
```

The demo script will:

1. Activate the `.venv` virtual environment
2. Load environment variables from `.env.local`
3. Check that gsheets dependencies are installed
4. List available worksheets in your spreadsheet
5. Export a demo row (timestamp + run_id) to the "leads" worksheet

### Python Usage

```python
from tools.gsheets_exporter import is_gsheets_available, export_rows

if is_gsheets_available():
    export_rows([{"name": "John Doe", "email": "john@example.com"}])
else:
    print("Google Sheets not installed. Run: pip install .[gsheets]")
```

---

## Tier0 — No external APIs

- Runs entirely locally with no external API dependencies.
- Suitable for offline audits, manual CSV exports, or local-only tooling.

## Tier1 — Sheets-first (Recommended minimal integration)

- Primary integration: Google Sheets export. Minimal required env variables:
  - `GOOGLE_SHEETS_CREDENTIALS_PATH` — path to service account JSON credentials
  - `GOOGLE_SHEETS_SPREADSHEET_ID` — destination spreadsheet ID
  - `BDR_ADAPTER_METRICS` — enable (1) or disable (0) adapter metrics
- Tier1 enables lightweight sharing and downstream analysis without provisioning full API integrations.

## Optional Integrations

- `SLACK_WEBHOOK_URL` — optional Slack incoming webhook for alerts. Treated as optional and not required for Tier1.

## Security Guidance

- Do not commit secrets. Keep secrets out of Git and use environment variables or secret stores.
- The repository `.gitignore` intentionally ignores `*.env` and `.env.*` while allowing `.env.example` as a template.

## Migration Path

- Start at Tier0 for offline/manual runs.
- Move to Tier1 to enable automated exports to Google Sheets.
- Add optional alerting (Slack) only after Tier1 is working and credentials are secured.
