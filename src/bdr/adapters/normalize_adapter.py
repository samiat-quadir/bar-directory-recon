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


def normalize(record: dict) -> dict:
    safe = os.getenv('BDR_SAFE_MODE', '1') != '0'
    tmo = int(os.getenv('BDR_ADAPTER_TIMEOUT_MS', '500'))
    if safe:
        # fallback path
        return {**record, '_normalized': True}
    try:
        from universal_recon.utils.record_normalizer import normalize as real_normalize
        kind, res = _timeout_call(real_normalize, args=(record,), timeout_ms=tmo)
        if kind == 'ok':
            return res
        return {**record, '_normalized': True, '_adapter_fallback': kind}
    except Exception:
        return {**record, '_normalized': True, '_adapter_fallback': 'import_error'}
