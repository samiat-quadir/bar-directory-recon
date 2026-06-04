# Support Packet Template

**Template for Gathering Troubleshooting Information**

**Last Updated**: 2026-02-03  
**Version**: v0.1.13

---

## When to Use This

Every time a client encounters an issue or error during pilot integration, ask them to:

1. Run the commands below (without executing anything dangerous)
2. Copy the output into a **sanitized** file (remove real Sheet IDs, paths, etc.)
3. Share that file via email or GitHub issue

**This packet provides the exact context support needs to diagnose quickly.**

---

## Support Packet Structure

### Section 1: Environment Information

Collect this **without running any code**:

```bash
# Show Python version
python --version

# Show where bar-directory-recon is installed
bdr --version

# Show operating system (Windows/Linux/macOS)
# Windows (cmd):
ver
# Linux/macOS (bash):
uname -a

# Show current working directory
# Windows (PowerShell):
Get-Location
# Linux/macOS (bash):
pwd
```

**Example Output to Include:**
```
Python version: Python 3.11.8
bdr version: 0.1.13
OS: Windows 11 Build 22000
Working directory: C:\Users\client\projects\export-data
```

---

### Section 2: Exact Command Used

**Copy the exact command that failed** (with real values sanitized):

```bash
# Example (sanitize the Sheet ID):
bdr export csv-to-sheets my_locations.csv \
  --sheet-id REDACTED_SHEET_ID \
  --dedupe-key location_id \
  --mode append
```

**Important**:
- Redact real Sheet IDs (use `REDACTED_SHEET_ID` instead)
- Keep flags and argument structure visible
- Include all flags (even if using defaults)

---

### Section 3: Health Check Output

Ask the client to run and capture:

```bash
# Run diagnostic (no credentials needed for this check)
bdr doctor --no-exec
```

**Expected output**:
```
Running bar-directory-recon doctor...
✓ Core dependencies: OK
✓ Python version: 3.11+ ✓
✓ Google Sheets API client: OK
Overall: PASS
```

**If they see errors here, share the full output.**

---

### Section 4: Full Error Message

When an error occurs, capture:

1. **Error type** (e.g., `AuthError`, `FileNotFoundError`, `ValueError`)
2. **Full stack trace** (from the first line to the last)
3. **Any warnings** before the error

**Example:**
```
Traceback (most recent call last):
  File "c:\Code\bar-directory-recon\cli\exporter.py", line 156, in run_export
    auth_result = self._authenticate_sheets()
  File "c:\Code\bar-directory-recon\adapters\gsheets_adapter.py", line 45, in _authenticate_sheets
    raise AuthError("Invalid credentials path or no Editor access")
AuthError: Invalid credentials path or no Editor access
```

---

### Section 5: Log File Contents

Ask the client to find and attach the most recent log:

```bash
# Find the log directory (default location; may vary)
# Windows:
ls $env:USERPROFILE\.bdr\logs\

# Linux/macOS:
ls ~/.bdr/logs/

# Show the latest export log (last 30 lines):
# Windows (PowerShell):
Get-Content "$env:USERPROFILE\.bdr\logs\export.log" -Tail 30

# Linux/macOS:
tail -30 ~/.bdr/logs/export.log
```

**What to include:**
- Timestamp of the error
- Any warnings before the error
- Sanitized error message (remove real file paths, Sheet IDs)

**Example Log Snippet:**
```
2026-02-03 14:35:22 | INFO    | Starting export: my_locations.csv → Sheet
2026-02-03 14:35:23 | DEBUG   | Credentials file found: [REDACTED]
2026-02-03 14:35:23 | ERROR   | Failed to authenticate: Invalid credentials path
2026-02-03 14:35:23 | ERROR   | Exiting with status 1
```

---

### Section 6: Input Data Sample (Sanitized)

If the issue seems data-related, provide:

```bash
# Show CSV headers (safe—no real data):
head -1 your_data.csv

# Show row count:
wc -l your_data.csv  # Linux/macOS
(Measure-Object -Path your_data.csv -Line).Lines  # Windows PowerShell

# Show first 2–3 data rows (sanitize identifiers):
head -3 your_data.csv  # Include headers
```

**Example:**
```
id,name,city,amount
1,[REDACTED],[REDACTED],1000
2,[REDACTED],[REDACTED],2000
Total rows: 150
```

---

### Section 7: Credentials Setup Verification (No Secrets!)

Ask them to **verify WITHOUT showing the JSON key**:

```bash
# Verify the env var is set (does NOT reveal the path content)
# Windows (PowerShell):
if ($env:GOOGLE_SHEETS_CREDENTIALS_PATH) { "✓ Env var is set" } else { "✗ Env var NOT set" }

# Linux/macOS (bash):
if [ -n "$GOOGLE_SHEETS_CREDENTIALS_PATH" ]; then echo "✓ Env var is set"; else echo "✗ Env var NOT set"; fi

# Verify the file exists (without showing contents):
# Windows:
Test-Path $env:GOOGLE_SHEETS_CREDENTIALS_PATH

# Linux/macOS:
test -f "$GOOGLE_SHEETS_CREDENTIALS_PATH" && echo "File exists" || echo "File not found"
```

**What they should report:**
```
Env var is set: ✓
File exists: ✓
File readable: ✓
```

---

## Complete Support Packet Template

Copy and fill this out:

```
═══════════════════════════════════════════════════════════
SUPPORT PACKET — bar-directory-recon Pilot Issue Report
═══════════════════════════════════════════════════════════

CLIENT NAME: [Your organization]
CONTACT: [Name & email]
DATE: [YYYY-MM-DD]

─────────────────────────────────────────────────────────
1. ENVIRONMENT
─────────────────────────────────────────────────────────
Python version: [output from python --version]
bdr version: [output from bdr --version]
Operating system: [Windows/Linux/macOS, version]
Working directory: [where you ran the command]

─────────────────────────────────────────────────────────
2. COMMAND EXECUTED
─────────────────────────────────────────────────────────
[Paste the exact command with sanitized values]

─────────────────────────────────────────────────────────
3. HEALTH CHECK (bdr doctor --no-exec)
─────────────────────────────────────────────────────────
[Paste full output]

─────────────────────────────────────────────────────────
4. ERROR MESSAGE
─────────────────────────────────────────────────────────
Error type: [e.g., AuthError, FileNotFoundError]
Full stack trace:
[Paste from first "Traceback" line to the end]

─────────────────────────────────────────────────────────
5. RECENT LOGS
─────────────────────────────────────────────────────────
Log file used: [e.g., ~/.bdr/logs/export.log]
Last 30 lines:
[Paste from log, sanitized]

─────────────────────────────────────────────────────────
6. INPUT DATA SAMPLE
─────────────────────────────────────────────────────────
CSV file name: [e.g., locations.csv]
CSV headers: [output from head -1 file.csv]
CSV row count: [e.g., 150 rows]
Sample rows (sanitized): [first 2–3 rows]

─────────────────────────────────────────────────────────
7. CREDENTIALS SETUP
─────────────────────────────────────────────────────────
Environment variable set: ✓ / ✗
JSON file exists: ✓ / ✗
File is readable: ✓ / ✗
Service account email: [from JSON, e.g., sa@project.iam...]
Sheet shared with SA: ✓ / ✗ (Editor access?)

─────────────────────────────────────────────────────────
8. ADDITIONAL CONTEXT
─────────────────────────────────────────────────────────
What were you trying to do? [e.g., first export, re-run, etc.]
When did it first occur? [first run / after N successful runs / etc.]
Steps taken so far to fix: [what you've tried]
Any other relevant info: [e.g., running in container, behind proxy, etc.]

═══════════════════════════════════════════════════════════
END SUPPORT PACKET
═══════════════════════════════════════════════════════════
```

---

## How Support Team Uses This

1. **Review environment**: Verify Python, OS, bdr version compatibility
2. **Reproduce command**: Run the exact command in a test environment
3. **Check logs**: Look for timestamps, warnings, specific error codes
4. **Diagnose**: Cross-reference error message against known issues
5. **Suggest fix**: Provide step-by-step remediation
6. **Verify**: Ask client to re-run and confirm fix works

---

## Sensitive Data Checklist

Before sending the support packet, verify:

- [ ] **No real Sheet IDs** (use `REDACTED_SHEET_ID`)
- [ ] **No file paths** with usernames (e.g., `C:\Users\{name}\...` → `~/...`)
- [ ] **No credentials exposed** (JSON key content should never appear)
- [ ] **No sensitive business data** (sanitize row contents, amounts, etc.)
- [ ] **No passwords or tokens** visible in env var output

---

## Support Packet Upload Options

### 1. Email
Send to: `[support email not defined yet—update when available]`
Subject: `[SUPPORT] bar-directory-recon v0.1.13 pilot issue`

### 2. GitHub Issue
1. Open [Issues](https://github.com/samiat-quadir/bar-directory-recon/issues)
2. Create new issue
3. Title: `[PILOT] {Brief issue description}`
4. Paste support packet in description
5. Attach log file if large (> 5 KB)

### 3. Direct Link
Include this in the support packet comment:
```
For faster response, reference: docs/ops/SUPPORT_PACKET.md
Version: v0.1.13, Filled: [DATE]
```

---

## Expected Response Time

- **Critical** (cannot install or run `doctor`): Within 4 business hours
- **Standard** (export fails mid-run): Within 24 business hours
- **Follow-up** (verification or optimization): Within 48 business hours

---

## Appendix: Common Errors & Quick Fixes

| Error | Likely Cause | Quick Fix |
|-------|--------------|-----------|
| `AuthError: Invalid credentials` | Wrong JSON path or no Editor access | Verify `GOOGLE_SHEETS_CREDENTIALS_PATH` and sheet sharing |
| `FileNotFoundError: your_data.csv` | CSV file not found | Use absolute path or check working directory |
| `ValueError: Sheet ID invalid` | Malformed Sheet ID | Extract from URL: `docs.google.com/spreadsheets/d/{ID}/... ` |
| `ConnectionError: timeout` | Network latency | Check internet; retry with `--timeout 120` |
| `RuntimeError: Dedup key not found` | Column name mismatch | Check CSV headers; verify exact column name |

For more, see [PILOT_RUN_SOP.md](PILOT_RUN_SOP.md#troubleshooting-quick-reference).
