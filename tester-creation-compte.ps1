# Script pour tester la création de compte complète

$API_BASE = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api"

# Générer des données de test
$timestamp = Get-Date -Format "yyyyMMddHHmmss"
$email = "test-$timestamp@example.com"
$username = "TestUser$timestamp"
# Mot de passe conforme: 12+ caractères, majuscule, minuscule, chiffre, caractère spécial
$password = "Test1234!Abc"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "TEST CRÉATION DE COMPTE" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Email: $email" -ForegroundColor White
Write-Host "Username: $username" -ForegroundColor White
Write-Host "Password: $password" -ForegroundColor White
Write-Host ""

# Étape 1: Créer le compte
Write-Host "Étape 1: Création du compte..." -ForegroundColor Yellow

$registerBody = @{
    email = $email
    username = $username
    password = $password
    firstName = "Test"
    lastName = "User"
    addresses = @()
} | ConvertTo-Json -Depth 3

Write-Host "Body envoye:" -ForegroundColor Gray
Write-Host $registerBody -ForegroundColor Gray
Write-Host ""

try {
    $registerResponse = Invoke-WebRequest -Uri "$API_BASE/user/register" `
        -Method POST `
        -ContentType "application/json" `
        -Body $registerBody `
        -ErrorAction Stop
    
    $registerData = $registerResponse.Content | ConvertFrom-Json
    
    Write-Host "✅ Compte créé avec succès!" -ForegroundColor Green
    Write-Host "   Status: $($registerResponse.StatusCode)" -ForegroundColor White
    Write-Host "   Response: $($registerResponse.Content)" -ForegroundColor Gray
    Write-Host ""
    
    # Étape 2: Vérifier si un code de vérification a été envoyé
    Write-Host "Étape 2: Vérification de l'envoi du code..." -ForegroundColor Yellow
    
    # Générer un code de test
    $code = (Get-Random -Minimum 100000 -Maximum 999999).ToString()
    
    $verifyBody = @{
        email = $email
        username = $username
        code = $code
    } | ConvertTo-Json
    
    $verifyResponse = Invoke-RestMethod -Uri "$API_BASE/user/send-verification-code" `
        -Method POST `
        -ContentType "application/json" `
        -Body $verifyBody `
        -ErrorAction Stop
    
    Write-Host "✅ Code de vérification envoyé!" -ForegroundColor Green
    Write-Host "   Success: $($verifyResponse.success)" -ForegroundColor White
    Write-Host "   Message: $($verifyResponse.message)" -ForegroundColor White
    Write-Host "   Dev Mode: $($verifyResponse.dev_mode)" -ForegroundColor White
    
    if ($verifyResponse.dev_mode -eq $true) {
        Write-Host ""
        Write-Host "⚠️  MODE DÉVELOPPEMENT" -ForegroundColor Yellow
        Write-Host "   L'email n'a pas été envoyé réellement" -ForegroundColor Yellow
        Write-Host "   SendGrid doit être configuré pour envoyer les emails" -ForegroundColor Yellow
    } else {
        Write-Host ""
        Write-Host "✅ EMAIL ENVOYÉ!" -ForegroundColor Green
        Write-Host "   Vérifiez votre boîte email: $email" -ForegroundColor White
    }
    
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "✅ TEST RÉUSSI!" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Cyan
    
} catch {
    Write-Host ""
    Write-Host "ERREUR lors du test:" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode.value__
        
        try {
            $stream = $_.Exception.Response.GetResponseStream()
            $reader = New-Object System.IO.StreamReader($stream)
            $responseBody = $reader.ReadToEnd()
            $reader.Close()
            $stream.Close()
            
            Write-Host "   Code HTTP: $statusCode" -ForegroundColor Red
            Write-Host "   Response: $responseBody" -ForegroundColor Red
            
            # Essayer de parser le JSON
            try {
                $errorData = $responseBody | ConvertFrom-Json
                if ($errorData.error) {
                    Write-Host ""
                    Write-Host "   Erreur detaillee: $($errorData.error)" -ForegroundColor Yellow
                }
                if ($errorData.code) {
                    Write-Host "   Code erreur: $($errorData.code)" -ForegroundColor Yellow
                }
            } catch {
                # Pas de JSON
            }
        } catch {
            Write-Host "   Code HTTP: $statusCode" -ForegroundColor Red
            Write-Host "   Impossible de lire la reponse" -ForegroundColor Red
        }
        
        try {
            $errorData = $responseBody | ConvertFrom-Json
            if ($errorData.error) {
                Write-Host "   Erreur: $($errorData.error)" -ForegroundColor Red
            }
            if ($errorData.message) {
                Write-Host "   Message: $($errorData.message)" -ForegroundColor Red
            }
        } catch {
            Write-Host "   Response brute: $responseBody" -ForegroundColor Red
        }
    } else {
        Write-Host "   $($_.Exception.Message)" -ForegroundColor Red
    }
}
