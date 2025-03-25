import os
import requests
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    filename="motion_task_creator.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

# Get API key from environment
MOTION_API_KEY = os.getenv("MOTION_API_KEY")

if not MOTION_API_KEY:
    logging.error("❌ MOTION_API_KEY is not set. Please check your .env file.")
    exit("Missing API key.")

# Task creation function
def create_motion_task(title, due_date=None, projectId=None):
    headers = {
        "Authorization": f"Bearer {MOTION_API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "name": title,
        "status": "Not Started",
        "priority": "high",
        "dueDate": due_date or (datetime.utcnow() + timedelta(days=1)).isoformat() + "Z"
    }

    if projectId:
        data["projectId"] = projectId

    try:
        response = requests.post(
            "https://api.usemotion.com/v1/tasks",
            json=data,
            headers=headers
        )
        response.raise_for_status()
        logging.info(f"✅ Task created: {title}")
        return True

    except requests.exceptions.HTTPError as err:
        logging.error(f"❌ HTTP error: {err}")
    except Exception as e:
        logging.error(f"❌ Unexpected error: {str(e)}")

    return False


# Example usage
if __name__ == "__main__":
    task_title = "🔁 Git Commit Auto-Check"
    create_motion_task(task_title)
