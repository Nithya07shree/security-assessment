"""
batch processing
- reduces network overhead, improves throughput, and prevents upstream LLM rate-limit spikes

how to work?
start flask app
1. bash--
curl -X POST http://localhost:5000/batch-process \
-H "Content-Type: application/json" \
-d "{\"items\":[{\"rule\":\"MFA missing\"},{\"rule\":\"Logs disabled\"}]}"

returns results for batch of 2 inputs

2. test max limit
bash--
python -c "import requests;print(requests.post('http://localhost:5000/batch-process',json={'items':[{'rule':'x'}]*21}).json())"

expected output: {"error":"max 20 items"}
"""
import os
import time
from flask import Blueprint,request,jsonify
from middleware.rate_limit import limiter
from middleware.input_sanitize import sanitize_request_body
from services.groq_client import GroqService

batch_process_bp=Blueprint("batch_process",__name__)
groq_service=GroqService()

def load_prompt_template(filename):
    curr_dir=os.path.dirname(__file__)
    template_path=os.path.join(curr_dir,"..","prompts",filename)

    with open(template_path,"r",encoding="utf-8") as f:
        return f.read()

@batch_process_bp.route("/batch-process",methods=["POST"])
@limiter.limit("5 per minute")
@sanitize_request_body(["items"])
def batch_process():
    data=request.get_json()
    items=data.get("items")
    if not items:
        return jsonify({
            "error":"items required"
        }),400
    if not isinstance(items,list):
        return jsonify({
            "error":"items must be array"
        }),400
    if len(items)>20:
        return jsonify({
            "error":"max 20 items"
        }),400
    template=load_prompt_template(
        "describe.txt"
    )
    system_prompt="""
You are a helpful security assistant.
Return valid JSON only.
"""
    results=[]
    for index,item in enumerate(items):
        rule=item.get("rule","")
        if not rule:
            results.append({
                "index":index,
                "success":False,
                "error":"rule missing"
            })
            continue
        try:
            prompt=template.format(rule=rule)
            ai_response=groq_service.call_groq(system_prompt,prompt)
            results.append({
                "index":index,
                "success":True,
                "description":
                    ai_response.get("description","No description"),
                "meta":
                    ai_response.get("meta")
            })
        except Exception as e:
            results.append({
                "index":index,
                "success":False,
                "error":str(e)
            })
        time.sleep(0.1)
    return jsonify({
        "count":len(results),
        "results":results
    }),200