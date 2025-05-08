# tools/resolve_venv_path.py

import getpass
import os


def resolve_venv_path():
    username = getpass.getuser().lower()
    base_path = f"C:\\Users\\{username}\\OneDrive - Digital Age Marketing Group\\Desktop\\Local Py\\Work Projects\\bar-directory-recon"
    activate_script = os.path.join(base_path, ".venv311", "Scripts", "Activate.ps1")

    if not os.path.exists(activate_script):
        raise FileNotFoundError(f"Activation script not found at: {activate_script}")

    print(f"✅ Venv activation script resolved for '{username}':\n{activate_script}")
    return activate_script


if __name__ == "__main__":
    resolve_venv_path()
