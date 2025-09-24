# universal_recon/core/multisite_config_manager.py

import json
import os


class ConfigManager:
    def __init__(self, config_path="universal_recon/multisite_config.json"):
        self.config = {}
        if os.path.exists(config_path):
            with open(config_path, encoding="utf-8") as f:
                self.config = json.load(f)

    def get_site_config(self, site_name):
        return self.config.get(site_name, {})

    def as_dict(self):
        return self.config
