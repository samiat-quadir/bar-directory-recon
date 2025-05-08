# tools/list_zip_contents.py

import os
import zipfile


def list_zip_contents(root_dir: str, output_file: str = "zip_contents.txt"):
    """
    Walks through root_dir, finds all .zip files, and writes each archive's
    member paths to output_file.
    """
    with open(output_file, "w", encoding="utf-8") as out:
        for dirpath, _, filenames in os.walk(root_dir):
            for fname in filenames:
                if fname.lower().endswith(".zip"):
                    full_path = os.path.join(dirpath, fname)
                    out.write(f"=== Archive: {os.path.relpath(full_path, root_dir)} ===\n")
                    try:
                        with zipfile.ZipFile(full_path, "r") as z:
                            for member in z.namelist():
                                out.write(f"{member}\n")
                    except zipfile.BadZipFile:
                        out.write("  [ERROR] Bad zip file\n")
                    out.write("\n")
    print(f"Wrote manifest to {output_file}")


if __name__ == "__main__":
    # adjust this path if your zips live elsewhere
    list_zip_contents(root_dir="universal_recon", output_file="zip_contents.txt")
