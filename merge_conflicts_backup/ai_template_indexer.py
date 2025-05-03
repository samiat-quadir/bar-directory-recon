"""TODO: Add docstring."""

from typing import Dict, List

<<<<<<< HEAD
from typing import Dict, List

=======
>>>>>>> 3ccf4fd (Committing all changes)

def apply(records: List[Dict], context: str = "ai_template_indexer") -> List[Dict]:
    """
    Classifies grouped records (template blocks) into profile templates:
    e.g., individual, firm, hybrid, or unknown based on field composition.
    """
    templates = []
    for group in records:
        template = group.copy()
        field_types = {r["type"] for r in group.get("fields", []) if "type" in r}
        if {"name", "email", "bar_number"}.issubset(field_types):
            template_type = "individual"
        elif {"firm_name", "phone"}.issubset(field_types):
            template_type = "firm"
        elif "name" in field_types and "firm_name" in field_types:
            template_type = "hybrid"
        else:
            template_type = "unknown"
        template["template_type"] = template_type
        template["template_score"] = len(field_types) / 8.0
        template["template_confidence"] = (
            "high" if template["template_score"] > 0.75 else "medium" if template["template_score"] > 0.5 else "low"
        )
        templates.append(template)
    return templates
