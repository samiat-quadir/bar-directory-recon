# Troubleshooting

Common issues and solutions when using `bar-directory-recon`.

## Health Check First

Always start with:

```bash
bdr doctor
```

This will identify configuration, credential, and API access issues immediately.

## Credentials & Authentication

### "GOOGLE_APPLICATION_CREDENTIALS is not set"

**Problem**: The environment variable pointing to your Google service account key is missing.

**Solution**:

Set it for your current session (temporary):

- **Linux/macOS**: `export GOOGLE_APPLICATION_CREDENTIALS=~/.config/gcp-key.json`
- **Windows (PowerShell)**: `$env:GOOGLE_APPLICATION_CREDENTIALS = "C:\path\to\key.json"`
- **Windows (Command Prompt)**: `set GOOGLE_APPLICATION_CREDENTIALS=C:\path\to\key.json`

To make it persistent, see [Google Sheets Setup](setup/gsheets.md#step-6-set-the-environment-variable).

### "Invalid credentials" or "Invalid key format"

**Problem**: The JSON key file is corrupted, missing, or pointing to wrong location.

**Solution**:

1. Verify the file exists:
   - `ls -la ~/.config/gcp-key.json` (Linux/macOS)
   - `dir %USERPROFILE%\.config\gcp-key.json` (Windows)

2. Regenerate the key:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Service Accounts → Your Account → KEYS
   - Delete the old JSON key
   - Click ADD KEY → Create new key → JSON
   - Download and save to correct location

3. Set the environment variable again

### "Permission denied" or "403 Forbidden"

**Problem**: The service account doesn't have access to the Google Sheet or API.

**Solution**:

1. Verify the Google Sheets API is enabled:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - APIs & Services → Library
   - Search "Google Sheets API"
   - Click in → Status should show "API enabled" (blue)
   - If not, click ENABLE

2. Share the Google Sheet with the service account:
   - Open your Google Sheet
   - Click Share (top right)
   - Use the service account email from your JSON key file:
     - Open the JSON key with a text editor
     - Look for `"client_email": "service-account-name@project.iam.gserviceaccount.com"`
   - In Share, paste this email and give **Editor** permissions
   - Click Share

3. Verify `bdr doctor` passes

## Google Sheets Issues

### "Sheet not found" or "Invalid sheet ID"

**Problem**: The sheet ID doesn't exist or hasn't been shared with the service account.

**Solution**:

1. **Find the correct sheet ID**:
   - Open your Google Sheet
   - Look at the URL: `https://docs.google.com/spreadsheets/d/[THIS]/edit`
   - Copy the part between `/d/` and `/edit`

2. **Check sharing**:
   - Make sure the sheet is shared with the service account email (see above)
   - You should have Editor permissions

3. **Verify with a dry run**:
   ```bash
   bdr export csv-to-sheets --input test.csv --sheet-id SHEET_ID --dry-run
   ```

### "Worksheet does not exist"

**Problem**: The worksheet (tab) name doesn't match any in the Google Sheet.

**Solution**:

1. Check the exact worksheet name in Google Sheets (they're case-sensitive)
2. To see available worksheets, you can use:
   ```bash
   bdr export csv-to-sheets --help
   ```
   (This will show examples)

3. If the worksheet doesn't exist, it will be created on first export—this is OK.

### "Too many requests" or "API quota exceeded"

**Problem**: You're hitting Google's API rate limits.

**Solution**:

1. **Wait**: The limit resets after ~60 seconds
2. **Reduce batch size**: Try exporting in smaller chunks
3. **Batch exports with a delay**:
   ```bash
   for i in 1 2 3; do
     bdr export csv-to-sheets --input data_$i.csv --sheet-id SHEET_ID
     sleep 5  # Wait 5 seconds between exports
   done
   ```

## Data Issues

### CSV file has wrong encoding or special characters

**Problem**: Characters appear garbled in Google Sheets.

**Solution**:

1. Verify your CSV is UTF-8 encoded:
   - **Linux/macOS**: `file data.csv`
   - **Windows (PowerShell)**: `Get-Content data.csv -Encoding UTF8`

2. Convert to UTF-8 if needed:
   - **Linux/macOS**:
     ```bash
     iconv -f ISO-8859-1 -t UTF-8 data.csv > data_utf8.csv
     ```
   - **Windows (PowerShell)**:
     ```powershell
     Get-Content data.csv -Encoding Latin1 | Set-Content data_utf8.csv -Encoding UTF8
     ```

3. Re-run the export with the converted file

### Headers are missing or incorrect

**Problem**: The first row isn't used as headers, or column names are wrong.

**Solution**:

1. Verify your CSV has a header row as the first line
2. Check for extra blank lines at the top:
   ```bash
   head -n 1 data.csv  # Show first line
   ```
3. If headers are missing, manually edit your CSV to add them
4. Re-export

### Deduplication isn't working

**Problem**: Duplicate rows still appear in the sheet despite `--dedupe-key`.

**Solution**:

1. Check the column names exactly match your CSV headers (case-sensitive):
   ```bash
   head -n 1 data.csv | cut -d, -f1  # Show first column name
   ```

2. For multiple columns, use comma separator with no spaces:
   ```bash
   bdr export csv-to-sheets --input data.csv --sheet-id SHEET_ID --dedupe-key "id,email"
   ```

3. Run with `--dry-run` first to see what would be deduplicated:
   ```bash
   bdr export csv-to-sheets --input data.csv --sheet-id SHEET_ID --dedupe-key "id" --dry-run
   ```

4. If still not working, verify your CSV doesn't have extra spaces around values

## Export Issues

### "Export failed" with no clear error

**Problem**: The command ran but didn't complete successfully.

**Solution**:

1. **Run in verbose mode**:
   ```bash
   bdr export csv-to-sheets --input data.csv --sheet-id SHEET_ID -v
   ```
   (or `--debug` if available)

2. **Check the CSV file**:
   - Is it valid (readable, not corrupted)?
   - Does it have content (not empty)?
   - Is it quoted correctly if values contain commas?

3. **Try a smaller test file**:
   ```bash
   head -n 100 data.csv > test_small.csv
   bdr export csv-to-sheets --input test_small.csv --sheet-id SHEET_ID
   ```

4. **Check Google Sheets limits**:
   - Google Sheets has a 10 million cell limit per sheet
   - If your data is very large, split it into multiple worksheets

### "Cannot write to worksheet"

**Problem**: The worksheet exists but the export fails when trying to write.

**Solution**:

1. Check if the worksheet is actually editable:
   - Open Google Sheets
   - Try manually typing in a cell in the target worksheet
   - If that fails, check the share permissions

2. If it's a protected sheet:
   - Go to Sheet menu → Protect sheets and ranges
   - Remove protection or add your service account email as an editor

3. Re-run the export

## Performance Issues

### Export is very slow

**Problem**: Large CSV files take a long time to export.

**Solution**:

1. **Check internet connection**: `ping google.com` (Mac/Linux) or `ping 8.8.8.8` (Windows)

2. **Reduce CSV size**:
   - Try exporting first 1000 rows to test:
     ```bash
     head -n 1001 large_data.csv > test.csv  # Headers + 1000 rows
     bdr export csv-to-sheets --input test.csv --sheet-id SHEET_ID
     ```

3. **Check for large cells**:
   - Very long text values in cells can slow uploads
   - Use `--dry-run` to see what will be exported

4. **Try exporting in batches**:
   - Split the CSV into smaller chunks
   - Export to different worksheets
   - Combine results in a separate "Master" sheet if needed

## Getting Help

If you can't find a solution:

1. **Run diagnostics**:
   ```bash
   bdr doctor > bdr_diagnostics.txt
   ```

2. **Check logs** (if available):
   - Look for error messages with timestamps
   - Check Google Cloud Console audit logs

3. **Report with context**:
   - Include output from `bdr doctor`
   - Your command (without credentials)
   - Error message verbatim
   - CSV file size and column count

## Prevention Tips

✅ **DO**:
- Use `--dry-run` before real exports
- Run `bdr doctor` regularly to catch issues early
- Keep your service account key secure (never commit to Git)
- Share Google Sheets with the service account email, not your personal email

❌ **DON'T**:
- Commit the JSON key file to Git (add `.gitignore` entry)
- Share the JSON key via email or chat
- Use the same service account key across multiple projects
- Export very large files (>1GB) without splitting into batches

## Still Stuck?

1. Check [Google Sheets Setup](setup/gsheets.md) for initial configuration
2. Review [CSV to Sheets Usage](usage/csv-to-sheets.md) for command examples
3. Run `bdr export csv-to-sheets --help` to see all available options
