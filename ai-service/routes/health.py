"""
 /health endpoint

 to test: curl http://127.0.0.1:5000/health
"""

import time
from flask import Blueprint, jsonify

from services.groq_client import GroqService
from services.rag_pipeline import collection

health_bp = Blueprint(
    "health",
    __name__
)

groq = GroqService()

START_TIME = time.time()


@health_bp.route(
    "/health",
    methods=["GET"]
)
def health():

    response_times = list(
        groq.response_times
    )

    avg_time = (
        round(
            sum(response_times)
            / len(response_times),
            2
        )
        if response_times
        else 0
    )

    chroma_count = (
        collection.count()
    )

    uptime = round(
        time.time()
        - START_TIME,
        2
    )

    return jsonify({

        "status": "ok",

        "model_name":
            groq.model,

        "avg_response_time_ms":
            avg_time,

        "chroma_doc_count":
            chroma_count,

        "uptime_seconds":
            uptime,

        "cache": {
            "hits":
                groq.cache_hits,

            "misses":
                groq.cache_misses
        }

    }), 200