from functools import wraps
from flask import request
import pickle
from app import redis


def cached(timeout=5 * 60, key='view/%s'):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = key % request.path
            rv = redis.get(cache_key)
            if rv:
                return pickle.loads(rv)
            rv = f(*args, **kwargs)
            redis.setex(cache_key, timeout, pickle.dumps(rv))
            return rv
        return decorated_function
    return decorator
