import os
import threading
import queue


def _timeout_call(fn, args=(), kwargs=None, timeout_ms=500):
    q = queue.Queue()

    def _run():
        try:
            q.put(('ok', fn(*args, **(kwargs or {}))))
        except Exception as e:
            q.put(('err', e))

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    t.join(timeout_ms / 1000.0)
    if t.is_alive():
        return ('timeout', None)
    return q.get_nowait()


def load_validators() -> dict:
    safe = os.getenv('BDR_SAFE_MODE', '1') != '0'
    tmo = int(os.getenv('BDR_ADAPTER_TIMEOUT_MS', '500'))
    if safe:
        return {'validators': [], '_adapter_fallback': 'safe'}
    try:
        from universal_recon.utils.validation_loader import load_validators as real_load
        kind, res = _timeout_call(real_load, timeout_ms=tmo)
        if kind == 'ok':
            return res
        return {'validators': [], '_adapter_fallback': kind}
    except Exception:
        return {'validators': [], '_adapter_fallback': 'import_error'}
