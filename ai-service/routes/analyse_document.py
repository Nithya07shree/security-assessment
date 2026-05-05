"""
POST /analyse-document

Accepts:
- raw text

Returns:
- structured findings

to test:
- bash --
curl -X POST http://localhost:5000/analyse-document \
-H "Content-Type: application/json" \
-d '{
"text":"Admin passwords are shared. Logs are not monitored. MFA is disabled."
}'
"""

import os
from flask import Blueprint,request,jsonify
from middleware.rate_limit import limiter
from middleware.input_sanitize import sanitize_request_body
from services.groq_client import GroqService

analyse_document_bp = Blueprint("analyse_document",__name__)
groq_service = GroqService()

def load_prompt_template(filename):
    curr_dir = os.path.dirname(__file__)
    template_path = os.path.join(curr_dir,"..","prompts",filename)
    with open(template_path,"r",encoding="utf-8") as f:
        return f.read()

@analyse_document_bp.route("/analyse-document",methods=["POST"])
@limiter.limit("10 per minute")
@sanitize_request_body(["text"])
def analyse_document():
    data = request.get_json()
    text = data.get("text")
    if not text:
        return jsonify({
            "error":"text is required"
        }), 400
    try:
        template = load_prompt_template("analyse_document.txt")
        prompt = template.format(text=text)
        SYSTEM_PROMPT = """
        You are a senior
        cybersecurity auditor.
        Return only valid JSON.
        Be concise.
        """
        ai_response = groq_service.call_groq(SYSTEM_PROMPT,prompt)
        findings = ai_response.get("findings",[])
        if not isinstance(findings,list):
            findings = []
        return jsonify({
            "findings":findings
        }), 200
    except Exception as e:
        return jsonify({
            "error":"Internal server error",
            "detail":str(e)
        }), 500