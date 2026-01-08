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


class WorksheetNotFoundError(ValueError):
    """Raised when specified worksheet is not found in the spreadsheet."""

    def __init__(
        self,
        worksheet_name: str,
        available_worksheets: List[str],
        spreadsheet_id: str = ""
    ) -> None:
        self.worksheet_name = worksheet_name
        self.available_worksheets = available_worksheets
        self.spreadsheet_id = spreadsheet_id

        available_str = ", ".join(f"'{w}'" for w in available_worksheets)
        suggestion = available_worksheets[0] if available_worksheets else "Sheet1"

        message = (
            f"Worksheet '{worksheet_name}' not found.\n"
            f"Available worksheets: {available_str}\n"
            f"Use --worksheet '{suggestion}' to select a valid worksheet."
        )
        super().__init__(message)


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


def list_worksheets(spreadsheet_id: str) -> List[str]:
    """
    List all worksheet names in a spreadsheet.

    Args:
        spreadsheet_id: Google Sheets spreadsheet ID

    Returns:
        List[str]: List of worksheet titles

    Raises:
        GSheetsNotInstalledError: If gsheets dependencies not installed
    """
    if not _check_gsheets_available():
        raise GSheetsNotInstalledError()

    gc = get_client()
    sh = gc.open_by_key(spreadsheet_id)
    return [ws.title for ws in sh.worksheets()]


def _get_worksheet_with_fallback(
    spreadsheet,
    worksheet_name: str,
    spreadsheet_id: str,
    use_fallback: bool = False
):
    """
    Get a worksheet by name, with helpful error if not found.

    Args:
        spreadsheet: gspread Spreadsheet object
        worksheet_name: Name of worksheet to find
        spreadsheet_id: Spreadsheet ID (for error messages)
        use_fallback: If True and worksheet not found, use first worksheet

    Returns:
        gspread.Worksheet: The worksheet object

    Raises:
        WorksheetNotFoundError: If worksheet not found and use_fallback is False
    """
    import gspread

    available = [ws.title for ws in spreadsheet.worksheets()]

    try:
        return spreadsheet.worksheet(worksheet_name)
    except gspread.exceptions.WorksheetNotFound:
        if use_fallback and available:
            # Fallback to first worksheet
            return spreadsheet.worksheet(available[0])
        raise WorksheetNotFoundError(
            worksheet_name=worksheet_name,
            available_worksheets=available,
            spreadsheet_id=spreadsheet_id
        )


def export_rows(
    spreadsheet_id: str,
    worksheet: str,
    rows: List[List],
    *,
    spreadsheet_id_from_env: bool = False,
    fallback_to_first: bool = False
) -> None:
    """
    Append rows to a Google Sheets worksheet.

    Args:
        spreadsheet_id: Google Sheets spreadsheet ID (or pass spreadsheet_id_from_env=True)
        worksheet: Name of the worksheet tab
        rows: List of rows (each row is a list of cell values)
        spreadsheet_id_from_env: If True, read spreadsheet_id from GOOGLE_SHEETS_SPREADSHEET_ID env var
        fallback_to_first: If True and worksheet not found, use first available worksheet

    Raises:
        GSheetsNotInstalledError: If gsheets dependencies not installed
        RuntimeError: If credentials or spreadsheet ID not configured
        WorksheetNotFoundError: If worksheet not found (with list of available worksheets)
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
    ws = _get_worksheet_with_fallback(
        spreadsheet=sh,
        worksheet_name=worksheet,
        spreadsheet_id=spreadsheet_id,
        use_fallback=fallback_to_first
    )
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
# CSV Import Functions
# ---------------------------------------------------------------------------

def load_csv(csv_path: str) -> List[List[str]]:
    """
    Load a CSV file and return rows as list of lists.

    Args:
        csv_path: Path to CSV file

    Returns:
        List[List[str]]: Rows including header row

    Raises:
        FileNotFoundError: If CSV file not found
        ValueError: If CSV is empty
    """
    import csv

    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    rows = []
    with open(csv_path, 'r', encoding='utf-8-sig', newline='') as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(row)

    if not rows:
        raise ValueError(f"CSV file is empty: {csv_path}")

    return rows


def dedupe_rows(
    rows: List[List[str]],
    key_column: str
) -> List[List[str]]:
    """
    Remove duplicate rows based on a key column.

    Args:
        rows: List of rows (first row is header)
        key_column: Column name to use for deduplication

    Returns:
        List[List[str]]: Deduplicated rows (header + unique data rows)

    Raises:
        ValueError: If key_column not found in header
    """
    if len(rows) < 2:
        return rows

    header = rows[0]

    try:
        key_index = header.index(key_column)
    except ValueError:
        available = ", ".join(header)
        raise ValueError(
            f"Dedupe key column '{key_column}' not found in CSV.\n"
            f"Available columns: {available}"
        )

    seen = set()
    unique_rows = [header]

    for row in rows[1:]:
        if key_index < len(row):
            key_value = row[key_index]
            if key_value not in seen:
                seen.add(key_value)
                unique_rows.append(row)
        else:
            # Row doesn't have enough columns, include it anyway
            unique_rows.append(row)

    return unique_rows


def export_csv_to_sheets(
    csv_path: str,
    spreadsheet_id: str,
    worksheet: str,
    *,
    mode: str = "append",
    dedupe_key: Optional[str] = None,
    spreadsheet_id_from_env: bool = False,
    fallback_to_first: bool = False
) -> int:
    """
    Export a CSV file to Google Sheets.

    Args:
        csv_path: Path to CSV file
        spreadsheet_id: Google Sheets spreadsheet ID
        worksheet: Name of the worksheet tab
        mode: "append" to add rows, "replace" to clear and write
        dedupe_key: Column name for deduplication (optional)
        spreadsheet_id_from_env: If True, read spreadsheet_id from env var
        fallback_to_first: If True and worksheet not found, use first worksheet

    Returns:
        int: Number of rows exported (excluding header)

    Raises:
        GSheetsNotInstalledError: If gsheets dependencies not installed
        FileNotFoundError: If CSV file not found
    """
    if not _check_gsheets_available():
        raise GSheetsNotInstalledError()

    # Load CSV
    rows = load_csv(csv_path)

    # Deduplicate if requested
    if dedupe_key:
        original_count = len(rows) - 1  # exclude header
        rows = dedupe_rows(rows, dedupe_key)
        deduped_count = len(rows) - 1
        if original_count != deduped_count:
            print(f"   Deduplicated: {original_count} → {deduped_count} rows (key: {dedupe_key})")

    # Resolve spreadsheet ID
    if spreadsheet_id_from_env or not spreadsheet_id:
        spreadsheet_id = os.environ.get('GOOGLE_SHEETS_SPREADSHEET_ID', spreadsheet_id)

    if not spreadsheet_id:
        raise RuntimeError(
            "Spreadsheet ID not provided. "
            "Pass spreadsheet_id argument or set GOOGLE_SHEETS_SPREADSHEET_ID environment variable."
        )

    gc = get_client()
    sh = gc.open_by_key(spreadsheet_id)
    ws = _get_worksheet_with_fallback(
        spreadsheet=sh,
        worksheet_name=worksheet,
        spreadsheet_id=spreadsheet_id,
        use_fallback=fallback_to_first
    )

    if mode == "replace":
        # Clear the worksheet and write all rows
        ws.clear()
        ws.update('A1', rows)
    else:
        # Append mode: add rows (skip header if sheet already has data)
        existing = ws.get_all_values()
        if existing:
            # Sheet has data, skip header row
            ws.append_rows(rows[1:])
        else:
            # Empty sheet, include header
            ws.append_rows(rows)

    return len(rows) - 1  # Return data row count (excluding header)


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

  # Export a CSV file to Google Sheets
  python -m tools.gsheets_exporter --csv leads.csv --worksheet leads

  # Replace worksheet contents (instead of append)
  python -m tools.gsheets_exporter --csv leads.csv --worksheet leads --mode replace

  # Deduplicate by email before exporting
  python -m tools.gsheets_exporter --csv leads.csv --dedupe-key email

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
    parser.add_argument(
        "--fallback",
        action="store_true",
        help="If worksheet not found, use first available worksheet"
    )
    parser.add_argument(
        "--list-worksheets",
        action="store_true",
        help="List all worksheets in the spreadsheet"
    )
    parser.add_argument(
        "--csv",
        type=str,
        default=None,
        help="Path to CSV file to export to Google Sheets"
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["append", "replace"],
        default="append",
        help="Export mode: 'append' adds rows, 'replace' clears sheet first (default: append)"
    )
    parser.add_argument(
        "--dedupe-key",
        type=str,
        default=None,
        help="Column name to use for deduplication (e.g., 'email')"
    )

    return parser


def _run_demo(
    worksheet: str,
    spreadsheet_id: Optional[str],
    dry_run: bool = False,
    fallback: bool = False
) -> int:
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
            rows=demo_row,
            fallback_to_first=fallback
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
            dry_run=parsed.dry_run,
            fallback=parsed.fallback
        )

    # --list-worksheets: show available worksheets
    if parsed.list_worksheets:
        sheet_id = parsed.spreadsheet_id or os.environ.get('GOOGLE_SHEETS_SPREADSHEET_ID', '')
        if not sheet_id:
            print("❌ Error: Spreadsheet ID not provided")
            print("   Use --spreadsheet-id or set GOOGLE_SHEETS_SPREADSHEET_ID env var")
            return 1

        if not is_gsheets_available():
            raise GSheetsNotInstalledError()

        try:
            worksheets = list_worksheets(sheet_id)
            print("📋 Available worksheets:")
            for ws in worksheets:
                print(f"   • {ws}")
            return 0
        except Exception as e:
            print(f"❌ Failed to list worksheets: {e}")
            return 1

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
                spreadsheet_id_from_env=not parsed.spreadsheet_id,
                fallback_to_first=parsed.fallback
            )
            print(f"✅ Exported {len(rows)} rows to {parsed.worksheet}")
            return 0
        except WorksheetNotFoundError as e:
            print(f"❌ {e}")
            return 1
        except Exception as e:
            print(f"❌ Export failed: {e}")
            return 1

    # --csv: export CSV file to Google Sheets
    if parsed.csv:
        sheet_id = parsed.spreadsheet_id or os.environ.get('GOOGLE_SHEETS_SPREADSHEET_ID', '')

        # Load and preview CSV
        try:
            rows = load_csv(parsed.csv)
        except FileNotFoundError as e:
            print(f"❌ {e}")
            return 1
        except ValueError as e:
            print(f"❌ {e}")
            return 1

        row_count = len(rows) - 1  # exclude header
        print(f"📄 CSV: {parsed.csv}")
        print(f"   Rows: {row_count} (+ header)")
        print(f"   Columns: {', '.join(rows[0][:5])}{'...' if len(rows[0]) > 5 else ''}")
        print(f"   Mode: {parsed.mode}")
        print(f"   Worksheet: {parsed.worksheet}")

        # Deduplicate if requested
        if parsed.dedupe_key:
            try:
                original_count = row_count
                rows = dedupe_rows(rows, parsed.dedupe_key)
                row_count = len(rows) - 1
                print(f"   Dedupe: {original_count} → {row_count} (key: {parsed.dedupe_key})")
            except ValueError as e:
                print(f"❌ {e}")
                return 1

        if parsed.dry_run:
            print(f"\n🔍 Dry run — would export {row_count} rows to {parsed.worksheet}")
            return 0

        if not sheet_id:
            print("\n❌ Error: Spreadsheet ID not provided")
            print("   Use --spreadsheet-id or set GOOGLE_SHEETS_SPREADSHEET_ID env var")
            return 1

        if not is_gsheets_available():
            raise GSheetsNotInstalledError()

        try:
            export_csv_to_sheets(
                csv_path=parsed.csv,
                spreadsheet_id=sheet_id,
                worksheet=parsed.worksheet,
                mode=parsed.mode,
                dedupe_key=parsed.dedupe_key,
                spreadsheet_id_from_env=not parsed.spreadsheet_id,
                fallback_to_first=parsed.fallback
            )
            mode_verb = "replaced" if parsed.mode == "replace" else "appended"
            print(f"\n✅ Successfully {mode_verb} {row_count} rows to '{parsed.worksheet}'")
            print(f"   https://docs.google.com/spreadsheets/d/{sheet_id}")
            return 0
        except WorksheetNotFoundError as e:
            print(f"\n❌ {e}")
            return 1
        except Exception as e:
            print(f"\n❌ Export failed: {e}")
            return 1

    # No action specified — show help
    parser.print_help()
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
