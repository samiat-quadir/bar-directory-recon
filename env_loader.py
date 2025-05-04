import os

from dotenv import load_dotenv


def load_environment():
    machine_type = os.getenv("MACHINE_TYPE", "work").lower()
    env_file = f".env.{machine_type}"

    if not os.path.exists(env_file):
        raise FileNotFoundError(f"{env_file} not found.")

    load_dotenv(env_file)
    print(f"Loaded environment from {env_file}")


if __name__ == "__main__":
    load_environment()
