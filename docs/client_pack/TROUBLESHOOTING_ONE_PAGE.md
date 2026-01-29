# Troubleshooting One-Page Guide

**Quick Diagnosis**: Run `bdr doctor --no-exec` before checking below.

---

## Installation & Setup

### ❌ "command not found: bdr"

**Causes**: Python not on PATH, package not installed  
**Fix**:
```bash
# Check installation
pip show bar-directory-recon

# Reinstall
pip uninstall bar-directory-recon && pip install bar-directory-recon==0.1.9

# Verify
bdr --version
```

### ❌ "Python 3.11+ required"

**Cause**: Python version too old  
**Fix**:
```bash
# Check version
python --version  # Must be 3.11+

# Install Python 3.11+
# Windows: https://python.org (select 3.11.x)
# macOS: brew install python@3.11
# Linux: apt install python3.11
```

---

## Google Sheets Authorization

### ❌ "No module named 'google'"

**Cause**: Google auth libraries not installed  
**Fix**:
```bash
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### ❌ "GOOGLE_SHEETS_CREDENTIALS_PATH environment variable not found"

**Cause**: Path not set, or wrong variable name  
**Fix**:

**Check if set:**
```bash
# Linux/macOS
echo $GOOGLE_SHEETS_CREDENTIALS_PATH

# Windows PowerShell
$env:GOOGLE_SHEETS_CREDENTIALS_PATH
```

**Set it (Linux/macOS)**:
```bash
export GOOGLE_SHEETS_CREDENTIALS_PATH="/path/to/credentials.json"
# Make permanent: add to ~/.bash_profile or ~/.zshrc
```

**Set it (Windows PowerShell)**:
```powershell
$env:GOOGLE_SHEETS_CREDENTIALS_PATH = "C:\path\to\credentials.json"
# Make permanent: add to $PROFILE
```

**Create .env file** (alternative):
```bash
# In project root, create .env
echo 'GOOGLE_SHEETS_CREDENTIALS_PATH=/path/to/credentials.json' > .env
```

### ❌ "Invalid credentials" or "Permission denied"

**Causes**: Key expired, JSON corrupted, service account missing permissions  
**Fix**:

1. **Verify JSON is valid**:
   ```bash
   python -c "import json; json.load(open('credentials.json'))"
   # If no error, JSON is valid
   ```

2. **Verify service account has Editor role**:
   - Open Google Sheet
   - Share → Add service account email (from JSON `client_email` field) as "Editor"

3. **Check key expiration**:
   - Google Cloud Console → Service Accounts → Select account → Keys
   - Look for red "Expired" labels
   - If expired, generate new key

4. **Recreate credentials if stuck**:
   - Follow [Google Sheets Setup Guide](../setup/gsheets.md)

---

## CSV & Data Issues

### ❌ "No such file or directory: data.csv"

**Cause**: CSV path incorrect or file missing  
**Fix**:
```bash
# Check file exists
ls -la data.csv  # Linux/macOS
dir data.csv     # Windows

# Use full path
bdr export csv-to-sheets /full/path/to/data.csv --sheet-id ID
```

### ❌ "CSV encoding error" or "Invalid UTF-8"

**Cause**: CSV not UTF-8 encoded  
**Fix**:
```bash
# Convert to UTF-8 (macOS/Linux)
iconv -f ISO-8859-1 -t UTF-8 data.csv > data_utf8.csv

# Convert to UTF-8 (Windows PowerShell)
(Get-Content data.csv | Out-String) | Out-File data_utf8.csv -Encoding UTF8
```

### ❌ "No columns found" or "Headers missing"

**Cause**: CSV has no header row, or empty first row  
**Fix**:
```bash
# Check headers
head -1 data.csv

# If missing, add headers manually:
# Option 1: Edit CSV with headers
# Option 2: Use correct CSV file
```

---

## Export Issues

### ❌ "Spreadsheet not found" or "Invalid sheet ID"

**Cause**: Wrong sheet ID or sheet deleted  
**Fix**:
```bash
# Get spreadsheet ID from URL
# https://docs.google.com/spreadsheets/d/[THIS_IS_THE_ID]/edit

# Use correct ID
bdr export csv-to-sheets data.csv --sheet-id abc123XYZ
```

### ❌ "Worksheet not found"

**Cause**: Worksheet name doesn't exist in spreadsheet  
**Fix**:
```bash
# Default worksheet: "leads"
# If using custom name, verify it exists

# Use correct name
bdr export csv-to-sheets data.csv --sheet-id ID --worksheet "My Sheet"
```

### ❌ "Permission denied" when writing to sheet

**Cause**: Service account not shared as "Editor", or sheet is read-only  
**Fix**:
1. Open Google Sheet
2. Click "Share"
3. Add service account email (from JSON `client_email`)
4. Grant "Editor" role
5. Make sure sheet is NOT read-only

### ❌ "Timeout" or "slow export"

**Cause**: CSV too large, slow network, or rate limiting  
**Fix**:
```bash
# Test with smaller file first
bdr export csv-to-sheets sample.csv --dry-run

# If CSV is huge (>100K rows), split and process in batches
# bdr handles this gracefully, but may take 5–10 minutes
```

---

## Docker/Container Issues

### ❌ ".venv not found" or "venv activation fails"

**Cause**: Virtual environment corruption  
**Fix**:
```bash
# Recreate venv
rm -rf .venv
python -m venv .venv

# Activate and reinstall
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\Activate.ps1   # Windows PowerShell

# Reinstall
pip install bar-directory-recon==0.1.9
```

---

## Scheduled Export Issues

### ❌ "Cron job not running" or "Task scheduler fails"

**Cause**: Script path wrong, permissions missing, or logs nowhere  
**Fix**:

**Linux/macOS (Cron)**:
```bash
# Test cron script directly
bash scripts/run_export.sh data.csv abc123

# Check crontab entry
crontab -l

# View cron logs
# macOS: log stream --predicate 'process == "cron"'
# Linux: tail -f /var/log/syslog | grep CRON
```

**Windows (Task Scheduler)**:
```powershell
# Test script directly
.\scripts\run_export.ps1 -CsvPath "data.csv" -SheetId "abc123"

# Check Task Scheduler logs
Get-WinEvent -LogName "Microsoft-Windows-TaskScheduler/Operational" -MaxEvents 20
```

---

## Advanced Diagnostics

### Enable debug logging:
```bash
# Linux/macOS
export BDR_DEBUG=1
bdr export csv-to-sheets data.csv --sheet-id ID

# Windows PowerShell
$env:BDR_DEBUG = "1"
bdr export csv-to-sheets data.csv --sheet-id ID
```

### Get full error trace:
```bash
# Python traceback for debugging
python -c "
from bdr.cli import app
app(['export', 'csv-to-sheets', 'data.csv', '--sheet-id', 'ID'])
"
```

### Verify dependencies:
```bash
bdr doctor --no-exec
# Check all [OK] marks
```

---

## Still Stuck?

Use [SUPPORT_TEMPLATE.md](SUPPORT_TEMPLATE.md) to report issues with:
- `bdr doctor --no-exec` output
- Exact CLI command (credentials redacted)
- CSV structure & size
- Full error message
- OS & Python version

---

_Tip: Most issues are credentials/permissions related. Start with `bdr doctor --no-exec`._
