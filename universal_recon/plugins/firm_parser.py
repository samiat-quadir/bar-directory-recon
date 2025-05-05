# Plugin: firm_parser | Shared | Opt-in | v1.0


def apply(driver, context="root"):
    """TODO: Add docstring."""
    from bs4 import BeautifulSoup
    from lxml import etree

    page_source = driver.page_source
    current_url = driver.current_url
    soup = BeautifulSoup(page_source, "html.parser")
    dom = etree.HTML(str(soup))

    firm_indicators = [
        "law firm",
        "attorneys at law",
        "LLP",
        "LLC",
        "P.C.",
        "& Associates",
        "Group",
    ]

    records = []
    for element in soup.find_all(text=True):
        text_val = element.strip()
        if not text_val or len(text_val) > 150:
            continue

        text_lower = text_val.lower()
        if any(indicator.lower() in text_lower for indicator in firm_indicators):
            try:
                xpath = dom.getpath(element.parent)
            except:
                xpath = None
            records.append(
                {
                    "type": "firm_name",
                    "value": text_val,
                    "xpath": xpath,
                    "context": context,
                    "url": current_url,
                    "confidence": 1.0,
                    "source": "plugin",
                    "category": "organization",
                }
            )

    return records
