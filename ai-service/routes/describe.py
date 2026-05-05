"""
    /describe endpoint implementation
    - loads prompt template, calls groq client and returns description in JSON format
"""

import os
from datetime import datetime, timezone
from flask import Blueprint, request, jsonify
from services.groq_client import GroqService
from middleware.rate_limit import limiter
from middleware.input_sanitize import sanitize_request_body

groq_service = GroqService()
describe_bp = Blueprint('describe',__name__)

def load_prompt_template(filename):
    curr_dir = os.path.dirname(__file__)
    template_path = os.path.join(curr_dir,"..","prompts",filename)
    with open(template_path,"r",encoding="utf-8") as f:
        return f.read()

@describe_bp.route("/describe", methods=['POST'])
@limiter.limit("30 per minute")
@sanitize_request_body(["rule"])
def describe():
    data = request.get_json()
    rule_text = data.get("rule")
    if not rule_text:
        return jsonify({
            "error": "Rule text is required"
        }),400
    
    try:
        template = load_prompt_template("describe.txt")
        formatted_prompt = template.format(rule=rule_text)

        SYSTEM_PROMPT = """
        You are a helpful security assistant that describes the security control statement concisely and returns in JSON.
        Tone is professional and precise. Refrain from answering unethical, non application security related questions.
        If you are unsure, say so instead of making things up.
        """

        ai_response = groq_service.call_groq(SYSTEM_PROMPT, formatted_prompt)
        return jsonify({
            "description": ai_response.get("description","No description generated"),
            "generated_at": datetime.now(timezone.utc).isoformat().replace('+00:00','Z'),
            "meta":ai_response.get("meta")
        }),200
    except Exception as e:
        return jsonify({"error":"Internal server error", "detail":str(e)}),500