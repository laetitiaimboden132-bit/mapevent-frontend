# Script pour tester le systeme de lien magique

$API_BASE = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api"

$email = "test-$(Get-Date -Format 'yyyyMMddHHmmss')@example.com"
$username = "TestUser$(Get-Date -Format 'yyyyMMddHHmmss')"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "TEST LIEN MAGIQUE DE VERIFICATION" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Email: $email" -ForegroundColor White
Write-Host "Username: $username" -ForegroundColor White
Write-Host ""

# Etape 1: Demander un lien de verification
Write-Host "Etape 1: Demande d'un lien de verification..." -ForegroundColor Yellow

$linkBody = @{
    email = $email
    username = $username
} | ConvertTo-Json

try {
    $linkResponse = Invoke-RestMethod -Uri "$API_BASE/user/send-verification-link" `
        -Method POST `
        -ContentType "application/json" `
        -Body $linkBody `
        -ErrorAction Stop
    
    Write-Host "OK - Lien genere avec succes!" -ForegroundColor Green
    Write-Host "   Success: $($linkResponse.success)" -ForegroundColor White
    Write-Host "   Message: $($linkResponse.message)" -ForegroundColor White
    Write-Host "   Dev Mode: $($linkResponse.dev_mode)" -ForegroundColor White
    
    if ($linkResponse.dev_mode -eq $true -and $linkResponse.verification_url) {
        Write-Host ""
        Write-Host "LIEN DE VERIFICATION (MODE DEV):" -ForegroundColor Cyan
        Write-Host "   $($linkResponse.verification_url)" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Copiez ce lien dans votre navigateur pour verifier l'email" -ForegroundColor Gray
        
        # Extraire le token
        $url = $linkResponse.verification_url
        if ($url -match 'token=([^&]+)') {
            $token = $matches[1]
            Write-Host ""
            Write-Host "Etape 2: Verification du lien..." -ForegroundColor Yellow
            Write-Host "   Token extrait: $($token.Substring(0, 20))..." -ForegroundColor Gray
            
            # Tester la verification
            $verifyUrl = "$API_BASE/user/verify-email-link?token=$token&email=$email"
            $verifyResponse = Invoke-RestMethod -Uri $verifyUrl -Method GET -ErrorAction Stop
            
            Write-Host "OK - Email verifie avec succes!" -ForegroundColor Green
            Write-Host "   Success: $($verifyResponse.success)" -ForegroundColor White
            Write-Host "   Message: $($verifyResponse.message)" -ForegroundColor White
        }
    } else {
        Write-Host ""
        Write-Host "OK - Email envoye! Verifiez votre boite email." -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "OK - TEST REUSSI!" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Cyan
    
} catch {
    Write-Host ""
    Write-Host "ERREUR:" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode.value__
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        $reader.Close()
        
        Write-Host "   Code HTTP: $statusCode" -ForegroundColor Red
        Write-Host "   Response: $responseBody" -ForegroundColor Red
    } else {
        Write-Host "   $($_.Exception.Message)" -ForegroundColor Red
    }
}
