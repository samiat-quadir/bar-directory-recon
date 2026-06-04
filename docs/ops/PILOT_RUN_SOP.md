# Pilot Run SOP

**Standard Operating Procedure for bar-directory-recon Pilot Integration**

**Last Updated**: 2026-02-03  
**Version**: v0.1.13

---

## Overview

This SOP guides pilot clients through a controlled integration of **bar-directory-recon** with their data pipeline. The goal is to safely export directory data to Google Sheets with verification checkpoints before any production use.

---

## Pre-Run: What You'll Need

### From Your Side
- **CSV data file** (standard format: headers + rows)
- **Google Sheet URL or Sheet ID** (the target destination)
- **Deduplication key** (column name or "none" if all rows unique)
- **Mode choice** (see below):
  - `append` (recommended for pilot): Add rows to existing sheet
  - `replace` (destructive): Clear sheet and reload all data
  - `safe-mode` (experimental): Dry-run with report, no write
- **Refresh cadence** (if periodic): daily / weekly / monthly / ad-hoc

### From Us
- **Installation**: See [docs/START_HERE.md](../START_HERE.md)
- **Credentials setup**: See docs/setup/gsheets.md
- **Commands reference**: See docs/usage/csv-to-sheets.md

---

## Defaults & Recommendations

| Setting | Default | Pilot Recommendation | Notes |
|---------|---------|----------------------|-------|
| **Mode** | `append` | `append` | Safe; new rows added only |
| **Dedupe** | Check source | Use your key column | Avoids duplicate rows on re-run |
| **Refresh** | Manual | Ad-hoc (testing) | Automate after validation |
| **Dry-run** | Off | Run first (safe-mode) | Preview results before commit |
| **Error handling** | Fail-fast | Capture + report | See "Support packet" section |

---

## Step-by-Step Run Order

### Phase 1: Verify Installation (5–10 min)

**1.1 Install from GitHub Release Wheel**
```bash
pip install https://github.com/samiat-quadir/bar-directory-recon/releases/download/v0.1.13/bar_directory_recon-0.1.13-py3-none-any.whl
```

**1.2 Set Environment Variable** (your service account key)
```bash
# Windows (CMD or PowerShell):
set GOOGLE_SHEETS_CREDENTIALS_PATH=C:\path\to\service-account-key.json

# Linux/macOS (bash/zsh):
export GOOGLE_SHEETS_CREDENTIALS_PATH=/path/to/service-account-key.json
```

**1.3 Run Doctor Diagnostic** (no credentials read yet)
```bash
bdr doctor --no-exec
```
**Expected output**:
```
Overall: PASS
...
```

---

### Phase 2: Prepare Your Data (10–15 min)

**2.1 Verify CSV format**
- Headers in first row (case-insensitive)
- No missing cells or encoding issues
- Sample command to inspect:
  ```bash
  head -5 your_data.csv
  ```

**2.2 Create Google Sheet** (or use existing)
- New sheet: Go to [sheets.google.com](https://sheets.google.com)
- Note the **Sheet ID** (from URL: `docs.google.com/spreadsheets/d/{SHEET_ID}/edit`)
- Share with your service account email (from service-account-key.json)

**2.3 Choose deduplication key**
- Example: If CSV has `id` column and you want to avoid duplicates on re-run, use `--dedupe-key id`
- If rows are unique, use `--dedupe-key none`

---

### Phase 3: Dry-Run (Safe Mode) (10 min)

**3.1 Preview without writing**
```bash
bdr export csv-to-sheets your_data.csv \
  --sheet-id YOUR_SHEET_ID \
  --dedupe-key your_key_column \
  --safe-mode
```

**3.2 Review report output**
- Check row counts, columns matched, preview of data shape
- Verify no credential errors or auth issues
- **If errors occur**, proceed to "Support packet" section below

---

### Phase 4: First Export (Append Mode) (5 min)

**4.1 Run with append (recommended for pilot)**
```bash
bdr export csv-to-sheets your_data.csv \
  --sheet-id YOUR_SHEET_ID \
  --dedupe-key your_key_column \
  --mode append
```

**4.2 Verify in Google Sheets**
- Open the Sheet in browser
- Check row counts match expected
- Spot-check a few rows for accuracy
- Take a screenshot for records

---

### Phase 5: Validation & Sign-Off (10 min)

**5.1 Data quality checks**
- [ ] All expected columns present
- [ ] No truncation or encoding artifacts
- [ ] Row count >= CSV row count (may vary with dedupe)
- [ ] No blank cells where data expected

**5.2 Performance notes**
- Command runtime (should be < 30s for typical data)
- Any warnings in console output (log them below)

**5.3 Sign-off template** (via email or issue reply)
```
✅ Pilot validation complete:
- Data file: [filename]
- Sheet ID: [redacted]
- Rows uploaded: [count]
- Mode: append
- Dedup key: [column]
- Issues: None / [list any]
- Next steps: Move to [daily/weekly] sync via [method]
```

---

## Support Packet

If issues arise, gather this info **before** contacting support:

### Command & Environment
```bash
# Show your command (safe; no secrets):
echo "Command used: bdr export csv-to-sheets ... [exact flags]"

# Python version:
python --version

# Installed version:
bdr --version

# OS:
uname -a  # Linux/macOS
ver       # Windows (cmd)
```

### Error Output
- **Full error message**: Copy from console (sanitize sheet IDs if sensitive)
- **Log file path**: Usually in `.bdr/logs/` or specified via `--log-path`
- **Log snippet**: Last 20–30 lines of error context
  ```bash
  tail -30 ~/.bdr/logs/export.log
  ```

### Data Sample (if safe)
- **CSV header row**: `head -1 your_data.csv`
- **CSV row count**: `wc -l your_data.csv` (Linux/macOS) or PowerShell Get-Content + Measure-Object
- **Sample problematic row** (if applicable): Copy a row that caused error

### Example Support Packet
```
[Support Request]
Command: bdr export csv-to-sheets locations.csv --sheet-id abc123... --dedupe-key id --mode append
Python: 3.11.8
bdr version: 0.1.13
OS: Windows 11

Error:
  AuthError: Invalid credentials in GOOGLE_SHEETS_CREDENTIALS_PATH
  File: /Users/pilot/.../service-account-key.json

CSV sample:
  id,name,city
  1,Acme Corp,NYC
  2,Beta Inc,LA

Suggested next: Verify service account has Editor access to Sheet
```

---

## Next Steps After Validation

1. **Schedule automation** (if approved):
   - Daily: Use task scheduler / cron job to run export at fixed time
   - Weekly: Similar, with `-frequency weekly` flag (if supported)
   - Ad-hoc: Manual command as needed

2. **Monitor & alert** (optional):
   - Log failures to Slack / email (via wrapper script)
   - Track row counts week-over-week for anomalies

3. **Scale to production** (after sign-off):
   - Widen scope to more CSV files
   - Automate with error handling / retry logic
   - Archive old reports for compliance

---

## Troubleshooting Quick Reference

| Symptom | Likely Cause | Action |
|---------|--------------|--------|
| `AuthError` during export | Invalid credentials or no Editor access | Verify service account email added to Sheet; re-download key from GCP Console |
| `FileNotFoundError: your_data.csv` | CSV path or credentials file wrong | Check working directory; use absolute paths |
| Rows not uploaded but no error | Dedup key removed all rows | Use `--dedupe-key none` or verify key column exists |
| Google Sheets shows old data | Used `--mode replace` by mistake | Undo in Sheets (Ctrl+Z) or restore from backup |
| Command hangs for > 1 min | Large file or network latency | Use `--timeout 120` flag or check internet connection |

---

## Appendix: Sample Full Command

```bash
bdr export csv-to-sheets \
  locations_2026_02.csv \
  --sheet-id "1ABC2DEF3GHI4JKL5MNO6PQR7STU8VWX9YZ" \ # pragma: allowlist secret
  --dedupe-key "location_id" \
  --mode append \
  --no-confirm \
  --log-path ./export_log_2026_02_03.txt
```

---

## Questions or Issues?

- **Check docs**: [docs/usage/csv-to-sheets.md](../usage/csv-to-sheets.md)
- **Open issue**: Include support packet details
- **Contact**: See repository CONTRIBUTING.md
