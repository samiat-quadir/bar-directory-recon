import json
import os
from copy import deepcopy

DEFAULT_CONFIG = {
    "general": {
        "headless": True,
        "max_iframe_depth": 5,
        "enable_screenshots": True,
        "screenshot_dir": "screenshots",
        "enable_html_snapshots": True,
        "snapshot_dir": "snapshots",
        "output_dir": "output",
        "retry_limit": 3,
        "log_file": "logs/recon.log",
        "result_file_prefix": "recon",
        "environment_file": ".env",
    },
    "ajax_handling": {"use_jquery_check": True, "wait_timeout": 15, "poll_interval": 1},
    "pagination_support": {
        "max_pages": 20,
        "next_button_selectors": ["a.next", "button.load-more"],
        "numeric_link_pattern": "page",
        "stop_condition": "content_repeat",
        "track_page_hashes": True,
    },
    "email_extraction": {
        "detect_mailto": True,
        "detect_obfuscated_entities": True,
        "entity_map": ["&#x40;", "&#64;", "&#46;"],
    },
    "form_submission": {
        "multi_step": True,
        "capture_fields": ["input", "hidden", "select", "textarea"],
        "dynamic_fill": True,
        "form_wait_timeout": 15,
    },
    "iframe_detection": {"recursive_depth": 5, "traversal_logging": True},
    "domain_specific": {},
    "integrations": {
        "email_notifications": False,
        "git_autocommit": False,
        "google_sheets_tracking": False,
    },
}


class ConfigManager:
    def __init__(self, config_path=None, cli_overrides=None):
        self.config = deepcopy(DEFAULT_CONFIG)
        if config_path and os.path.exists(config_path):
            with open(config_path, encoding="utf-8") as f:
                file_config = json.load(f)
                self._deep_merge(self.config, file_config)
        if cli_overrides:
            self._deep_merge(self.config, cli_overrides)

    def get(self, path, default=None):
        keys = path.split(".")
        val = self.config
        for key in keys:
            val = val.get(key, {}) if isinstance(val, dict) else {}
        return val or default

    def _deep_merge(self, base, overrides):
        for k, v in overrides.items():
            if isinstance(v, dict):
                base[k] = self._deep_merge(base.get(k, {}), v)
            else:
                base[k] = v
        return base

    def as_dict(self):
        return self.config
