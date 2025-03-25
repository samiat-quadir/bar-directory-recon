import os
from dotenv import load_dotenv
import getpass

def load_environment():
    username = getpass.getuser().lower()

    if username == "samq":
        env_file = ".env.work"
    elif username == "samqu":
        env_file = ".env.asus"
    else:
        raise EnvironmentError(f"⚠️ Unknown machine username '{username}'. Check env_loader.py settings.")

    load_dotenv(env_file)
    print(f"✅ Loaded environment from {env_file}")

if __name__ == "__main__":
    load_environment()
