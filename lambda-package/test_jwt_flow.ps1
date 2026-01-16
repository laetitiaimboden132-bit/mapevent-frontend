# Test complet du flux JWT : login puis /api/user/me
# Usage: .\test_jwt_flow.ps1

$API_BASE = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api"

Write-Host "=== TEST FLUX JWT - MapEventAI ===" -ForegroundColor Cyan
Write-Host ""

# Test 1: Health check
Write-Host "[1/4] Test /health..." -ForegroundColor Yellow
try {
    $healthResponse = Invoke-WebRequest -Uri "$API_BASE/health" -Method GET -ErrorAction Stop
    Write-Host "SUCCESS: /health returns $($healthResponse.StatusCode)" -ForegroundColor Green
    $healthData = $healthResponse.Content | ConvertFrom-Json
    Write-Host "   Response: $($healthData | ConvertTo-Json)" -ForegroundColor Gray
} catch {
    Write-Host "ERROR: /health failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Test 2: Health DB check
Write-Host "[2/4] Test /api/health/db..." -ForegroundColor Yellow
try {
    $dbHealthResponse = Invoke-WebRequest -Uri "$API_BASE/health/db" -Method GET -ErrorAction Stop
    Write-Host "SUCCESS: /api/health/db returns $($dbHealthResponse.StatusCode)" -ForegroundColor Green
    $dbHealthData = $dbHealthResponse.Content | ConvertFrom-Json
    Write-Host "   Response: $($dbHealthData | ConvertTo-Json)" -ForegroundColor Gray
} catch {
    Write-Host "WARNING: /api/health/db failed: $($_.Exception.Message)" -ForegroundColor Yellow
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        $reader.Close()
        Write-Host "   Response: $responseBody" -ForegroundColor Yellow
    }
}

Write-Host ""

# Test 3: Login (obtenir tokens)
Write-Host "[3/4] Test Login..." -ForegroundColor Yellow
$loginBody = @{
    email = "testjwt@example.com"
    password = "TestPassword123!"
} | ConvertTo-Json

try {
    $loginResponse = Invoke-WebRequest -Uri "$API_BASE/auth/login" `
        -Method POST `
        -Headers @{"Content-Type"="application/json"} `
        -Body $loginBody `
        -ErrorAction Stop
    
    Write-Host "SUCCESS: Login returns $($loginResponse.StatusCode)" -ForegroundColor Green
    $loginData = $loginResponse.Content | ConvertFrom-Json
    
    $accessToken = $loginData.accessToken
    $refreshToken = $loginData.refreshToken
    $user = $loginData.user
    
    Write-Host "   Access Token: $($accessToken.Substring(0, [Math]::Min(50, $accessToken.Length)))..." -ForegroundColor Gray
    Write-Host "   Refresh Token: $($refreshToken.Substring(0, [Math]::Min(50, $refreshToken.Length)))..." -ForegroundColor Gray
    Write-Host "   User: $($user.email) (Role: $($user.role), Subscription: $($user.subscription))" -ForegroundColor Gray
    
    if (-not $accessToken -or -not $refreshToken) {
        Write-Host "ERROR: Tokens manquants dans la reponse!" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "ERROR: Login failed: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        $reader.Close()
        Write-Host "   Response: $responseBody" -ForegroundColor Red
    }
    exit 1
}

Write-Host ""

# Test 4: GET /api/user/me (avec token)
Write-Host "[4/4] Test GET /api/user/me..." -ForegroundColor Yellow
try {
    $meResponse = Invoke-WebRequest -Uri "$API_BASE/user/me" `
        -Method GET `
        -Headers @{
            "Content-Type"="application/json"
            "Authorization"="Bearer $accessToken"
        } `
        -ErrorAction Stop
    
    Write-Host "SUCCESS: GET /api/user/me returns $($meResponse.StatusCode)" -ForegroundColor Green
    $meData = $meResponse.Content | ConvertFrom-Json
    $meUser = $meData.user
    
    Write-Host "   User ID: $($meUser.id)" -ForegroundColor Gray
    Write-Host "   Email: $($meUser.email)" -ForegroundColor Gray
    Write-Host "   Username: $($meUser.username)" -ForegroundColor Gray
    Write-Host "   Role: $($meUser.role)" -ForegroundColor Gray
    Write-Host "   Subscription: $($meUser.subscription)" -ForegroundColor Gray
    Write-Host "   Profile Photo: $($meUser.profile_photo_url)" -ForegroundColor Gray
    
    if ($meUser.email -ne "testjwt@example.com") {
        Write-Host "WARNING: Email incorrect dans la reponse!" -ForegroundColor Yellow
    }
} catch {
    Write-Host "ERROR: GET /api/user/me failed: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode.value__
        Write-Host "   Status Code: $statusCode" -ForegroundColor Red
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        $reader.Close()
        Write-Host "   Response: $responseBody" -ForegroundColor Red
    }
    exit 1
}

Write-Host ""
Write-Host "=== TOUS LES TESTS REUSSIS ===" -ForegroundColor Green



