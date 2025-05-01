import os
from pathlib import Path

from dotenv import load_dotenv


def load_environment():
    """
    Load environment variables based on MACHINE_TYPE.
    Looks for .env.<machine_type> in this script's folder; if missing,
    falls back to .env. Raises an error listing available .env* files if none found.
    """
    project_root = Path(__file__).resolve().parent

    # Clean up MACHINE_TYPE: strip any quotes, default to 'work'
    raw = os.getenv("MACHINE_TYPE", "work")
    machine_type = raw.strip('"').strip("'").lower()

    # Determine file paths
    env_specific = project_root / f".env.{machine_type}"
    env_default = project_root / ".env"

    # Choose the file
    if env_specific.exists():
        env_file = env_specific
    elif env_default.exists():
        env_file = env_default
        print(f"WARNING: {env_specific.name} not found; using fallback {env_file.name}")
    else:
        available = [p.name for p in project_root.glob(".env*")]
        raise FileNotFoundError(
            "No .env file found!\n"
            f"Tried: {env_specific.name} and {env_default.name}\n"
            f"Available: {available}"
        )

    # Load and report
    load_dotenv(env_file)
    print(f"Loaded environment from {env_file.name}")


if __name__ == "__main__":
    load_environment()
