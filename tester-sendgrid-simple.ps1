# Script simple pour tester SendGrid (sans caracteres speciaux)

$API_BASE = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "TEST DE CONFIGURATION SENDGRID" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

$testEmail = Read-Host "Entrez votre adresse email pour le test"
if ([string]::IsNullOrWhiteSpace($testEmail)) {
    $testEmail = "test@example.com"
}

Write-Host ""
Write-Host "Envoi d'un code de verification a: $testEmail" -ForegroundColor Cyan
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
    
    Write-Host "OK - Reponse du serveur:" -ForegroundColor Green
    Write-Host "   Success: $($response.success)" -ForegroundColor White
    Write-Host "   Message: $($response.message)" -ForegroundColor White
    Write-Host ""
    
    if ($response.dev_mode -eq $true) {
        Write-Host "MODE DEVELOPPEMENT DETECTE" -ForegroundColor Yellow
        Write-Host "L'email n'a PAS ete envoye reellement" -ForegroundColor Yellow
        Write-Host "Raison probable: SENDGRID_API_KEY non configuree" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "ACTIONS A FAIRE:" -ForegroundColor Cyan
        Write-Host "   1. Verifiez les variables d'environnement Lambda" -ForegroundColor White
        Write-Host "   2. Verifiez que SENDGRID_API_KEY est configuree" -ForegroundColor White
        Write-Host "   3. Verifiez que la cle API SendGrid est valide" -ForegroundColor White
    } else {
        Write-Host "EMAIL ENVOYE AVEC SUCCES!" -ForegroundColor Green
        Write-Host "   Verifiez votre boite email: $testEmail" -ForegroundColor White
        Write-Host "   (Verifiez aussi les spams)" -ForegroundColor Gray
    }
    
    if ($response.code) {
        Write-Host ""
        Write-Host "CODE DE VERIFICATION (DEV): $($response.code)" -ForegroundColor Cyan
    }
    
} catch {
    Write-Host ""
    Write-Host "ERREUR lors du test:" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        
        Write-Host "   Code HTTP: $statusCode" -ForegroundColor Red
        Write-Host "   Reponse: $responseBody" -ForegroundColor Red
        
        try {
            $errorData = $responseBody | ConvertFrom-Json
            if ($errorData.error) {
                Write-Host "   Erreur: $($errorData.error)" -ForegroundColor Red
            }
        } catch {
            Write-Host "   Reponse brute: $responseBody" -ForegroundColor Red
        }
    } else {
        Write-Host "   $($_.Exception.Message)" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "FIN DU TEST" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
