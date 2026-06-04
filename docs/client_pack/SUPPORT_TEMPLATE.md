# Support Request Template

**Use this template when reporting issues or requesting help.**

---

## Basic Info

```
Product:     bar-directory-recon
Version:     [paste output of: bdr --version]
Python:      [paste output of: python --version]
OS:          [Windows / macOS / Linux]
Shell:       [PowerShell / bash / zsh]
Installed:   [pip / conda / other]
```

---

## Health Check

**Output of `bdr doctor --no-exec`**:
```
[Paste full doctor output below]


```

---

## Environment

**Credentials path set?**
```bash
# Linux/macOS
echo $GOOGLE_SHEETS_CREDENTIALS_PATH

# Windows PowerShell
$env:GOOGLE_SHEETS_CREDENTIALS_PATH
```

**Output**:
```
[Paste output or "not set"]
```

**Spreadsheet accessible?**
- [ ] Yes, I can open the sheet in browser
- [ ] No, I get "Permission denied"
- [ ] Not sure

**Service account shared as Editor?**
- [ ] Yes, confirmed in sheet share settings
- [ ] No, not shared
- [ ] Not sure

---

## Problem Description

**What were you trying to do?**
```
[Describe the operation: dry-run, full export, scheduled task, etc.]
```

**What went wrong?**
```
[Describe the error or unexpected behavior]
```

**When did it start?**
- [ ] First time using bdr
- [ ] Was working, then broke
- [ ] Worked on one machine, not another

---

## CSV Details

**CSV file info**:
```
File name:        [example: leads.csv]
Size:             [number of rows/bytes] (optional: wc -l or ls -lh)
Column count:     [number of columns]
First row:        [paste first row here, hide sensitive values]
Rows 2-3:         [paste sample rows, hide sensitive values]
```

**CSV encoding**: 
```
file type to check:
# Linux/macOS: file -b leads.csv
# Windows: Get-Content leads.csv -Encoding byte | Select-Object -First 4
```

**Output**:
```
[Paste encoding info]
```

---

## Command & Error

**Exact command used** (hide credentials):
```bash
# Example:
# bdr export csv-to-sheets leads.csv --sheet-id abc123XYZ --mode append

[Paste your command, redact --sheet-id, GOOGLE_SHEETS_CREDENTIALS_PATH, etc.]
```

**Full error message**:
```
[Paste complete stderr/stdout output below]


```

---

## Screenshots (Optional)

Attach:
- [ ] Spreadsheet share settings (to confirm service account has access)
- [ ] Google Cloud Console service account page
- [ ] Terminal output screenshot (if cut off in copy/paste)

---

## What You've Already Tried

- [ ] Ran `bdr doctor --no-exec` (confirm all [OK])
- [ ] Verified credentials file exists and is readable
- [ ] Confirmed spreadsheet is shared with service account as Editor
- [ ] Tested with sample CSV from `docs/client_pack/sample_data/sample.csv`
- [ ] Tried on a different machine or Python version
- [ ] Checked [TROUBLESHOOTING_ONE_PAGE.md](TROUBLESHOOTING_ONE_PAGE.md)

**What did you try, and what happened?**
```
[Describe attempts and results]
```

---

## Additional Context

**Is this blocking production?**
- [ ] Yes, critical outage
- [ ] No, can work around
- [ ] Not sure

**Are you using the wrapper scripts?**
- [ ] Yes: `scripts/run_export.ps1` or `scripts/run_export.sh`
- [ ] No, running CLI directly
- [ ] Not sure

**Scheduled or manual export?**
- [ ] Manual (one-time)
- [ ] Scheduled (cron / Task Scheduler)
- [ ] Both

**Anything else that might help?**
```
[Any other context, logs, or observations]
```

---

## Checklist Before Submitting

- [ ] Ran `bdr doctor --no-exec` successfully
- [ ] Verified Python 3.11+
- [ ] Confirmed credentials path is set and JSON is valid
- [ ] Checked [TROUBLESHOOTING_ONE_PAGE.md](TROUBLESHOOTING_ONE_PAGE.md) first
- [ ] Redacted sensitive info (sheet IDs, email addresses, file paths)
- [ ] Included full error message (not just summary)
- [ ] Described what you were trying to do (not just "it broke")

---

## Submit To

Email or open an issue with:
1. This completed template
2. `bdr doctor --no-exec` output
3. Exact error message (full traceback if available)
4. CSV structure (rows, columns, sample data with PII redacted)

---

_You'll get faster support if you complete all sections. Thanks!_
