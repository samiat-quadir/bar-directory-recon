# plugin_test_harness.py

"""
Test runner for plugins in isolation.

Usage:
  python plugin_test_harness.py --plugin email_plugin --html snapshots/sample.html --strict
"""

import argparse
import importlib
import os
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

from utils.record_field_validator import validate_all
from utils.logger import get_logger
from core.config_loader import ConfigManager

def load_html_into_driver(html_path: str) -> WebDriver:
    if not os.path.exists(html_path):
        raise FileNotFoundError(f"HTML file not found: {html_path}")

    with open(html_path, "r", encoding="utf-8") as f:
        html_content = f.read()

    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.get("data:text/html;charset=utf-8," + html_content)
    return driver

def main():
    parser = argparse.ArgumentParser(description="Plugin Test Harness")
    parser.add_argument("--plugin", required=True, help="Plugin name, e.g. email_plugin")
    parser.add_argument("--html", required=True, help="Path to HTML snapshot file")
    parser.add_argument("--strict", action="store_true", help="Enable strict schema validation")
    args = parser.parse_args()

    config_path = os.path.join("configs", "defaults.json")
    config = ConfigManager(config_path)
    logger = get_logger()

    # Load plugin module dynamically
    try:
        plugin_module = importlib.import_module(f"plugins.{args.plugin}")
        plugin = plugin_module
    except ImportError as e:
        print(f"[ERROR] Could not load plugin '{args.plugin}': {e}")
        return

    print(f"✅ Loaded plugin: {args.plugin}")
    driver = load_html_into_driver(args.html)
    context = "plugin_test"

    try:
        if hasattr(plugin, "apply"):
            records = plugin.apply(driver, context)
        else:
            print(f"[WARN] Plugin {args.plugin} has no .apply() method.")
            return
    except Exception as e:
        print(f"[ERROR] Error running plugin: {e}")
        return
    finally:
        driver.quit()

    print(f"🔍 Plugin returned {len(records)} records.")

    # Run schema validation
    validated, errors = validate_all(records, strict=args.strict, logger=logger)
    print(f"✅ Validation complete. {len(validated)} records | {errors} schema issues")

    # Print summary
    for rec in validated:
        print(f"- {rec['type']} → {rec.get('value')} [{rec.get('label', '')}]")

if __name__ == "__main__":
    main()
