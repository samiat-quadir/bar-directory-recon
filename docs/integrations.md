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

### Usage

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
