"""
 generate-report endpoint
 to test:
 run flask app: python app.py
 bash--
 curl -N -X POST http://localhost:5000/generate-report \
-H "Content-Type: application/json" \
-d "{\"input\":\"Weak password policy and missing MFA\"}"s
"""

from flask import Blueprint, request, jsonify, Response
from middleware.rate_limit import limiter
from middleware.input_sanitize import sanitize_request_body
from services.groq_client import GroqService
import json
import time

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

    def event_stream():
        yield("data: Starting report generation...\n")
        try:
            result = groq.call_groq(system, prompt)
            text = json.dumps(result, indent =2)
            for line in text.splitlines():
                yield(f"data: {line}\n")
                time.sleep(0.15)
            yield ("data: [DONE]\n")

        except Exception:
            yield ("data: report generation failed\n")
    return Response(event_stream(), mimetype="text/event-stream")