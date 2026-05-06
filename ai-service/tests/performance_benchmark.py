"""
performance benchmark for endpoints

run flask app, execute this file

expected output: PASS on all endpoints

"""
import sys,time,json,statistics,requests
from pathlib import Path
import os
from dotenv import load_dotenv
load_dotenv()

sys.path.append(str(Path(__file__).resolve().parents[1]))

BASE_URL= os.getenv("BASE_URL")
REQUESTS_PER_ENDPOINT=50
WARMUP_REQUESTS=5
TIMEOUT=60

ENDPOINTS={
"/describe":{"rule":"Admin accounts do not use MFA"},
"/recommend":{"rule":"Passwords are weak"},
"/categorise":{"rule":"Audit logs disabled"},
"/analyse-document":{"text":"Admin passwords are shared. MFA disabled."},
"/query":{"question":"How to secure passwords?"},
"/generate-report":{"input":"MFA missing"},
"/health":None
}

TARGETS={
"p50":1000,
"p95":3000,
"p99":5000
}


def percentile(values,p):
    values=sorted(values)
    index=round((p/100)*(len(values)-1))
    return round(values[index],2)


def benchmark_endpoint(session, endpoint,payload):
    print(f"\n{endpoint}")
    timings=[]
    failures=0
    total_requests = WARMUP_REQUESTS + REQUESTS_PER_ENDPOINT
    for i in range(total_requests):
        start=time.perf_counter()
        try:
            if payload is None:
                response=session.get(
                    BASE_URL+endpoint,
                    timeout=TIMEOUT
                )
            else:
                response=session.post(
                    BASE_URL+endpoint,
                    json=payload,
                    timeout=TIMEOUT
                )
            elapsed=(time.perf_counter()-start)*1000
            is_warmup = i < WARMUP_REQUESTS
            if response.status_code<500 and not is_warmup:
                timings.append(elapsed)
            elif response.status_code>=500 and not is_warmup:
                failures+=1
        except Exception:
            if i >= WARMUP_REQUESTS:
                failures+=1
    if not timings:
        return None
    p50=percentile(timings,50)
    p95=percentile(timings,95)
    p99=percentile(timings,99)
    result={
        "count":len(timings),
        "failures":failures,
        "warmup_requests":WARMUP_REQUESTS,
        "p50":p50,
        "p95":p95,
        "p99":p99
    }
    print(json.dumps(result,indent=2))
    if p95>TARGETS["p95"]:
        print("OPTIMISATION REQUIRED")
    else:
        print("PASS")

    return result

def print_recommendations(results):
    print("\nOPTIMISATION PLAN")
    print("="*60)
    for endpoint,data in results.items():
        if not data:
            continue
        if data["p95"]<=TARGETS["p95"]:
            continue
        print(f"\n{endpoint}")
        if endpoint in [
            "/describe",
            "/recommend",
            "/categorise"
        ]:
            print("- enable Redis cache")
            print("- warm prompt templates")
            print("- reduce token output")
        elif endpoint=="/query":
            print("- preload ChromaDB")
            print("- reuse embeddings")
            print("- reduce top_k")
        elif endpoint=="/generate-report":
            print("- use async mode")
            print("- reduce report verbosity")
        elif endpoint=="/health":
            print("- cache health stats")

def main():
    results={}
    print("\nPERFORMANCE BENCHMARK")
    print(f"BASE_URL={BASE_URL}")
    with requests.Session() as session:
        for endpoint,payload in ENDPOINTS.items():
            results[endpoint]=benchmark_endpoint(
                session,
                endpoint,
                payload
            )
    print("\nFINAL RESULTS")
    print("="*60)
    for endpoint,data in results.items():
        if not data:
            continue
        print(
            f"{endpoint} | "
            f"p50={data['p50']}ms | "
            f"p95={data['p95']}ms | "
            f"p99={data['p99']}ms"
        )
    print_recommendations(results)

if __name__=="__main__":
    main()