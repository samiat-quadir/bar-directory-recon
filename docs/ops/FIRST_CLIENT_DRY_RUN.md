# FIRST CLIENT DRY RUN — CHECKLIST

Use this checklist to validate a first-time client setup in a safe, repeatable way.

## Pre-run

1) Create a fresh venv
```bash
python -m venv .venv
```

2) Install the exact client package
```bash
pip install "bar-directory-recon[gsheets]==<version>"
```

3) Verify CLI is available
```bash
bdr --help
```

4) Run health check (no side effects)
```bash
bdr doctor --no-exec
```

5) Verify credentials env var is set (placeholder path)
```bash
# Linux/macOS
export GOOGLE_SHEETS_CREDENTIALS_PATH="/path/to/service-account-key.json"

# Windows PowerShell
$env:GOOGLE_SHEETS_CREDENTIALS_PATH = "C:\Path\To\service-account-key.json"
```

6) Verify sheet is shared to service account email (placeholder)
- Example: `service-account@YOUR_PROJECT.iam.gserviceaccount.com` has Editor access

## Dry run

7) Run a dry-run export (non-destructive)
```bash
bdr export csv-to-sheets --csv-file <sample.csv> --sheet-id <test_sheet_id> --dry-run
```

8) If a dry-run flag is not available, use the safest non-destructive mode instead:
- Use a **test sheet** (not production)
- Use a **new worksheet name** (e.g., `dry_run_test`)
- Use `--mode append`

## Post-run

9) Confirm logs created
- If using `scripts/run_export.ps1`, logs are written to `logs/exports/<timestamp>.log`
- Otherwise, capture console output and any `logs/` artifacts

10) Confirm expected row counts / dedupe behavior (if used)
- Compare CSV row count with dry-run output

11) Capture support packet (if failure occurs)
- `bdr --version`
- `bdr doctor --no-exec` output
- Exact CLI command used (no credentials)
- CSV row count + first 2–3 header columns
- Log file(s) from `logs/` or wrapper transcript
