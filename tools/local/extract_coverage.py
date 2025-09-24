import pathlib
import re

txt = pathlib.Path("logs/roi2/coverage_report_after.txt").read_text()
m = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", txt)
observed = int(m.group(1)) if m else 0
print(observed)
