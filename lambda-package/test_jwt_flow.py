#!/usr/bin/env python3
"""Test complet du flux JWT : login puis /api/user/me"""
import requests
import json
import sys

API_BASE = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api"

print("=== TEST FLUX JWT - MapEventAI ===")
print("")

# Test 1: Health check
print("[1/4] Test /health...")
try:
    response = requests.get(f"{API_BASE}/health", timeout=10)
    print(f"SUCCESS: /health returns {response.status_code}")
    print(f"   Response: {response.text}")
except Exception as e:
    print(f"ERROR: /health failed: {e}")
    sys.exit(1)

print("")

# Test 2: Health DB check
print("[2/4] Test /api/health/db...")
try:
    response = requests.get(f"{API_BASE}/health/db", timeout=30)
    print(f"SUCCESS: /api/health/db returns {response.status_code}")
    print(f"   Response: {response.text}")
except Exception as e:
    print(f"WARNING: /api/health/db failed: {e}")

print("")

# Test 3: Login (obtenir tokens)
print("[3/4] Test Login...")
login_body = {
    "email": "testjwt@example.com",
    "password": "TestPassword123!"
}

try:
    response = requests.post(f"{API_BASE}/auth/login", json=login_body, timeout=30)
    if response.status_code == 200:
        print(f"SUCCESS: Login returns {response.status_code}")
        data = response.json()
        access_token = data.get('accessToken')
        refresh_token = data.get('refreshToken')
        user = data.get('user')
        
        if not access_token or not refresh_token:
            print("ERROR: Tokens manquants dans la reponse!")
            print(f"   Response: {response.text}")
            sys.exit(1)
        
        print(f"   Access Token: {access_token[:50]}...")
        print(f"   Refresh Token: {refresh_token[:50]}...")
        print(f"   User: {user.get('email')} (Role: {user.get('role')}, Subscription: {user.get('subscription')})")
    else:
        print(f"ERROR: Login failed with code {response.status_code}")
        print(f"   Response: {response.text}")
        sys.exit(1)
except Exception as e:
    print(f"ERROR: Login failed: {e}")
    sys.exit(1)

print("")

# Test 4: GET /api/user/me (avec token)
print("[4/4] Test GET /api/user/me...")
try:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get(f"{API_BASE}/user/me", headers=headers, timeout=30)
    
    if response.status_code == 200:
        print(f"SUCCESS: GET /api/user/me returns {response.status_code}")
        data = response.json()
        user = data.get('user')
        print(f"   User ID: {user.get('id')}")
        print(f"   Email: {user.get('email')}")
        print(f"   Username: {user.get('username')}")
        print(f"   Role: {user.get('role')}")
        print(f"   Subscription: {user.get('subscription')}")
        print(f"   Profile Photo: {user.get('profile_photo_url', 'N/A')}")
    else:
        print(f"ERROR: GET /api/user/me failed with code {response.status_code}")
        print(f"   Response: {response.text}")
        sys.exit(1)
except Exception as e:
    print(f"ERROR: GET /api/user/me failed: {e}")
    sys.exit(1)

print("")
print("=== TOUS LES TESTS REUSSIS ===")



