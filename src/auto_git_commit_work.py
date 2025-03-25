# auto_git_commit_work.py (Work Desktop)
import subprocess
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv('.env.work')

# Logging configuration
logging.basicConfig(
    filename='git_commit.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    encoding='utf-8'
)

# Local Git Repository path
repo_path = os.getenv('LOCAL_GIT_REPO')

# Git operations
def run_git_commands():
    try:
        commands = [
            ['git', '-C', repo_path, 'add', '.'],
            ['git', '-C', repo_path, 'commit', '-m', '📄 Auto-commit from Work Desktop'],
            ['git', '-C', repo_path, 'push', 'origin', 'main']
        ]

        for command in commands:
            subprocess.run(command, check=True)

        logging.info('✅ Successfully committed and pushed changes.')

    except subprocess.CalledProcessError as e:
        logging.error(f'❌ Git command failed: {e}')

if __name__ == "__main__":
    run_git_commands()