"""TODO: Add docstring."""

import re

from bs4 import BeautifulSoup
from lxml import etree


def decode_obfuscated_email(text, entity_map):
    """Replace known obfuscation HTML entities with characters."""
    for entity in entity_map:
        if "40" in entity:
            text = text.replace(entity, "@")
        elif "46" in entity:
            text = text.replace(entity, ".")
    return text


def detect_emails(html_source, entity_map=None, context="root"):
    """Detects email addresses (plaintext or obfuscated) in HTML."""
    results = []
    entity_map = entity_map or ["&#x40;", "&#64;", "&#46;"]
    soup = BeautifulSoup(html_source, "html.parser")
    dom = etree.HTML(str(soup))
    email_regex = re.compile("[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]+")
    for el in soup.find_all(text=True):
        raw = el.strip()
        if not raw:
            continue
        decoded = decode_obfuscated_email(raw, entity_map)
        if email_regex.search(decoded):
            xpath = dom.getpath(el.parent) if dom is not None else None
            results.append({"type": "email", "value": decoded, "xpath": xpath, "context": context})
<<<<<<< HEAD

=======
>>>>>>> 3ccf4fd (Committing all changes)
    return results
