"""Build POST /recommend — return 3 actionable
recommendations as JSON array, each with action_type,
description, priority
"""

import json
import os
from flask import Blueprint, request, jsonify
from services.groq_client import GroqService
from middleware.rate_limit import limiter
from middleware.input_sanitize import sanitize_request_body

groq_service = GroqService()
recommend_bp = Blueprint('recommend',__name__)

def load_prompt_template(filename):
    curr_dir = os.path.dirname(__file__)
    template_path = os.path.join(curr_dir,"..","prompts",filename)
    with open(template_path,"r",encoding="utf-8") as f:
        return f.read()

@recommend_bp.route("/recommend",methods=['POST'])
@limiter.limit("30 per minute")
@sanitize_request_body(["rule"])
def recommend():
    data = request.get_json()
    rule_text = data.get("rule")
    if not rule_text:
        return jsonify({
            "error": "Rule text is required"
        }),400
    
    try:
        template = load_prompt_template("recommend.txt")
        formatted_prompt = template.format(rule=rule_text)

        SYSTEM_PROMPT = """
        You are a helpful security assistant that recommends security control mitigation recommendations for a given security control statement and returns a JSON response.
        Tone is professional and precise. Refrain from answering unethical, non application security related questions.
        If you are unsure, say so instead of making things up.
        """
        ai_response = groq_service.call_groq(SYSTEM_PROMPT, formatted_prompt)
        return jsonify(ai_response.get("recommendations", "No recommendations generated")),200
    except Exception as e:
        return jsonify({
            "error":"Internal server error",
            "detail":str(e)
        }),500