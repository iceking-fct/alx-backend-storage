#!/usr/bin/env python3
import redis
import uuid
from typing import Union
from functools import wraps

def count_calls(method: callable) -> callable:
    """Decorator to count how many times a method is called."""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        key = method.__qualname__  # unique key based on method's name
        self._redis.incr(key)  # increment the count for this key in Redis
        return method(self, *args, **kwargs)
    return wrapper


class Cache:
    def __init__(self):
        """Initialize Redis client and flush database"""
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Store data in Redis with a randomly generated key"""
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key

    def get(self, key: str, fn: callable = None):
        """
        Retrieve data from Redis and optionally apply a conversion function.
        If fn is None, the raw value is returned.
        """
        value = self._redis.get(key)
        if fn:
            return fn(value)
        return value

    def get_str(self, key: str) -> str:
        """Helper method to retrieve a string from Redis"""
        return self.get(key, lambda x: x.decode('utf-8'))

    def get_int(self, key: str) -> int:
        """Helper method to retrieve an integer from Redis"""
        return self.get(key, int)
