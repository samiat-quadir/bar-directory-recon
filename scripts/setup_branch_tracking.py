#!/usr/bin/env python3
"""
VS Code Branch Tracking Setup Script
Prevents "Publish Branch" prompts by ensuring proper upstream tracking.
"""

import subprocess
import sys
from pathlib import Path
from typing import Tuple, Optional


class BranchTrackingManager:
    """Manages git branch upstream tracking to prevent VS Code publish prompts."""
    
    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
    
    def run_command(self, cmd: list, description: str) -> Tuple[bool, str]:
        """Run a command and return success status and output."""
        print(f"[*] {description}...")
        try:
            result = subprocess.run(
                cmd, 
                check=True, 
                capture_output=True, 
                text=True, 
                cwd=self.workspace_path
            )
            print(f"[+] {description} completed successfully")
            return True, result.stdout.strip()
        except subprocess.CalledProcessError as e:
            error_msg = f"[-] {description} failed: {e}"
            if e.stderr:
                error_msg += f"\nSTDERR: {e.stderr}"
            print(error_msg)
            return False, e.stderr.strip() if e.stderr else ""
    
    def get_current_branch(self) -> Optional[str]:
        """Get current branch name."""
        success, output = self.run_command(
            ["git", "branch", "--show-current"], 
            "Getting current branch"
        )
        return output if success and output else None
    
    def check_upstream_tracking(self, branch: str) -> bool:
        """Check if branch has upstream tracking set."""
        success, output = self.run_command(
            ["git", "config", "--get", f"branch.{branch}.remote"],
            f"Checking upstream tracking for {branch}"
        )
        return success and output == "origin"
    
    def check_remote_branch_exists(self, branch: str) -> bool:
        """Check if remote branch exists."""
        success, _ = self.run_command(
            ["git", "ls-remote", "--heads", "origin", branch],
            f"Checking if remote branch {branch} exists"
        )
        return success
    
    def setup_upstream_tracking(self, branch: str, force_create: bool = False) -> bool:
        """Set up upstream tracking for a branch."""
        print(f"[*] Setting up upstream tracking for branch: {branch}")
        
        # Check if remote branch exists
        remote_exists = self.check_remote_branch_exists(branch)
        
        if not remote_exists:
            print(f"[!] Remote branch '{branch}' doesn't exist")
            if force_create:
                print("[*] Creating remote branch with upstream tracking...")
                success, _ = self.run_command(
                    ["git", "push", "-u", "origin", branch],
                    f"Creating and tracking remote branch {branch}"
                )
                return success
            else:
                print("[-] Cannot set upstream tracking - remote branch missing")
                print("    Use --create-remote to create the remote branch")
                return False
        
        # Remote exists, set up tracking
        success, _ = self.run_command(
            ["git", "branch", f"--set-upstream-to=origin/{branch}", branch],
            f"Setting upstream tracking to origin/{branch}"
        )
        
        if success:
            print(f"[+] Upstream tracking configured: {branch} -> origin/{branch}")
            print("[+] VS Code will no longer prompt 'Publish Branch'")
        
        return success
    
    def fix_all_branches(self) -> bool:
        """Fix upstream tracking for all local branches."""
        print("[*] Scanning all local branches...")
        
        # Get all local branches
        success, output = self.run_command(
            ["git", "branch", "--format=%(refname:short)"],
            "Getting all local branches"
        )
        
        if not success:
            return False
        
        branches = [line.strip() for line in output.split('\n') if line.strip()]
        fixed_count = 0
        
        for branch in branches:
            if branch == "main" or branch == "master":
                continue  # Skip main branches
            
            print(f"\n[*] Checking branch: {branch}")
            
            if self.check_upstream_tracking(branch):
                print(f"[+] Branch {branch} already has upstream tracking")
                continue
            
            if self.check_remote_branch_exists(branch):
                if self.setup_upstream_tracking(branch):
                    fixed_count += 1
            else:
                print(f"[!] Branch {branch} has no remote - skipping")
        
        print(f"\n[+] Fixed upstream tracking for {fixed_count} branches")
        return True
    
    def auto_setup_current_branch(self) -> bool:
        """Automatically set up current branch with proper tracking."""
        branch = self.get_current_branch()
        if not branch:
            print("[-] Could not determine current branch")
            return False
        
        print(f"[*] Auto-setting up branch: {branch}")
        
        # Check if already has tracking
        if self.check_upstream_tracking(branch):
            print(f"[+] Branch {branch} already has proper upstream tracking")
            return True
        
        # Set up tracking (create remote if needed)
        return self.setup_upstream_tracking(branch, force_create=True)


def main():
    """Main function."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="VS Code Branch Tracking Setup - Prevents 'Publish Branch' prompts"
    )
    parser.add_argument("--current", action="store_true",
                       help="Set up tracking for current branch only")
    parser.add_argument("--all", action="store_true",
                       help="Fix tracking for all local branches")
    parser.add_argument("--create-remote", action="store_true",
                       help="Create remote branch if it doesn't exist")
    parser.add_argument("--branch", 
                       help="Specific branch to set up tracking for")
    
    args = parser.parse_args()
    
    workspace = Path.cwd()
    manager = BranchTrackingManager(workspace)
    
    if args.all:
        success = manager.fix_all_branches()
    elif args.branch:
        success = manager.setup_upstream_tracking(args.branch, args.create_remote)
    else:
        # Default: set up current branch
        success = manager.auto_setup_current_branch()
    
    if success:
        print("\n[+] Branch tracking setup completed!")
        print("[*] VS Code should no longer prompt for 'Publish Branch'")
        print("[*] You can now use Ctrl+Shift+P > Git: Push normally")
    else:
        print("\n[-] Branch tracking setup failed")
        print("[*] You may need to resolve conflicts manually")
        sys.exit(1)


if __name__ == "__main__":
    main()
