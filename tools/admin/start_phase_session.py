import os
from datetime import datetime

# 1. Create logs/phase_28/ if it doesn't exist
phase_log_dir = os.path.join("logs", "phase_28")
os.makedirs(phase_log_dir, exist_ok=True)

# 2. Define timestamp variable <YYYYMMDD_HHMMSS>
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

# 3. Expose timestamp and log path to subsequent scripts
phase_log_path = os.path.join(phase_log_dir, f"phase_28_{timestamp}.log")

# Option 1: Write to a config file for other scripts to read
phase_env_path = os.path.join(phase_log_dir, "phase_env.txt")
with open(phase_env_path, "w", encoding="utf-8") as f:
    f.write(f"TIMESTAMP={timestamp}\n")
    f.write(f"PHASE_LOG_PATH={phase_log_path}\n")

# Option 2: Set environment variables for subprocesses (if run from this script)
os.environ["PHASE28_TIMESTAMP"] = timestamp
os.environ["PHASE28_LOG_PATH"] = phase_log_path

# Print for debug/confirmation
print(f"Phase 28 log path: {phase_log_path}")
print(f"Phase 28 env file: {phase_env_path}")
