import subprocess
import sys

def get_conflicted_files():
    """Get a dynamic list of all conflicted files."""
    result = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=U"],
        capture_output=True, text=True, check=True
    )
    return result.stdout.strip().splitlines()

def resolve_file(file, primary_strategy, fallback_strategy):
    """Attempt to resolve conflicts with primary strategy first, fallback if fails."""
    try:
        subprocess.run(["git", "checkout", f"--{primary_strategy}", file], check=True, capture_output=True)
        print(f"✅ Resolved {file} using '{primary_strategy}' strategy.")
    except subprocess.CalledProcessError:
        print(f"⚠️ '{primary_strategy}' failed for {file}, trying '{fallback_strategy}'...")
        try:
            subprocess.run(["git", "checkout", f"--{fallback_strategy}", file], check=True, capture_output=True)
            print(f"✅ Resolved {file} using '{fallback_strategy}' strategy.")
        except subprocess.CalledProcessError as e:
            print(f"❌ Both strategies failed for {file}: {e.stderr}")
            sys.exit(1)
    subprocess.run(["git", "add", file], check=True)

def resolve_conflicts(primary_strategy="ours", fallback_strategy="theirs"):
    conflicted_files = get_conflicted_files()

    if not conflicted_files:
        print("✅ No merge conflicts detected.")
        return

    print(f"🔍 Conflicted files detected: {len(conflicted_files)}")

    for file in conflicted_files:
        resolve_file(file, primary_strategy, fallback_strategy)

    print(f"🎉 Successfully resolved all conflicts using '{primary_strategy}' with fallback to '{fallback_strategy}'.")
    print("\nNext step: run 'git rebase --continue' to finalize your rebase.")

if __name__ == "__main__":
    resolve_conflicts()
