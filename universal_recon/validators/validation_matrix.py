import yaml
import os
from typing import Any, Dict, Optional


def load_validation_matrix(yaml_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Loads the validation matrix YAML file and returns its contents as a dictionary.
    Handles missing file gracefully (prints error, returns empty dict).
    Args:
        yaml_path (str, optional): Path to the validation matrix YAML file. Defaults to
            'universal_recon/validators/validation_matrix.yaml' (relative to project root).
    Returns:
        dict: Parsed validation matrix or empty dict if file missing.
    """
    if yaml_path is None:
        yaml_path = os.path.join(os.path.dirname(__file__), "validation_matrix.yaml")
    if not os.path.exists(yaml_path):
        print(f"[load_validation_matrix] Validation matrix not found: {yaml_path}")
        return {}
    with open(yaml_path, "r", encoding="utf-8") as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(f"[load_validation_matrix] Failed to parse validation matrix YAML: {e}")
            return {}
