"""
/query endpoint for RAG pipeline.

how to use?
-- bash
curl -X POST http://127.0.0.1:5000/query -H "Content-Type: application/json" -d "{\"question\":\"How to secure passwords?\"}"
"""

from flask import Blueprint, jsonify, request
from middleware.rate_limit import limiter
from middleware.input_sanitize import sanitize_request_body
from services.rag_pipeline import query_docs

query_bp = Blueprint("query", __name__)

@query_bp.route("/query", methods=["POST"])
@limiter.limit("15 per minute")
@sanitize_request_body(["question"])
def query():
    data = request.get_json()
    question = data.get("question")

    if not question:
        return jsonify({"error": "question required"}), 400

    results = query_docs(question)

    docs = results["documents"][0]

    return jsonify({
        "question": question,
        "sources": docs
    }), 200