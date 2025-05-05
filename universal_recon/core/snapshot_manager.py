# universal_recon/core/snapshot_manager.py

import shutil
from datetime import datetime
from pathlib import Path


class SnapshotArchiver:
    def __init__(self, matrix_path="output/schema_matrix.json", archive_dir="output/archive/"):
        self.matrix_path = Path(matrix_path)
        self.archive_dir = Path(archive_dir)

    def archive_latest_matrix(self):
        if not self.matrix_path.exists():
            print("[archiver] ❌ No schema matrix found to archive.")
            return

        self.archive_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
        dst = self.archive_dir / f"schema_matrix_{timestamp}.json"
        shutil.copy(self.matrix_path, dst)
        print(f"[archiver] ✅ Archived matrix to {dst}")
