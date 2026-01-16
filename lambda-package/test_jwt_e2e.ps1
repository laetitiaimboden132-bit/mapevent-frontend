# Test End-to-End JWT System
# Usage: .\test_jwt_e2e.ps1

# Configuration
$LAMBDA_URL = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"
$API_BASE = "$LAMBDA_URL/api"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "TEST END-TO-END JWT SYSTEM" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Test 1: Health Check
Write-Host "[TEST 1] Health Check" -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "$LAMBDA_URL/health" -Method GET
    if ($health.ok) {
        Write-Host "  OK: Health check passed" -ForegroundColor Green
    } else {
        Write-Host "  FAIL: Health check returned false" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "  FAIL: Health check failed - $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 2: Register (si nécessaire)
Write-Host "`n[TEST 2] Register" -ForegroundColor Yellow
$randomSuffix = Get-Random -Minimum 1000 -Maximum 9999
$TEST_EMAIL = "test-$randomSuffix@example.com"
$TEST_PASSWORD = "Test123!@#"
$TEST_USERNAME = "testuser$randomSuffix"

$registerBody = @{
    email = $TEST_EMAIL
    password = $TEST_PASSWORD
    username = $TEST_USERNAME
    first_name = "Test"
    last_name = "User"
} | ConvertTo-Json

try {
    $registerResponse = Invoke-RestMethod -Uri "$API_BASE/user/register" -Method POST -Body $registerBody -ContentType "application/json"
    Write-Host "  OK: User registered - ID: $($registerResponse.user.id), Email: $($registerResponse.user.email)" -ForegroundColor Green
} catch {
    Write-Host "  WARN: Register failed (user may exist) - $($_.Exception.Message)" -ForegroundColor Yellow
    # Utiliser des credentials existants pour les tests suivants
    $TEST_EMAIL = "test@example.com"
    $TEST_PASSWORD = "Test123!@#"
    Write-Host "  INFO: Using existing credentials: $TEST_EMAIL" -ForegroundColor Cyan
}

# Test 3: Login
Write-Host "`n[TEST 3] Login" -ForegroundColor Yellow
$loginBody = @{
    email = $TEST_EMAIL
    password = $TEST_PASSWORD
} | ConvertTo-Json

try {
    $loginResponse = Invoke-RestMethod -Uri "$API_BASE/auth/login" -Method POST -Body $loginBody -ContentType "application/json"
    $ACCESS_TOKEN = $loginResponse.accessToken
    $REFRESH_TOKEN = $loginResponse.refreshToken
    
    if ($ACCESS_TOKEN -and $REFRESH_TOKEN) {
        Write-Host "  OK: Login successful" -ForegroundColor Green
        Write-Host "      Access Token: $($ACCESS_TOKEN.Substring(0, 30))..." -ForegroundColor Gray
        Write-Host "      Refresh Token: $($REFRESH_TOKEN.Substring(0, 30))..." -ForegroundColor Gray
    } else {
        Write-Host "  FAIL: Login response missing tokens" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "  FAIL: Login failed - $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "      Response: $responseBody" -ForegroundColor Red
    }
    exit 1
}

# Test 4: GET /api/user/me
Write-Host "`n[TEST 4] GET /api/user/me" -ForegroundColor Yellow
$headers = @{
    "Authorization" = "Bearer $ACCESS_TOKEN"
    "Content-Type" = "application/json"
}
try {
    $meResponse = Invoke-RestMethod -Uri "$API_BASE/user/me" -Method GET -Headers $headers
    if ($meResponse.user -and $meResponse.user.email) {
        Write-Host "  OK: User profile retrieved" -ForegroundColor Green
        Write-Host "      Email: $($meResponse.user.email)" -ForegroundColor Gray
        Write-Host "      Username: $($meResponse.user.username)" -ForegroundColor Gray
        Write-Host "      Role: $($meResponse.user.role)" -ForegroundColor Gray
        Write-Host "      Subscription: $($meResponse.user.subscription)" -ForegroundColor Gray
    } else {
        Write-Host "  FAIL: User profile missing data" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "  FAIL: GET /api/user/me failed - $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "      Response: $responseBody" -ForegroundColor Red
    }
    exit 1
}

# Test 5: Refresh Token
Write-Host "`n[TEST 5] POST /api/auth/refresh" -ForegroundColor Yellow
$refreshBody = @{
    refreshToken = $REFRESH_TOKEN
} | ConvertTo-Json

try {
    $refreshResponse = Invoke-RestMethod -Uri "$API_BASE/auth/refresh" -Method POST -Body $refreshBody -ContentType "application/json"
    $NEW_ACCESS_TOKEN = $refreshResponse.accessToken
    
    if ($NEW_ACCESS_TOKEN) {
        Write-Host "  OK: Refresh token successful" -ForegroundColor Green
        Write-Host "      New Access Token: $($NEW_ACCESS_TOKEN.Substring(0, 30))..." -ForegroundColor Gray
    } else {
        Write-Host "  FAIL: Refresh response missing accessToken" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "  FAIL: Refresh failed - $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "      Response: $responseBody" -ForegroundColor Red
    }
    exit 1
}

# Test 6: GET /api/user/me avec nouveau token
Write-Host "`n[TEST 6] GET /api/user/me (avec nouveau token)" -ForegroundColor Yellow
$newHeaders = @{
    "Authorization" = "Bearer $NEW_ACCESS_TOKEN"
    "Content-Type" = "application/json"
}
try {
    $meResponse2 = Invoke-RestMethod -Uri "$API_BASE/user/me" -Method GET -Headers $newHeaders
    if ($meResponse2.user -and $meResponse2.user.email) {
        Write-Host "  OK: User profile retrieved with new token" -ForegroundColor Green
        Write-Host "      Email: $($meResponse2.user.email)" -ForegroundColor Gray
    } else {
        Write-Host "  FAIL: User profile missing data" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "  FAIL: GET /api/user/me failed with new token - $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "      Response: $responseBody" -ForegroundColor Red
    }
    exit 1
}

# Test 7: Logout
Write-Host "`n[TEST 7] POST /api/auth/logout" -ForegroundColor Yellow
try {
    $logoutResponse = Invoke-RestMethod -Uri "$API_BASE/auth/logout" -Method POST -Headers $newHeaders
    if ($logoutResponse.message) {
        Write-Host "  OK: Logout successful" -ForegroundColor Green
        Write-Host "      Message: $($logoutResponse.message)" -ForegroundColor Gray
        Write-Host "      NOTE: Logout is client-side only (refresh tokens not stored server-side)" -ForegroundColor Cyan
    } else {
        Write-Host "  FAIL: Logout response missing message" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "  FAIL: Logout failed - $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "      Response: $responseBody" -ForegroundColor Red
    }
    exit 1
}

# Test 8: GET /api/user/me après logout (doit échouer)
Write-Host "`n[TEST 8] GET /api/user/me (après logout - doit echouer)" -ForegroundColor Yellow
try {
    $meResponse3 = Invoke-RestMethod -Uri "$API_BASE/user/me" -Method GET -Headers $newHeaders
    Write-Host "  FAIL: GET /api/user/me should have failed after logout!" -ForegroundColor Red
    exit 1
} catch {
    if ($_.Exception.Response.StatusCode -eq 401) {
        Write-Host "  OK: GET /api/user/me correctly failed with 401 (as expected)" -ForegroundColor Green
    } else {
        Write-Host "  WARN: GET /api/user/me failed with unexpected status - $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

# Résumé
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "RESUME: Tous les tests sont passes!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Cyan

Write-Host "Prochaines etapes:" -ForegroundColor Cyan
Write-Host "  1. Valider les tests manuels sur https://mapevent.world" -ForegroundColor White
Write-Host "  2. Verifier les logs ASCII dans la console du navigateur" -ForegroundColor White
Write-Host "  3. Verifier que l'avatar s'affiche correctement" -ForegroundColor White
Write-Host "  4. Une fois valide, passer a Stripe webhooks + synchro subscription->role" -ForegroundColor White



