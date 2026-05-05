"""
PII audit.
Scans:
- prompt templates
- log files
- seed documents

Checks:
- email
- phone
- credit card
- SSN
- Aadhaar-like numbers
- IP addresses
"""

import re
from pathlib import Path
ROOT = (Path(__file__).resolve().parents[1])

SCAN_TARGETS = [
    "prompts",
    "data",
    "application_logs.log"
]

PATTERNS = {
    "EMAIL":
        r"\b[A-Za-z0-9._%+-]+"
        r"@[A-Za-z0-9.-]+"
        r"\.[A-Za-z]{2,}\b",
    "PHONE":
        r"\b(?:\+91|\+1)?[6-9]\d{9}\b",
    "CREDIT_CARD":
        r"\b(?:\d[ -]*?){13,16}\b",
    "SSN":
        r"\b\d{3}-\d{2}-\d{4}\b",
    "AADHAAR":
        r"\b\d{4}\s?\d{4}\s?\d{4}\b",
    "IP_ADDRESS":
        r"\b(?:25[0-5]|2[0-4]\d|1?\d?\d)"
        r"(?:\.(?:25[0-5]|2[0-4]\d|1?\d?\d)){3}\b",
}

total_files = 0
total_issues = 0

def scan_text(text):
    findings = []
    for label, pattern in (PATTERNS.items()):
        matches = re.findall(pattern,text)
    for match in matches:
        if label == "IP_ADDRESS":
            if str(match).startswith(("127.", "10.", "192.168.", "172.")):
                continue
        findings.append(label)
    return findings

def scan_file(file_path):
    global total_issues
    try:
        text = file_path.read_text(encoding="utf-8",errors="ignore")
    except Exception:
        return
    findings = scan_text(text)
    if findings:
        total_issues += 1
        print(
            f"[FAIL] {file_path} : {findings}")
    else:
        print(
            f"[PASS] {file_path}")

def main():
    global total_files
    print("\nPII AUDIT\n")
    for target in (SCAN_TARGETS):
        path = (ROOT / target)
        # single file
        if path.is_file():
            total_files += 1
            scan_file(path)
            continue
        # folder
        if path.is_dir():
            for file in (path.rglob("*")):
                if not file.is_file():
                    continue
                total_files += 1
                scan_file(file)
    print("\nSUMMARY")
    print(f"Files scanned: {total_files}")
    print(f"Issues found: {total_issues}")
    if total_issues == 0:
        print("RESULT: PASS")
    else:
        print("RESULT: FAIL")

if __name__ == "__main__":
    main()