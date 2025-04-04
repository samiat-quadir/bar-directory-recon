import os
from dotenv import load_dotenv
import getpass

def load_environment():
    # Use os.environ["USERNAME"] if available, otherwise fallback to getpass.getuser()
    current_user = os.environ.get("USERNAME", "").lower() or getpass.getuser().lower()
    
    if current_user == "samq":
        env_file = ".env.work"
    elif current_user == "samqu":
        env_file = ".env.asus"
    else:
        raise EnvironmentError(f"Unknown user '{current_user}'. Cannot determine which .env file to load.")
    
    # Resolve the absolute path to the env file relative to this script (project root)
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), env_file)
    load_dotenv(dotenv_path=env_path)
    print(f"Loaded environment from {env_file}")

if __name__ == "__main__":
    load_environment()
