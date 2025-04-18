import time
import functools

def retry(max_tries=3, delay=1, backoff=2, exceptions=(Exception,)):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            tries, wait = 0, delay
            while tries < max_tries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    print(f"⚠️ Retry {tries + 1}/{max_tries} after exception: {e}")
                    time.sleep(wait)
                    wait *= backoff
                    tries += 1
            raise RuntimeError(f"Function {func.__name__} failed after {max_tries} retries")
        return wrapper
    return decorator