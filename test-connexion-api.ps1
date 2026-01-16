# Script de test pour vérifier la connexion à l'API

param(
    [string]$Email = "",
    [string]$Password = "",
    [string]$ApiUrl = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"
)

Write-Host "TEST DE CONNEXION A L'API" -ForegroundColor Cyan
Write-Host "URL: $ApiUrl" -ForegroundColor Cyan
Write-Host ""

if ([string]::IsNullOrWhiteSpace($Email) -or [string]::IsNullOrWhiteSpace($Password)) {
    Write-Host "Usage: .\test-connexion-api.ps1 -Email 'votre-email@example.com' -Password 'votre-mot-de-passe'" -ForegroundColor Yellow
    exit 1
}

# Test 1: Vérifier que l'API répond
Write-Host "Test 1: Verification de l'accessibilite de l'API..." -ForegroundColor Cyan
try {
    $healthCheck = Invoke-WebRequest -Uri "$ApiUrl/api/health" -Method GET -ErrorAction Stop
    Write-Host "  OK: L'API est accessible" -ForegroundColor Green
} catch {
    Write-Host "  ATTENTION: L'API ne repond pas au endpoint /api/health" -ForegroundColor Yellow
    Write-Host "  (Ce n'est pas forcement un probleme si l'endpoint n'existe pas)" -ForegroundColor Gray
}

Write-Host ""

# Test 2: Tentative de connexion
Write-Host "Test 2: Tentative de connexion..." -ForegroundColor Cyan
$loginBody = @{
    email = $Email
    password = $Password
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$ApiUrl/api/auth/login" `
        -Method POST `
        -ContentType "application/json" `
        -Body $loginBody `
        -ErrorAction Stop
    
    Write-Host "  SUCCES: Connexion reussie!" -ForegroundColor Green
    Write-Host "  Token JWT obtenu: $($response.accessToken.Substring(0, 20))..." -ForegroundColor Gray
    Write-Host ""
    Write-Host "Vous pouvez maintenant utiliser ce token pour supprimer les comptes:" -ForegroundColor Cyan
    Write-Host "  .\supprimer-tous-comptes.ps1 -JwtToken '$($response.accessToken)' -Confirm 'OUI'" -ForegroundColor Yellow
    
} catch {
    Write-Host "  ERREUR: Echec de la connexion" -ForegroundColor Red
    Write-Host "  Status: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Red
    Write-Host "  Message: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.ErrorDetails.Message) {
        Write-Host ""
        Write-Host "  Details de l'erreur:" -ForegroundColor Yellow
        Write-Host "  $($_.ErrorDetails.Message)" -ForegroundColor Yellow
        
        try {
            $errorJson = $_.ErrorDetails.Message | ConvertFrom-Json
            if ($errorJson.error) {
                Write-Host ""
                Write-Host "  Erreur API: $($errorJson.error)" -ForegroundColor Red
            }
        } catch {
            # Ignorer si ce n'est pas du JSON
        }
    }
    
    Write-Host ""
    Write-Host "VERIFICATIONS:" -ForegroundColor Cyan
    Write-Host "  1. Verifiez que votre email est correct: $Email" -ForegroundColor Yellow
    Write-Host "  2. Verifiez que votre mot de passe est correct" -ForegroundColor Yellow
    Write-Host "  3. Verifiez que votre compte existe dans la base de donnees" -ForegroundColor Yellow
    Write-Host "  4. Verifiez que votre compte a le role 'director' ou 'admin'" -ForegroundColor Yellow
    
    exit 1
}



