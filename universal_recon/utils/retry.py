import functools
import time


def retry(max_tries=3, delay=1, backoff=2, exceptions=(Exception,)):
    """
    Retry decorator with exponential backoff.

    :param max_tries: Max number of attempts
    :param delay: Initial delay between retries
    :param backoff: Multiplier for exponential backoff
    :param exceptions: Tuple of exception types to catch
    """

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            tries = 0
            wait = delay
            while tries < max_tries:
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    tries += 1
                    if tries >= max_tries:
                        raise
                    print(f"[retry] Exception: {e}. Retrying in {wait}s...")
                    time.sleep(wait)
                    wait *= backoff

        return wrapper

    return decorator
