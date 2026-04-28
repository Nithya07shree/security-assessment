"""
Rate Limiting configuration

- Set rate limit for how many requests each IP can make
- Default rate: 30 requests/minute for all endpoints
- /generate-report limit: 10 requests/minute specifically
- Returns http 429 response with retry_after when limit is hit
- IP based limiting used. A better implementation would be user based limiting based on JWT identity.

Tech used: 
1. flask-limiter - Built specifically for Flask, supports Redis as storage, easy to use
2. Redis - Storage backend, survives application restarts, for storing counters that lives seperate from Flask

"""

import os
import logging
from flask_limiter import Limit, Limiter
from flask_limiter.util import get_remote_address
from flask import jsonify

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL")
STORAGE_URI = REDIS_URL if REDIS_URL else "memory://"

limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["30 per minute"],
    storage_uri=STORAGE_URI,
    strategy="fixed-window",
)

def register_rate_limiting(app):
    """
    register rate limiting with Flask app
    - using a seperate function instead of initializing directly to handle custom error handling along with the limiter

    Args:
        app (_type_): flask application
    """
    limiter.init_app(app)
    _register_429_handler(app)
    logger.info("Rate limiting registered - 30 req/min default, Redis Backend")

def _register_429_handler(app):
    """
    custom 429 error handler for too many requests

    - returns a proper json body with error message, retry_after field, status code

    Args:
        app (_type_): flask app
    """
    @app.errorhandler(429)
    def rate_limit_exceeded(e):
        retry_after = _find_retry_after(str(e.description))
        logger.warning(
            f"Rate limit exceeded | "
            f"IP: {_get_ip()} | "
            f"Endpoint: {_get_endpoint()} | "
            f"Retry after: {retry_after}s"
        )

        response = jsonify({
            "error": "Too many requests",
            "detail": "You have exceeded the request rate. Please slow down.",
            "retry_after": retry_after,       # seconds until they can try again
            "retry_after_unit": "seconds",
            "status": 429
        })

        response.status_code = 429
        response.headers["Retry-After"] = str(retry_after)
        return response


def _find_retry_after(description: str):
    """
    extract retry_after value in seconds from flask limiter's error description
    
    if description cannot be parsed, return 60 as fallback
    Args:
        description (str): _description_
    """
    try:
        description = description.lower()
        if "second" in description:
            return 1
        elif "minute" in description:
            return 60
        elif "hour" in description:
            return 3600
        elif "day" in description:
            return 86400
        else:
            return 60
    except Exception:
        return 60

def _get_ip():
    """
    get IP for logging
    """
    try:
        from flask import request
        return request.remote_addr or "unknown"
    except Exception:
        return "unknown"

def _get_endpoint():
    """
    get current endpoint path for logging
    """
    try:
        from flask import request
        return request.path or "unknown"
    except Exception:
        return "unknown"

# exporting the rate limiter for route files to import it

__all__ = ["limiter", "register_rate_limiting"]