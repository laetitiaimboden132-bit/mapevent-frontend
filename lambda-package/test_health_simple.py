#!/usr/bin/env python3
"""Test simple de /health avec requests"""
import requests
import sys

url = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/health"

print(f"Test GET {url}")
try:
    response = requests.get(url, timeout=10)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    if response.status_code == 200:
        print("SUCCESS: /health returns 200")
        sys.exit(0)
    else:
        print(f"ERROR: Expected 200, got {response.status_code}")
        sys.exit(1)
except Exception as e:
    print(f"ERROR: {e}")
    sys.exit(1)



