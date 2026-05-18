import redis
import json
import os
from dotenv import load_dotenv

load_dotenv()

r = redis.from_url(os.getenv("REDIS_URL", "redis://localhost:6379"))

TTL = 7200   
def get(key):
    val = r.get(key)
    return json.loads(val) if val else None

def set(key, data):
    r.setex(key, TTL, json.dumps(data))