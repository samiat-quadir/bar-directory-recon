#!/usr/bin/env python3#!/usr/bin/env python3#!/usr/bin/env python3#!/usr/bin/env python3#!/usr/bin/env python3

"""Smart commit tool - avoid repo pollution"""

import subprocess"""Smart Git - Only commit important changes to avoid repo pollution"""

import sys

"""Smart Git Commit Tool - Only commit important changes"""

def smart_commit(msg):

    """Only commit important files"""import subprocess

    result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)

    if not result.stdout.strip():import sys"""Smart Git Commit Tool - Only commit important changes""""""

        print("No changes")

        return Falsefrom pathlib import Path

    

    important = ['src/', 'universal_recon/', 'tests/', 'scripts/', 'pyproject.toml']import subprocess

    files_to_add = []

    

    for line in result.stdout.strip().split('\n'):

        if len(line) > 3:def smart_commit(message):from pathlib import PathSmart Git Commit Strategy - Only commit important changes

            filepath = line[3:]

            if any(pattern in filepath for pattern in important):    """Smart commit that filters out noise"""

                files_to_add.append(filepath)

                print(f"✅ {filepath}")    print("🧠 Smart Git Analysis...")

            else:

                print(f"⏭️  {filepath}")    

    

    if not files_to_add:    # Get changed filesimport subprocessAvoids overwhelming the repo with excessive log files and artifacts

        print("No important files")

        return False    result = subprocess.run(['git', 'status', '--porcelain'], 

    

    subprocess.run(['git', 'reset'], capture_output=True)                          capture_output=True, text=True)def smart_add_and_commit(message):

    for f in files_to_add:

        subprocess.run(['git', 'add', f], capture_output=True)    if not result.stdout.strip():

    

    result = subprocess.run(['git', 'commit', '-m', msg], capture_output=True, text=True)        print("No changes to commit")    """Smart commit with filtering - only important files"""from pathlib import Path"""

    success = result.returncode == 0

    print(f"{'✅' if success else '❌'} {msg if success else result.stderr}")        return False

    return success

        print("🧠 Smart Git Analysis...")

if __name__ == "__main__":

    smart_commit(sys.argv[1] if len(sys.argv) == 2 else "Smart commit")    lines = result.stdout.strip().split('\n')

    include = []    

    skip = []

        # Get current status

    # Important patterns to always include

    important = [    result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)import subprocess

        'src/', 'universal_recon/', 'tests/', 'scripts/',

        'pyproject.toml', 'requirements.txt', 'README.md',    if not result.stdout.strip():

        '.gitignore', 'pytest.ini', '.github/', 'config/'

    ]        print("No changes to commit")def get_changed_files():from pathlib import Path

    

    # Patterns to always skip        return False

    noise = [

        '__pycache__/', '.pytest_cache/', '.coverage',        """Get all changed files"""from typing import List, Optional

        '*.pyc', '*.log', 'logs/debug/', 'logs/temp/',

        '*.tmp', '*.swp', '.env', '.venv/'    lines = result.stdout.strip().split('\n')

    ]

        important_files = []    try:

    for line in lines:

        if len(line) < 3:    skipped_files = []

            continue

        filepath = line[3:]            # Get unstaged changesclass SmartCommitFilter:

        

        # Skip noise    # Define patterns

        if any(pattern in filepath for pattern in noise):

            skip.append(filepath)    important_patterns = [        result = subprocess.run(    def __init__(self, project_root: str = "."):

            print(f"⏭️  Skip: {filepath}")

            continue        'src/', 'universal_recon/', 'tests/', 'scripts/', 

        

        # Include important        'pyproject.toml', 'requirements.txt', 'setup.py',            ["git", "diff", "--name-only"],        self.project_root = Path(project_root)

        if any(pattern in filepath for pattern in important):

            include.append(filepath)        '.github/', 'monitoring/', 'config/', 'Dockerfile',

            print(f"✅ Include: {filepath}")

            continue        'README.md', 'CHANGELOG.md', '.gitignore', 'pytest.ini'            capture_output=True, text=True        

        

        # Small logs/reports only    ]

        if any(x in filepath for x in ['logs/', 'reports/']):

            try:            )        # Define what we ALWAYS want to commit (high value)

                if Path(filepath).exists():

                    size_mb = Path(filepath).stat().st_size / (1024 * 1024)    skip_patterns = [

                    if size_mb < 0.5:  # Under 500KB

                        include.append(filepath)        '__pycache__/', '.pytest_cache/', '*.pyc',         unstaged = result.stdout.strip().split('\n') if result.stdout.strip() else []        self.always_include = {

                        print(f"📄 Small file: {filepath}")

                    else:        'logs/verbose/', 'logs/debug/', 'logs/temp/',

                        skip.append(filepath)

                        print(f"⏭️  Large file: {filepath}")        '*.tmp', '*.swp', '*.bak', '.env', '.venv/'                    "src/", "universal_recon/",  # Source code

                else:

                    include.append(filepath)    ]

                    print(f"📄 New file: {filepath}")

            except Exception:            # Get untracked files            "tests/", "test_",           # Tests

                skip.append(filepath)

                print(f"⏭️  Skip: {filepath}")    for line in lines:

        else:

            skip.append(filepath)        if len(line) < 3:        result = subprocess.run(            "scripts/",                  # Automation scripts

            print(f"⏭️  Skip: {filepath}")

                continue

    if not include:

        print("No important files to commit")        filepath = line[3:]  # Remove git status prefix            ["git", "ls-files", "--others", "--exclude-standard"],            "pyproject.toml", "setup.py", "requirements.txt",  # Config

        return False

            if not filepath:

    print(f"📝 Committing {len(include)} files, skipping {len(skip)}")

                continue            capture_output=True, text=True            "README.md", "CHANGELOG.md", "LICENSE",  # Documentation

    # Reset and add only important files

    subprocess.run(['git', 'reset'], capture_output=True)            

    for f in include:

        subprocess.run(['git', 'add', f], capture_output=True)        # Check if should skip        )            ".github/", "Dockerfile", "docker-compose.yml",  # CI/CD

    

    # Commit        should_skip = any(pattern in filepath for pattern in skip_patterns)

    result = subprocess.run(['git', 'commit', '-m', message], 

                          capture_output=True, text=True)        if should_skip:        untracked = result.stdout.strip().split('\n') if result.stdout.strip() else []            "monitoring/", "config/",    # Infrastructure

    if result.returncode == 0:

        print(f"✅ Success: {message}")            skipped_files.append(filepath)

        return True

    else:            print(f"⏭️  Skipping: {filepath}")                }

        print(f"❌ Failed: {result.stderr}")

        return False            continue



                return list(set(unstaged + untracked))        

if __name__ == "__main__":

    if len(sys.argv) != 2:        # Check if important

        print("Usage: python scripts/smart_commit.py 'message'")

        sys.exit(1)        is_important = any(pattern in filepath for pattern in important_patterns)    except Exception:        # Define what we SELECTIVELY commit (only if small/important)

    smart_commit(sys.argv[1])
        if is_important:

            important_files.append(filepath)        return []        self.selective_patterns = {

            print(f"✅ Including: {filepath}")

            continue            "logs/": {"max_files": 3, "max_size_mb": 1},

        

        # Check logs/reports size            "reports/": {"max_files": 5, "max_size_mb": 2},

        if any(x in filepath for x in ['logs/', 'reports/', 'coverage_']):

            try:def is_important_file(filepath):            "artifacts/": {"max_files": 3, "max_size_mb": 1},

                if Path(filepath).exists():

                    size_mb = Path(filepath).stat().st_size / (1024 * 1024)    """Check if file is important enough to commit"""            "coverage_": {"max_files": 2, "max_size_mb": 0.5},

                    if size_mb < 1.0:

                        important_files.append(filepath)    # Always include these patterns            ".log": {"max_files": 2, "max_size_mb": 0.1},

                        print(f"📄 Including small file: {filepath} ({size_mb:.2f}MB)")

                    else:    important_patterns = [        }

                        skipped_files.append(filepath)

                        print(f"⏭️  Skipping large file: {filepath} ({size_mb:.2f}MB)")        "src/", "universal_recon/", "tests/", "test_",        

                else:

                    important_files.append(filepath)        "scripts/", "pyproject.toml", "requirements.txt",        # Define what we NEVER commit (noise)

                    print(f"📄 Including: {filepath} (new file)")

            except Exception:        "README.md", "CHANGELOG.md", ".github/",        self.never_include = {

                skipped_files.append(filepath)

                print(f"⏭️  Skipping: {filepath} (error reading)")        "monitoring/", "config/", "Dockerfile"            "__pycache__/", ".pytest_cache/", ".coverage",

        else:

            skipped_files.append(filepath)    ]            "node_modules/", ".env", ".venv/",

            print(f"⏭️  Skipping: {filepath} (not important)")

                    "*.pyc", "*.pyo", "*.pyd",

    if not important_files:

        print("❌ No important files to commit after filtering")    # Never include these patterns            ".DS_Store", "Thumbs.db",

        return False

        skip_patterns = [            "logs/verbose/", "logs/debug/", "logs/temp/",

    print(f"📝 Summary: Including {len(important_files)} files, skipping {len(skipped_files)} files")

            "__pycache__/", ".pytest_cache/", ".coverage",            "*.tmp", "*.temp", "*.swp", "*.bak",

    # Add important files

    subprocess.run(['git', 'reset'], capture_output=True)  # Reset staging        "*.pyc", "*.pyo", "*.log", ".env", ".venv/",        }

    

    for filepath in important_files:        "logs/verbose/", "logs/debug/", "logs/temp/",

        try:

            result = subprocess.run(['git', 'add', filepath], capture_output=True, text=True)        "*.tmp", "*.temp", "*.swp", "*.bak"    def get_staged_files(self) -> List[str]:

            if result.returncode != 0:

                print(f"⚠️  Failed to add {filepath}: {result.stderr}")    ]        """Get currently staged files"""

        except Exception as e:

            print(f"⚠️  Error adding {filepath}: {e}")            try:

    

    # Commit    # Check if should skip            result = subprocess.run(

    try:

        result = subprocess.run(['git', 'commit', '-m', message], capture_output=True, text=True)    for pattern in skip_patterns:                ["git", "diff", "--cached", "--name-only"],

        if result.returncode == 0:

            print(f"✅ Smart commit successful: {message}")        if pattern in filepath:                capture_output=True, text=True, cwd=self.project_root

            return True

        else:            return False            )

            print(f"❌ Commit failed: {result.stderr}")

            return False                return result.stdout.strip().split('\n') if result.stdout.strip() else []

    except Exception as e:

        print(f"❌ Commit error: {e}")    # Check if important        except Exception:

        return False

    for pattern in important_patterns:            return []



if __name__ == "__main__":        if pattern in filepath:

    import sys

    if len(sys.argv) != 2:            return True    def get_unstaged_files(self) -> List[str]:

        print("Usage: python scripts/smart_commit.py 'commit message'")

        sys.exit(1)            """Get unstaged changes"""

    

    message = sys.argv[1]    # Check file size for logs/reports (only small ones)        try:

    success = smart_add_and_commit(message)

    sys.exit(0 if success else 1)    if any(x in filepath for x in ["logs/", "reports/", "coverage_"]):            result = subprocess.run(

        try:                ["git", "diff", "--name-only"],

            size_mb = Path(filepath).stat().st_size / (1024 * 1024)                capture_output=True, text=True, cwd=self.project_root

            return size_mb < 1.0  # Only include files under 1MB            )

        except Exception:            return result.stdout.strip().split('\n') if result.stdout.strip() else []

            return False        except Exception:

                return []

    return False

    def get_untracked_files(self) -> List[str]:

        """Get untracked files"""

def smart_commit(message):        try:

    """Smart commit with filtering"""            result = subprocess.run(

    print("🧠 Smart Git Analysis...")                ["git", "ls-files", "--others", "--exclude-standard"],

                    capture_output=True, text=True, cwd=self.project_root

    files = get_changed_files()            )

    if not files:            return result.stdout.strip().split('\n') if result.stdout.strip() else []

        print("No changes to commit")        except Exception:

        return False            return []

    

    # Filter files    def should_always_include(self, filepath: str) -> bool:

    important_files = []        """Check if file should always be included"""

    skipped_files = []        return any(pattern in filepath for pattern in self.always_include)

    

    for filepath in files:    def should_never_include(self, filepath: str) -> bool:

        if not filepath:        """Check if file should never be included"""

            continue        return any(pattern in filepath for pattern in self.never_include)

        if is_important_file(filepath):

            important_files.append(filepath)    def get_file_size_mb(self, filepath: str) -> float:

            print(f"✅ Including: {filepath}")        """Get file size in MB"""

        else:        try:

            skipped_files.append(filepath)            full_path = self.project_root / filepath

            print(f"⏭️  Skipping: {filepath}")            if full_path.exists():

                    return full_path.stat().st_size / (1024 * 1024)

    if not important_files:        except Exception:

        print("No important files to commit")            pass

        return False        return 0

    

    print(f"📝 Including {len(important_files)} files, skipping {len(skipped_files)}")    def should_selectively_include(self, filepath: str) -> bool:

            """Check if file passes selective inclusion criteria"""

    # Reset and add only important files        for pattern, limits in self.selective_patterns.items():

    subprocess.run(["git", "reset"], capture_output=True)            if pattern in filepath:

                    size_mb = self.get_file_size_mb(filepath)

    for filepath in important_files:                if size_mb <= limits["max_size_mb"]:

        try:                    return True

            subprocess.run(["git", "add", filepath], check=True)                else:

        except Exception as e:                    print(f"⚠️  Skipping {filepath} (too large: {size_mb:.2f}MB)")

            print(f"Failed to add {filepath}: {e}")                    return False

            return False

    # Commit

    try:    def filter_files(self, files: List[str]) -> tuple[List[str], List[str]]:

        subprocess.run(["git", "commit", "-m", message], check=True)        """Filter files into include/exclude lists"""

        print(f"✅ Smart commit successful: {message}")        include = []

        return True        exclude = []

    except Exception as e:        

        print(f"❌ Commit failed: {e}")        for filepath in files:

        return False            if not filepath:  # Skip empty strings

                continue

                

if __name__ == "__main__":            if self.should_never_include(filepath):

    import sys                exclude.append(filepath)

    if len(sys.argv) != 2:                print(f"❌ Excluding: {filepath} (blacklisted)")

        print("Usage: python smart_commit.py 'commit message'")            elif self.should_always_include(filepath):

        sys.exit(1)                include.append(filepath)

                    print(f"✅ Including: {filepath} (always include)")

    message = sys.argv[1]            elif self.should_selectively_include(filepath):

    smart_commit(message)                include.append(filepath)
                print(f"🎯 Including: {filepath} (selective)")
            else:
                exclude.append(filepath)
                print(f"⏭️  Skipping: {filepath} (not important)")
        
        return include, exclude

    def smart_add(self, commit_message: str = None) -> bool:
        """Smart add and commit only important files"""
        print("🧠 Smart Git Analysis Starting...")
        
        # Get all pending changes
        staged = self.get_staged_files()
        unstaged = self.get_unstaged_files()
        untracked = self.get_untracked_files()
        
        all_files = list(set(staged + unstaged + untracked))
        
        if not all_files:
            print("ℹ️  No changes to commit")
            return False
        
        print(f"📊 Analyzing {len(all_files)} changed files...")
        
        # Filter files
        include_files, exclude_files = self.filter_files(all_files)
        
        if not include_files:
            print("⚠️  No important files to commit after filtering")
            return False
        
        print(f"\n📝 Summary:")
        print(f"  • Including: {len(include_files)} files")
        print(f"  • Excluding: {len(exclude_files)} files")
        
        # Reset staging area
        subprocess.run(["git", "reset"], cwd=self.project_root, capture_output=True)
        
        # Add only the important files
        for filepath in include_files:
            try:
                result = subprocess.run(
                    ["git", "add", filepath],
                    cwd=self.project_root, capture_output=True, text=True
                )
                if result.returncode != 0:
                    print(f"⚠️  Failed to add {filepath}: {result.stderr}")
            except Exception as e:
                print(f"⚠️  Error adding {filepath}: {e}")
        
        # Create commit if message provided
        if commit_message:
            try:
                result = subprocess.run(
                    ["git", "commit", "-m", commit_message],
                    cwd=self.project_root, capture_output=True, text=True
                )
                if result.returncode == 0:
                    print(f"✅ Smart commit successful: {commit_message}")
                    return True
                else:
                    print(f"❌ Commit failed: {result.stderr}")
            except Exception as e:
                print(f"❌ Commit error: {e}")
        
        return False

    def create_branch_summary(self) -> str:
        """Create a summary of what's in this branch"""
        try:
            # Get commits since main
            result = subprocess.run(
                ["git", "log", "--oneline", "main..HEAD"],
                capture_output=True, text=True, cwd=self.project_root
            )
            commits = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            # Get file changes
            result = subprocess.run(
                ["git", "diff", "--name-only", "main..HEAD"],
                capture_output=True, text=True, cwd=self.project_root
            )
            changed_files = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            # Categorize changes
            source_changes = [f for f in changed_files if any(p in f for p in ["src/", "universal_recon/", "tests/"])]
            config_changes = [f for f in changed_files if any(p in f for p in ["pyproject.toml", "requirements", "config/"])]
            script_changes = [f for f in changed_files if "scripts/" in f]
            
            summary = f"""
## 📊 Branch Summary: {subprocess.run(['git', 'branch', '--show-current'], capture_output=True, text=True, cwd=self.project_root).stdout.strip()}

### 📈 Commits: {len(commits)}
{chr(10).join(f"  • {commit}" for commit in commits[:5])}
{'  • ... and more' if len(commits) > 5 else ''}

### 📁 File Changes: {len(changed_files)}
  • Source code: {len(source_changes)} files
  • Configuration: {len(config_changes)} files  
  • Scripts: {len(script_changes)} files
  • Other: {len(changed_files) - len(source_changes) - len(config_changes) - len(script_changes)} files

### 🎯 Key Changes:
{chr(10).join(f"  • {f}" for f in source_changes[:3])}
{chr(10).join(f"  • {f}" for f in config_changes[:3])}
"""
            return summary
        except Exception as e:
            return f"Error generating summary: {e}"


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Smart Git Commit Tool")
    parser.add_argument("--message", "-m", help="Commit message")
    parser.add_argument("--summary", "-s", action="store_true", help="Show branch summary")
    parser.add_argument("--dry-run", "-d", action="store_true", help="Show what would be committed")
    
    args = parser.parse_args()
    
    filter_tool = SmartCommitFilter()
    
    if args.summary:
        print(filter_tool.create_branch_summary())
        return
    
    if args.dry_run:
        print("🔍 DRY RUN - Showing what would be committed:")
        all_files = filter_tool.get_unstaged_files() + filter_tool.get_untracked_files()
        include_files, exclude_files = filter_tool.filter_files(all_files)
        print(f"\n📝 Would commit {len(include_files)} files:")
        for f in include_files:
            print(f"  ✅ {f}")
        return
    
    if args.message:
        filter_tool.smart_add(args.message)
    else:
        print("Please provide a commit message with --message")


if __name__ == "__main__":
    main()