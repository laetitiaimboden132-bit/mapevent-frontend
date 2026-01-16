# Test d'inscription email/mot de passe (sans vérification email)
# Comme les leaders mondiaux (Reddit, Twitter, etc.)

$API_BASE_URL = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api"

# Générer un email unique pour le test
$timestamp = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
$testEmail = "test-$timestamp@example.com"
$testUsername = "TestUser$timestamp"
$testPassword = "Test1234!Abc"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TEST INSCRIPTION EMAIL/MOT DE PASSE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Email: $testEmail" -ForegroundColor Yellow
Write-Host "Username: $testUsername" -ForegroundColor Yellow
Write-Host "Password: $testPassword" -ForegroundColor Yellow
Write-Host ""

$body = @{
    email = $testEmail
    username = $testUsername
    password = $testPassword
    firstName = "Test"
    lastName = "User"
    addresses = @()
} | ConvertTo-Json

Write-Host "Envoi de la requête d'inscription..." -ForegroundColor Gray

try {
    $response = Invoke-RestMethod -Uri "$API_BASE_URL/user/register" `
        -Method POST `
        -ContentType "application/json" `
        -Body $body `
        -ErrorAction Stop
    
    Write-Host ""
    Write-Host "✅ SUCCÈS !" -ForegroundColor Green
    Write-Host "Compte créé sans vérification email (comme les leaders mondiaux)" -ForegroundColor Green
    Write-Host ""
    Write-Host "Réponse:" -ForegroundColor Cyan
    $response | ConvertTo-Json -Depth 10
    
    if ($response.accessToken) {
        Write-Host ""
        Write-Host "✅ Token d'accès reçu - Connexion automatique réussie !" -ForegroundColor Green
    }
    
} catch {
    Write-Host ""
    Write-Host "❌ ERREUR" -ForegroundColor Red
    Write-Host ""
    
    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode.value__
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        
        Write-Host "Code HTTP: $statusCode" -ForegroundColor Red
        Write-Host "Réponse:" -ForegroundColor Red
        Write-Host $responseBody -ForegroundColor Red
        
        if ($statusCode -eq 409) {
            Write-Host ""
            Write-Host "⚠️ Email ou username déjà utilisé" -ForegroundColor Yellow
            Write-Host "C'est normal si vous avez déjà testé avec cet email" -ForegroundColor Gray
        }
    } else {
        Write-Host "Erreur réseau:" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TEST TERMINÉ" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
