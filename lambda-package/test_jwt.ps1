# Script PowerShell pour tester les endpoints JWT
# Usage: .\test_jwt.ps1

$API_BASE = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api"

Write-Host "=== TESTS JWT - MapEventAI ===" -ForegroundColor Cyan
Write-Host ""

# Test 1: Créer un utilisateur (register)
Write-Host "[1/5] Test Register..." -ForegroundColor Yellow
$registerBody = @{
    email = "testjwt@example.com"
    password = "TestPassword123!"
    username = "testjwt"
    firstName = "Test"
    lastName = "JWT"
    addresses = @(
        @{
            street = "Rue de Test 1"
            city = "Lausanne"
            zip = "1000"
            country = "CH"
            lat = 46.5197
            lng = 6.6323
        }
    )
} | ConvertTo-Json -Depth 10

try {
    $registerResponse = Invoke-WebRequest -Uri "$API_BASE/user/register" `
        -Method POST `
        -Headers @{"Content-Type"="application/json"} `
        -Body $registerBody `
        -ErrorAction Stop
    
    Write-Host "✅ Register OK: $($registerResponse.StatusCode)" -ForegroundColor Green
    $registerData = $registerResponse.Content | ConvertFrom-Json
    Write-Host "   User ID: $($registerData.userId)" -ForegroundColor Gray
} catch {
    if ($_.Exception.Response.StatusCode -eq 409) {
        Write-Host "⚠️  Utilisateur existe déjà (OK pour test)" -ForegroundColor Yellow
    } else {
        Write-Host "❌ Register FAILED: $($_.Exception.Message)" -ForegroundColor Red
        if ($_.Exception.Response) {
            $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
            $responseBody = $reader.ReadToEnd()
            Write-Host "   Response: $responseBody" -ForegroundColor Red
        }
        exit 1
    }
}

Write-Host ""

# Test 2: Login (obtenir tokens)
Write-Host "[2/5] Test Login..." -ForegroundColor Yellow
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
    
    Write-Host "✅ Login OK: $($loginResponse.StatusCode)" -ForegroundColor Green
    $loginData = $loginResponse.Content | ConvertFrom-Json
    
    $accessToken = $loginData.accessToken
    $refreshToken = $loginData.refreshToken
    $user = $loginData.user
    
    Write-Host "   Access Token: $($accessToken.Substring(0, 50))..." -ForegroundColor Gray
    Write-Host "   Refresh Token: $($refreshToken.Substring(0, 50))..." -ForegroundColor Gray
    Write-Host "   User: $($user.email) (Role: $($user.role), Subscription: $($user.subscription))" -ForegroundColor Gray
    
    if (-not $accessToken -or -not $refreshToken) {
        Write-Host "❌ Tokens manquants dans la réponse!" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Login FAILED: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "   Response: $responseBody" -ForegroundColor Red
    }
    exit 1
}

Write-Host ""

# Test 3: GET /api/user/me (avec token)
Write-Host "[3/5] Test GET /api/user/me..." -ForegroundColor Yellow
try {
    $meResponse = Invoke-WebRequest -Uri "$API_BASE/user/me" `
        -Method GET `
        -Headers @{
            "Content-Type"="application/json"
            "Authorization"="Bearer $accessToken"
        } `
        -ErrorAction Stop
    
    Write-Host "✅ GET /api/user/me OK: $($meResponse.StatusCode)" -ForegroundColor Green
    $meData = $meResponse.Content | ConvertFrom-Json
    $meUser = $meData.user
    
    Write-Host "   User: $($meUser.email)" -ForegroundColor Gray
    Write-Host "   Role: $($meUser.role)" -ForegroundColor Gray
    Write-Host "   Subscription: $($meUser.subscription)" -ForegroundColor Gray
    Write-Host "   Username: $($meUser.username)" -ForegroundColor Gray
    
    if ($meUser.email -ne "testjwt@example.com") {
        Write-Host "❌ Email incorrect dans la réponse!" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ GET /api/user/me FAILED: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "   Response: $responseBody" -ForegroundColor Red
    }
    exit 1
}

Write-Host ""

# Test 4: Refresh token
Write-Host "[4/5] Test Refresh Token..." -ForegroundColor Yellow
$refreshBody = @{
    refreshToken = $refreshToken
} | ConvertTo-Json

try {
    $refreshResponse = Invoke-WebRequest -Uri "$API_BASE/auth/refresh" `
        -Method POST `
        -Headers @{"Content-Type"="application/json"} `
        -Body $refreshBody `
        -ErrorAction Stop
    
    Write-Host "✅ Refresh OK: $($refreshResponse.StatusCode)" -ForegroundColor Green
    $refreshData = $refreshResponse.Content | ConvertFrom-Json
    $newAccessToken = $refreshData.accessToken
    
    Write-Host "   New Access Token: $($newAccessToken.Substring(0, 50))..." -ForegroundColor Gray
    
    if (-not $newAccessToken) {
        Write-Host "❌ Nouveau token manquant!" -ForegroundColor Red
        exit 1
    }
    
    # Tester le nouveau token
    $meResponse2 = Invoke-WebRequest -Uri "$API_BASE/user/me" `
        -Method GET `
        -Headers @{
            "Content-Type"="application/json"
            "Authorization"="Bearer $newAccessToken"
        } `
        -ErrorAction Stop
    
    Write-Host "✅ Nouveau token fonctionne!" -ForegroundColor Green
} catch {
    Write-Host "❌ Refresh FAILED: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Test 5: Test avec token invalide (doit retourner 401)
Write-Host "[5/5] Test Token Invalide (doit retourner 401)..." -ForegroundColor Yellow
try {
    $invalidResponse = Invoke-WebRequest -Uri "$API_BASE/user/me" `
        -Method GET `
        -Headers @{
            "Content-Type"="application/json"
            "Authorization"="Bearer invalid-token-12345"
        } `
        -ErrorAction Stop
    
    Write-Host "❌ Token invalide accepté (ne devrait pas arriver)!" -ForegroundColor Red
    exit 1
} catch {
    if ($_.Exception.Response.StatusCode -eq 401) {
        Write-Host "✅ Token invalide correctement rejeté (401)" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Erreur inattendue: $($_.Exception.Response.StatusCode)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "=== TOUS LES TESTS RÉUSSIS ===" -ForegroundColor Green
Write-Host ""
Write-Host "Prochaines étapes:" -ForegroundColor Cyan
Write-Host "1. Configurer JWT_SECRET dans Lambda (AWS Console)" -ForegroundColor White
Write-Host "2. Créer la table user_passwords dans PostgreSQL" -ForegroundColor White
Write-Host "3. Tester avec un vrai utilisateur" -ForegroundColor White

