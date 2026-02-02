# Script PowerShell pour vérifier la configuration Stripe dans Lambda
# Usage: .\verifier-stripe-lambda.ps1

$LAMBDA_FUNCTION_NAME = "mapevent-backend"
$REGION = "eu-west-1"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "VÉRIFICATION STRIPE DANS LAMBDA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

try {
    # Récupérer la configuration Lambda
    Write-Host "📥 Récupération de la configuration Lambda..." -ForegroundColor Cyan
    $config = aws lambda get-function-configuration --function-name $LAMBDA_FUNCTION_NAME --region $REGION | ConvertFrom-Json
    
    if ($config.Environment -and $config.Environment.Variables) {
        $envVars = $config.Environment.Variables
        Write-Host "✅ Variables d'environnement trouvées: $($envVars.Count)" -ForegroundColor Green
        Write-Host ""
        
        # Vérifier STRIPE_SECRET_KEY
        if ($envVars.STRIPE_SECRET_KEY) {
            $secretKey = $envVars.STRIPE_SECRET_KEY
            $preview = $secretKey.Substring(0, [Math]::Min(20, $secretKey.Length))
            Write-Host "✅ STRIPE_SECRET_KEY: $preview..." -ForegroundColor Green
            if ($secretKey.StartsWith("sk_test_")) {
                Write-Host "   Mode: TEST" -ForegroundColor Yellow
            } elseif ($secretKey.StartsWith("sk_live_")) {
                Write-Host "   Mode: LIVE" -ForegroundColor Green
            } else {
                Write-Host "   ⚠️ Format inattendu" -ForegroundColor Yellow
            }
        } else {
            Write-Host "❌ STRIPE_SECRET_KEY: NON CONFIGURÉE" -ForegroundColor Red
        }
        
        Write-Host ""
        
        # Vérifier STRIPE_PUBLIC_KEY
        if ($envVars.STRIPE_PUBLIC_KEY) {
            $publicKey = $envVars.STRIPE_PUBLIC_KEY
            $preview = $publicKey.Substring(0, [Math]::Min(20, $publicKey.Length))
            Write-Host "✅ STRIPE_PUBLIC_KEY: $preview..." -ForegroundColor Green
            if ($publicKey.StartsWith("pk_test_")) {
                Write-Host "   Mode: TEST" -ForegroundColor Yellow
            } elseif ($publicKey.StartsWith("pk_live_")) {
                Write-Host "   Mode: LIVE" -ForegroundColor Green
            } else {
                Write-Host "   ⚠️ Format inattendu" -ForegroundColor Yellow
            }
        } else {
            Write-Host "❌ STRIPE_PUBLIC_KEY: NON CONFIGURÉE" -ForegroundColor Red
        }
        
        Write-Host ""
        
        # Vérifier STRIPE_WEBHOOK_SECRET (optionnel)
        if ($envVars.STRIPE_WEBHOOK_SECRET) {
            $webhookSecret = $envVars.STRIPE_WEBHOOK_SECRET
            $preview = $webhookSecret.Substring(0, [Math]::Min(20, $webhookSecret.Length))
            Write-Host "✅ STRIPE_WEBHOOK_SECRET: $preview..." -ForegroundColor Green
        } else {
            Write-Host "⚠️ STRIPE_WEBHOOK_SECRET: Non configuré (optionnel)" -ForegroundColor Yellow
        }
        
    } else {
        Write-Host "❌ Aucune variable d'environnement trouvée" -ForegroundColor Red
    }
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "VÉRIFICATION DES LOGS LAMBDA" -ForegroundColor Cyan
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Pour voir les logs récents:" -ForegroundColor Yellow
    Write-Host "  aws logs tail /aws/lambda/$LAMBDA_FUNCTION_NAME --follow --region $REGION" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Ou dans AWS Console:" -ForegroundColor Yellow
    Write-Host "  Lambda → $LAMBDA_FUNCTION_NAME → Monitor → Logs" -ForegroundColor Gray
    Write-Host ""
    
} catch {
    Write-Host "❌ Erreur lors de la vérification: $_" -ForegroundColor Red
    Write-Host "`n💡 Assurez-vous que:" -ForegroundColor Yellow
    Write-Host "   1. Le nom de la fonction Lambda est correct ($LAMBDA_FUNCTION_NAME)" -ForegroundColor Gray
    Write-Host "   2. Vous avez les permissions IAM nécessaires" -ForegroundColor Gray
    Write-Host "   3. AWS CLI est configuré correctement" -ForegroundColor Gray
    exit 1
}

Write-Host "========================================" -ForegroundColor Green
Write-Host "VÉRIFICATION TERMINÉE" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
