# Plugin: email_plugin | Shared | Opt-in | v1.0
from detection.email import detect_emails

from utils.snapshot_manager import save_screenshot


def apply(driver, context="post_core", config=None, logger=None):
    try:
        html = driver.page_source
        records = detect_emails(html, context=context)
        for r in records:
            r["source"] = "plugin_email"
        if logger:
            logger(f"[PLUGIN:email_plugin] Extracted {len(records)} emails.")
        save_screenshot(driver, "email_plugin_output", config=config, logger=logger)
        return records
    except Exception as e:
        if logger:
            logger(f"[PLUGIN:email_plugin] Failed: {e}", level="ERROR")
        return []
