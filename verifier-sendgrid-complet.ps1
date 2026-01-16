# Script complet pour verifier SendGrid
# 1. Verifie si SENDGRID_API_KEY est configuree dans Lambda
# 2. Teste l'envoi d'email

param(
    [string]$Email = ""
)

$FUNCTION_NAME = "mapevent-backend"
$REGION = "eu-west-1"
$API_BASE = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "VERIFICATION COMPLETE SENDGRID" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# ETAPE 1: Verifier dans Lambda
Write-Host "ETAPE 1: Verification dans AWS Lambda..." -ForegroundColor Yellow
Write-Host ""

try {
    $config = aws lambda get-function-configuration `
        --function-name $FUNCTION_NAME `
        --region $REGION `
        --query 'Environment.Variables' `
        --output json 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERREUR: Impossible de recuperer la configuration Lambda" -ForegroundColor Red
        Write-Host "   Message: $config" -ForegroundColor Red
        Write-Host ""
        Write-Host "VERIFICATIONS:" -ForegroundColor Cyan
        Write-Host "   1. AWS CLI est installe et configure" -ForegroundColor White
        Write-Host "   2. Vous avez les permissions Lambda" -ForegroundColor White
        Write-Host "   3. La fonction '$FUNCTION_NAME' existe" -ForegroundColor White
        exit 1
    }
    
    $envVars = $config | ConvertFrom-Json
    
    if ($envVars.PSObject.Properties.Name -contains "SENDGRID_API_KEY") {
        $keyValue = $envVars.SENDGRID_API_KEY
        
        if ([string]::IsNullOrWhiteSpace($keyValue)) {
            Write-Host "❌ SENDGRID_API_KEY est configuree mais VIDE" -ForegroundColor Red
            Write-Host ""
        } elseif ($keyValue -match "^SG\.") {
            $keyLength = $keyValue.Length
            $maskedKey = $keyValue.Substring(0, 5) + "..." + $keyValue.Substring($keyLength - 5)
            Write-Host "✅ SENDGRID_API_KEY est configuree dans Lambda" -ForegroundColor Green
            Write-Host "   Cle (masquee): $maskedKey" -ForegroundColor Gray
            Write-Host "   Longueur: $keyLength caracteres" -ForegroundColor Gray
            Write-Host ""
        } else {
            Write-Host "⚠️  SENDGRID_API_KEY est configuree mais format suspect" -ForegroundColor Yellow
            Write-Host "   (Une cle SendGrid commence par 'SG.')" -ForegroundColor Yellow
            Write-Host ""
        }
    } else {
        Write-Host "❌ SENDGRID_API_KEY N'EST PAS configuree dans Lambda" -ForegroundColor Red
        Write-Host ""
        Write-Host "ACTIONS A FAIRE:" -ForegroundColor Cyan
        Write-Host "   1. Allez sur AWS Console > Lambda > $FUNCTION_NAME" -ForegroundColor White
        Write-Host "   2. Configuration > Environment variables" -ForegroundColor White
        Write-Host "   3. Ajoutez SENDGRID_API_KEY avec votre cle SendGrid" -ForegroundColor White
        Write-Host ""
    }
    
} catch {
    Write-Host "ERREUR lors de la verification Lambda:" -ForegroundColor Red
    Write-Host "   $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
}

# ETAPE 2: Tester l'envoi d'email
Write-Host "ETAPE 2: Test d'envoi d'email..." -ForegroundColor Yellow
Write-Host ""

if ([string]::IsNullOrWhiteSpace($Email)) {
    $Email = Read-Host "Entrez votre email de test"
}

if ([string]::IsNullOrWhiteSpace($Email)) {
    Write-Host "Email non fourni, test annule" -ForegroundColor Yellow
    exit 0
}

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
        Write-Host "⚠️  MODE DEVELOPPEMENT DETECTE" -ForegroundColor Yellow
        Write-Host "   L'email n'a PAS ete envoye reellement" -ForegroundColor Yellow
        Write-Host "   Raison: SENDGRID_API_KEY non configuree ou invalide" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "ACTIONS A FAIRE:" -ForegroundColor Cyan
        Write-Host "   1. Verifiez que SENDGRID_API_KEY est dans Lambda" -ForegroundColor White
        Write-Host "   2. Verifiez que la cle est valide (commence par 'SG.')" -ForegroundColor White
        Write-Host "   3. Verifiez que votre compte SendGrid est actif" -ForegroundColor White
    } else {
        Write-Host "✅ EMAIL ENVOYE AVEC SUCCES!" -ForegroundColor Green
        Write-Host "   Verifiez votre boite email: $Email" -ForegroundColor White
        Write-Host "   (Verifiez aussi les spams)" -ForegroundColor Gray
    }
    
    if ($response.code) {
        Write-Host ""
        Write-Host "CODE DE VERIFICATION (DEV): $($response.code)" -ForegroundColor Cyan
    }
    
} catch {
    Write-Host ""
    Write-Host "❌ ERREUR lors du test:" -ForegroundColor Red
    
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
Write-Host "FIN DE LA VERIFICATION" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
