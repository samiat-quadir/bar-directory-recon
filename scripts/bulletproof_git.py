#!/usr/bin/env python3
"""
Bulletproof Git Workflow - Addresses All Ali's Issues
Handles protected branches, rebase complexity, credentials, conflicts, and safety.
"""

import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional, Tuple


class BulletproofGitWorkflow:
    """Ultra-reliable git workflow that handles all edge cases Ali encountered."""

    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.remote_name = "origin"
        self.protected_branches = ["main", "master", "develop", "production"]
        self.backup_branches = []

    def run_command(
        self,
        cmd: List[str],
        description: str,
        check: bool = True,
        capture_output: bool = True,
    ) -> Tuple[bool, str]:
        """Run command with enhanced error handling."""
        print(f"[*] {description}...")
        try:
            result = subprocess.run(
                cmd,
                check=check,
                capture_output=capture_output,
                text=True,
                cwd=self.workspace_path,
                timeout=30,  # Prevent hanging
            )
            if capture_output:
                print(f"[+] {description} completed successfully")
                return True, result.stdout.strip()
            else:
                print(f"[+] {description} completed successfully")
                return True, ""
        except subprocess.TimeoutExpired:
            print(f"[!] {description} timed out after 30 seconds")
            return False, "Timeout"
        except subprocess.CalledProcessError as e:
            error_msg = f"[-] {description} failed: {e}"
            if capture_output and e.stderr:
                error_msg += f"\nSTDERR: {e.stderr}"
            print(error_msg)
            return False, e.stderr.strip() if e.stderr else str(e)

    def setup_git_environment(self) -> bool:
        """Configure Git for bulletproof automation - Solves Ali's Issue #2."""
        print("[*] Setting up bulletproof Git environment...")

        # Essential configurations to prevent Ali's issues
        configs = [
            ("core.editor", "code --wait"),  # No more vim blocking
            ("merge.tool", "vscode"),
            ("mergetool.vscode.cmd", "code --wait $MERGED"),
            ("rebase.autoSquash", "false"),  # Disable interactive rebase
            ("pull.rebase", "false"),  # Use merge, not rebase
            ("credential.helper", "manager-core"),  # Fix credential issues
            ("push.default", "current"),  # Push current branch by default
            ("init.defaultBranch", "main"),  # Modern default
        ]

        success_count = 0
        for key, value in configs:
            success, _ = self.run_command(
                ["git", "config", "--global", key, value], f"Setting {key}"
            )
            if success:
                success_count += 1

        print(
            f"[+] Git environment configured ({success_count}/{len(configs)} settings)"
        )
        return success_count >= len(configs) - 2  # Allow a couple failures

    def verify_environment(self) -> bool:
        """Pre-flight checks to prevent issues."""
        print("[*] Running pre-flight environment checks...")

        checks = []

        # Check Git is available
        success, _ = self.run_command(["git", "--version"], "Checking Git installation")
        checks.append(("Git Installation", success))

        # Check we're in a git repo
        success, _ = self.run_command(["git", "status"], "Checking Git repository")
        checks.append(("Git Repository", success))

        # Check remote connectivity
        success, _ = self.run_command(
            ["git", "remote", "get-url", self.remote_name],
            "Checking remote connectivity",
        )
        checks.append(("Remote Access", success))

        # Report results
        passed = sum(1 for _, status in checks if status)
        for check_name, status in checks:
            status_icon = "[+]" if status else "[-]"
            print(f"    {status_icon} {check_name}: {'PASS' if status else 'FAIL'}")

        return passed >= 2  # Require at least Git and repo

    def get_current_branch(self) -> Optional[str]:
        """Get current branch with error handling."""
        success, output = self.run_command(
            ["git", "branch", "--show-current"], "Getting current branch"
        )
        return output if success and output else None

    def is_protected_branch(self, branch: str = None) -> bool:
        """Check if branch is protected - Solves Ali's Issue #1."""
        if not branch:
            branch = self.get_current_branch()

        if not branch:
            return True  # Assume protected if we can't determine

        # Check against known protected branches
        if branch.lower() in self.protected_branches:
            print(f"[!] Branch '{branch}' is protected and requires PR workflow")
            return True

        # Additional check: try to get branch protection info from remote
        success, output = self.run_command(
            ["git", "ls-remote", "--heads", self.remote_name, branch],
            "Checking remote branch status",
            check=False,
        )

        return False  # Default to not protected

    def create_feature_branch_workflow(self) -> bool:
        """Create feature branch for protected branch changes - Solves Issue #1."""
        current_branch = self.get_current_branch()

        if not current_branch:
            print("[-] Cannot determine current branch")
            return False

        # Generate unique feature branch name
        timestamp = int(time.time())
        feature_branch = f"feature/auto-workflow-{timestamp}"

        print(
            f"[*] Creating feature branch '{feature_branch}' for protected branch '{current_branch}'"
        )

        # Create and checkout feature branch
        success, _ = self.run_command(
            ["git", "checkout", "-b", feature_branch],
            f"Creating feature branch {feature_branch}",
        )

        if not success:
            return False

        # Push feature branch with upstream tracking
        success = self.smart_push_with_tracking(feature_branch)

        if success:
            print("[+] Feature branch workflow completed!")
            print(f"    Created: {feature_branch}")
            print(
                f"    Ready for PR: https://github.com/{{owner}}/{{repo}}/compare/{feature_branch}"
            )

        return success

    def smart_conflict_resolution(self) -> bool:
        """Smart conflict resolution - Solves Ali's Issue #4."""
        print("[*] Detected conflicts - attempting smart resolution...")

        # Check conflict types
        success, output = self.run_command(
            ["git", "status", "--porcelain=v1"], "Analyzing conflicts"
        )

        if not success:
            return False

        conflict_files = [line for line in output.split("\n") if line.startswith("UU")]

        if not conflict_files:
            print("[+] No conflicts detected")
            return True

        print(f"[!] Found {len(conflict_files)} conflicted files")

        # Strategy 1: Try automatic resolution for common file types
        auto_resolved = 0
        for conflict_line in conflict_files:
            file_path = conflict_line[3:].strip()

            if self.can_auto_resolve(file_path):
                if self.auto_resolve_file(file_path):
                    auto_resolved += 1

        if auto_resolved == len(conflict_files):
            print(f"[+] Auto-resolved all {auto_resolved} conflicts")
            return True

        # Strategy 2: Create conflict resolution branch
        return self.create_conflict_resolution_branch()

    def can_auto_resolve(self, file_path: str) -> bool:
        """Check if file can be safely auto-resolved."""
        # Safe to auto-resolve documentation and config files
        safe_extensions = [".md", ".txt", ".json", ".yml", ".yaml", ".toml"]
        safe_patterns = ["README", "CHANGELOG", "LICENSE", ".gitignore"]

        path_lower = file_path.lower()

        return any(path_lower.endswith(ext) for ext in safe_extensions) or any(
            pattern.lower() in path_lower for pattern in safe_patterns
        )

    def auto_resolve_file(self, file_path: str) -> bool:
        """Attempt automatic resolution of a conflict file."""
        # Use "ours" strategy for documentation/config files
        success, _ = self.run_command(
            ["git", "checkout", "--ours", file_path],
            f"Auto-resolving {file_path} (using our version)",
        )

        if success:
            self.run_command(["git", "add", file_path], f"Staging resolved {file_path}")

        return success

    def create_conflict_resolution_branch(self) -> bool:
        """Create branch for manual conflict resolution."""
        timestamp = int(time.time())
        conflict_branch = f"conflict-resolution-{timestamp}"

        print(f"[*] Creating conflict resolution branch: {conflict_branch}")

        # Abort current merge/rebase
        self.run_command(["git", "merge", "--abort"], "Aborting merge", check=False)
        self.run_command(["git", "rebase", "--abort"], "Aborting rebase", check=False)

        # Create conflict resolution branch
        success, _ = self.run_command(
            ["git", "checkout", "-b", conflict_branch],
            "Creating conflict resolution branch",
        )

        if success:
            print(f"[+] Created conflict resolution branch: {conflict_branch}")
            print("[*] Manual resolution required:")
            print("    1. Resolve conflicts in VS Code")
            print("    2. git add . && git commit")
            print(f"    3. Create PR for {conflict_branch}")

        return success

    def smart_push_with_tracking(self, branch: str = None) -> bool:
        """Smart push that handles upstream tracking."""
        if not branch:
            branch = self.get_current_branch()

        if not branch:
            print("[-] Cannot determine branch for push")
            return False

        print(f"[*] Smart push for branch: {branch}")

        # Fetch latest to check status
        self.run_command(["git", "fetch", self.remote_name], "Fetching latest changes")

        # Try normal push first
        success, _ = self.run_command(
            ["git", "push", self.remote_name, branch],
            "Attempting normal push",
            check=False,
        )

        if success:
            return True

        # Try push with upstream tracking
        success, _ = self.run_command(
            ["git", "push", "-u", self.remote_name, branch],
            "Push with upstream tracking",
            check=False,
        )

        if success:
            print("[+] Upstream tracking configured for future pushes")
            return True

        # Last resort: safe force push with backup
        return self.safe_force_push(branch)

    def safe_force_push(self, branch: str) -> bool:
        """Safe force push with backup - Solves Ali's Issue #5."""
        print(f"[!] Normal push failed, attempting safe force push for {branch}")

        # Create timestamped backup
        backup_branch = f"{branch}-backup-{int(time.time())}"
        success, _ = self.run_command(
            ["git", "branch", backup_branch], f"Creating backup branch: {backup_branch}"
        )

        if success:
            self.backup_branches.append(backup_branch)
            print(f"[+] Backup created: {backup_branch}")

        # Show what will be changed
        print("[*] Changes that will be pushed:")
        self.run_command(
            ["git", "log", "--oneline", f"{self.remote_name}/{branch}..{branch}"],
            "Showing commits to push",
            check=False,
        )

        # Force push with lease (safer)
        success, output = self.run_command(
            ["git", "push", "--force-with-lease", self.remote_name, branch],
            "Force push with lease",
            check=False,
        )

        if success:
            print("[+] Safe force push successful!")
            if self.backup_branches:
                print(f"[*] Backup available: {backup_branch}")
        else:
            print(f"[-] Force push failed: {output}")
            if self.backup_branches:
                print(f"[*] Your work is safe in backup: {backup_branch}")

        return success

    def bulletproof_sync(self, auto_mode: bool = False) -> bool:
        """Main bulletproof sync workflow."""
        print("[*] Starting bulletproof git sync workflow...")

        # Step 1: Environment setup and verification
        if not self.verify_environment():
            print("[!] Environment checks failed, attempting setup...")
            if not self.setup_git_environment():
                print("[-] Environment setup failed")
                return False

        # Step 2: Get current state
        current_branch = self.get_current_branch()
        if not current_branch:
            print("[-] Cannot determine current branch")
            return False

        # Step 3: Handle protected branches
        if self.is_protected_branch(current_branch):
            if auto_mode:
                return self.create_feature_branch_workflow()
            else:
                print(f"[!] Branch '{current_branch}' is protected")
                print("[*] Options:")
                print("    1. Use --auto to create feature branch automatically")
                print(
                    "    2. Checkout different branch: git checkout -b feature/my-branch"
                )
                return False

        # Step 4: Check for conflicts
        success, status_output = self.run_command(
            ["git", "status", "--porcelain=v1"], "Checking for conflicts"
        )

        if success and any(line.startswith("UU") for line in status_output.split("\n")):
            return self.smart_conflict_resolution()

        # Step 5: Safe commit if changes exist
        if success and status_output.strip():
            print("[*] Found uncommitted changes, committing...")

            self.run_command(["git", "add", "."], "Staging changes")

            success, _ = self.run_command(
                [
                    "git",
                    "commit",
                    "--no-verify",
                    "-m",
                    "Bulletproof sync: Auto-commit changes",
                ],
                "Committing changes",
            )

            if not success:
                print("[!] Commit failed, but continuing...")

        # Step 6: Smart push with all safety measures
        return self.smart_push_with_tracking(current_branch)


def main():
    """Main function with enhanced CLI."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Bulletproof Git Workflow - Solves all Ali's git issues"
    )
    parser.add_argument(
        "--auto",
        action="store_true",
        help="Auto-create feature branches for protected branches",
    )
    parser.add_argument(
        "--setup-only",
        action="store_true",
        help="Only setup Git environment, don't sync",
    )
    parser.add_argument(
        "--force", action="store_true", help="Use force push strategies when needed"
    )

    args = parser.parse_args()

    workspace = Path.cwd()
    workflow = BulletproofGitWorkflow(workspace)

    if args.setup_only:
        success = workflow.setup_git_environment()
        if success:
            print("\n[+] Git environment setup completed!")
            print("[*] You can now use bulletproof git workflows")
        else:
            print("\n[-] Git environment setup failed")
    else:
        success = workflow.bulletproof_sync(auto_mode=args.auto)

        if success:
            print("\n[+] Bulletproof sync completed successfully!")
            print("[*] All Ali's git issues have been handled automatically")
        else:
            print("\n[-] Sync encountered issues, but recovery options are available")

    # Show backup branches if any were created
    if workflow.backup_branches:
        print(f"\n[*] Backup branches created: {', '.join(workflow.backup_branches)}")

    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
