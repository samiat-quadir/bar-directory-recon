# 🚀 Client Pack v1 — Quick Start Guide

Welcome! This guide will get you exporting data to Google Sheets in under 10 minutes.

## Prerequisites

- Python 3.9 or later
- A Google account (for service account setup)
- A Google Sheet you own or can edit
- The bar-directory-recon package installed

## Installation (2 minutes)

```bash
pip install bar-directory-recon[gsheets]
```

This installs the package with Google Sheets support (includes `google-auth` and `gspread`).

## Service Account Setup (5 minutes)

Before you can write to Google Sheets, you need a service account:

1. **Follow [docs/setup/gsheets.md](setup/gsheets.md)** for step-by-step instructions
   - It takes ~5 minutes
   - You'll get a `service-account-key.json` file
   - Then set `GOOGLE_APPLICATION_CREDENTIALS` environment variable

2. **Share your Google Sheet with the service account email** (from the JSON key)
   - Example: `my-service-account@YOUR_PROJECT.iam.gserviceaccount.com`
   - Give it **Editor** access
   - This is a one-time permission grant

## Health Check (30 seconds)

Run the diagnostic tool:

```bash
bdr doctor
```

Output should show:
- ✅ Google auth credentials accessible
- ✅ Credentials can authenticate
- ✅ All core dependencies satisfied

If you see ❌ on Google auth, revisit the permission grant in step 2 above.

## Your First Export

The simplest example: export a CSV to Google Sheets

```bash
bdr export csv-to-sheets \
  --csv-file data.csv \
  --sheet-id "YOUR_SHEET_ID_HERE" \
  --worksheet "Sheet1"
```

**Where do you find the sheet ID?**
- Open your Google Sheet in a browser
- Copy the ID from the URL:  
  `https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit#gid=0`

### Command Breakdown

| Option | Meaning |
|--------|---------|
| `--csv-file` | Path to your CSV file |
| `--sheet-id` | Google Sheets ID (from URL above) |
| `--worksheet` | Tab name in the sheet (e.g., "Sheet1") |
| `--dedupe-key` | (Optional) Column name for duplicate removal |
| `--mode` | (Optional) `append` (default) or `replace` |
| `--dry-run` | (Optional) Preview without uploading |

## Next Steps

- **Full usage docs**: [docs/usage/csv-to-sheets.md](usage/csv-to-sheets.md)
- **Troubleshooting**: [docs/troubleshooting.md](troubleshooting.md)
- **Security notes**: See [Credential Handling](#credential-handling) below

## Credential Handling

### ✅ DO

- Store `service-account-key.json` **outside** the repo (e.g., `~/.config/service-account-key.json`)
- Use `GOOGLE_APPLICATION_CREDENTIALS` environment variable to point to it
- Never commit credentials to Git

### ❌ DON'T

- Add API keys to `.env.local` or `config.json`
- Commit `service-account-key.json` to the repo
- Share the JSON key file with others

### Environment Setup Example

**Linux/macOS:**
```bash
export GOOGLE_APPLICATION_CREDENTIALS=~/.config/service-account-key.json
bdr export csv-to-sheets --csv-file data.csv --sheet-id "YOUR_SHEET_ID"
```

**Windows (PowerShell):**
```powershell
$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\Users\YourName\.config\service-account-key.json"
bdr export csv-to-sheets --csv-file data.csv --sheet-id "YOUR_SHEET_ID"
```

**Windows (Command Prompt):**
```cmd
set GOOGLE_APPLICATION_CREDENTIALS=C:\Users\YourName\.config\service-account-key.json
bdr export csv-to-sheets --csv-file data.csv --sheet-id "YOUR_SHEET_ID"
```

## Common Issues

| Issue | Solution |
|-------|----------|
| `PermissionError: access denied` | Make sure you shared the sheet with the service account email |
| `Invalid sheet ID` | Double-check the ID copied from the URL |
| `credentials not found` | Verify `GOOGLE_APPLICATION_CREDENTIALS` environment variable is set |
| `Module 'gspread' not found` | Run `pip install bar-directory-recon[gsheets]` again |

See [docs/troubleshooting.md](troubleshooting.md) for more help.

## Getting Help

- **CLI help**: `bdr --help` or `bdr export csv-to-sheets --help`
- **Health check**: `bdr doctor`
- **Troubleshooting**: [docs/troubleshooting.md](troubleshooting.md)

---

**Ready?** Start with [docs/setup/gsheets.md](setup/gsheets.md) to set up your service account.
