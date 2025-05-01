# === universal_recon/core/orchestrator.py ===
from .config_loader import ConfigManager
from .driver_manager import DriverManager
from .logger import Logger


class ReconOrchestrator:
    def __init__(self, config_path=None, cli_overrides=None):
        self.config_mgr = ConfigManager(config_path=config_path, cli_overrides=cli_overrides)
        self.logger = Logger(self.config_mgr.get("general.log_file"))
        self.driver_mgr = DriverManager(self.config_mgr, self.logger)

    def run_recon(self, site_name, url):
        self.logger.log(f"Starting recon for {site_name}: {url}")
        success = self.driver_mgr.fetch_page(url)
        if not success:
            self.logger.log(f"Failed to load {url} for {site_name}", level="ERROR")
            return
        self.logger.log(f"Page loaded successfully for {site_name}")
        # Future: data detection, pagination, plugins...

    def shutdown(self):
        self.logger.log("Shutting down orchestrator.")
        self.driver_mgr.close_driver()
        self.logger.close()
