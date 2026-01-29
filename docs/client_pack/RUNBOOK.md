# bar-directory-recon Operations Runbook

**Version**: v0.1.9  
**Audience**: Operators & DevOps teams  
**Last Updated**: 2026-01-28

This runbook covers day-to-day operations: health checks, common workflows, and expected outputs.

---

## Daily Operations

### 1. Pre-Export Health Check

**Run this every morning or before any export:**

```bash
bdr doctor --no-exec
```

**Expected Output**:
```
bdr doctor report
Version: 0.1.9
Python: 3.11.x
Platform: [your OS]
Execution: [PKG] Installed Mode (top-level imports)
no-exec: True

[OK] Core dependencies
    - OK selenium
    - OK webdriver-manager
    - OK beautifulsoul4
    ... (more dependencies)

[OK] Optional integrations
    - WARN twilio: No module named 'twilio'
    - WARN google-auth: No module named 'google'

[OK] Framework modules
    - OK src.config_loader.ConfigLoader (installed)
    ... (more modules)

[OK] Runtime smoke
    - Skipped (no-exec mode)

Overall: PASS
```

**What to check**:
- ✅ Version matches v0.1.9
- ✅ Python 3.11+
- ✅ Core dependencies all [OK]
- ✅ Overall: PASS

**If anything fails**: STOP and refer to [TROUBLESHOOTING_ONE_PAGE.md](TROUBLESHOOTING_ONE_PAGE.md).

---

### 2. Canonical Export Workflow

#### Step 1: Validate CSV

```bash
head -5 your_data.csv
```

Expected: Clean headers and data, no special characters in file path.

#### Step 2: Dry-Run (No Network)

```bash
bdr export csv-to-sheets your_data.csv --dry-run
```

**Expected Output**:
```
CSV loaded: your_data.csv (1234 rows, 8 columns)
Columns: email, name, company, phone, status, created_at, notes, verified
Worksheet target: "leads" (default)
Export mode: "append" (default)
Dedup column: None

[DRY-RUN] Would export 1234 rows to "leads" in append mode
[DRY-RUN] First 3 rows:
  Row 1: email=alice@company.com, name=Alice Smith, ...
  Row 2: email=bob@company.com, name=Bob Jones, ...
  Row 3: email=charlie@company.com, name=Charlie Brown, ...

[DRY-RUN] OK to proceed: Yes
```

**What to check**:
- ✅ Row and column counts match your CSV
- ✅ Column names parse correctly
- ✅ No encoding errors
- ✅ Sample rows look reasonable

#### Step 3: Full Export

```bash
bdr export csv-to-sheets your_data.csv \
  --sheet-id YOUR_SPREADSHEET_ID \
  --worksheet leads \
  --mode append
```

**Expected Output**:
```
[INFO] Authorizing via GOOGLE_SHEETS_CREDENTIALS_PATH...
[INFO] Connected to spreadsheet: "My Project Leads"
[INFO] Using worksheet: "leads"
[INFO] Export mode: append
[INFO] Exporting 1234 rows...
[PROGRESS] ████████████████████ 100%
[OK] Successfully exported 1234 rows to worksheet "leads"
[OK] Export complete in 12.34 seconds
```

**What to check**:
- ✅ Authorization successful
- ✅ Worksheet found
- ✅ Progress bar reaches 100%
- ✅ Row count matches input
- ✅ "Export complete" message

#### Step 4: Verify in Google Sheets

1. Open your spreadsheet: https://docs.google.com/spreadsheets/d/YOUR_SPREADSHEET_ID
2. Navigate to "leads" worksheet
3. Check:
   - ✅ New rows appended (or all replaced if mode=replace)
   - ✅ Column headers intact
   - ✅ Data visible without scrolling
   - ✅ No truncation or corruption

---

### 3. Export with Deduplication

Use when you want to avoid duplicate entries by a key field (e.g., email):

```bash
bdr export csv-to-sheets your_data.csv \
  --sheet-id YOUR_SPREADSHEET_ID \
  --dedupe-key email \
  --mode append
```

**Expected Behavior**:
- Compares CSV rows against existing sheet data by email
- Skips rows with duplicate email (already in sheet)
- Appends only new rows
- Logs: "Skipped X duplicates, imported Y new rows"

**Example**:
```
[INFO] Deduplication enabled on column: "email"
[INFO] Scanning sheet for existing emails...
[INFO] Found 500 existing emails
[INFO] Checking CSV for duplicates... 
[PROGRESS] ████████████████████ 100%
[INFO] Skipped 234 duplicates, imported 1000 new rows
[OK] Export complete
```

---

### 4. Replace Mode (Clear & Reload)

Use when you want to completely refresh the worksheet:

```bash
bdr export csv-to-sheets your_data.csv \
  --sheet-id YOUR_SPREADSHEET_ID \
  --mode replace
```

**Expected Behavior**:
- Clears ALL data from target worksheet
- Adds headers from CSV
- Adds all rows from CSV
- Useful for: rebuilding stale data, correcting corrupted sheets

**Warning**: ⚠️ This deletes existing data. Use only when you intend to refresh.

---

## Scheduled Exports (Automated)

### Windows: PowerShell Wrapper

Use `scripts/run_export.ps1` for automated daily exports:

```powershell
# First time: test the wrapper
.\scripts\run_export.ps1 -CsvPath "data.csv" -SheetId "abc123"

# Then: Create scheduled task
# Open Task Scheduler → Create Basic Task
# - Trigger: Daily at 2:00 AM
# - Action: Start a program
# - Program: C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe
# - Arguments: -ExecutionPolicy Bypass -File "C:\path\to\run_export.ps1"
```

### Linux/macOS: Bash Wrapper

Use `scripts/run_export.sh` for automated daily exports:

```bash
# First time: test the wrapper
bash scripts/run_export.sh "data.csv" "abc123"

# Then: Add to crontab
# crontab -e
# 0 2 * * * bash /path/to/run_export.sh "data.csv" "abc123" >> /var/log/bdr-export.log 2>&1
```

**What the wrapper does**:
1. Validates Python 3.11+
2. Runs `bdr doctor --no-exec`
3. Runs canonical export command
4. Logs output to file
5. Exits with status code (0=success, 1=failure)

---

## Troubleshooting Quick Paths

| Symptom | Check First |
|---------|------------|
| "No such file or directory" | Is CSV path correct? (`realpath data.csv`) |
| "Google auth failed" | Is `GOOGLE_SHEETS_CREDENTIALS_PATH` set? (`echo $GOOGLE_SHEETS_CREDENTIALS_PATH`) |
| "Worksheet not found" | Does the worksheet exist in the spreadsheet? |
| "Permission denied" | Does the service account have "Editor" role on sheet? |
| "Slow export" | Large CSV? Use sample first, then process in batches |

**Full troubleshooting**: See [TROUBLESHOOTING_ONE_PAGE.md](TROUBLESHOOTING_ONE_PAGE.md).

---

## Expected Runtimes

| Operation | Expected Duration |
|-----------|-------------------|
| `bdr doctor --no-exec` | 1–2 seconds |
| `bdr export --dry-run` (1000 rows) | 2–3 seconds |
| Full export (1000 rows) | 10–20 seconds |
| Full export (10K rows) | 60–120 seconds |

> Times vary based on Python environment and network. First run may be slower due to module loading.

---

## Health Check Frequency

| Frequency | Check | Command |
|-----------|-------|---------|
| Daily (before exports) | Doctor | `bdr doctor --no-exec` |
| Weekly | Test with sample data | `bdr export csv-to-sheets sample.csv --dry-run` |
| Monthly | Update docs/run sanity check | Review this runbook |

---

## Contact & Support

**Issue?** Use the template in [SUPPORT_TEMPLATE.md](SUPPORT_TEMPLATE.md) and include:
- Output of `bdr doctor --no-exec`
- Exact CLI command (with credentials redacted)
- CSV structure (rows, columns, size)
- Full error message

---

## Appendix: Key Commands Reference

```bash
# Health & validation
bdr doctor --no-exec                              # Full health check
bdr --help                                        # Show all commands
bdr export csv-to-sheets --help                   # Export help

# Dry-run (safe, no network)
bdr export csv-to-sheets data.csv --dry-run

# Standard export
bdr export csv-to-sheets data.csv --sheet-id ID

# With options
bdr export csv-to-sheets data.csv \
  --sheet-id ID \
  --worksheet "My Sheet" \
  --mode append \
  --dedupe-key email

# Environment variables
export GOOGLE_SHEETS_CREDENTIALS_PATH="path/to/key.json"
export GOOGLE_SHEETS_SPREADSHEET_ID="sheet_id"  # (optional, use --sheet-id instead)
```

---

_Last updated: 2026-01-28 | Version: v0.1.9_
