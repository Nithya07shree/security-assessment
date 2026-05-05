"""
Week 2 AI Quality Review
tests each endpoint for 10 inputs. The outputs are automatically reviewed by the same Groq Service

to test, run flask application, execute this file
"""
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))
import requests
import json
from statistics import mean
import os
from dotenv import load_dotenv
from services.groq_client import GroqService

load_dotenv()
BASE_URL= os.getenv("BASE_URL")
judge = GroqService()

TEST_DATA={
"/describe":[
{"rule":"Admin accounts do not use MFA."},
{"rule":"Password rotation policy missing."},
{"rule":"Inactive users retain access."},
{"rule":"Audit logs are disabled."},
{"rule":"TLS is not enforced."},
{"rule":"Shared admin credentials are used."},
{"rule":"Security patches are delayed."},
{"rule":"Privileged actions are not logged."},
{"rule":"Guest accounts are enabled."},
{"rule":"Root access is unrestricted."}
],
"/recommend":[
{"rule":"MFA is disabled."},
{"rule":"Passwords are weak."},
{"rule":"Logs are not monitored."},
{"rule":"Firewall rules are outdated."},
{"rule":"Certificates expired."},
{"rule":"Admin sessions never expire."},
{"rule":"Backups are unencrypted."},
{"rule":"USB ports are unrestricted."},
{"rule":"SIEM not configured."},
{"rule":"Sensitive files are public."}
],
"/categorise":[
{"rule":"No MFA on admin accounts."},
{"rule":"Logs are disabled."},
{"rule":"Backups are not encrypted."},
{"rule":"Firewall ports are open."},
{"rule":"Passwords are reused."},
{"rule":"Guest users have admin rights."},
{"rule":"TLS certificates expired."},
{"rule":"No audit trail."},
{"rule":"RBAC not enforced."},
{"rule":"Patching delayed."}
],
"/analyse-document":[
{"text":"Admin passwords are shared. Logs are not monitored. MFA is disabled."},
{"text":"Guest users retain access after termination."},
{"text":"Backups are stored without encryption."},
{"text":"Critical servers are not patched."},
{"text":"Firewall ports are exposed."},
{"text":"Root access is unrestricted."},
{"text":"No alerting on suspicious activity."},
{"text":"Expired certificates in production."},
{"text":"Audit trails missing."},
{"text":"Sensitive data transmitted in plain text."}
],
"/query":[
{"question":"How should MFA be implemented?"},
{"question":"How to secure passwords?"},
{"question":"How to monitor logs?"},
{"question":"What is RBAC?"},
{"question":"How to secure backups?"},
{"question":"What is least privilege?"},
{"question":"How to secure root accounts?"},
{"question":"How to patch critical systems?"},
{"question":"How to encrypt data at rest?"},
{"question":"How to secure API tokens?"}
]
}


def score_response(endpoint,payload,response):

    system_prompt="""
You are an AI quality evaluator.

Evaluate:
1. Accuracy
2. Security relevance
3. Completeness
4. JSON correctness

Return STRICT JSON:
{
 "score":1-5
}
"""

    user_prompt=f"""
Endpoint:
{endpoint}

Input:
{json.dumps(payload)}

Output:
{json.dumps(response)}
"""

    result=judge.call_groq(
        system_prompt,
        user_prompt,
        fresh=True
    )

    score=result.get("score",0)

    try:
        score=float(score)
    except:
        score=0

    return score


def review_endpoint(endpoint):

    url=BASE_URL+endpoint

    print(f"\n{endpoint}")

    scores=[]

    for i,payload in enumerate(TEST_DATA[endpoint],start=1):

        response=requests.post(
            url,
            json=payload,
            timeout=30
        )

        if response.status_code!=200:
            print(f"{i}. FAIL ({response.status_code})")
            scores.append(0)
            continue

        data=response.json()

        score=score_response(
            endpoint,
            payload,
            data
        )

        scores.append(score)

        print(f"{i}. Score={score}")

    avg=round(mean(scores),2)

    print(f"Average={avg}")

    if avg<4:
        print("PROMPT REVIEW REQUIRED")
    else:
        print("PASS")

    return avg


def main():

    final_scores={}

    for endpoint in TEST_DATA:
        final_scores[endpoint]=review_endpoint(endpoint)

    print("\nFINAL REPORT")

    for endpoint,score in final_scores.items():
        print(f"{endpoint}: {score}/5")

    overall=round(mean(final_scores.values()),2)

    print(f"\nOVERALL={overall}/5")

    if overall>=4:
        print("WEEK 2 QUALITY PASS")
    else:
        print("PROMPT TUNING REQUIRED")


if __name__=="__main__":
    main()