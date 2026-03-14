import time
import functools
from app.utils.logger import get_logger

logger = get_logger("RETRY_HANDLER")

def with_retries(max_retries=3, base_delay=1):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(correlation_id, order_id, *args, **kwargs):
            retries = 0
            while retries <= max_retries:
                try:
                    return func(correlation_id, order_id, *args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries > max_retries:
                        logger.error(correlation_id, order_id, "Max retries exceeded", error=str(e), function=func.__name__)
                        raise e
                    delay = base_delay * (2 ** (retries - 1))
                    logger.warning(correlation_id, order_id, "Operation failed, retrying", attempt=retries, delay=delay, error=str(e), function=func.__name__)
                    time.sleep(delay)
        return wrapper
    return decorator

class TimeoutException(Exception):
    pass

def with_timeout(seconds=5):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(correlation_id, order_id, *args, **kwargs):
            import threading
            result = [None]
            error = [None]
            
            def target():
                try:
                    result[0] = func(correlation_id, order_id, *args, **kwargs)
                except Exception as e:
                    error[0] = e
                    
            thread = threading.Thread(target=target)
            thread.start()
            thread.join(timeout=seconds)
            
            if thread.is_alive():
                logger.error(correlation_id, order_id, f"Operation timed out after {seconds}s", function=func.__name__)
                # We can't really kill the thread cleanly in Python, but we raise timeout
                raise TimeoutException(f"Execution exceeded {seconds} seconds")
                
            if error[0]:
                raise error[0]
                
            return result[0]
        return wrapper
    return decorator
