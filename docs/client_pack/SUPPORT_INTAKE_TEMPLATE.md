# Support Intake Template

Use this template when reporting issues or requesting support. Fill out as much detail as possible so we can help quickly.

## Issue Summary

**One-line description:**  
[e.g., "Export to Google Sheets fails with 'KeyError: email'"]

**When did it start?**  
[e.g., "After updating to v0.1.10" or "First run today"]

---

## Environment

**Operating System:**  
[ ] Windows  
[ ] macOS  
[ ] Linux  
**Version:** _______________

**Python Version:**  
```
python --version
# (paste output below)

```

**Bar Directory Recon Version:**  
```
bdr --version
# (paste output below)

```

**Installation method:**  
[ ] pip install (latest)  
[ ] pip install bar-directory-recon[gsheets]==0.1.10  
[ ] From source  
[ ] Other: _______________

---

## The Problem

**Command you ran:**  
(copy/paste the exact command, sanitized of secrets)
```
bdr export csv-to-sheets <sanitized>
```

**Error output:**  
(first 50 lines of error; hide any API keys, emails, or file paths with `***`)
```
[paste error output here]
```

**Log file location (if using wrapper script):**  
`logs/exports/YYYY-MM-DD_HH-MM-SS.log`  
(attach or paste contents if relevant)

---

## What You Provided

**Google Sheet ID:**  
`***` (not the full URL, just the ID)

**CSV row count:**  
[e.g., "100 rows + header"]

**CSV column count:**  
[e.g., "7 columns: Name, Email, Phone, Firm, ..."]

**Target worksheet name:**  
[e.g., "leads" or custom name]

**Export mode:**  
[ ] append (default)  
[ ] replace  
[ ] update-only  

**Dedupe key (if used):**  
[e.g., "Email" or "none"]

---

## Pre-Flight Checks

Run these and paste the output:

```bash
# Check environment health
bdr doctor --no-exec

# Verify credentials file
ls $GOOGLE_SHEETS_CREDENTIALS_PATH    # macOS/Linux
dir $env:GOOGLE_SHEETS_CREDENTIALS_PATH  # Windows PowerShell
```

**Doctor output:**
```
[paste here]
```

---

## What You Expect

[e.g., "1. Read 100 rows from CSV. 2. Create 100 new rows in 'leads' worksheet. 3. Complete with 0 errors."]

---

## What Actually Happened

[e.g., "1. Doctor passed. 2. Attempted to write row 50 of 100. 3. Failed with KeyError."]

---

## Previous Troubleshooting

Have you already tried?
- [ ] Running `bdr doctor --no-exec` (did it pass?)
- [ ] Checking that the Google Sheet is shared with the Service Account email
- [ ] Re-downloading the Service Account JSON file
- [ ] Using a smaller test CSV (e.g., 5 rows)
- [ ] Checking for network connectivity to googleapis.com

What was the result?
```
[paste results here]
```

---

## Additional Context

**Anything else we should know?**

[e.g., "First time using Google Sheets API", "Running in a Docker container", "Behind a corporate proxy", etc.]

---

## How to Submit This Form

**Email:** [support email or contact form]  
**GitHub Issue:** [link to issue template]  
**Slack/Chat:** [if applicable]

---

**Thank you for the detailed report!** We'll get back to you within 24–48 hours.
