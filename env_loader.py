import os
import sys
from dotenv import load_dotenv

def load_environment():
    PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)

    machine_type = os.getenv("MACHINE_TYPE", "").lower()
    env_file = ".env.work" if machine_type == "work" else ".env.asus"

    load_dotenv(env_file)
    print(f"Loaded environment from {env_file}")
