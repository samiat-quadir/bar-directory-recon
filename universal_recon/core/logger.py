import os
from datetime import datetime


class Logger:
    def __init__(self, log_path):
        self.log_path = log_path
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        self.handle = open(log_path, "a", encoding="utf-8")
        self.log("Logger initialized.")

    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        line = f"[{level}] {timestamp} - {message}\n"
        print(line, end="")
        if self.handle:
            self.handle.write(line)
            self.handle.flush()

    def close(self):
        if self.handle:
            self.handle.close()
            self.handle = None
