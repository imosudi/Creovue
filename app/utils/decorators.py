# Creovue/utils/decorators.py

import time
import functools
import logging

# In-memory cache
_cache_store = {}

def cached(expiry_seconds=3600):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            key = (func.__name__, args, frozenset(kwargs.items()))
            now = time.time()
            if key in _cache_store:
                result, timestamp = _cache_store[key]
                if now - timestamp < expiry_seconds:
                    return result
            result = func(*args, **kwargs)
            _cache_store[key] = (result, now)
            return result
        return wrapper
    return decorator

def handle_api_error(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.exception(f"[YouTube API Error] in {func.__name__}: {e}")
            return {}  # or raise if you prefer to fail loudly
    return wrapper
