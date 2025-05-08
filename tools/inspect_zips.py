#!/usr/bin/env python3
# tools/inspect_zips.py

import argparse
import datetime
import json
import os
import zipfile


def inspect_zip(path):
    """Return a dict describing the contents of the zip at `path`."""
    z = zipfile.ZipFile(path, "r")
    manifest = {"zip_file": os.path.abspath(path), "scanned_at": datetime.datetime.now().isoformat(), "entries": []}
    for info in z.infolist():
        manifest["entries"].append(
            {
                "name": info.filename,
                "compressed_size": info.compress_size,
                "uncompressed_size": info.file_size,
                "compression_ratio": (round(info.compress_size / info.file_size, 3) if info.file_size else None),
            }
        )
    return manifest


def main():
    parser = argparse.ArgumentParser(description="Scan all .zip files in a directory and output a JSON manifest.")
    parser.add_argument(
        "-z", "--zip-dir", default=".", help="Directory to scan for .zip files (default: current folder)"
    )
    parser.add_argument(
        "-o",
        "--output",
        default="zip_manifest.json",
        help="Path to write the JSON manifest (default: zip_manifest.json)",
    )
    args = parser.parse_args()

    all_manifests = []
    for fname in sorted(os.listdir(args.zip_dir)):
        if fname.lower().endswith(".zip"):
            all_manifests.append(inspect_zip(os.path.join(args.zip_dir, fname)))

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(all_manifests, f, indent=2)
    print(f"✅ Wrote manifest with {len(all_manifests)} archives to {args.output}")


if __name__ == "__main__":
    main()
