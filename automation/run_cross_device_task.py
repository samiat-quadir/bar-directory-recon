#!/usr/bin/env python3
"""
Cross-Device Task Runner for ROG-LUCCI Control
Loads tasks from YAML configuration and executes them via SSH
"""

import argparse
import subprocess
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional

import yaml


class CrossDeviceTaskRunner:
    def __init__(self, config_path: str = "cross_device_tasks.yaml"):
        """Initialize the task runner with configuration file."""
        self.config_path = config_path
        self.config = self._load_config()
        self.remote_host = self.config.get("remote_host", "ROG-LUCCI")
        self.base_path = self.config.get("base_path", "C:/Code/bar-directory-recon")

    def _load_config(self) -> dict[str, Any]:
        """Load configuration from YAML file."""
        try:
            with open(self.config_path, encoding="utf-8") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"❌ Configuration file not found: {self.config_path}")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"❌ Error parsing YAML configuration: {e}")
            sys.exit(1)

    def _format_command(self, command: str, **kwargs) -> str:
        """Format command string with provided parameters."""
        # Add default formatting variables
        format_vars = {
            "date": datetime.now().strftime("%Y%m%d"),
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
            **kwargs,
        }

        try:
            return command.format(**format_vars)
        except KeyError as e:
            print(f"⚠️  Missing variable in command template: {e}")
            return command

    def _execute_ssh_command(
        self, command: str, capture_output: bool = True
    ) -> subprocess.CompletedProcess:
        """Execute command on remote host via SSH."""
        ssh_command = ["ssh", self.remote_host, command]

        print(f"🔄 Executing on {self.remote_host}: {command}")

        try:
            if capture_output:
                result = subprocess.run(
                    ssh_command,
                    capture_output=True,
                    text=True,
                    timeout=300,  # 5 minute timeout
                )
            else:
                result = subprocess.run(ssh_command, timeout=300)

            return result
        except subprocess.TimeoutExpired:
            print("⏱️  Command timed out after 5 minutes")
            return subprocess.CompletedProcess(
                ssh_command, 124, "", "Command timed out"
            )
        except Exception as e:
            print(f"❌ Error executing SSH command: {e}")
            return subprocess.CompletedProcess(ssh_command, 1, "", str(e))

    def _find_task(self, task_name: str) -> dict[str, Any] | None:
        """Find task configuration by name across all categories."""
        for category, tasks in self.config.items():
            if category in ["remote_host", "base_path"]:
                continue

            if isinstance(tasks, dict) and task_name in tasks:
                task_config = tasks[task_name].copy()
                task_config["category"] = category
                return task_config

        return None

    def run_task(self, task_name: str, **kwargs) -> bool:
        """Run a single task by name."""
        task_config = self._find_task(task_name)

        if not task_config:
            print(f"❌ Task '{task_name}' not found in configuration")
            return False

        print(f"📋 Running task: {task_name}")
        print(f"📝 Description: {task_config.get('description', 'No description')}")

        # Check if task requires admin privileges
        if task_config.get("requires_admin", False):
            print(
                "⚠️  This task requires administrator privileges on the remote machine"
            )

        # Handle workflow tasks (multiple steps)
        if "steps" in task_config:
            return self._run_workflow(task_config["steps"], **kwargs)

        # Handle single command tasks
        if "command" in task_config:
            command = self._format_command(task_config["command"], **kwargs)
            result = self._execute_ssh_command(command)

            if result.returncode == 0:
                print("✅ Task completed successfully")
                if result.stdout:
                    print("📤 Output:")
                    print(result.stdout)
                return True
            else:
                print(f"❌ Task failed with exit code {result.returncode}")
                if result.stderr:
                    print("📥 Error:")
                    print(result.stderr)
                return False

        print(f"❌ Task '{task_name}' has no executable command")
        return False

    def _run_workflow(self, steps: list[str], **kwargs) -> bool:
        """Run a workflow consisting of multiple tasks."""
        print(f"🔄 Running workflow with {len(steps)} steps")

        for i, step in enumerate(steps, 1):
            print(f"\n--- Step {i}/{len(steps)}: {step} ---")
            if not self.run_task(step, **kwargs):
                print(f"❌ Workflow failed at step {i}: {step}")
                return False

        print("✅ Workflow completed successfully")
        return True

    def list_tasks(self) -> None:
        """List all available tasks organized by category."""
        print("📋 Available Tasks:")
        print("=" * 50)

        for category, tasks in self.config.items():
            if category in ["remote_host", "base_path"]:
                continue

            if isinstance(tasks, dict):
                print(f"\n🏷️  {category.upper()}:")
                for task_name, task_config in tasks.items():
                    if isinstance(task_config, dict):
                        description = task_config.get("description", "No description")
                        print(f"  • {task_name}: {description}")

    def test_connection(self) -> bool:
        """Test SSH connection to remote host."""
        print(f"🔗 Testing connection to {self.remote_host}...")
        result = self._execute_ssh_command("echo 'Connection test successful'")

        if result.returncode == 0:
            print("✅ Connection test passed")
            return True
        else:
            print("❌ Connection test failed")
            return False


def main():
    """Main entry point for the task runner."""
    parser = argparse.ArgumentParser(
        description="Cross-Device Task Runner for ROG-LUCCI Control",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_cross_device_task.py --list
  python run_cross_device_task.py --test
  python run_cross_device_task.py connection_test
  python run_cross_device_task.py run_script --script_name main.py
  python run_cross_device_task.py health_check
        """,
    )

    parser.add_argument("task", nargs="?", help="Task name to execute")
    parser.add_argument(
        "--list", "-l", action="store_true", help="List all available tasks"
    )
    parser.add_argument("--test", "-t", action="store_true", help="Test SSH connection")
    parser.add_argument(
        "--config",
        "-c",
        default="cross_device_tasks.yaml",
        help="Path to configuration file (default: cross_device_tasks.yaml)",
    )

    # Dynamic arguments for task parameters
    parser.add_argument("--script_name", help="Script name for run_script task")
    parser.add_argument("--service_name", help="Service name for admin tasks")

    args, unknown_args = parser.parse_known_args()

    # Handle unknown arguments as key=value pairs
    kwargs = {}
    for arg in unknown_args:
        if "=" in arg:
            key, value = arg.split("=", 1)
            kwargs[key.lstrip("-")] = value

    # Initialize task runner
    try:
        runner = CrossDeviceTaskRunner(args.config)
    except Exception as e:
        print(f"❌ Failed to initialize task runner: {e}")
        sys.exit(1)

    # Handle command line arguments
    if args.list:
        runner.list_tasks()
    elif args.test:
        success = runner.test_connection()
        sys.exit(0 if success else 1)
    elif args.task:
        # Add command line arguments to kwargs
        for key, value in vars(args).items():
            if value is not None and key not in ["task", "list", "test", "config"]:
                kwargs[key] = value

        success = runner.run_task(args.task, **kwargs)
        sys.exit(0 if success else 1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
