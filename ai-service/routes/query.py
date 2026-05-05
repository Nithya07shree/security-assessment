"""
query endpoint

how to use?
run flask app: python app.py
--bash
curl -X POST http://127.0.0.1:5000/query -H "Content-Type: 
application/json" -d "{\"question\":\"How is encryption used?\"}"
"""

from flask import Blueprint, request, jsonify
from middleware.rate_limit import limiter
from middleware.input_sanitize import sanitize_request_body
from services.rag_pipeline import query_docs
from services.groq_client import GroqService

query_bp = Blueprint("query", __name__)
groq = GroqService()

@query_bp.route("/query", methods=["POST"])
@limiter.limit("15 per minute")
@sanitize_request_body(["question"])
def query():
    data = request.get_json()
    question = data.get("question")

    if not question:
        return jsonify({"error":"question required"}), 400

    results = query_docs(question)

    docs = results["documents"][0]
    context = "\n".join(docs)

    prompt = f"""
Use ONLY the context below.

Context:
{context}

Question:
{question}

Return JSON:
{{
 "answer":"",
 "confidence":0.0
}}
"""

    system = "You answer using retrieved security documents only."

    try:
        answer = groq.call_groq(system, prompt)

        return jsonify({
            "answer": answer["answer"],
            "confidence": answer["confidence"],
            "sources": docs,
            "meta":answer.get("meta")
        }), 200

    except Exception:
        return jsonify({
            "answer":"Unable to answer currently.",
            "confidence":0.0,
            "sources":docs
        }), 200