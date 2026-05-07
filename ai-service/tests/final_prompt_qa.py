import json,time,requests
from dotenv import load_dotenv
import os
load_dotenv()

BASE_URL=os.getenv("BASE_URL")

ENDPOINTS={
"/describe":"rule",
"/recommend":"rule",
"/categorise":"rule",
"/analyse-document":"text",
"/generate-report":"input"
}

DEMO_RECORDS=[
"Admin accounts do not use MFA.",
"Passwords are reused across systems.",
"Audit logs are disabled.",
"Security patches are delayed.",
"Privileged access is shared.",
"TLS is not enforced.",
"Backups are not encrypted.",
"Incident plans are missing.",
"Cloud buckets are public.",
"Unused ports are open.",
"Dormant accounts remain active.",
"Logs are retained only 7 days.",
"Default passwords still exist.",
"Production secrets are hardcoded.",
"Database traffic is unencrypted.",
"Shared root accounts exist.",
"Firewall rules are outdated.",
"Vulnerability scans are missing.",
"Admin consoles lack MFA.",
"Critical patches exceed SLA.",
"RBAC is not enforced.",
"Internal APIs lack auth.",
"Audit evidence is incomplete.",
"Monitoring alerts are ignored.",
"Certificates are expired.",
"Keys are not rotated.",
"Email phishing controls missing.",
"SIEM integration unavailable.",
"Remote access lacks VPN.",
"Endpoint protection disabled."
]

def validate_output(data):
    if not data:
        return False,"empty"
    if isinstance(data,str):
        try:
            data=json.loads(data)
        except Exception:
            return False,"not_json"
    if not isinstance(data,(dict,list)):
        return False,"not_json"

    if isinstance(data,dict):
        meta=data.get("meta",{})
        if meta.get("is_fallback"):
            return False,"fallback"
    return True,"ok"

def test_endpoint(endpoint,field):
    print(f"\n{endpoint}")
    passed=0
    failed=[]
    for i,record in enumerate(DEMO_RECORDS,start=1):
        payload={field:record}
        try:
            response=requests.post(
                BASE_URL+endpoint,
                json=payload,
                timeout=60
            )
            if response.status_code!=200:
                failed.append(f"{i}:http_{response.status_code}")
                continue
            data=response.json()
            ok,reason=validate_output(data)
            if ok:
                passed+=1
            else:
                failed.append(f"{i}:{reason}")
        except Exception as e:
            failed.append(f"{i}:exception")
        time.sleep(2.1)
    score=round((passed/30)*100,2)
    print(f"PASS {passed}/30 ({score}%)")
    if failed:
        print("FAILED:",failed)
    return score

def main():
    print("\nFINAL PROMPT QA")
    final_scores={}
    for endpoint,field in ENDPOINTS.items():
        final_scores[endpoint]=test_endpoint(endpoint,field)
    print("\nFINAL SUMMARY")
    all_pass=True
    for endpoint,score in final_scores.items():
        print(endpoint,score)
        if score<100:
            all_pass=False
    if all_pass:
        print("\nDEMO READY")
    else:
        print("\nPROMPT TUNING REQUIRED")

if __name__=="__main__":
    main()