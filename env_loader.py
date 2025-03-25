import os
from dotenv import load_dotenv

def load_environment():
    current_user = os.getlogin()
    if current_user == "samq":
        env_file = ".env.work"
    elif current_user == "samqu":
        env_file = ".env.asus"
    else:
        raise EnvironmentError("⚠️ Unknown machine. Could not determine which .env file to load.")

    load_dotenv(env_file)
    print(f"✅ Loaded environment from {env_file}")

if __name__ == "__main__":
    load_environment()
