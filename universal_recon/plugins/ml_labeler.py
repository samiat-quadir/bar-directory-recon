"""
Plugin: ml_labeler | Shared | Opt-in | v1.0
Purpose: Label structured text fields (e.g. names, firms, bar numbers)
"""

from bs4 import BeautifulSoup
from lxml import etree

# Keywords to look for around values
FIELD_HINTS = {
    "bar_number": ["bar #", "bar number", "license number"],
    "firm_name": ["law firm", "firm", "organization"],
    "title": ["position", "title", "role"],
    "jurisdiction": ["court", "jurisdiction", "state admitted"],
}


def apply(driver, context="root"):
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    dom = etree.HTML(str(soup))
    results = []
    url = driver.current_url

    for el in soup.find_all(string=True):
        txt = el.strip()
        if not txt or len(txt) > 100:
            continue

        parent = el.parent
        context_txt = parent.get_text(" ", strip=True).lower()
        for label, hints in FIELD_HINTS.items():
            for hint in hints:
                if hint in context_txt:
                    xpath = dom.getpath(parent) if dom is not None else None
                    results.append(
                        {
                            "type": "labeled_field",
                            "value": txt,
                            "xpath": xpath,
                            "context": context,
                            "url": url,
                            "label": label,
                            "source": "ml_labeler",
                            "confidence": 0.8,
                            "category": "field",
                        }
                    )
                    break
    return results
