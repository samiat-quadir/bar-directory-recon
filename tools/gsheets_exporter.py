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


# ---------------------------------------------------------------------------
# CLI Entrypoint
# ---------------------------------------------------------------------------

def _create_parser():
    """Create argument parser for CLI."""
    import argparse

    parser = argparse.ArgumentParser(
        prog="python -m tools.gsheets_exporter",
        description="Google Sheets Exporter CLI — Export data to Google Sheets",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Environment variables:
  GOOGLE_SHEETS_CREDENTIALS_PATH  Path to service account JSON credentials
  GOOGLE_SHEETS_SPREADSHEET_ID    Destination spreadsheet ID

Examples:
  # Check if Google Sheets dependencies are installed
  python -m tools.gsheets_exporter --check

  # Run demo: export 1 test row to configured sheet
  python -m tools.gsheets_exporter --demo

  # Export custom data (JSON format)
  python -m tools.gsheets_exporter --worksheet "Sheet1" --data '[["A", "B"], [1, 2]]'
"""
    )

    parser.add_argument(
        "--check",
        action="store_true",
        help="Check if Google Sheets dependencies are installed"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Export 1 demo row (timestamp + run_id) to configured sheet"
    )
    parser.add_argument(
        "--worksheet",
        type=str,
        default="Sheet1",
        help="Worksheet name (default: Sheet1)"
    )
    parser.add_argument(
        "--spreadsheet-id",
        type=str,
        default=None,
        help="Spreadsheet ID (or use GOOGLE_SHEETS_SPREADSHEET_ID env var)"
    )
    parser.add_argument(
        "--data",
        type=str,
        default=None,
        help="JSON-encoded rows to export, e.g. '[[\"col1\", \"col2\"], [\"val1\", \"val2\"]]'"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be exported without making network calls"
    )

    return parser


def _run_demo(worksheet: str, spreadsheet_id: Optional[str], dry_run: bool = False) -> int:
    """
    Run demo mode: export 1 row with timestamp and run_id.

    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    import uuid
    from datetime import datetime, timezone

    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    run_id = str(uuid.uuid4())[:8]

    demo_row = [["timestamp", "run_id", "source"], [timestamp, run_id, "gsheets_exporter_demo"]]

    print("📊 Google Sheets Exporter Demo")
    print(f"   Worksheet: {worksheet}")
    print(f"   Timestamp: {timestamp}")
    print(f"   Run ID:    {run_id}")

    if dry_run:
        print("\n🔍 Dry run mode — no data exported")
        print(f"   Would export: {demo_row}")
        return 0

    # Check env vars
    creds_path = os.environ.get('GOOGLE_SHEETS_CREDENTIALS_PATH', '')
    sheet_id = spreadsheet_id or os.environ.get('GOOGLE_SHEETS_SPREADSHEET_ID', '')

    if not creds_path:
        print("\n❌ Error: GOOGLE_SHEETS_CREDENTIALS_PATH not set")
        print("   Set this environment variable to your service account JSON path")
        return 1

    if not sheet_id:
        print("\n❌ Error: Spreadsheet ID not provided")
        print("   Use --spreadsheet-id or set GOOGLE_SHEETS_SPREADSHEET_ID env var")
        return 1

    if not is_gsheets_available():
        raise GSheetsNotInstalledError()

    try:
        export_rows(
            spreadsheet_id=sheet_id,
            worksheet=worksheet,
            rows=demo_row
        )
        print("\n✅ Successfully exported demo row to Google Sheets!")
        print(f"   https://docs.google.com/spreadsheets/d/{sheet_id}")
        return 0
    except Exception as e:
        print(f"\n❌ Export failed: {e}")
        return 1


def main(args: Optional[List[str]] = None) -> int:
    """
    CLI main entrypoint.

    Args:
        args: Command line arguments (defaults to sys.argv[1:])

    Returns:
        int: Exit code
    """
    parser = _create_parser()
    parsed = parser.parse_args(args)

    # --check: report dependency status
    if parsed.check:
        available = is_gsheets_available()
        if available:
            print("✅ Google Sheets dependencies are installed")
            return 0
        else:
            print("❌ Google Sheets dependencies NOT installed")
            print("   Install with: pip install .[gsheets]")
            return 1

    # --demo: export 1 row
    if parsed.demo:
        return _run_demo(
            worksheet=parsed.worksheet,
            spreadsheet_id=parsed.spreadsheet_id,
            dry_run=parsed.dry_run
        )

    # --data: export custom data
    if parsed.data:
        import json
        try:
            rows = json.loads(parsed.data)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in --data: {e}")
            return 1

        sheet_id = parsed.spreadsheet_id or os.environ.get('GOOGLE_SHEETS_SPREADSHEET_ID', '')

        if parsed.dry_run:
            print(f"🔍 Dry run — would export {len(rows)} rows to {parsed.worksheet}")
            return 0

        if not is_gsheets_available():
            raise GSheetsNotInstalledError()

        try:
            export_rows(
                spreadsheet_id=sheet_id,
                worksheet=parsed.worksheet,
                rows=rows,
                spreadsheet_id_from_env=not parsed.spreadsheet_id
            )
            print(f"✅ Exported {len(rows)} rows to {parsed.worksheet}")
            return 0
        except Exception as e:
            print(f"❌ Export failed: {e}")
            return 1

    # No action specified — show help
    parser.print_help()
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
