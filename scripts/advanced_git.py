#!/usr/bin/env python3
"""
Advanced Git Workflow Manager for Autonomous Development.
Handles git push conflicts and branch synchronization automatically.
"""

import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional, Tuple


class AdvancedGitWorkflow:
    """Advanced git workflow manager that handles complex scenarios."""

    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.remote_name = "origin"

    def run_command(self, cmd: List[str], description: str) -> Tuple[bool, str]:
        """Run a command and return success status and output."""
        print(f"[*] {description}...")
        try:
            result = subprocess.run(
                cmd, check=True, capture_output=True, text=True, cwd=self.workspace_path
            )
            print(f"[+] {description} completed successfully")
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            error_msg = f"[-] {description} failed: {e}"
            if e.stdout:
                error_msg += f"\nSTDOUT: {e.stdout}"
            if e.stderr:
                error_msg += f"\nSTDERR: {e.stderr}"
            print(error_msg)
            return False, error_msg

    def get_current_branch(self) -> Optional[str]:
        """Get the current branch name."""
        success, output = self.run_command(
            ["git", "branch", "--show-current"], "Getting current branch"
        )
        if success and output.strip():
            return output.strip()
        return None

    def smart_push_current_branch(self, force: bool = False) -> bool:
        """Smart push for current branch that handles various scenarios."""
        branch_name = self.get_current_branch()
        if not branch_name:
            print("[-] Could not determine current branch")
            return False

        print(f"[*] Smart push for branch: {branch_name}")

        # Step 1: Fetch latest changes
        success, _ = self.run_command(
            ["git", "fetch", self.remote_name], "Fetching latest changes"
        )
        if not success:
            print("[!] Fetch failed, attempting push anyway...")

        # Step 2: Try normal push first
        success, _ = self.run_command(
            ["git", "push", self.remote_name, branch_name], "Attempting normal push"
        )

        if success:
            return True

        # Step 3: If normal push failed, try with upstream
        success, _ = self.run_command(
            ["git", "push", "-u", self.remote_name, branch_name],
            "Attempting push with upstream",
        )

        if success:
            return True

        # Step 4: Handle conflicts
        print("[!] Push failed - handling conflicts...")

        if force:
            return self._force_push_with_backup(branch_name)
        else:
            return self._handle_push_conflict(branch_name)

    def _handle_push_conflict(self, branch_name: str) -> bool:
        """Handle push conflicts with rebase."""
        print("[*] Attempting to resolve conflicts with rebase...")

        # Try to rebase on remote
        success, _ = self.run_command(
            ["git", "pull", "--rebase", self.remote_name, branch_name],
            "Rebasing on remote changes",
        )

        if success:
            # Rebase successful, try push again
            success, _ = self.run_command(
                ["git", "push", self.remote_name, branch_name], "Pushing after rebase"
            )
            return success
        else:
            print("[-] Automatic rebase failed")
            print("[*] Manual resolution options:")
            print("    1. git rebase --abort  (cancel rebase)")
            print("    2. Resolve conflicts manually")
            print("    3. Use force push: python scripts/advanced_git.py --force")
            return False

    def _force_push_with_backup(self, branch_name: str) -> bool:
        """Force push after creating a backup."""
        # Create backup branch
        backup_branch = f"{branch_name}-backup-{int(time.time())}"
        success, _ = self.run_command(
            ["git", "branch", backup_branch], f"Creating backup branch: {backup_branch}"
        )

        if success:
            print(f"[+] Backup created: {backup_branch}")

        # Force push with lease (safer than regular force)
        success, _ = self.run_command(
            ["git", "push", "--force-with-lease", self.remote_name, branch_name],
            "Force pushing with lease",
        )

        return success

    def reset_to_remote(self) -> bool:
        """Reset local branch to match remote (destructive)."""
        branch_name = self.get_current_branch()
        if not branch_name:
            print("[-] Could not determine current branch")
            return False

        # Create backup first
        backup_branch = f"{branch_name}-local-backup-{int(time.time())}"
        self.run_command(
            ["git", "branch", backup_branch], f"Creating local backup: {backup_branch}"
        )

        # Fetch latest
        self.run_command(["git", "fetch", self.remote_name], "Fetching latest")

        # Reset to remote
        success, _ = self.run_command(
            ["git", "reset", "--hard", f"{self.remote_name}/{branch_name}"],
            "Resetting to remote branch",
        )

        return success

    def autonomous_sync_and_push(self, commit_message: Optional[str] = None) -> bool:
        """Complete autonomous workflow: format, commit, and push."""
        print("[*] Starting autonomous sync and push workflow...")

        # Step 1: Format code
        format_success = self._run_formatter()
        if not format_success:
            print("[!] Code formatting failed, continuing anyway...")

        # Step 2: Check for changes
        success, output = self.run_command(
            ["git", "status", "--porcelain"], "Checking for changes"
        )

        if not success:
            return False

        if not output.strip():
            print("[*] No changes to commit")
            return True

        # Step 3: Commit changes
        if not commit_message:
            commit_message = "Autonomous commit: Update implementation"

        success, _ = self.run_command(["git", "add", "."], "Staging all changes")
        if not success:
            return False

        success, _ = self.run_command(
            ["git", "commit", "--no-verify", "-m", commit_message], "Committing changes"
        )
        if not success:
            return False

        # Step 4: Smart push
        return self.smart_push_current_branch()

    def _run_formatter(self) -> bool:
        """Run the code formatter."""
        formatter_script = self.workspace_path / "scripts" / "format_code.py"
        if formatter_script.exists():
            success, _ = self.run_command(
                [sys.executable, str(formatter_script)], "Running code formatter"
            )
            return success
        return True


def main() -> None:
    """Main function for command-line usage."""
    import argparse

    parser = argparse.ArgumentParser(description="Advanced Git Workflow Manager")
    parser.add_argument("--force", action="store_true", help="Force push with backup")
    parser.add_argument(
        "--reset-to-remote",
        action="store_true",
        help="Reset local branch to match remote",
    )
    parser.add_argument(
        "--auto-sync", action="store_true", help="Autonomous sync, commit and push"
    )
    parser.add_argument("--message", "-m", help="Commit message for auto-sync")

    args = parser.parse_args()

    workspace = Path.cwd()
    git_workflow = AdvancedGitWorkflow(workspace)

    if args.reset_to_remote:
        success = git_workflow.reset_to_remote()
    elif args.auto_sync:
        success = git_workflow.autonomous_sync_and_push(args.message)
    else:
        # Default: smart push (with force if requested)
        success = git_workflow.smart_push_current_branch(force=args.force)

    if success:
        print("\n[+] Git workflow completed successfully!")
    else:
        print("\n[-] Git workflow failed. Check output above for details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
