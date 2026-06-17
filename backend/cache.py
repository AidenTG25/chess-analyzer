import redis
import json
import os
from dotenv import load_dotenv

load_dotenv()

TTL = 7200

try:
    r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))
    r.ping()
    REDIS_AVAILABLE = True
except Exception:
    r = None
    REDIS_AVAILABLE = False
    print("Warning: Redis unavailable, caching disabled")

def get(key):
    if not REDIS_AVAILABLE or r is None:
        return None
    try:
        val = r.get(key)
        return json.loads(val) if val else None
    except Exception:
        return None

def set(key, data):
    if not REDIS_AVAILABLE or r is None:
        return
    try:
        r.setex(key, TTL, json.dumps(data))
    except Exception:
        pass