# Script PowerShell pour configurer les clés Stripe dans Lambda
# Usage: .\configure-stripe-lambda.ps1

$LAMBDA_FUNCTION_NAME = "mapevent-backend"
$REGION = "eu-west-1"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CONFIGURATION STRIPE DANS LAMBDA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Demander les clés Stripe
Write-Host "Entrez vos clés Stripe:" -ForegroundColor Yellow
Write-Host ""

$stripeSecretKey = Read-Host "STRIPE_SECRET_KEY (sk_test_... ou sk_live_...)"
$stripePublicKey = Read-Host "STRIPE_PUBLIC_KEY (pk_test_... ou pk_live_...)"

# Demander le webhook secret (optionnel)
Write-Host ""
$useWebhook = Read-Host "Voulez-vous configurer STRIPE_WEBHOOK_SECRET? (o/n)"
$stripeWebhookSecret = ""
if ($useWebhook -eq "o" -or $useWebhook -eq "O") {
    $stripeWebhookSecret = Read-Host "STRIPE_WEBHOOK_SECRET (whsec_...)"
}

# Vérifier que les clés ne sont pas vides
if ([string]::IsNullOrWhiteSpace($stripeSecretKey) -or [string]::IsNullOrWhiteSpace($stripePublicKey)) {
    Write-Host "❌ Erreur: Les clés Stripe ne peuvent pas être vides!" -ForegroundColor Red
    exit 1
}

# Vérifier le format des clés
if (-not $stripeSecretKey.StartsWith("sk_test_") -and -not $stripeSecretKey.StartsWith("sk_live_")) {
    Write-Host "⚠️ Attention: STRIPE_SECRET_KEY ne commence pas par sk_test_ ou sk_live_" -ForegroundColor Yellow
    $continue = Read-Host "Continuer quand même? (o/n)"
    if ($continue -ne "o" -and $continue -ne "O") {
        exit 1
    }
}

if (-not $stripePublicKey.StartsWith("pk_test_") -and -not $stripePublicKey.StartsWith("pk_live_")) {
    Write-Host "⚠️ Attention: STRIPE_PUBLIC_KEY ne commence pas par pk_test_ ou pk_live_" -ForegroundColor Yellow
    $continue = Read-Host "Continuer quand même? (o/n)"
    if ($continue -ne "o" -and $continue -ne "O") {
        exit 1
    }
}

Write-Host ""
Write-Host "Configuration en cours..." -ForegroundColor Yellow
Write-Host "   Fonction Lambda: $LAMBDA_FUNCTION_NAME" -ForegroundColor Gray
Write-Host "   Région: $REGION" -ForegroundColor Gray

try {
    # Récupérer la configuration actuelle
    Write-Host "`n📥 Récupération de la configuration actuelle..." -ForegroundColor Cyan
    $currentConfig = aws lambda get-function-configuration --function-name $LAMBDA_FUNCTION_NAME --region $REGION | ConvertFrom-Json
    
    # Récupérer les variables d'environnement existantes
    $envVars = @{}
    if ($currentConfig.Environment -and $currentConfig.Environment.Variables) {
        $envVars = $currentConfig.Environment.Variables
        Write-Host "✅ Variables existantes trouvées: $($envVars.Count)" -ForegroundColor Green
    }
    
    # Ajouter/modifier les variables Stripe
    $envVars["STRIPE_SECRET_KEY"] = $stripeSecretKey
    $envVars["STRIPE_PUBLIC_KEY"] = $stripePublicKey
    
    if (-not [string]::IsNullOrWhiteSpace($stripeWebhookSecret)) {
        $envVars["STRIPE_WEBHOOK_SECRET"] = $stripeWebhookSecret
    }
    
    # Convertir en JSON
    $envJson = $envVars | ConvertTo-Json -Compress
    
    # Mettre à jour la configuration
    Write-Host "`n📤 Mise à jour de la configuration Lambda..." -ForegroundColor Cyan
    $updateResult = aws lambda update-function-configuration `
        --function-name $LAMBDA_FUNCTION_NAME `
        --region $REGION `
        --environment "Variables=$envJson" `
        | ConvertFrom-Json
    
    if ($updateResult.LastUpdateStatus -eq "InProgress") {
        Write-Host "✅ Configuration mise à jour avec succès !" -ForegroundColor Green
        Write-Host "   Variables configurées:" -ForegroundColor Gray
        Write-Host "   - STRIPE_SECRET_KEY=$($stripeSecretKey.Substring(0, [Math]::Min(20, $stripeSecretKey.Length)))..." -ForegroundColor Gray
        Write-Host "   - STRIPE_PUBLIC_KEY=$($stripePublicKey.Substring(0, [Math]::Min(20, $stripePublicKey.Length)))..." -ForegroundColor Gray
        if (-not [string]::IsNullOrWhiteSpace($stripeWebhookSecret)) {
            Write-Host "   - STRIPE_WEBHOOK_SECRET=$($stripeWebhookSecret.Substring(0, [Math]::Min(20, $stripeWebhookSecret.Length)))..." -ForegroundColor Gray
        }
        Write-Host "`n⏳ Attente de la finalisation de la mise à jour..." -ForegroundColor Yellow
        
        # Attendre que la mise à jour soit terminée
        $maxAttempts = 30
        $attempt = 0
        $completed = $false
        
        while (-not $completed -and $attempt -lt $maxAttempts) {
            Start-Sleep -Seconds 2
            $status = aws lambda get-function-configuration --function-name $LAMBDA_FUNCTION_NAME --region $REGION --query "LastUpdateStatus" --output text
            if ($status -eq "Successful") {
                $completed = $true
                Write-Host "✅ Mise à jour finalisée avec succès !" -ForegroundColor Green
            } elseif ($status -eq "Failed") {
                Write-Host "❌ Échec de la mise à jour" -ForegroundColor Red
                break
            }
            $attempt++
        }
    } else {
        Write-Host "✅ Configuration mise à jour !" -ForegroundColor Green
    }
    
} catch {
    Write-Host "❌ Erreur lors de la configuration: $_" -ForegroundColor Red
    Write-Host "`n💡 Assurez-vous que:" -ForegroundColor Yellow
    Write-Host "   1. Le nom de la fonction Lambda est correct ($LAMBDA_FUNCTION_NAME)" -ForegroundColor Gray
    Write-Host "   2. Vous avez les permissions IAM nécessaires" -ForegroundColor Gray
    Write-Host "   3. La fonction Lambda existe dans la région $REGION" -ForegroundColor Gray
    Write-Host "   4. AWS CLI est configuré correctement" -ForegroundColor Gray
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "✅ CONFIGURATION TERMINÉE !" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Les clés Stripe ont été configurées dans Lambda." -ForegroundColor Cyan
Write-Host "Vous pouvez maintenant tester les paiements Stripe." -ForegroundColor Cyan
Write-Host ""
