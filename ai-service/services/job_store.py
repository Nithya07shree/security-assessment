import uuid
import threading

_jobs={}
_lock=threading.Lock()

def create_job():
    job_id=str(uuid.uuid4())
    with _lock:
        _jobs[job_id]={"job_id":job_id,"status":"queued","result":None}
    return job_id

def update_job(job_id,status,result=None):
    with _lock:
        if job_id not in _jobs:
            return
        _jobs[job_id]["status"]=status
        if result is not None:
            _jobs[job_id]["result"]=result

def get_job(job_id):
    with _lock:
        return _jobs.get(job_id)