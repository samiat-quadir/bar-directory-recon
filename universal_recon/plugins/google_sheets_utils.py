"""
Google Sheets utility functions for plugins
Shared functionality for exporting lead data to Google Sheets

This is an optional integration. Install with: pip install .[gsheets]

Environment variables (standardized):
    GOOGLE_SHEETS_CREDENTIALS_PATH — path to service account JSON credentials
    GOOGLE_SHEETS_SPREADSHEET_ID — destination spreadsheet ID

Legacy env vars (deprecated, still supported):
    GOOGLE_SA_JSON — deprecated, use GOOGLE_SHEETS_CREDENTIALS_PATH
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lazy import handling
# ---------------------------------------------------------------------------
_GSHEETS_AVAILABLE: Optional[bool] = None


class GSheetsNotInstalledError(ImportError):
    """Raised when Google Sheets dependencies are not installed."""

    def __init__(self) -> None:
        super().__init__(
            "Google Sheets dependencies not installed.\n"
            "Install with: pip install .[gsheets]\n"
            "Or: pip install google-api-python-client google-auth google-auth-oauthlib"
        )


def _check_gsheets_available() -> bool:
    """Lazily check if Google Sheets dependencies are available."""
    global _GSHEETS_AVAILABLE
    if _GSHEETS_AVAILABLE is None:
        try:
            from google.oauth2.service_account import Credentials  # noqa: F401
            from googleapiclient.discovery import build  # noqa: F401
            _GSHEETS_AVAILABLE = True
        except ImportError:
            _GSHEETS_AVAILABLE = False
    return _GSHEETS_AVAILABLE


def is_gsheets_available() -> bool:
    """Check if Google Sheets dependencies are installed."""
    return _check_gsheets_available()


# For backwards compatibility (module-level constant check)
GOOGLE_SHEETS_AVAILABLE = is_gsheets_available()


def _get_credentials_path() -> Optional[str]:
    """
    Get credentials path from environment variables.

    Checks (in order):
        1. GOOGLE_SHEETS_CREDENTIALS_PATH (preferred)
        2. GOOGLE_SA_JSON (legacy fallback)
        3. config/google_service_account.json (hardcoded fallback)
    """
    # Preferred: standardized env var
    path = os.environ.get("GOOGLE_SHEETS_CREDENTIALS_PATH")
    if path and os.path.exists(path):
        return path

    # Legacy fallback
    path = os.environ.get("GOOGLE_SA_JSON")
    if path and os.path.exists(path):
        logger.warning(
            "GOOGLE_SA_JSON is deprecated. "
            "Use GOOGLE_SHEETS_CREDENTIALS_PATH instead."
        )
        return path

    # Hardcoded fallback for backwards compatibility
    fallback = os.path.join("config", "google_service_account.json")
    if os.path.exists(fallback):
        return fallback

    return None


def export_to_google_sheets(
    data: List[Dict[str, Any]],
    sheet_id: Optional[str] = None,
    sheet_name: Optional[str] = None,
    plugin_name: str = "Lead_Scraper"
) -> bool:
    """
    Export lead data to Google Sheets.

    Args:
        data: List of lead dictionaries
        sheet_id: Google Sheets spreadsheet ID (or use GOOGLE_SHEETS_SPREADSHEET_ID env var)
        sheet_name: Name for the sheet tab (optional)
        plugin_name: Name of the plugin for default sheet naming

    Returns:
        bool: True if successful, False otherwise
    """
    if not _check_gsheets_available():
        logger.warning(
            "Google Sheets integration not available. "
            "Install with: pip install .[gsheets]"
        )
        return False

    if not data:
        logger.warning("No data to export to Google Sheets")
        return False

    # Resolve sheet_id from env var if not provided
    if not sheet_id:
        sheet_id = os.environ.get("GOOGLE_SHEETS_SPREADSHEET_ID")
        if not sheet_id:
            logger.error(
                "No spreadsheet ID provided. Set GOOGLE_SHEETS_SPREADSHEET_ID "
                "or pass sheet_id parameter."
            )
            return False

    try:
        # Set up credentials
        credentials_path = _get_credentials_path()
        if not credentials_path:
            logger.warning(
                "Google Sheets credentials not found. "
                "Set GOOGLE_SHEETS_CREDENTIALS_PATH env var."
            )
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
