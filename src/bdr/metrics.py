# src/bdr/metrics.py
ENABLED = False
COUNTERS = {'normalize_calls':0,'normalize_fallbacks':0,'validate_calls':0,'validate_fallbacks':0,'timeouts':0}
def enable(flag: bool):
    global ENABLED; ENABLED = bool(flag)
def inc(key: str):
    if ENABLED and key in COUNTERS: COUNTERS[key]+=1
def snapshot():
    return dict(COUNTERS)