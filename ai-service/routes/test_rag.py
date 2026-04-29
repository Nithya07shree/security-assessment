"""
/test_rag endpoint for RAG pipeline.

how to use?
-- bash
curl -X POST http://127.0.0.1:5000/test_rag -H "Content-Type: application/json" -d "{\"question\":\"How to secure passwords?\"}"
"""

from flask import Blueprint, jsonify, request
from middleware.rate_limit import limiter
from middleware.input_sanitize import sanitize_request_body
from services.rag_pipeline import test_rag_docs

test_rag_bp = Blueprint("test_rag", __name__)

@test_rag_bp.route("/test_rag", methods=["POST"])
@limiter.limit("15 per minute")
@sanitize_request_body(["question"])
def test_rag():
    data = request.get_json()
    question = data.get("question")

    if not question:
        return jsonify({"error": "question required"}), 400

    results = test_rag_docs(question)

    docs = results["documents"][0]

    return jsonify({
        "question": question,
        "sources": docs
    }), 200