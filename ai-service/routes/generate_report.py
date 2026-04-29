from flask import Blueprint, request, jsonify
from middleware.rate_limit import limiter
from middleware.input_sanitize import sanitize_request_body
from services.groq_client import GroqService

generate_report_bp = Blueprint("generate_report", __name__)
groq = GroqService()

@generate_report_bp.route("/generate-report", methods=["POST"])
@limiter.limit("10 per minute")
@sanitize_request_body(["input"])
def generate_report():
    data = request.get_json()
    user_input = data.get("input")

    if not user_input:
        return jsonify({"error": "input required"}), 400

    prompt = f"""
Generate professional cybersecurity assessment report.

Input:
{user_input}

Return STRICT JSON:

{{
"title":"",
"executive_summary":"",
"overview":"",
"top_items":["","",""],
"recommendations":["","",""]
}}
"""

    system = "You are a senior cybersecurity consultant."

    try:
        result = groq.call_groq(system, prompt)
        return jsonify(result), 200

    except Exception:
        return jsonify({
            "title":"Fallback Report",
            "executive_summary":"Unable to generate live report.",
            "overview":"Temporary AI outage.",
            "top_items":[],
            "recommendations":[]
        }), 200
        