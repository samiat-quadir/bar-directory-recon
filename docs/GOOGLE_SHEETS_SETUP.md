# Google Sheets Integration Setup Guide

## Overview

The Universal Lead Generation system includes optional Google Sheets integration for automatically uploading scraped leads to Google Sheets.

## Prerequisites

1. **Install required packages:**

   ```bash
   pip install -r requirements_google_sheets.txt
   ```

2. **Google Cloud Project Setup:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable the Google Sheets API
   - Create service account credentials

## Setup Steps

### 1. Create Service Account

1. In Google Cloud Console, go to "IAM & Admin" > "Service Accounts"
2. Click "Create Service Account"
3. Enter name (e.g., "universal-recon-sheets")
4. Grant "Editor" role
5. Click "Create Key" and download JSON file

### 2. Configure Credentials

1. Create `config/` directory in project root if it doesn't exist
2. Save the JSON file as `config/google_service_account.json`
3. Keep this file secure and never commit to git

### 3. Share Google Sheet

1. Create or open your target Google Sheet
2. Copy the Sheet ID from the URL:

   ```
   https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit
   ```

3. Share the sheet with your service account email (found in the JSON file)
4. Grant "Editor" permissions

## Usage Examples

### CLI Mode with Google Sheets

```bash
# Upload to Google Sheets automatically
python universal_automation.py \
  --industry lawyers \
  --city Miami \
  --state FL \
  --google-sheet-id "your_sheet_id_here" \
  --google-sheet-name "Miami_Lawyers"

# Without sheet name (auto-generated)
python universal_automation.py \
  --industry pool_contractors \
  --city Tampa \
  --state FL \
  --google-sheet-id "your_sheet_id_here"
```

### Interactive Mode

The interactive mode will prompt for Google Sheets integration if credentials are available.

## Troubleshooting

### Common Issues

1. **Import Error**: Install google-api-python-client packages
2. **Permission Denied**: Check service account has access to the sheet
3. **Authentication Failed**: Verify credentials file path and format
4. **Sheet Not Found**: Ensure Sheet ID is correct and accessible

### Enable Debug Logging

```bash
python universal_automation.py --verbose --google-sheet-id "your_id"
```

## Security Notes

- Never commit service account JSON files to version control
- Use environment variables for Sheet IDs in production
- Regularly rotate service account credentials
- Limit service account permissions to minimum required

## Optional Environment Variables

```bash
export GOOGLE_APPLICATION_CREDENTIALS="config/google_service_account.json"
export DEFAULT_GOOGLE_SHEET_ID="your_default_sheet_id"
```
