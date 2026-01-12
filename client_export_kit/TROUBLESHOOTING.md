# Troubleshooting Guide

Common issues and solutions for the Client Export Kit.

---

## "GOOGLE_SHEETS_CREDENTIALS_PATH not set"

**Cause**: The `.env.local` file is missing or doesn't contain the credentials path.

**Solution**:

1. Create `.env.local` in the repository root
2. Add this line (adjust path to your credentials file):

```text
GOOGLE_SHEETS_CREDENTIALS_PATH=C:\secrets\your-service-account.json
```

---

## "Credentials file not found"

**Cause**: The path in `.env.local` doesn't point to a valid file.

**Solution**:

1. Verify the file exists at the specified path
2. Use the full absolute path (e.g., `C:\secrets\creds.json`)
3. Check for typos in the filename

---

## "SECURITY ERROR: Credentials file is inside the repository"

**Cause**: Your credentials JSON file is stored inside the repository folder.

**Solution**:

1. Move the credentials file outside the repository
2. Recommended location: `C:\secrets\` or `%USERPROFILE%\secrets\`
3. Update `.env.local` with the new path

> ⚠️ **Never commit credentials to Git!**

---

## "Worksheet 'leads' not found"

**Cause**: The target worksheet doesn't exist in your spreadsheet.

**Solution**:

1. Create a worksheet named "leads" in your Google Spreadsheet, OR
2. Specify a different worksheet:

```powershell
.\Run-Import.ps1 -CsvPath .\leads.csv -Worksheet "Sheet1"
```

3. List available worksheets:

```powershell
python -m tools.gsheets_exporter --list-worksheets
```

---

## "Permission denied" on spreadsheet

**Cause**: The service account doesn't have access to the spreadsheet.

**Solution**:

1. Open your Google Spreadsheet
2. Click "Share" button
3. Add your service account email (e.g., `bdr@your-project.iam.gserviceaccount.com`)
4. Give it "Editor" access

---

## "Google Sheets dependencies NOT installed"

**Cause**: The gsheets optional dependency isn't installed.

**Solution**:

```powershell
pip install .[gsheets]
```

---

## CSV columns not mapping correctly

**Cause**: Your CSV column names don't match the expected headers.

**Supported column names**:

| Your CSV | Maps To |
|----------|---------|
| `name`, `fullname`, `full_name` | `full_name` |
| `email`, `email_address` | `email` |
| `firm`, `company`, `law_firm` | `firm` |
| `city` | `city` |
| `state` | `state` |
| `bar_number`, `bar_id` | `bar_number` |

**Solution**:

Rename your CSV columns to match the supported names, or the closest synonym.

---

## "CSV file not found"

**Cause**: The path to your CSV file is incorrect.

**Solution**:

1. Use the full absolute path:

```powershell
.\Run-Import.ps1 -CsvPath "C:\Users\You\Desktop\leads.csv"
```

2. Or place the CSV in the repository folder and use a relative path:

```powershell
.\Run-Import.ps1 -CsvPath .\leads.csv
```

---

## Import runs but no data appears

**Cause**: The CSV might be empty or have encoding issues.

**Solution**:

1. Open the CSV in a text editor to verify it has data
2. Ensure the file is UTF-8 encoded
3. Run with `--dry-run` to preview what would be imported:

```powershell
.\Run-Import.ps1 -CsvPath .\leads.csv -DryRun
```

---

## Still stuck?

Contact support with:

1. The exact error message
2. Your Python version (`python --version`)
3. Your OS (Windows 10/11)
4. The command you ran

Email: your-email@example.com
