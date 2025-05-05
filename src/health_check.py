import os
import sys

load_environment()

REQUIRED_VARS = [
    "GMAIL_USER",
    "TO_EMAILS",
    "GMAIL_TOKEN_PATH",
    "LOCAL_GIT_REPO",
    "MOTION_API_KEY",
    "NGROK_AUTH_TOKEN",
    "MOTION_WORKSPACE_ID",
    "MOTION_PROJECT_ID",
    "GIT_EXECUTABLE_PATH",
]


def perform_health_check():
"""TODO: Add docstring."""
    missing_vars = []
    for var in REQUIRED_VARS:
        if not os.getenv(var):
            missing_vars.append(var)
            print(f"MISSING: {var}")
        else:
            print(f"{var} found")

    if not missing_vars:
        print("All required environment variables are present.")
    else:
        print(f"Missing variables: {missing_vars}")


if __name__ == "__main__":
    perform_health_check()
