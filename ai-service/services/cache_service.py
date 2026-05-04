import os
import json
import hashlib
import redis


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

    decode_responses=True
)


cache_hits = 0
cache_misses = 0


CACHE_TTL = 900


def generate_key(
        text
):

    return hashlib.sha256(

        text.encode()

    ).hexdigest()


def get_cached(
        text
):

    global cache_hits
    global cache_misses

    key = generate_key(
        text
    )

    cached = redis_client.get(
        key
    )

    if cached:

        cache_hits += 1

        return json.loads(
            cached
        )

    cache_misses += 1

    return None


def set_cached(
        text,
        result
):

    key = generate_key(
        text
    )

    redis_client.setex(

        key,

        CACHE_TTL,

        json.dumps(
            result
        )
    )