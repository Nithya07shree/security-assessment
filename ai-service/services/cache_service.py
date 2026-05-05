import os
import json
import time
import redis
import hashlib
import logging

logger = logging.getLogger(__name__)

CACHE_TTL_SECONDS = 900
cache_hits = 0
cache_misses = 0
memory_cache = {}
REDIS_AVAILABLE = True

try:
    redis_client = redis.Redis(
        host=os.getenv(
            "REDIS_HOST",
            "localhost"
        ),
        port=int(
            os.getenv(
                "REDIS_PORT",
                6379
            )
        ),
        decode_responses=True,
        socket_connect_timeout=1,
        socket_timeout=1
    )
    redis_client.ping()
    logger.info(
        "Redis cache enabled"
    )
except Exception:
    REDIS_AVAILABLE = False
    redis_client = None
    logger.warning(
        "Redis unavailable. "
        "Using in-memory cache."
    )

def build_cache_key(text: str):
    return hashlib.sha256(
        text.encode(
            "utf-8"
        )
    ).hexdigest()

def _get_memory(key):
    item = memory_cache.get(key)
    if not item:
        return None
    if time.time() > item["expires_at"]:
        del memory_cache[key]
        return None
    return item["value"]

def _set_memory(key,value):
    memory_cache[key] = {
        "value":value,
        "expires_at":time.time() + CACHE_TTL_SECONDS
    }

def get_cached(prompt: str):
    global cache_hits
    global cache_misses
    key = build_cache_key(
        prompt
    )
    cached = None
    if REDIS_AVAILABLE:
        try:
            cached = redis_client.get(key)
        except Exception:
            logger.warning(
                "Redis read failed. "
                "Falling back "
                "to memory."
            )
    if cached is None:
        cached = _get_memory(key)
    if cached:
        cache_hits += 1
        logger.info("CACHE HIT")
        if isinstance(cached,str):
            return json.loads(cached)
        return cached
    cache_misses += 1
    logger.info("CACHE MISS")
    return None

def set_cached(prompt: str,result: dict):
    key = build_cache_key(prompt)
    payload = json.dumps(result)
    if REDIS_AVAILABLE:
        try:
            redis_client.setex(key,CACHE_TTL_SECONDS,payload)
            logger.info("Stored in Redis")
            return
        except Exception:
            logger.warning(
                "Redis write failed. "
                "Using memory cache."
            )
    _set_memory(key,result)

def should_cache(result):
    if not result:
        return False
    if not isinstance(result,dict):
        return False
    if result.get("error"):
        return False
    if result.get("is_fallback"):
        return False
    return True

def get_cache_stats():
    return {
        "backend":"redis" if REDIS_AVAILABLE else "memory",
        "hits":cache_hits,
        "misses":cache_misses,
        "memory_items":len(memory_cache)
    }