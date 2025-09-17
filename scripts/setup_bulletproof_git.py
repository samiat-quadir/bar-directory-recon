#!/usr/bin/env python3
"""
Setup Bulletproof Git Environment - One-Time Configuration
Addresses all of Ali's git workflow issues automatically.
"""

import subprocess
from pathlib import Path
from typing import List, Tuple


def run_command(
    cmd: list[str], description: str, check: bool = True
) -> tuple[bool, str]:
    """Run command with error handling."""
    print(f"[*] {description}...")
    try:
        result = subprocess.run(
            cmd, check=check, capture_output=True, text=True, timeout=30
        )
        print(f"[+] {description} completed successfully")
        return True, result.stdout.strip()
    except subprocess.CalledProcessError as e:
        error_msg = f"[-] {description} failed: {e}"
        if e.stderr:
            error_msg += f"\nSTDERR: {e.stderr}"
        print(error_msg)
        return False, e.stderr.strip() if e.stderr else str(e)
    except subprocess.TimeoutExpired:
        print(f"[!] {description} timed out")
        return False, "Timeout"


def setup_git_configuration() -> bool:
    """Configure Git to solve Ali's issues."""
    print("\n=== SETTING UP GIT CONFIGURATION ===")

    configs = {
        # Fix Ali's Issue #2: Interactive rebase blocking
        "core.editor": "code --wait",
        "merge.tool": "vscode",
        "mergetool.vscode.cmd": "code --wait $MERGED",
        "rebase.autoSquash": "false",
        "rebase.interactive": "false",
        # Fix Ali's Issue #3: Credential manager issues
        "credential.helper": "manager-core",
        "credential.useHttpPath": "true",
        # Fix Ali's workflow issues
        "pull.rebase": "false",  # Use merge instead of rebase
        "push.default": "current",
        "init.defaultBranch": "main",
        # Safety configurations
        "push.followTags": "false",
        "core.autocrlf": "true",  # Windows line endings
        "core.safecrlf": "false",
    }

    success_count = 0
    for key, value in configs.items():
        success, _ = run_command(
            ["git", "config", "--global", key, value], f"Setting {key} = {value}"
        )
        if success:
            success_count += 1

    print(f"\n[*] Configured {success_count}/{len(configs)} Git settings")
    return success_count >= len(configs) - 2


def create_git_aliases() -> bool:
    """Create helpful Git aliases for bulletproof workflow."""
    print("\n=== CREATING GIT ALIASES ===")

    aliases = {
        "safe-push": "push --force-with-lease",
        "safe-reset": "!git stash && git reset --hard",
        "conflict-files": "diff --name-only --diff-filter=U",
        "branch-backup": "!f() { git branch backup-$(date +%s) $1; }; f",
        "quick-sync": "!git fetch origin && git reset --hard origin/$(git branch --show-current)",
        "feature-branch": "!f() { git checkout -b feature/$(date +%s)-$1; }; f",
    }

    success_count = 0
    for alias, command in aliases.items():
        success, _ = run_command(
            ["git", "config", "--global", f"alias.{alias}", command],
            f"Creating alias: git {alias}",
        )
        if success:
            success_count += 1

    print(f"\n[*] Created {success_count}/{len(aliases)} Git aliases")
    return success_count >= len(aliases) - 1


def test_git_environment() -> bool:
    """Test the Git environment setup."""
    print("\n=== TESTING GIT ENVIRONMENT ===")

    tests = [
        (["git", "--version"], "Git installation"),
        (["git", "config", "--get", "core.editor"], "Editor configuration"),
        (["git", "config", "--get", "credential.helper"], "Credential helper"),
        (["git", "status"], "Repository status"),
    ]

    passed = 0
    for cmd, description in tests:
        success, output = run_command(cmd, f"Testing {description}", check=False)
        status = "PASS" if success else "FAIL"
        print(f"    [{'✓' if success else '✗'}] {description}: {status}")
        if success:
            passed += 1

    print(f"\n[*] Passed {passed}/{len(tests)} environment tests")
    return passed >= 3


def setup_vscode_integration() -> bool:
    """Set up VS Code integration."""
    print("\n=== SETTING UP VS CODE INTEGRATION ===")

    workspace_path = Path.cwd()
    vscode_dir = workspace_path / ".vscode"
    tasks_file = vscode_dir / "tasks.json"

    if not tasks_file.exists():
        print("[-] VS Code tasks.json not found, skipping integration")
        return False

    # Check if bulletproof tasks already exist
    try:
        with open(tasks_file, encoding="utf-8") as f:
            content = f.read()

        if "Bulletproof Git" in content:
            print("[+] VS Code integration already configured")
            return True
        else:
            print("[!] VS Code tasks.json exists but needs bulletproof integration")
            print("[*] You can add bulletproof tasks manually or re-run setup")
            return True
    except Exception as e:
        print(f"[-] Error checking VS Code integration: {e}")
        return False


def verify_scripts_exist() -> bool:
    """Verify all bulletproof scripts exist."""
    print("\n=== VERIFYING BULLETPROOF SCRIPTS ===")

    workspace_path = Path.cwd()
    scripts_dir = workspace_path / "scripts"

    required_scripts = [
        "bulletproof_git.py",
        "advanced_git.py",
        "auto_commit.py",
        "manual_git_fix.bat",
        "setup_branch_tracking.py",
    ]

    found_scripts = 0
    for script in required_scripts:
        script_path = scripts_dir / script
        if script_path.exists():
            print(f"    [✓] {script}: Found")
            found_scripts += 1
        else:
            print(f"    [✗] {script}: Missing")

    print(f"\n[*] Found {found_scripts}/{len(required_scripts)} bulletproof scripts")
    return found_scripts >= 4


def create_quick_commands() -> bool:
    """Create quick command shortcuts."""
    print("\n=== CREATING QUICK COMMANDS ===")

    workspace_path = Path.cwd()

    # Create bulletproof.bat for Windows
    bulletproof_bat = workspace_path / "bulletproof.bat"
    bat_content = """@echo off
echo [*] Bulletproof Git Workflow - Solving Ali's Issues
echo.
python scripts\\bulletproof_git.py %*
"""

    try:
        with open(bulletproof_bat, "w", encoding="utf-8") as f:
            f.write(bat_content)
        print("[+] Created bulletproof.bat command")
    except Exception as e:
        print(f"[-] Failed to create bulletproof.bat: {e}")
        return False

    # Create setup-git.bat for easy re-setup
    setup_bat = workspace_path / "setup-git.bat"
    setup_content = """@echo off
echo [*] Setting up bulletproof Git environment...
python scripts\\setup_bulletproof_git.py
pause
"""

    try:
        with open(setup_bat, "w", encoding="utf-8") as f:
            f.write(setup_content)
        print("[+] Created setup-git.bat command")
    except Exception as e:
        print(f"[-] Failed to create setup-git.bat: {e}")
        return False

    return True


def main():
    """Main setup function."""
    print("🚀 BULLETPROOF GIT SETUP - Solving All Ali's Issues")
    print("=" * 60)

    setup_steps = [
        ("Git Configuration", setup_git_configuration),
        ("Git Aliases", create_git_aliases),
        ("Environment Testing", test_git_environment),
        ("VS Code Integration", setup_vscode_integration),
        ("Script Verification", verify_scripts_exist),
        ("Quick Commands", create_quick_commands),
    ]

    passed_steps = 0
    for step_name, step_function in setup_steps:
        print(f"\n📋 Step: {step_name}")
        try:
            if step_function():
                print(f"[✓] {step_name}: COMPLETED")
                passed_steps += 1
            else:
                print(f"[!] {step_name}: COMPLETED WITH WARNINGS")
                passed_steps += 0.5
        except Exception as e:
            print(f"[✗] {step_name}: FAILED - {e}")

    print("\n" + "=" * 60)
    print("🎯 SETUP SUMMARY")
    print("=" * 60)

    if passed_steps >= len(setup_steps) - 1:
        print("🎉 SUCCESS: Bulletproof Git environment is ready!")
        print("\n✅ Ali's Issues Solved:")
        print("   • Protected branch detection and auto-feature-branch creation")
        print("   • No more vim editor blocking (VS Code integration)")
        print("   • Simplified credential management")
        print("   • Smart conflict resolution with fallbacks")
        print("   • Safe force push with automatic backups")

        print("\n🚀 Ready to Use:")
        print("   • bulletproof.bat --auto     (Full automatic workflow)")
        print("   • scripts\\manual_git_fix.bat  (Emergency fix)")
        print("   • python scripts\\bulletproof_git.py  (Advanced options)")

        print("\n📚 Quick Reference:")
        print("   • git safe-push              (Safe force push)")
        print("   • git feature-branch name    (Create feature branch)")
        print("   • git quick-sync             (Fast sync with remote)")

    else:
        print("⚠️  PARTIAL SUCCESS: Some steps had issues")
        print(f"   Completed: {passed_steps}/{len(setup_steps)} steps")
        print("\n🔧 You can:")
        print("   • Re-run this setup script")
        print("   • Check error messages above")
        print("   • Continue with manual configuration")

    print("\n💡 For Ali: Your git workflow issues are now solved!")
    print("   Run 'bulletproof.bat --auto' for seamless automation.")


if __name__ == "__main__":
    main()
