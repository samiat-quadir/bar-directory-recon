import os

v = os.getenv("SCRAPER_API_KEY")
print("SCRAPER_API_KEY set?", bool(v))
