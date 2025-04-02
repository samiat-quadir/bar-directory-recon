import time
import logging
from functools import wraps

def with_retry(max_tries=3, delay=2, exceptions=(Exception,)):
    """
    Decorator to retry a function call on failure.
    Example usage:
      @with_retry(max_tries=3, delay=2)
      def fetch_data():
          ...
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(1, max_tries + 1):
                try:
                    return fn(*args, **kwargs)
                except exceptions as e:
                    logging.warning(f"[Retry] Attempt {attempt}/{max_tries} failed: {e}")
                    if attempt < max_tries:
                        time.sleep(delay)
                    else:
                        logging.error(f"[Retry] Final attempt failed. Giving up on: {fn.__name__}")
                        raise
        return wrapper
    return decorator
