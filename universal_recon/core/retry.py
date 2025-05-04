import functools
import time


def retry(max_tries=3, delay=1, backoff=2, exceptions=(Exception,)):
"""TODO: Add docstring."""
    def decorator(func):
    """TODO: Add docstring."""
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
        """TODO: Add docstring."""
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
