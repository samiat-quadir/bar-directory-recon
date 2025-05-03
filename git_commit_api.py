import logging
import os
import subprocess
from datetime import datetime

from flask import Flask, jsonify

from notifier import send_html_notification

# Logging setup
LOG_FILE = "git_commit_api.log"
logging.basicConfig(
)

app = Flask(__name__)


@app.route("/trigger_git_commit", methods=["GET"])
def trigger_git_commit():
"""TODO: Add docstring."""
    try:
        logging.info("🔁 Git commit trigger received...")

        # Run auto_git_commit.py
        result = subprocess.run(["python", "auto_git_commit.py"], capture_output=True, text=True)
        logging.info(result.stdout)

        # Send notification email
        subject = "✅ Git Commit Triggered from ChatGPT API"
        body = f"The Git auto-commit script was triggered successfully at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.\n\nLog:\n{result.stdout}"
        send_html_notification(subject, body)

        return (
            jsonify({"status": "success", "message": "Git commit and notification sent."}),
            200,
        )

    except Exception as e:
        logging.error(f"❌ API Error: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
