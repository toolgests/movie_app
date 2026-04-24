import os

import redis
import json

REDIS_URL = os.getenv("REDIS_URL")
r = redis.Redis(host="localhost", port=6379, decode_responses=True)


def get_cache(key):
    data = r.get(key)
    return json.loads(data) if data else None


def set_cache(key, value, expire=3600):  # 👈 ADD expire
    r.set(key, value, ex=expire)

