"""Command-line entry point for the bar-directory-recon package."""
from __future__ import annotations

import json
from enum import Enum

import typer

from . import get_version
from .doctor import format_report, run_doctor

app = typer.Typer(add_completion=False, help="Utilities for validating bar-directory-recon installs.")


class OutputFormat(str, Enum):
    TEXT = "text"
    JSON = "json"


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


def entrypoint() -> None:
    """Console script shim so Typer can launch the app."""

    app()


if __name__ == "__main__":
    entrypoint()
