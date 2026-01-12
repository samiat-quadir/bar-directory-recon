# Client Export Kit — Quick Start Guide

Import your leads into Google Sheets in **one command**.

---

## Prerequisites

1. **Python 3.11+** installed
2. **Google service account** credentials (JSON file)
3. **Google Spreadsheet** shared with your service account

---

## Setup (One-Time)

### 1. Install Dependencies

```powershell
cd C:\Code\bar-directory-recon
pip install -e .[gsheets]
```

### 2. Configure Credentials

Create a file named `.env.local` in the repository root:

```
GOOGLE_SHEETS_CREDENTIALS_PATH=C:\secrets\your-service-account.json
GOOGLE_SHEETS_SPREADSHEET_ID=your-spreadsheet-id-here
```

> ⚠️ **Security**: Keep your credentials file OUTSIDE the repository folder.

---

## Import Your CSV

Run the import script:

```powershell
.\client_export_kit\Run-Import.ps1 -CsvPath .\your-leads.csv
```

### Options

| Option | Default | Description |
|--------|---------|-------------|
| `-CsvPath` | (required) | Path to your CSV file |
| `-Worksheet` | `leads` | Target worksheet name |
| `-Mode` | `append` | `append` or `replace` |
| `-DryRun` | off | Preview without writing |

### Examples

```powershell
# Basic import
.\client_export_kit\Run-Import.ps1 -CsvPath .\leads.csv

# Replace all data
.\client_export_kit\Run-Import.ps1 -CsvPath .\leads.csv -Mode replace

# Preview first (dry-run)
.\client_export_kit\Run-Import.ps1 -CsvPath .\leads.csv -DryRun
```

---

## CSV Format

Your CSV should have a header row with these columns:

| Column | Required | Description |
|--------|----------|-------------|
| `name` or `full_name` | Yes | Attorney name |
| `email` | Yes | Email address |
| `firm` or `company` | No | Firm/company name |
| `city` | No | City |
| `state` | No | State |
| `bar_number` | No | Bar ID |

See `examples/sample_leads.csv` for a template.

---

## Troubleshooting

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues and solutions.

---

## Support

Contact: your-email@example.com
