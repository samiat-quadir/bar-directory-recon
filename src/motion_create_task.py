import os
import sys
import logging
import requests
from datetime import datetime, timedelta

# === ENV LOADING ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(BASE_DIR)
if PARENT_DIR not in sys.path:
    sys.path.append(PARENT_DIR)

from env_loader import load_environment
load_environment()

# === LOGGING ===
logging.basicConfig(
    filename="motion_task_creator.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

MOTION_API_KEY = os.getenv("MOTION_API_KEY")
MOTION_PROJECT_ID = os.getenv("MOTION_PROJECT_ID")

def create_motion_task(title, due_date=None, duration=15):
    if not MOTION_API_KEY:
        print("MOTION_API_KEY is not set.")
        return

    if not due_date:
        due_date = (datetime.now().astimezone().replace(microsecond=0) + timedelta(days=1)).isoformat()

    graphql_query = """
    mutation CreateTask($input: CreateTaskInput!) {
      createTask(input: $input) {
        id
        name
        dueDate
      }
    }
    """

    variables = {
        "input": {
            "name": title,
            "projectId": MOTION_PROJECT_ID,
            "dueDate": due_date,
            "duration": duration,
            "status": "Not Started",
            "priority": "MEDIUM",
            "autoSchedule": True
        }
    }

    headers = {
        "Authorization": f"Bearer {MOTION_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            "https://api.usemotion.com/graphql",
            headers=headers,
            json={"query": graphql_query, "variables": variables}
        )
        response.raise_for_status()
        data = response.json()

        if "errors" in data:
            print(f"Motion API error: {data['errors']}")
            logging.error(f"Motion API error: {data['errors']}")
            return None

        task_info = data['data']['createTask']
        print(f"Motion task created: {task_info['id']} - {task_info['name']}")
        logging.info(f"Task created: {task_info}")
        return task_info

    except requests.exceptions.HTTPError as errh:
        print(f"HTTP Error: {response.status_code} - {response.text}")
        logging.error(f"HTTP Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        logging.error(f"Unexpected error: {e}")

    return None

if __name__ == "__main__":
    title = f"Git Auto-Commit: {datetime.now().strftime('%B %d, %Y')}"
    create_motion_task(title)
