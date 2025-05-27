import time
import logging

logger = logging.getLogger(__name__)

def safe_api_call(func, retries=3, delay=2, *args, **kwargs):
    """Retries a function on exception with delay."""
    for attempt in range(1, retries + 1):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.warning(f"Attempt {attempt} failed: {e}")
            if attempt == retries:
                logger.error(f"All {retries} attempts failed for {func.__name__}")
                raise
            time.sleep(delay)
