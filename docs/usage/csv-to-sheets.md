# CSV to Google Sheets Export

This guide shows how to export your data from CSV format to Google Sheets using `bar-directory-recon`.

## Prerequisites

- `bar-directory-recon[gsheets]` installed
- Google Sheets API configured (see [Google Sheets Setup](../setup/gsheets.md))
- `GOOGLE_APPLICATION_CREDENTIALS` environment variable set
- A Google Sheet ready to receive data

## Quick Start

The **canonical command** for most use cases:

```bash
bdr export csv-to-sheets \
  --input data.csv \
  --sheet-id YOUR_SHEET_ID \
  --worksheet "Sheet1"
```

Replace:
- `data.csv` with your CSV file path
- `YOUR_SHEET_ID` with your Google Sheet's ID (found in the sheet's URL)
- `"Sheet1"` with the worksheet tab name

## Detailed Usage

### Basic Export

```bash
bdr export csv-to-sheets --input data.csv --sheet-id YOUR_SHEET_ID
```

By default:
- Exports to worksheet "Sheet1"
- Clears existing data before writing
- Uses the first row as headers

### Export to Specific Worksheet

If your Google Sheet has multiple tabs, export to a specific one:

```bash
bdr export csv-to-sheets \
  --input data.csv \
  --sheet-id YOUR_SHEET_ID \
  --worksheet "Sales Data"
```

The worksheet will be created if it doesn't exist.

### Deduplication

Remove duplicate rows based on specific columns:

```bash
bdr export csv-to-sheets \
  --input data.csv \
  --sheet-id YOUR_SHEET_ID \
  --dedupe-key "id,email"
```

This keeps only the first occurrence of each unique combination of the `id` and `email` columns.

### Dry Run (Preview Changes)

See what would be exported without actually writing to Google Sheets:

```bash
bdr export csv-to-sheets \
  --input data.csv \
  --sheet-id YOUR_SHEET_ID \
  --dry-run
```

Output shows:
- Number of rows to be written
- Which columns will be included
- Any deduplication that would happen

### Finding Your Sheet ID

Your Google Sheet's ID is in the URL:

```
https://docs.google.com/spreadsheets/d/[THIS_IS_YOUR_SHEET_ID]/edit#gid=0
```

Copy the long string between `/d/` and `/edit`.

Alternatively, with shell expansion:

```bash
# Extract from a Google Sheets URL
SHEET_ID="https://docs.google.com/spreadsheets/d/1A_B2c3D4e5F6g7H8i9J0k1L2m3N4o5P6/edit"
bdr export csv-to-sheets --input data.csv --sheet-id ${SHEET_ID#*d/} --sheet-id ${SHEET_ID%/edit*}
```

## Examples

### Example 1: Daily Data Sync

Export a daily report to a Google Sheet:

```bash
bdr export csv-to-sheets \
  --input daily_report_$(date +%Y-%m-%d).csv \
  --sheet-id 1A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p \
  --worksheet "Daily Reports"
```

### Example 2: Merge Data with Deduplication

Combine multiple CSV files and deduplicate:

```bash
# First, combine your CSVs
cat new_data.csv >> existing_data.csv

# Then export with deduping on user_id
bdr export csv-to-sheets \
  --input existing_data.csv \
  --sheet-id 1A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p \
  --dedupe-key "user_id" \
  --worksheet "Users"
```

### Example 3: Append to Multiple Worksheets

Create worksheets for different data categories:

```bash
bdr export csv-to-sheets \
  --input sales.csv \
  --sheet-id 1A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p \
  --worksheet "Sales"

bdr export csv-to-sheets \
  --input customers.csv \
  --sheet-id 1A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p \
  --worksheet "Customers"
```

### Example 4: Preview Before Committing

Always dry-run first on large datasets:

```bash
# Preview
bdr export csv-to-sheets \
  --input large_data.csv \
  --sheet-id 1A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p \
  --dry-run

# If satisfied, export for real
bdr export csv-to-sheets \
  --input large_data.csv \
  --sheet-id 1A1b2C3d4E5f6G7h8I9j0K1l2M3n4O5p
```

## Output Behavior

### Headers

- The first row of your CSV becomes the first row of the Google Sheet
- Column order is preserved from your CSV

### Data Types

- All data is imported as **text** (Google Sheets auto-detection can be enabled manually in Sheets)
- Numbers with leading zeros are preserved (e.g., "001" stays "001")
- Empty cells are supported

### Performance

- Files up to 100,000 rows typically complete in seconds
- Deduplication is done on the client side before uploading
- No size limits except Google Sheets' 10 million cell limit per sheet

## Troubleshooting

### "Sheet not found" or "Invalid sheet ID"

- Double-check the sheet ID in the URL
- Make sure it's shared with the service account (see [Google Sheets Setup](../setup/gsheets.md))
- Run `bdr doctor` to verify credentials

### "Worksheet does not exist"

This is usually OK—empty worksheets are created automatically on first export.

If you need to create a worksheet first:
1. Open your Google Sheet
2. Click the **+** button at the bottom
3. Name it and click **Create**
4. Re-run the export with `--worksheet "Your Worksheet Name"`

### Export is slow

- Large CSV files (>100MB) may take longer
- Check your internet connection
- Try a smaller test file first

### Deduplication not working

- Check that the column names in `--dedupe-key` exactly match your CSV headers
- Use quotes around multi-column keys: `--dedupe-key "col1,col2"`
- Run with `--dry-run` to see what would be deduplicated

## Next Steps

- Review [Troubleshooting](../troubleshooting.md) for more solutions
- Run `bdr export csv-to-sheets --help` for all available options
- See [START_HERE](../START_HERE.md) for other export formats
