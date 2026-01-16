# Script pour tester SendGrid avec email en parametre

param(
    [string]$Email = "test@example.com"
)

$API_BASE = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "TEST DE CONFIGURATION SENDGRID" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Email de test: $Email" -ForegroundColor Cyan
Write-Host ""

# Generer un code a 6 chiffres
$code = (Get-Random -Minimum 100000 -Maximum 999999).ToString()

$body = @{
    email = $Email
    username = "Test User"
    code = $code
} | ConvertTo-Json

Write-Host "Code genere: $code" -ForegroundColor Gray
Write-Host ""

try {
    Write-Host "Appel de l'API..." -ForegroundColor Yellow
    $response = Invoke-RestMethod -Uri "$API_BASE/user/send-verification-code" `
        -Method POST `
        -ContentType "application/json" `
        -Body $body `
        -ErrorAction Stop
    
    Write-Host ""
    Write-Host "OK - Reponse du serveur:" -ForegroundColor Green
    Write-Host "   Success: $($response.success)" -ForegroundColor White
    Write-Host "   Message: $($response.message)" -ForegroundColor White
    Write-Host "   Dev Mode: $($response.dev_mode)" -ForegroundColor White
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
        Write-Host "   Verifiez votre boite email: $Email" -ForegroundColor White
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
        
        if ([string]::IsNullOrWhiteSpace($responseBody)) {
            Write-Host "   (Reponse vide - verifiez les logs CloudWatch)" -ForegroundColor Yellow
        } else {
            try {
                $errorData = $responseBody | ConvertFrom-Json
                if ($errorData.error) {
                    Write-Host "   Erreur: $($errorData.error)" -ForegroundColor Red
                }
                if ($errorData.message) {
                    Write-Host "   Message: $($errorData.message)" -ForegroundColor Red
                }
            } catch {
                Write-Host "   Reponse brute: $responseBody" -ForegroundColor Red
            }
        }
    } else {
        Write-Host "   $($_.Exception.Message)" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "VERIFICATIONS:" -ForegroundColor Cyan
    Write-Host "   1. Verifiez que Lambda est accessible" -ForegroundColor White
    Write-Host "   2. Verifiez les logs CloudWatch" -ForegroundColor White
    Write-Host "   3. Verifiez la configuration SendGrid dans Lambda" -ForegroundColor White
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "FIN DU TEST" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
