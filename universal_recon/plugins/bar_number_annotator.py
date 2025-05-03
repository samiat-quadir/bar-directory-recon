# Plugin: bar_number_annotator | Shared | Opt-in | v0.1
# Description: Detects attorney bar numbers using regex and heuristic parsing.
# Author: Claude 3.7

import re

from bs4 import BeautifulSoup
from lxml import etree

BAR_PATTERNS = [
    re.compile(r"\b(?:Bar\s*#|Bar\s*Number|License\s*#)[:\s]*([A-Z0-9\-]+)\b", re.IGNORECASE),
    re.compile(r"\b([A-Z]{2}\d{6})\b"),  # Example: CA123456
    re.compile(r"\b\d{6,9}\b"),  # Fallback for pure numeric bar numbers
]


def apply(driver, context="root"):
"""TODO: Add docstring."""
    records = []
    try:
        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")
        dom = etree.HTML(str(soup))

        for tag in soup.find_all(text=True):
            text = tag.strip()
            if not text or len(text) > 120:
                continue
            for pattern in BAR_PATTERNS:
                match = pattern.search(text)
                if match:
                    bar_id = match.group(1)
                    xpath = dom.getpath(tag.parent) if hasattr(dom, "getpath") else None
                    records.append(
                        {
                            "type": "bar_number",
                            "value": bar_id,
                            "xpath": xpath,
                            "context": context,
                            "url": driver.current_url,
                            "confidence": 1.0,
                            "source": "plugin",
                            "category": "credential",
                        }
                    )
                    break
    except Exception as e:
        print(f"[bar_number_annotator] Error: {e}")
    return records
