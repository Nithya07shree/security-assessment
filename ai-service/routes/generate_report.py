# Endpoint has 2 modes: sync and async.
#
# Test sync mode (old behavior):
# curl -X POST http://localhost:5000/generate-report -H "Content-Type: application/json" -d "{\"input\": \"Admin accounts do not use MFA\"}"
# Expected: status 200, response does not contain job_id.
#
# Test async mode:
# curl -X POST http://localhost:5000/generate-report -H "Content-Type: application/json" -d "{\"input\":\"Admin accounts do not use MFA\",\"async\":true}"
# Expected: status 202 with response {"job_id":"...","status":"queued"}.

# Test poll joob:
# curl http://localhost:5000/jobs/<job_id>
# first response: {"job_id":"...","status":"processing","result":null}
# run again, returns with result


import threading
import requests
from flask import Blueprint,request,jsonify
from middleware.rate_limit import limiter
from middleware.input_sanitize import sanitize_request_body
from services.ai_service import groq_service
from services.job_store import create_job,update_job

generate_report_bp=Blueprint("generate_report",__name__)

def build_prompt(user_input):
    return f"""
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

def generate_result(user_input):
    system="You are a senior cybersecurity consultant."
    prompt=build_prompt(user_input)

    try:
        return groq_service.call_groq(system,prompt)
    except Exception:
        return {
            "title":"Fallback Report",
            "executive_summary":"Unable to generate live report.",
            "overview":"Temporary AI outage.",
            "top_items":[],
            "recommendations":[]
        }

def process_job(job_id,user_input,webhook_url=None):
    update_job(job_id,"processing")
    result=generate_result(user_input)
    update_job(job_id,"completed",result)

    if webhook_url:
        try:
            requests.post(webhook_url,json={"job_id":job_id,"status":"completed"},timeout=10)
        except Exception:
            pass

@generate_report_bp.route("/generate-report",methods=["POST"])
@limiter.limit("10 per minute")
@sanitize_request_body(["input"])
def generate_report():
    data=request.get_json()

    user_input=data.get("input")
    async_mode=data.get("async",False)
    webhook_url=data.get("webhook_url")

    if not user_input:
        return jsonify({"error":"input required"}),400

    if not async_mode:
        return jsonify(generate_result(user_input)),200

    job_id=create_job()

    threading.Thread(
        target=process_job,
        args=(job_id,user_input,webhook_url),
        daemon=True
    ).start()

    return jsonify({"job_id":job_id,"status":"queued"}),202