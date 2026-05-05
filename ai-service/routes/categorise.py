"""
/categorise endpoint

how to use?
--bash
$ curl -X POST http://127.0.0.1:5000/categorise -H "Content-Type: application/json" -d "{\"rule\":\"Use MFA for admin accounts\"}"
"""

from flask import Blueprint, request, jsonify
from middleware.rate_limit import limiter
from middleware.input_sanitize import sanitize_request_body
from services.groq_client import GroqService

categorise_bp = Blueprint("categorise", __name__)
groq = GroqService()

CATEGORIES = [
    "Access Control",
    "Authentication",
    "Encryption",
    "Network Security",
    "Patch Management",
    "Monitoring",
    "Compliance",
    "Incident Response"
]

@categorise_bp.route("/categorise", methods=["POST"])
@limiter.limit("30 per minute")
@sanitize_request_body(["rule"])
def categorise():
    data = request.get_json()
    rule = data.get("rule")

    if not rule:
        return jsonify({"error": "rule is required"}), 400

    prompt = f"""
Classify this security control into one category only.

Categories:
{", ".join(CATEGORIES)}

Input:
{rule}

Return JSON:
{{
 "category":"...",
 "confidence":0.0,
 "reasoning":"..."
}}
"""

    system = "You are a cybersecurity classifier."

    try:
        result = groq.call_groq(system, prompt)
        return jsonify(result), 200

    except Exception as e:
        return jsonify({
            "category": "Unknown",
            "confidence": 0.0,
            "reasoning": str(e),
            "meta":ai_response.get("meta")
        }), 200