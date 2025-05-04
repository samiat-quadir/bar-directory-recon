# validators/record_field_validator_v3.py

<<<<<<< HEAD
import json
import re
from pathlib import Path
from typing import Dict, List

import yaml

SCHEMA_PATH = Path(__file__).parent.parent / "schema"
with open(SCHEMA_PATH / "field_schema.json", "r", encoding="utf-8") as f:
    FIELD_SCHEMA = json.load(f)
with open(SCHEMA_PATH / "validation_matrix.yaml", "r", encoding="utf-8") as f:
    VALIDATION_MATRIX = yaml.safe_load(f)
=======
<<<<<<< HEAD
import re

from validators.validation_matrix import load_validation_matrix

=======
import json
import re
from pathlib import Path
from typing import Dict, List

import yaml

>>>>>>> 54c6ae3 (Committing all changes)

def run_field_validators(fieldmap, verbose=False):
    matrix = load_validation_matrix()
    results = []
    for field in fieldmap.get("fields", []):
        field_name = field.get("name")
        if not field_name:
            continue

<<<<<<< HEAD
        if verbose:
            print(f"[•] Validating field: {field_name}")
=======
def run_analysis(records=None, config=None):
"""TODO: Add docstring."""
    if records is None:
        records = [{"type": "email", "value": "test@example.com", "rank": 1, "plugin": "test"}]
    return {"plugin": "record_field_validator_v3", "results": validate_records(records)}
>>>>>>> 54c6ae3 (Committing all changes)
>>>>>>> 3ccf4fd (Committing all changes)


def run_analysis(records=None, config=None):
    if records is None:
        records = [{"type": "email", "value": "test@example.com", "rank": 1, "plugin": "test"}]
    return {"plugin": "record_field_validator_v3", "results": validate_records(records)}


def validate_field(field: Dict, strict: bool = False) -> Dict:
    ftype = field.get("type")
    value = field.get("value", "")
    plugin = field.get("plugin", "record_field_validator_v3")

    result = {
        "type": ftype,
        "value": value,
        "plugin": plugin,
        "valid": True,
        "error": None,
        "score": 5,
        "rank": field.get("rank", 0),
        "severity": "none",
    }

    if not ftype or ftype not in FIELD_SCHEMA:
        result.update(
            {
                "valid": False,
                "error": "Unknown field type",
                "score": 0,
                "severity": "critical",
            }
        )
        return result

    pattern = FIELD_SCHEMA[ftype].get("pattern")
    if pattern and not re.fullmatch(pattern, value):
        result["valid"] = False
        result["error"] = f"Failed pattern: {pattern}"
        result["score"] = 2 if strict else 3
        result["severity"] = VALIDATION_MATRIX.get(ftype, {}).get("pattern_fail", "warning")

    return result


def validate_records(fields: List[Dict], strict: bool = False, verbose: bool = False) -> List[Dict]:
    return [validate_field(f, strict=strict) for f in fields]
