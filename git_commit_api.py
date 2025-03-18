from flask import Flask, jsonify
import subprocess

app = Flask(__name__)

@app.route('/trigger_git_commit', methods=['GET'])
def trigger_git_commit():
    """Trigger the Git commit script."""
    try:
        result = subprocess.run(["python", "auto_git_commit.py"], capture_output=True, text=True)
        return jsonify({"message": "Git commit triggered.", "output": result.stdout}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
