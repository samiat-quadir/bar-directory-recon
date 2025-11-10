#!/usr/bin/env python3
"""
Example usage of Google Sheets exporter.

Before running:
1. Set up a Google Service Account with Sheets API access
2. Download the JSON key file
3. Set GOOGLE_SA_JSON environment variable to point to the key file
4. Share your Google Sheet with the service account email
"""

import sys

from tools.gsheets_exporter import export_rows


def main():
    """Example: Export sample data to Google Sheets."""
    # Example data
    sample_data = [
        ['Date', 'Event', 'Status'],
        ['2025-08-18', 'Plugin CLI Created', 'Complete'],
        ['2025-08-18', 'Google Sheets Export', 'In Progress'],
    ]

    # Configuration (would normally come from environment or config file)
    spreadsheet_id = 'your_spreadsheet_id_here'  # Get from Google Sheets URL
    worksheet_name = 'Sheet1'  # Or whatever your sheet is named

    try:
        print("Exporting data to Google Sheets...")
        export_rows(spreadsheet_id, worksheet_name, sample_data)
        print("✅ Export successful!")
    except Exception as e:
        print(f"❌ Export failed: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
