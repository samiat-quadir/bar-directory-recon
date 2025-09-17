import re

p = "logs/dc_full_run.txt"
with open(p, encoding="utf8", errors="ignore") as f:
    s = f.read()
m = re.search(r"<coverage[^>]*line-rate=\"([0-9.]+)\"", s)
if m:
    print(m.group(1))
else:
    print("")
