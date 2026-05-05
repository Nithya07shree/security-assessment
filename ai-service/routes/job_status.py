from flask import Blueprint,jsonify
from services.job_store import get_job

job_status_bp=Blueprint("job_status",__name__)

@job_status_bp.route("/jobs/<job_id>",methods=["GET"])
def job_status(job_id):
    job=get_job(job_id)
    if not job:
        return jsonify({"error":"job not found"}),404
    return jsonify(job),200