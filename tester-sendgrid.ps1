# Script pour tester la configuration SendGrid
# Vérifie si la clé API SendGrid est configurée et valide

$API_BASE = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "TEST DE CONFIGURATION SENDGRID" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Vérifier si l'endpoint de test existe
Write-Host "[TEST 1] Test de l'envoi d'un code de vérification..." -ForegroundColor Yellow
Write-Host ""

$testEmail = Read-Host "Entrez votre adresse email pour le test (ou appuyez sur Entrée pour utiliser test@example.com)"
if ([string]::IsNullOrWhiteSpace($testEmail)) {
    $testEmail = "test@example.com"
}

Write-Host ""
Write-Host "Envoi d'un code de vérification à: $testEmail" -ForegroundColor Cyan
Write-Host ""

$body = @{
    email = $testEmail
    username = "Test User"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$API_BASE/user/send-verification-code" `
        -Method POST `
        -ContentType "application/json" `
        -Body $body `
        -ErrorAction Stop
    
    Write-Host "✅ Réponse du serveur:" -ForegroundColor Green
    Write-Host "   Success: $($response.success)" -ForegroundColor White
    Write-Host "   Message: $($response.message)" -ForegroundColor White
    
    if ($response.dev_mode -eq $true) {
        Write-Host ""
        Write-Host "⚠️  MODE DÉVELOPPEMENT DÉTECTÉ" -ForegroundColor Yellow
        Write-Host "   L'email n'a PAS été envoyé réellement" -ForegroundColor Yellow
        Write-Host "   Raison probable: SENDGRID_API_KEY non configurée ou invalide" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "📝 ACTIONS À FAIRE:" -ForegroundColor Cyan
        Write-Host "   1. Vérifiez les variables d'environnement Lambda" -ForegroundColor White
        Write-Host "   2. Vérifiez que SENDGRID_API_KEY est configurée" -ForegroundColor White
        Write-Host "   3. Vérifiez que la clé API SendGrid est valide" -ForegroundColor White
        Write-Host "   4. Consultez les logs CloudWatch pour plus de détails" -ForegroundColor White
    } else {
        Write-Host ""
        Write-Host "✅ EMAIL ENVOYÉ AVEC SUCCÈS!" -ForegroundColor Green
        Write-Host "   Vérifiez votre boîte email: $testEmail" -ForegroundColor White
        Write-Host "   (Vérifiez aussi les spams)" -ForegroundColor Gray
    }
    
    if ($response.code) {
        Write-Host ""
        Write-Host "🔐 CODE DE VÉRIFICATION (DEV): $($response.code)" -ForegroundColor Cyan
    }
    
} catch {
    Write-Host ""
    Write-Host "❌ ERREUR lors du test:" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        
        Write-Host "   Code HTTP: $statusCode" -ForegroundColor Red
        Write-Host "   Réponse: $responseBody" -ForegroundColor Red
        
        try {
            $errorData = $responseBody | ConvertFrom-Json
            if ($errorData.error) {
                Write-Host "   Erreur: $($errorData.error)" -ForegroundColor Red
            }
        } catch {
            Write-Host "   Réponse brute: $responseBody" -ForegroundColor Red
        }
    } else {
        Write-Host "   $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "📝 VÉRIFICATIONS À FAIRE:" -ForegroundColor Cyan
    Write-Host "   1. Vérifiez que Lambda est accessible" -ForegroundColor White
    Write-Host "   2. Vérifiez les logs CloudWatch" -ForegroundColor White
    Write-Host "   3. Vérifiez la configuration SendGrid dans Lambda" -ForegroundColor White
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "FIN DU TEST" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
