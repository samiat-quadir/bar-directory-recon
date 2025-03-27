import os
import sys
import logging
import requests
from datetime import datetime, timedelta
from env_loader import load_environment

# Load environment
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
        print("❌ MOTION_API_KEY is not set.")
        return False

    headers = {
        "Authorization": f"Bearer {MOTION_API_KEY}",
        "Content-Type": "application/json"
    }

    if not due_date:
        due_date = (datetime.now().astimezone().replace(microsecond=0) + timedelta(days=1)).isoformat()

    task_data = {
        "name": title,
        "status": "Not Started",
        "priority": "high",
        "dueDate": due_date,
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
        print(f"✅ Motion task created: {task_response.get('id')}")
        return task_response

    except requests.exceptions.HTTPError as errh:
        logging.error(f"❌ HTTP Error: {errh}")
        print(f"❌ HTTP Error: {response.status_code} - {response.text}")
    except Exception as e:
        logging.error(f"❌ Unexpected error: {str(e)}")
        print(f"❌ Unexpected error: {e}")

    return None

# ✅ ACTUALLY RUN THE FUNCTION
if __name__ == "__main__":
    result = create_motion_task("🧠 Test Motion Task - Manual Trigger")
    if result:
        print("✅ Task created successfully.")
    else:
        print("❌ Task creation failed.")
