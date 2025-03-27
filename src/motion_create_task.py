import sys
import os
import logging
import requests
from datetime import datetime, timedelta

# Add root folder to path so we can import env_loader
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from env_loader import load_environment

# Load environment (.env.asus or .env.work)
load_environment()

# Setup logging
logging.basicConfig(
    filename="motion_task_creator.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

MOTION_API_KEY = os.getenv("MOTION_API_KEY")

def create_motion_task(title, label="Auto", due_date=None, project_id=None):
    if not MOTION_API_KEY:
        logging.error("❌ MOTION_API_KEY is not set.")
        return False

    headers = {
        "Authorization": f"Bearer {MOTION_API_KEY}",
        "Content-Type": "application/json"
    }

    task_data = {
        "name": title,
        "status": "Not Started",
        "priority": "high",
        "dueDate": due_date or (datetime.utcnow() + timedelta(days=1)).isoformat() + "Z",
        "labels": [label],
        "duration": 30,
        "autoScheduled": True,
        "schedule": "Work hours"
    }

    if project_id:
        task_data["projectId"] = project_id

    try:
        response = requests.post(
            "https://api.usemotion.com/v1/tasks",
            headers=headers,
            json=task_data
        )
        response.raise_for_status()
        task_response = response.json()
        logging.info(f"✅ Task created: {title} | ID: {task_response.get('id')}")
        return task_response

    except requests.exceptions.HTTPError as errh:
        logging.error(f"❌ HTTP error occurred: {errh}")
    except Exception as e:
        logging.error(f"❌ Unexpected error: {str(e)}")

    return None

# Example usage
if __name__ == "__main__":
    result = create_motion_task("📌 Review Latest Git Auto-Commit")
    if result:
        print("✅ Motion task successfully created.")
    else:
        print("❌ Failed to create Motion task.")
