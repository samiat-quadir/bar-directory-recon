# env_loader.py
import os
import platform
from dotenv import load_dotenv

def load_environment():
    machine_name = platform.node().lower()

    if "rog" in machine_name or "asus" in machine_name:
        env_file = ".env.asus"
    elif "damg" in machine_name or "acer" in machine_name:
        env_file = ".env.work"
    else:
        raise EnvironmentError("⚠️ Unknown machine. Could not determine which .env file to load.")

    env_path = os.path.join(os.path.dirname(__file__), env_file)
    load_dotenv(env_path)
    print(f"✅ Loaded environment from {env_file}")
