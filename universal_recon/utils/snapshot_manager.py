# === utils/snapshot_manager.py ===

from pathlib import Path
import os

def fallback_latest_matrix_path(archive_dir="output/archive"):
    """
    Finds the most recent schema_matrix_*.json in the archive directory.
    """
    archive_path = Path(archive_dir)
    if not archive_path.exists():
        return None

    matrix_files = sorted(
        [f for f in archive_path.glob("schema_matrix_*.json")],
        reverse=True
    )
    return str(matrix_files[0]) if matrix_files else None
