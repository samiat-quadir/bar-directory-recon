#!/usr/bin/env python3
"""Smart commit - only important files"""
import subprocess
import sys

def smart_commit(message):
    result = subprocess.run(["git", "status", "--porcelain"], capture_output=True, text=True)
    if not result.stdout.strip():
        return False
    
    important = ["src/", "universal_recon/", "tests/", "scripts/", "pyproject.toml"]
    files_to_add = []
    
    for line in result.stdout.strip().split("\n"):
        if len(line) > 3:
            filepath = line[3:]
            if any(p in filepath for p in important):
                files_to_add.append(filepath)
                print(f"✅ {filepath}")
            else:
                print(f"⏭️  {filepath}")
    
    if not files_to_add:
        return False
    
    subprocess.run(["git", "reset"], capture_output=True)
    for f in files_to_add:
        subprocess.run(["git", "add", f], capture_output=True)
    
    result = subprocess.run(["git", "commit", "-m", message], capture_output=True, text=True)
    print(f"✅ {message}" if result.returncode == 0 else f"❌ Failed")
    return result.returncode == 0

if __name__ == "__main__":
    smart_commit(sys.argv[1] if len(sys.argv) == 2 else "Smart commit")
