# === core/output_manager.py ===

import json
import os
from datetime import datetime


def write_json(data, path, indent=2):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent)


def timestamped_filename(base: str, ext: str = ".json", prefix: str = "") -> str:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H%M")
    return f"{prefix}{base}_{timestamp}{ext}"


def archive_file_if_exists(src_path: str, archive_dir: str = "output/archive") -> str:
    if not os.path.exists(src_path):
        return ""

    os.makedirs(archive_dir, exist_ok=True)
    filename = timestamped_filename("schema_matrix", prefix="")
    dst_path = os.path.join(archive_dir, filename)
    os.rename(src_path, dst_path)
    return dst_path
