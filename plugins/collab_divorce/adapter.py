"""
Collaborative Divorce Adapter Plugin

This adapter processes CSV files containing collaborative divorce attorney data
and standardizes them into a common format for the bar directory reconnaissance system.
"""

import csv
import pathlib
import re
from dataclasses import dataclass
from typing import Any, Dict, Optional
from collections.abc import Generator


def detect_csv_dialect(sample: str) -> Any:
    """Detect the CSV dialect from a sample string.

    This function wraps csv.Sniffer().sniff but provides safe fallbacks
    for small or malformed samples. It always returns a dialect instance
    suitable for passing to `csv.DictReader`.

    Args:
        sample: A string containing the beginning of a CSV file.

    Returns:
        A csv.Dialect (or compatible object) describing delimiter/quotechar.
    """
    sniffer = csv.Sniffer()
    try:
        # Try to sniff; if it fails, fall back to comma delimiter
        dialect = sniffer.sniff(sample)
    except Exception:
        # Use the well-known 'excel' dialect instance as a safe fallback
        try:
            dialect = csv.get_dialect("excel")  # type: ignore
        except Exception:
            dialect = csv.excel()  # type: ignore
    return dialect


def normalize_email(email: str | None) -> str:
    """Normalize an email string to a lowercase, trimmed value.

    This function performs lightweight validation and normalization:
    - Returns an empty string for falsy inputs
    - Strips surrounding whitespace
    - Converts to lowercase
    - If the string contains multiple emails separated by ';' or ',', returns the first candidate
    - Returns '' if the resulting token doesn't look like an email

    Args:
        email: Optional raw email string from input

    Returns:
        Normalized email string or empty string when invalid/missing.
    """
    if not email:
        return ""
    s = email.strip()
    # take first token if multiple
    for sep in (";", ","):
        if sep in s:
            s = s.split(sep, 1)[0].strip()
            break
    s = s.lower()
    # basic validation
    if re.match(r"^[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}$", s):
        return s
    return ""


@dataclass
class CollabDivorceAdapter:
    """
    Adapter for processing collaborative divorce attorney CSV files.

    This adapter reads CSV files containing attorney information and yields
    standardized profile dictionaries with consistent field names.
    """

    source_csv: pathlib.Path

    def iter_profiles(self) -> Generator[dict[str, Any], None, None]:
        """
        Iterate over attorney profiles from the source CSV file.

        Yields:
            Dict[str, Any]: Standardized attorney profile with fields:
                - name: Attorney full name
                - email: Email address (normalized to lowercase)
                - firm: Law firm or organization name
                - specialty: Set to "Collaborative Divorce"
        """
        p = pathlib.Path(self.source_csv)
        if not p.exists():
            return

        try:
            with p.open(newline="", encoding="utf-8", errors="ignore") as fh:
                # Read a small sample to detect dialect, then rewind
                sample = fh.read(2048)
                fh.seek(0)
                dialect = detect_csv_dialect(sample)
                reader = csv.DictReader(fh, dialect=dialect)
                for row in reader:
                    # Extract and normalize data from various possible column names
                    name = (
                        row.get("Name")
                        or row.get("Full Name")
                        or row.get("Attorney Name")
                        or row.get("Attorney")
                        or ""
                    ).strip()

                    raw_email = (
                        row.get("Email")
                        or row.get("Email Address")
                        or row.get("E-mail")
                        or ""
                    )
                    email = normalize_email(raw_email)

                    firm = (
                        row.get("Firm")
                        or row.get("Organization")
                        or row.get("Law Firm")
                        or row.get("Company")
                        or ""
                    ).strip()

                    # Only yield if we have at least a name
                    if name:
                        yield {
                            "name": name,
                            "email": email,
                            "firm": firm,
                            "specialty": "Collaborative Divorce",
                            "source": str(p.name),
                        }
        except Exception as e:
            # Log error but don't fail completely
            print(f"Warning: Error processing {p}: {e}")
            return
