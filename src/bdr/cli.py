"""Command-line entry point for the bar-directory-recon package."""
from __future__ import annotations

import json
from enum import Enum
from pathlib import Path
from typing import Optional

import typer

from . import get_version
from .doctor import format_report, run_doctor

app = typer.Typer(add_completion=False, help="Utilities for validating bar-directory-recon installs.")

# Export subcommand group
export_app = typer.Typer(help="Export data to various destinations (Google Sheets, etc.)")
app.add_typer(export_app, name="export")


class OutputFormat(str, Enum):
    TEXT = "text"
    JSON = "json"


class ExportMode(str, Enum):
    APPEND = "append"
    REPLACE = "replace"


def _version_banner() -> str:
    return f"bar-directory-recon {get_version()}"


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(
        False,
        "--version",
        "-V",
        help="Show version information and exit.",
    ),
) -> None:
    if version:
        typer.echo(_version_banner())
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        typer.echo(ctx.get_help())
        raise typer.Exit(code=0)


@app.command()
def doctor(
    no_exec: bool = typer.Option(
        True,
        "--no-exec/--exec",
        help="Skip commands that perform live automation (default).",
    ),
    output_format: OutputFormat = typer.Option(
        OutputFormat.TEXT,
        "--format",
        case_sensitive=False,
        help="Render the report as plain text or JSON.",
    ),
) -> None:
    """Run dependency and framework diagnostics."""

    report = run_doctor(no_exec=no_exec)

    if output_format is OutputFormat.JSON:
        typer.echo(json.dumps(report.to_dict(), indent=2, sort_keys=True))
    else:
        typer.echo(format_report(report))

    raise typer.Exit(code=0 if report.passed else 1)


# ---------------------------------------------------------------------------
# Export Commands — Golden Path: CSV → Google Sheets
# ---------------------------------------------------------------------------


@export_app.command("csv-to-sheets")
def csv_to_sheets(
    csv: Path = typer.Argument(
        ...,
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        help="Path to the CSV file to export.",
    ),
    sheet_id: Optional[str] = typer.Option(
        None,
        "--sheet-id",
        "-s",
        envvar="GOOGLE_SHEETS_SPREADSHEET_ID",
        help="Google Sheets spreadsheet ID. Can also use GOOGLE_SHEETS_SPREADSHEET_ID env var.",
    ),
    worksheet: str = typer.Option(
        "leads",
        "--worksheet",
        "-w",
        help="Target worksheet name within the spreadsheet.",
    ),
    mode: ExportMode = typer.Option(
        ExportMode.APPEND,
        "--mode",
        "-m",
        help="Export mode: 'append' adds rows, 'replace' clears sheet first.",
    ),
    dedupe_key: Optional[str] = typer.Option(
        None,
        "--dedupe-key",
        "-d",
        help="Column name for deduplication (e.g., 'email').",
    ),
    dry_run: bool = typer.Option(
        False,
        "--dry-run",
        help="Preview what would be exported without making network calls.",
    ),
) -> None:
    """
    Export a CSV file to Google Sheets.

    This is the GOLDEN PATH for bar-directory-recon exports.

    Prerequisites:
    - Set GOOGLE_SHEETS_CREDENTIALS_PATH to your service account JSON
    - Set GOOGLE_SHEETS_SPREADSHEET_ID (or pass --sheet-id)
    - Credentials must be stored OUTSIDE the repository

    Examples:
        bdr export csv-to-sheets leads.csv --sheet-id abc123
        bdr export csv-to-sheets leads.csv --mode replace
        bdr export csv-to-sheets leads.csv --dedupe-key email --dry-run
    """
    import sys

    # Add tools directory to path for import
    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    tools_path = repo_root / "tools"
    if str(tools_path) not in sys.path:
        sys.path.insert(0, str(tools_path))

    try:
        from gsheets_exporter import (
            is_gsheets_available,
            load_csv,
            dedupe_rows,
            export_csv_to_sheets,
            GSheetsNotInstalledError,
            WorksheetNotFoundError,
        )
    except ImportError as e:
        typer.secho(f"❌ Failed to import gsheets_exporter: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    # Load and preview CSV
    try:
        rows = load_csv(str(csv))
    except FileNotFoundError as e:
        typer.secho(f"❌ {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    except ValueError as e:
        typer.secho(f"❌ {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)

    row_count = len(rows) - 1  # exclude header
    header_preview = ", ".join(rows[0][:5]) + ("..." if len(rows[0]) > 5 else "")

    typer.echo("")
    typer.secho("═══════════════════════════════════════════════════════════════", fg=typer.colors.CYAN)
    typer.secho("  CSV → Google Sheets Export (Golden Path)", fg=typer.colors.CYAN)
    typer.secho("═══════════════════════════════════════════════════════════════", fg=typer.colors.CYAN)
    typer.echo(f"📄 CSV: {csv}")
    typer.echo(f"   Rows: {row_count} (+ header)")
    typer.echo(f"   Columns: {header_preview}")
    typer.echo(f"   Mode: {mode.value}")
    typer.echo(f"   Worksheet: {worksheet}")

    # Deduplicate if requested
    if dedupe_key:
        try:
            original_count = row_count
            rows = dedupe_rows(rows, dedupe_key)
            row_count = len(rows) - 1
            typer.echo(f"   Dedupe: {original_count} → {row_count} (key: {dedupe_key})")
        except ValueError as e:
            typer.secho(f"❌ {e}", fg=typer.colors.RED)
            raise typer.Exit(code=1)

    if dry_run:
        typer.echo("")
        typer.secho(f"🔍 Dry run — would export {row_count} rows to '{worksheet}'", fg=typer.colors.YELLOW)
        raise typer.Exit(code=0)

    if not sheet_id:
        typer.echo("")
        typer.secho("❌ Error: Spreadsheet ID not provided", fg=typer.colors.RED)
        typer.echo("   Use --sheet-id or set GOOGLE_SHEETS_SPREADSHEET_ID env var")
        raise typer.Exit(code=1)

    if not is_gsheets_available():
        typer.echo("")
        typer.secho("❌ Google Sheets dependencies not installed", fg=typer.colors.RED)
        typer.echo("   Install with: pip install .[gsheets]")
        raise typer.Exit(code=1)

    try:
        exported_count, mapping_info = export_csv_to_sheets(
            csv_path=str(csv),
            spreadsheet_id=sheet_id,
            worksheet=worksheet,
            mode=mode.value,
            dedupe_key=dedupe_key,
        )

        mode_verb = "replaced" if mode == ExportMode.REPLACE else "appended"
        typer.echo("")
        typer.secho(f"✅ Successfully {mode_verb} {row_count} rows to '{worksheet}'", fg=typer.colors.GREEN)

        # Show mapping info
        if mapping_info["type"] == "header":
            mapped = ", ".join(mapping_info["mapped_columns"][:5])
            extra = "..." if len(mapping_info["mapped_columns"]) > 5 else ""
            typer.echo(f"   Mapping: header-based ({mapped}{extra})")
            if mapping_info["unmapped_columns"]:
                unmapped = ", ".join(mapping_info["unmapped_columns"])
                typer.secho(f"   Unmapped: {unmapped}", fg=typer.colors.YELLOW)
        else:
            typer.echo("   Mapping: positional append")

        typer.echo(f"   https://docs.google.com/spreadsheets/d/{sheet_id}")
        raise typer.Exit(code=0)

    except WorksheetNotFoundError as e:
        typer.echo("")
        typer.secho(f"❌ {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    except RuntimeError as e:
        typer.echo("")
        typer.secho(f"❌ {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)
    except GSheetsNotInstalledError:
        typer.echo("")
        typer.secho("❌ Google Sheets dependencies not installed", fg=typer.colors.RED)
        typer.echo("   Install with: pip install .[gsheets]")
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo("")
        typer.secho(f"❌ Export failed: {e}", fg=typer.colors.RED)
        raise typer.Exit(code=1)


def entrypoint() -> None:
    """Console script shim so Typer can launch the app."""

    app()


if __name__ == "__main__":
    entrypoint()
