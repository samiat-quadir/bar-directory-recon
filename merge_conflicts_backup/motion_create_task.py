import logging
import os
<<<<<<< HEAD
=======
import sys
>>>>>>> 3ccf4fd (Committing all changes)
from datetime import datetime, timedelta

import requests

# Load project path dynamically
from project_path import set_root_path

set_root_path()

from env_loader import load_environment

load_environment()

# Setup logging
logging.basicConfig(
    filename="motion_task_creator.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8",
)

MOTION_API_KEY = os.getenv("MOTION_API_KEY")
MOTION_PROJECT_ID = os.getenv("MOTION_PROJECT_ID")


def create_motion_task(title, label="Auto", due_date=None, duration=15, priority="high"):
"""TODO: Add docstring."""
    if not MOTION_API_KEY:
        logging.error("MOTION_API_KEY is not set.")
        print("MOTION_API_KEY is not set.")
        return False

    endpoint = "https://api.usemotion.com/graphql"
<<<<<<< HEAD
    headers = {
        "Authorization": f"Bearer {MOTION_API_KEY}",
        "Content-Type": "application/json",
    }
=======
    headers = {"Authorization": f"Bearer {MOTION_API_KEY}", "Content-Type": "application/json"}
>>>>>>> 3ccf4fd (Committing all changes)

    query = """
    mutation CreateTask($input: TaskInput!) {
        createTask(input: $input) {
            task {
                id
                name
            }
        }
    }
    """

    if not due_date:
        due_date = (datetime.now().astimezone() + timedelta(days=1)).replace(microsecond=0).isoformat()

    variables = {
        "input": {
            "workspaceId": os.getenv("MOTION_WORKSPACE_ID"),
            "projectId": MOTION_PROJECT_ID,
            "name": title,
            "status": "Not Started",
            "priority": priority,
            "dueDate": due_date,
            "labels": [label],
            "duration": duration,
            "autoScheduled": True,
            "schedule": "Work hours",
        }
    }

    try:
        response = requests.post(endpoint, headers=headers, json={"query": query, "variables": variables}, timeout=10)
        response.raise_for_status()
        task_response = response.json()

        if "errors" in task_response:
            logging.error(f"Motion API errors: {task_response['errors']}")
            print(f"Motion API errors: {task_response['errors']}")
            return None

        task_info = task_response.get("data", {}).get("createTask", {}).get("task")
        if task_info:
            logging.info(f"Task created successfully: {task_info['id']} - {task_info['name']}")
            print(f"Task created successfully: {task_info['id']}")
            return task_info
        else:
            logging.error("Task creation failed with unknown error.")
            print("Task creation failed.")
            return None

    except requests.exceptions.HTTPError as err:
        logging.error(f"HTTP Error: {err.response.status_code} - {err.response.text}")
        print(f"HTTP Error: {err.response.status_code} - {err.response.text}")
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print(f"Unexpected error: {e}")

    return None


if __name__ == "__main__":
    create_motion_task("Review Auto Git Commit")
