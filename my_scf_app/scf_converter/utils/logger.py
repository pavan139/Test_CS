# scf_converter/utils/logger.py

import logging
import functools

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        ch = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        ch.setFormatter(formatter)
        logger.addHandler(ch)

    return logger

def log_call(logger: logging.Logger):
    """
    Decorator to log function calls.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.debug(f"Calling {func.__name__}() with args={args}, kwargs={kwargs}")
            result = func(*args, **kwargs)
            logger.debug(f"Finished {func.__name__}() -> {result}")
            return result
        return wrapper
    return decorator
