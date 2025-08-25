"""
Collaborative Divorce Adapter Plugin

This adapter processes CSV files containing collaborative divorce attorney data
and standardizes them into a common format for the bar directory reconnaissance system.
"""
import csv
import pathlib
from dataclasses import dataclass
from typing import Any, Dict, Generator


@dataclass
class CollabDivorceAdapter:
    """
    Adapter for processing collaborative divorce attorney CSV files.

    This adapter reads CSV files containing attorney information and yields
    standardized profile dictionaries with consistent field names.
    """
    source_csv: pathlib.Path

    def iter_profiles(self) -> Generator[Dict[str, Any], None, None]:
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
                reader = csv.DictReader(fh)
                for row in reader:
                    # Extract and normalize data from various possible column names
                    name = (
                        row.get("Name") or
                        row.get("Full Name") or
                        row.get("Attorney Name") or
                        row.get("Attorney") or
                        ""
                    ).strip()

                    email = (
                        row.get("Email") or
                        row.get("Email Address") or
                        row.get("E-mail") or
                        ""
                    ).strip().lower()

                    firm = (
                        row.get("Firm") or
                        row.get("Organization") or
                        row.get("Law Firm") or
                        row.get("Company") or
                        ""
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
