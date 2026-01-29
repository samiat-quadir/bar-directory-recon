# bar-directory-recon Client Onboarding Checklist

**Version**: v0.1.9  
**Last Updated**: 2026-01-28

This checklist walks you through everything needed to deploy and use bar-directory-recon in your environment.

---

## Phase 1: Environment & Prerequisites

- [ ] **Python 3.11+ installed**
  ```bash
  python --version  # Should show 3.11.x or higher
  ```

- [ ] **bar-directory-recon v0.1.9 installed** (with Google Sheets support)
  ```bash
  pip install "bar-directory-recon[gsheets]==0.1.9"
  ```
  Or for latest version:
  ```bash
  pip install "bar-directory-recon[gsheets]"
  ```

- [ ] **Validate installation**
  ```bash
  bdr --help
  bdr --version
  ```

- [ ] **Run health check**
  ```bash
  bdr doctor --no-exec
  ```
  Expected output: `Overall: PASS` (core dependencies OK)

---

## Phase 2: Google Sheets Authorization

### A. Create Service Account

Follow [Google Sheets Setup Guide](../setup/gsheets.md) to:

- [ ] Create Google Cloud Project
- [ ] Enable Google Sheets API
- [ ] Create Service Account with "Editor" role
- [ ] Generate JSON key
- [ ] **Save JSON to a secure location OUTSIDE your repository**
  ```
  ✅ Good:  ~/secure/bdr-credentials.json
  ❌ Bad:   C:\project\bdr-credentials.json  (in repo)
  ```

### B. Configure Credentials Environment Variable

**Linux/macOS** (in `~/.bash_profile`, `~/.zshrc`, or `.env`):
```bash
export GOOGLE_SHEETS_CREDENTIALS_PATH="/path/to/bdr-credentials.json"
```

**Windows** (in PowerShell Profile or `.env`):
```powershell
$env:GOOGLE_SHEETS_CREDENTIALS_PATH = "C:\secure\bdr-credentials.json"
```

**Verify it's set:**
```bash
# Linux/macOS
echo $GOOGLE_SHEETS_CREDENTIALS_PATH

# Windows (PowerShell)
$env:GOOGLE_SHEETS_CREDENTIALS_PATH
```

- [ ] Credentials file path set and verified
- [ ] JSON key readable by current user
- [ ] Credentials NOT in version control
- [ ] **Share the target Google Sheet with the Service Account email (Editor access).** (This is required.)

### C. Get Spreadsheet ID

- [ ] Create or open the target Google Sheet
- [ ] Copy the Spreadsheet ID from the URL:
  ```
  https://docs.google.com/spreadsheets/d/[THIS_IS_THE_ID]/edit
  ```
- [ ] Store ID securely (or pass via CLI flag)

---

## Phase 3: Prepare Data

- [ ] **CSV file ready** for export
  - Format: standard CSV (comma-separated, UTF-8 encoding)
  - First row: column headers (required)
  - Example: `email,name,company,phone`

- [ ] **Sample data validated** (optional)
  - Use `docs/client_pack/sample_data/sample.csv` to test first
  - Confirm export works before using production data

---

## Phase 4: Configure Export Options

- [ ] **Choose export mode**:
  - `--mode append` (default): Add rows to existing sheet
  - `--mode replace`: Clear sheet first, then add rows
**Mode safety:**
- `append` (recommended): adds/updates rows without clearing the sheet
- `replace` (destructive): clears the target worksheet before writing new rows


- [ ] **Choose target worksheet** (if not using "leads")
  - Default worksheet: `leads`
  - Override: `--worksheet "My Sheet Name"`

- [ ] **Optional: Set deduplication column**
  - Example: `--dedupe-key email` (removes duplicate emails)
  - Leave blank if no deduplication needed

---:
```bash
bdr export csv-to-sheets your_data.csv --dry-run
```
Note: --dry-run does not write to Google Sheets. Depending on configuration, it may still validate inputs and/or credentials.
**Dry-run first** (no network calls):
```bash
bdr export csv-to-sheets your_data.csv --dry-run
```

**Full export**:
```bash
bdr export csv-to-sheets your_data.csv \
  --sheet-id YOUR_SPREADSHEET_ID \
  --worksheet leads \
  --mode append
```

**With deduplication**:
```bash
bdr export csv-to-sheets your_data.csv \
  --sheet-id YOUR_SPREADSHEET_ID \
  --dedupe-key email \
  --mode append
```

- [ ] Dry-run succeeds without errors
- [ ] Review dry-run output
- [ ] Full export completes successfully
- [ ] Confirm data appears in Google Sheets

---

## Phase 6: Verify Success

- [ ] Data visible in target worksheet
- [ ] Row count matches expected
- [ ] Column headers preserved
- [ ] No truncation or encoding issues
- [ ] Dedupe applied correctly (if used)

---

## Phase 7: Set Up Recurring Exports (Optional)

### Windows Task Scheduler

Use `scripts/run_export.ps1` wrapper for automation:

```powershell
# Test the wrapper
.\scripts\run_export.ps1 -CsvPath "your_data.csv" -SheetId "YOUR_ID"

# Schedule via Task Scheduler
# Create task to run hourly/daily
```

### Linux/macOS Cron

Use `scripts/run_export.sh` wrapper:

```bash
# Test the wrapper
bash scripts/run_export.sh "your_data.csv" "YOUR_ID"

# Add to crontab for daily 2am export
0 2 * * * bash /path/to/scripts/run_export.sh "data.csv" "ID" >> export.log 2>&1
```

- [ ] Wrapper script tested (optional)
- [ ] Scheduled task created (optional)
- [ ] Log file location confirmed

---

## Troubleshooting

Encounter an issue? See [TROUBLESHOOTING_ONE_PAGE.md](TROUBLESHOOTING_ONE_PAGE.md) for common problems and solutions.

Need support? Use the template in [SUPPORT_TEMPLATE.md](SUPPORT_TEMPLATE.md) to report issues effectively.

---

## What to Provide to the bdr Team

When opening a support issue, gather:

```
✅ Python version:                 python --version
✅ bdr version:                    bdr --version
✅ Doctor output:                  bdr doctor --no-exec
✅ CLI command used:               (exact command, hide credentials)
✅ CSV file size & row count:      (approx, first few rows structure)
✅ Error message:                  (full stderr output)
✅ OS & shell:                     (Windows/Linux/macOS, PowerShell/bash)
✅ Credentials validation:         (can Python import google auth modules?)
```

See [SUPPORT_TEMPLATE.md](SUPPORT_TEMPLATE.md) for the full template.

---

## Checklist Summary

**Total Steps**: 30+  
**Time Estimate**: 15–30 minutes (depending on Google Sheets setup speed)

### Quick Path (Sample Data Only)
If you just want to test:
1. Install bdr (Phase 1)
2. Set up credentials (Phase 2)
3. Run dry-run with sample data (Phase 5)
4. Confirm output (Phase 6)

### Production Path
Complete all 7 phases before scheduling exports.

---

## Next Steps

- ✅ **Completed onboarding?** → Move to [RUNBOOK.md](RUNBOOK.md) for day-to-day operations
- ❓ **Issues?** → Check [TROUBLESHOOTING_ONE_PAGE.md](TROUBLESHOOTING_ONE_PAGE.md)
- 🆘 **Need help?** → Use [SUPPORT_TEMPLATE.md](SUPPORT_TEMPLATE.md) to report

---

_Questions? Refer to [START_HERE.md](../START_HERE.md) or [RUNBOOK.md](RUNBOOK.md)._
