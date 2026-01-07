"""
Google Sheets Exporter — Optional Integration

This module provides Google Sheets export functionality as an optional dependency.
Install with: pip install .[gsheets]

Environment variables (standardized):
    GOOGLE_SHEETS_CREDENTIALS_PATH — path to service account JSON credentials
    GOOGLE_SHEETS_SPREADSHEET_ID — destination spreadsheet ID (optional, can be passed to functions)
"""

import os
from typing import List, Optional

# Lazy import flag
_GSHEETS_AVAILABLE: Optional[bool] = None

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']


class GSheetsNotInstalledError(ImportError):
    """Raised when Google Sheets dependencies are not installed."""

    def __init__(self) -> None:
        super().__init__(
            "Google Sheets dependencies not installed. "
            "Install with: pip install .[gsheets]"
        )


def _check_gsheets_available() -> bool:
    """
    Lazily check if Google Sheets dependencies are available.
    Caches the result for performance.
    """
    global _GSHEETS_AVAILABLE
    if _GSHEETS_AVAILABLE is None:
        try:
            import google.oauth2.service_account  # noqa: F401
            import gspread  # noqa: F401
            _GSHEETS_AVAILABLE = True
        except ImportError:
            _GSHEETS_AVAILABLE = False
    return _GSHEETS_AVAILABLE


def is_gsheets_available() -> bool:
    """
    Check if Google Sheets integration is available.

    Returns:
        bool: True if gsheets dependencies are installed
    """
    return _check_gsheets_available()


def get_client():
    """
    Get an authorized gspread client using service account credentials.

    Environment variables:
        GOOGLE_SHEETS_CREDENTIALS_PATH — path to service account JSON file

    Returns:
        gspread.Client: Authorized client

    Raises:
        GSheetsNotInstalledError: If gsheets dependencies not installed
        RuntimeError: If credentials path not configured or file not found
    """
    if not _check_gsheets_available():
        raise GSheetsNotInstalledError()

    # Lazy imports inside function
    from google.oauth2.service_account import Credentials
    import gspread

    # Standardized env variable
    creds_path = os.environ.get('GOOGLE_SHEETS_CREDENTIALS_PATH', '')

    # Fallback to legacy env var for backwards compatibility
    if not creds_path:
        creds_path = os.environ.get('GOOGLE_SA_JSON', '')

    if not creds_path:
        raise RuntimeError(
            "GOOGLE_SHEETS_CREDENTIALS_PATH not set. "
            "Set this environment variable to the path of your service account JSON file."
        )

    if not os.path.exists(creds_path):
        raise RuntimeError(
            f"Credentials file not found: {creds_path}. "
            "Ensure GOOGLE_SHEETS_CREDENTIALS_PATH points to a valid service account JSON file."
        )

    creds = Credentials.from_service_account_file(creds_path, scopes=SCOPES)
    return gspread.authorize(creds)


def export_rows(
    spreadsheet_id: str,
    worksheet: str,
    rows: List[List],
    *,
    spreadsheet_id_from_env: bool = False
) -> None:
    """
    Append rows to a Google Sheets worksheet.

    Args:
        spreadsheet_id: Google Sheets spreadsheet ID (or pass spreadsheet_id_from_env=True)
        worksheet: Name of the worksheet tab
        rows: List of rows (each row is a list of cell values)
        spreadsheet_id_from_env: If True, read spreadsheet_id from GOOGLE_SHEETS_SPREADSHEET_ID env var

    Raises:
        GSheetsNotInstalledError: If gsheets dependencies not installed
        RuntimeError: If credentials or spreadsheet ID not configured
    """
    if not _check_gsheets_available():
        raise GSheetsNotInstalledError()

    # Allow reading spreadsheet ID from env
    if spreadsheet_id_from_env or not spreadsheet_id:
        spreadsheet_id = os.environ.get('GOOGLE_SHEETS_SPREADSHEET_ID', spreadsheet_id)

    if not spreadsheet_id:
        raise RuntimeError(
            "Spreadsheet ID not provided. "
            "Pass spreadsheet_id argument or set GOOGLE_SHEETS_SPREADSHEET_ID environment variable."
        )

    gc = get_client()
    sh = gc.open_by_key(spreadsheet_id)
    ws = sh.worksheet(worksheet)
    ws.append_rows(rows)


def export_dataframe(
    df,
    spreadsheet_id: str,
    worksheet: str,
    *,
    include_header: bool = True,
    spreadsheet_id_from_env: bool = False
) -> None:
    """
    Export a pandas DataFrame to a Google Sheets worksheet.

    Args:
        df: pandas DataFrame to export
        spreadsheet_id: Google Sheets spreadsheet ID
        worksheet: Name of the worksheet tab
        include_header: Whether to include column headers as first row
        spreadsheet_id_from_env: If True, read spreadsheet_id from GOOGLE_SHEETS_SPREADSHEET_ID env var

    Raises:
        GSheetsNotInstalledError: If gsheets dependencies not installed
    """
    rows = []
    if include_header:
        rows.append(df.columns.tolist())
    rows.extend(df.values.tolist())
    export_rows(spreadsheet_id, worksheet, rows, spreadsheet_id_from_env=spreadsheet_id_from_env)
