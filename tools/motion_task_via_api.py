#!/usr/bin/env python
"""
Motion Task API Integration.

This script creates tasks in Motion via API when MOTION_API_TOKEN is set in the environment.
"""
import json
import os
import socket
import sys
import traceback
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional, Union

import requests
from dotenv import load_dotenv

# Constants
MOTION_API_ENDPOINT = "https://api.usemotion.com/v1"
LOG_FILE = "logs/motion_task_creator.log"


def get_timestamp() -> str:
    """Return formatted timestamp for logs."""
    return datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")


def log_message(message: str, to_console: bool = True, to_file: bool = True) -> None:
    """
    Log message with timestamp to console and/or file.

    Args:
        message (str): Message to log
        to_console (bool): Whether to print to console
        to_file (bool): Whether to write to log file
    """
    timestamped_message = f"{get_timestamp()} {message}"

    if to_console:
        print(timestamped_message)

    if to_file:
        log_dir = Path(LOG_FILE).parent
        os.makedirs(log_dir, exist_ok=True)

        with open(LOG_FILE, "a", encoding="utf-8") as log_file:
            log_file.write(f"{timestamped_message}\n")


def get_project_root() -> Path:
    """Get the project root directory."""
    # Start with the current script's directory
    current_dir = Path(__file__).resolve().parent
    # Navigate up to the project root (parent of 'tools')
    return current_dir.parent


def load_environment() -> Optional[str]:
    """
    Load environment variables from .env file.

    Returns:
        Optional[str]: API token if found, None otherwise
    """
    env_path = get_project_root() / ".env"

    if not env_path.exists():
        log_message(f"[WARNING] Environment file not found at {env_path}")
        log_message("[INFO] Trying to create .env using sync_env.py...")

        # Try to run sync_env.py to create the .env file
        try:
            sync_env_script = get_project_root() / "tools" / "sync_env.py"
            if sync_env_script.exists():
                os.system(f'python "{sync_env_script}"')
                log_message("[INFO] Attempted to create .env file, checking again...")
                if not env_path.exists():
                    log_message("[ERROR] Failed to create .env file")
                    return None
            else:
                log_message("[ERROR] sync_env.py not found")
                return None
        except Exception as e:
            log_message(f"[ERROR] Error running sync_env.py: {e}")
            return None

    # Load the .env file
    load_dotenv(dotenv_path=env_path)

    # Check if the API token is set
    token = os.environ.get("MOTION_API_TOKEN")
    if not token:
        log_message("[ERROR] MOTION_API_TOKEN not set in environment")
        log_message("Please add it to your .env file and try again")
        return None

    return token


def validate_priority(priority: str) -> str:
    """
    Validate and normalize task priority.

    Args:
        priority (str): User-provided priority

    Returns:
        str: Normalized priority value
    """
    valid_priorities = {"low", "normal", "high", "urgent"}
    priority = priority.lower()

    if priority not in valid_priorities:
        log_message(f"[WARNING] Invalid priority: '{priority}'. Using 'normal' instead.")
        return "normal"

    return priority


def validate_date(date_str: str) -> Optional[str]:
    """
    Validate date string format (YYYY-MM-DD).

    Args:
        date_str (str): Date string to validate

    Returns:
        Optional[str]: Validated date string or None if invalid
    """
    try:
        # Try to parse the date
        datetime.strptime(date_str, "%Y-%m-%d")
        return date_str
    except ValueError:
        log_message(f"[ERROR] Invalid date format: '{date_str}'. Use YYYY-MM-DD format.")
        return None


def create_task(
    title: str, description: Optional[str] = None, due_date: Optional[str] = None, priority: str = "normal"
) -> Optional[Dict[str, Union[str, Dict]]]:
    """
    Create a new task in Motion via API.

    Args:
        title (str): Task title
        description (str, optional): Task description
        due_date (str, optional): Due date in ISO format (YYYY-MM-DD)
        priority (str, optional): Task priority (low, normal, high, urgent)

    Returns:
        Optional[Dict]: API response or None if failed
    """
    if not title or not title.strip():
        log_message("[ERROR] Task title cannot be empty")
        return None

    # Validate parameters
    priority = validate_priority(priority)

    if due_date:
        due_date = validate_date(due_date)
        if not due_date:
            # If date validation failed, set to tomorrow
            tomorrow = datetime.now() + timedelta(days=1)
            due_date = tomorrow.strftime("%Y-%m-%d")
            log_message(f"[INFO] Using tomorrow's date instead: {due_date}")
    else:
        # Set due date to tomorrow if not provided
        tomorrow = datetime.now() + timedelta(days=1)
        due_date = tomorrow.strftime("%Y-%m-%d")

    # Load environment and get token
    token = load_environment()
    if not token:
        return None

    # Prepare request
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}

    payload = {"title": title, "dueDate": due_date, "priority": priority}

    if description:
        payload["description"] = description

    # Log request details
    log_message(f"[INFO] Creating task: {title}")
    log_message(f"[DEBUG] API Endpoint: {MOTION_API_ENDPOINT}/tasks", to_console=False)
    log_message(f"[DEBUG] Payload: {json.dumps(payload)}", to_console=False)

    # Send the request
    try:
        response = requests.post(
            f"{MOTION_API_ENDPOINT}/tasks", headers=headers, data=json.dumps(payload), timeout=30  # Add timeout
        )

        if response.status_code == 201:
            result = response.json()
            task_id = result.get("id", "unknown")
            log_message(f"[SUCCESS] Task created: {title} (ID: {task_id})")
            return result
        else:
            log_message(f"[ERROR] Failed to create task. Status: {response.status_code}")
            log_message(f"Response: {response.text}")
            return None
    except requests.exceptions.Timeout:
        log_message("[ERROR] Request timed out. Check your internet connection.")
        return None
    except requests.exceptions.ConnectionError:
        log_message("[ERROR] Connection error. Check your internet connection.")
        return None
    except Exception as e:
        log_message(f"[ERROR] Exception while creating task: {e}")
        log_message(traceback.format_exc(), to_console=False)
        return None


def main() -> int:
    """
    Main function to demonstrate task creation.

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    log_message(f"[INFO] Motion Task API Script - Running on {socket.gethostname()}")

    if len(sys.argv) < 2:
        log_message('Usage: python motion_task_via_api.py "Task title" [description] [due_date] [priority]')
        log_message(
            'Example: python motion_task_via_api.py "Update documentation" "Add new API endpoints" 2025-05-10 high'
        )
        return 1

    # Parse arguments
    title = sys.argv[1]
    description = sys.argv[2] if len(sys.argv) > 2 else None
    due_date = sys.argv[3] if len(sys.argv) > 3 else None
    priority = sys.argv[4] if len(sys.argv) > 4 else "normal"

    # Create task
    result = create_task(title, description, due_date, priority)
    if result:
        log_message("[INFO] Task details:")
        log_message(json.dumps(result, indent=2))
        return 0
    else:
        log_message("[ERROR] Failed to create task")
        return 1


if __name__ == "__main__":
    try:
        # Create logs directory
        logs_dir = Path(LOG_FILE).parent
        logs_dir.mkdir(exist_ok=True)

        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        log_message(f"[CRITICAL] Unhandled exception: {e}")
        log_message(traceback.format_exc())
        sys.exit(1)
