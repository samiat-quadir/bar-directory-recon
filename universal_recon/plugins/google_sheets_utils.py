"""
Google Sheets utility functions for plugins
Shared functionality for exporting lead data to Google Sheets
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd

# Google Sheets integration (optional)
try:
    GOOGLE_SHEETS_AVAILABLE = True
except ImportError:
    GOOGLE_SHEETS_AVAILABLE = False

logger = logging.getLogger(__name__)


def export_to_google_sheets(
    data: List[Dict[str, Any]],
    sheet_id: str,
    sheet_name: Optional[str] = None,
    plugin_name: str = "Lead_Scraper"
) -> bool:
    """
    Export lead data to Google Sheets.

    Args:
        data: List of lead dictionaries
        sheet_id: Google Sheets spreadsheet ID
        sheet_name: Name for the sheet tab (optional)
        plugin_name: Name of the plugin for default sheet naming

    Returns:
        bool: True if successful, False otherwise
    """
    if not GOOGLE_SHEETS_AVAILABLE:
        logger.warning("Google Sheets integration not available. Install google-api-python-client packages.")
        return False

    if not data:
        logger.warning("No data to export to Google Sheets")
        return False

    try:
        # Set up credentials
        credentials_path = os.path.join("config", "google_service_account.json")
        if not os.path.exists(credentials_path):
            logger.warning(f"Google Sheets credentials not found at: {credentials_path}")
            return False

        from google.oauth2.service_account import Credentials
        from googleapiclient.discovery import build

        # Define the required scopes
        SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

        # Load credentials
        credentials = Credentials.from_service_account_file(credentials_path, scopes=SCOPES)

        # Build the service
        service = build('sheets', 'v4', credentials=credentials)

        # Set default sheet name
        if not sheet_name:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
            sheet_name = f"{plugin_name}_Leads_{timestamp}"

        # Convert data to format for Google Sheets
        df = pd.DataFrame(data)
        headers = df.columns.tolist()
        values = [headers] + df.values.tolist()

        # Try to create a new sheet
        try:
            body = {
                'requests': [{
                    'addSheet': {
                        'properties': {
                            'title': sheet_name
                        }
                    }
                }]
            }
            service.spreadsheets().batchUpdate(spreadsheetId=sheet_id, body=body).execute()
            logger.info(f"Created new sheet: {sheet_name}")
        except Exception:
            logger.info(f"Using existing sheet: {sheet_name}")

        # Upload data
        range_name = f"{sheet_name}!A1"
        body = {
            'values': values
        }

        service.spreadsheets().values().update(
            spreadsheetId=sheet_id,
            range=range_name,
            valueInputOption='RAW',
            body=body
        ).execute()

        logger.info(f"Successfully exported {len(data)} leads to Google Sheets: {sheet_name}")
        return True

    except Exception as e:
        logger.error(f"Error exporting to Google Sheets: {e}")
        return False


def get_sheet_url(sheet_id: str, sheet_name: Optional[str] = None) -> str:
    """
    Generate a direct URL to the Google Sheet.

    Args:
        sheet_id: Google Sheets spreadsheet ID
        sheet_name: Name of the specific sheet tab (optional)

    Returns:
        str: Direct URL to the Google Sheet
    """
    base_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}"
    if sheet_name:
        # URL encode the sheet name for use in fragment
        encoded_name = sheet_name.replace(" ", "%20")
        return f"{base_url}#gid={encoded_name}"
    return base_url
