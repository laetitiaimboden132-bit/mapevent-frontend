#!/bin/bash
# Test complet du flux JWT avec curl : login puis /api/user/me
# Usage: bash test_jwt_flow_curl.sh

API_BASE="https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api"

echo "=== TEST FLUX JWT - MapEventAI ==="
echo ""

# Test 1: Health check
echo "[1/4] Test /health..."
HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$API_BASE/health")
HEALTH_BODY=$(echo "$HEALTH_RESPONSE" | head -n -1)
HEALTH_CODE=$(echo "$HEALTH_RESPONSE" | tail -n 1)

if [ "$HEALTH_CODE" = "200" ]; then
    echo "SUCCESS: /health returns 200"
    echo "   Response: $HEALTH_BODY"
else
    echo "ERROR: /health failed with code $HEALTH_CODE"
    echo "   Response: $HEALTH_BODY"
    exit 1
fi

echo ""

# Test 2: Health DB check
echo "[2/4] Test /api/health/db..."
DB_HEALTH_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$API_BASE/health/db")
DB_HEALTH_BODY=$(echo "$DB_HEALTH_RESPONSE" | head -n -1)
DB_HEALTH_CODE=$(echo "$DB_HEALTH_RESPONSE" | tail -n 1)

if [ "$DB_HEALTH_CODE" = "200" ]; then
    echo "SUCCESS: /api/health/db returns 200"
    echo "   Response: $DB_HEALTH_BODY"
else
    echo "WARNING: /api/health/db returned $DB_HEALTH_CODE"
    echo "   Response: $DB_HEALTH_BODY"
fi

echo ""

# Test 3: Login (obtenir tokens)
echo "[3/4] Test Login..."
LOGIN_BODY='{"email":"testjwt@example.com","password":"TestPassword123!"}'

LOGIN_RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_BASE/auth/login" \
    -H "Content-Type: application/json" \
    -d "$LOGIN_BODY")

LOGIN_BODY_RESPONSE=$(echo "$LOGIN_RESPONSE" | head -n -1)
LOGIN_CODE=$(echo "$LOGIN_RESPONSE" | tail -n 1)

if [ "$LOGIN_CODE" = "200" ]; then
    echo "SUCCESS: Login returns 200"
    ACCESS_TOKEN=$(echo "$LOGIN_BODY_RESPONSE" | grep -o '"accessToken":"[^"]*' | cut -d'"' -f4)
    REFRESH_TOKEN=$(echo "$LOGIN_BODY_RESPONSE" | grep -o '"refreshToken":"[^"]*' | cut -d'"' -f4)
    
    if [ -z "$ACCESS_TOKEN" ] || [ -z "$REFRESH_TOKEN" ]; then
        echo "ERROR: Tokens manquants dans la reponse!"
        echo "   Response: $LOGIN_BODY_RESPONSE"
        exit 1
    fi
    
    echo "   Access Token: ${ACCESS_TOKEN:0:50}..."
    echo "   Refresh Token: ${REFRESH_TOKEN:0:50}..."
else
    echo "ERROR: Login failed with code $LOGIN_CODE"
    echo "   Response: $LOGIN_BODY_RESPONSE"
    exit 1
fi

echo ""

# Test 4: GET /api/user/me (avec token)
echo "[4/4] Test GET /api/user/me..."
ME_RESPONSE=$(curl -s -w "\n%{http_code}" -X GET "$API_BASE/user/me" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $ACCESS_TOKEN")

ME_BODY_RESPONSE=$(echo "$ME_RESPONSE" | head -n -1)
ME_CODE=$(echo "$ME_RESPONSE" | tail -n 1)

if [ "$ME_CODE" = "200" ]; then
    echo "SUCCESS: GET /api/user/me returns 200"
    echo "   Response: $ME_BODY_RESPONSE"
else
    echo "ERROR: GET /api/user/me failed with code $ME_CODE"
    echo "   Response: $ME_BODY_RESPONSE"
    exit 1
fi

echo ""
echo "=== TOUS LES TESTS REUSSIS ==="



