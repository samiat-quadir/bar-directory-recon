# === utils/validation_loader.py ===

try:
    import yaml
except ImportError as e:
    raise ImportError("The 'yaml' module is required but not installed. Install it using 'pip install pyyaml'.") from e
from pathlib import Path

def load_validation_matrix(yaml_path="validators/validation_matrix.yaml"):
    """
    Loads the validator-to-plugin mapping from the YAML config file.
    """
    path = Path(yaml_path)
    if not path.exists():
        raise FileNotFoundError(f"Validation matrix not found at: {yaml_path}")

    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
