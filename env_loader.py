import os
from dotenv import load_dotenv

def load_environment():
    # Use USERNAME from environment for reliability
    current_user = os.environ.get("USERNAME", "").lower()
    
    if current_user == "samq":
        env_file = ".env.work"
    elif current_user == "samqu":
        env_file = ".env.asus"
    else:
        raise EnvironmentError(f"⚠️ Unknown user '{current_user}'. Cannot determine which .env file to load.")

    # Always resolve the path relative to this script
    env_path = os.path.join(os.path.dirname(__file__), env_file)
    load_dotenv(dotenv_path=env_path)

    print(f"✅ Loaded environment from {env_file}")

if __name__ == "__main__":
    load_environment()
