"""Logging configuration loader."""
import os
import logging.config
import yaml
from pathlib import Path
from typing import Optional

def setup_logging(
    config_path: Optional[str] = None,
    default_level: int = logging.INFO
) -> None:
    """Set up logging configuration from YAML file.
    
    Args:
        config_path: Optional path to logging config YAML file
        default_level: Default logging level if config file not found
    """
    if config_path is None:
        config_path = os.path.join("config", "logging.yaml")
    
    config_path = Path(config_path)
    
    if config_path.exists():
        with open(config_path, "rt", encoding="utf-8") as f:
            try:
                config = yaml.safe_load(f)
                # Ensure log directories exist
                for handler in config.get("handlers", {}).values():
                    if "filename" in handler:
                        log_dir = os.path.dirname(handler["filename"])
                        os.makedirs(log_dir, exist_ok=True)
                
                logging.config.dictConfig(config)
                logging.info(f"Logging configuration loaded from {config_path}")
            except Exception as e:
                print(f"Error loading logging configuration: {e}")
                setup_default_logging(default_level)
    else:
        setup_default_logging(default_level)

def setup_default_logging(level: int = logging.INFO) -> None:
    """Set up basic default logging configuration.
    
    Args:
        level: Logging level to use
    """
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    logging.warning("Using default logging configuration")