# import os

# import redis
# import json

# REDIS_URL = os.getenv("REDIS_URL")
# r = redis.Redis(host="localhost", port=6379, decode_responses=True)


# def get_cache(key):
#     data = r.get(key)
#     return json.loads(data) if data else None


# def set_cache(key, value, expire=3600):  # 👈 ADD expire
#     r.set(key, value, ex=expire)

import os
import redis
import json

REDIS_URL = os.getenv("REDIS_URL")

# ✅ Use Render Redis URL (IMPORTANT)
try:
    r = redis.from_url(REDIS_URL, decode_responses=True)
except:
    r = None


def get_cache(key):
    try:
        if r:
            data = r.get(key)
            return json.loads(data) if data else None
    except:
        return None


def set_cache(key, value, expire=3600):
    try:
        if r:
            # always store as string
            if isinstance(value, dict):
                value = json.dumps(value)

            r.set(key, value, ex=expire)
    except:
        pass
