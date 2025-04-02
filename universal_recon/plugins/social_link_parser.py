# Plugin: social_link_parser | Shared | Opt-in | v0.1

from bs4 import BeautifulSoup
import re

def apply(driver, context="root"):
    html = driver.page_source
    current_url = getattr(driver, "current_url", "http://unknown")
    soup = BeautifulSoup(html, "html.parser")

    social_patterns = {
        "linkedin": re.compile(r"linkedin\.com/in/|linkedin\.com/company/"),
        "twitter": re.compile(r"twitter\.com/(?!share)"),
        "facebook": re.compile(r"facebook\.com/"),
        "instagram": re.compile(r"instagram\.com/"),
    }

    results = []

    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        for platform, pattern in social_patterns.items():
            if pattern.search(href):
                results.append({
                    "type": "social_link",
                    "value": href,
                    "category": platform,
                    "url": current_url,
                    "context": context,
                    "confidence": 1.0,
                    "source": "social_link_parser",
                    "xpath": None  # Can be enriched if needed
                })
                break  # prevent double-matching

    return results
