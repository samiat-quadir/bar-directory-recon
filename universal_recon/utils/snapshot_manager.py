# snapshot_manager.py
import os
from datetime import datetime


def save_screenshot(driver, label, config=None, logger=None):
    if not config or not config.get("general", {}).get("enable_screenshots", False):
        return
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = config["general"].get("screenshot_dir", "screenshots")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{label}_{timestamp}.png")
    driver.save_screenshot(path)
    if logger:
        logger(f"[SnapshotManager] Screenshot saved: {path}")

    if not config or not config.get("general", {}).get("enable_html_snapshots", False):
        return
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_dir = config["general"].get("snapshot_dir", "snapshots")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{label}_{timestamp}.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(driver.page_source)
    if logger:
        logger(f"[SnapshotManager] HTML snapshot saved: {path}")
