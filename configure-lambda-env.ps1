# Script PowerShell pour configurer les variables d'environnement Lambda
# Remplacez LAMBDA_FUNCTION_NAME par le nom de votre fonction Lambda

$LAMBDA_FUNCTION_NAME = "mapevent-backend"  # Nom de la fonction Lambda
$REGION = "eu-west-1"

Write-Host "🔧 Configuration des variables d'environnement Lambda..." -ForegroundColor Yellow
Write-Host "   Fonction: $LAMBDA_FUNCTION_NAME" -ForegroundColor Gray
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
    
    # Ajouter/modifier les variables S3
    $envVars["S3_AVATARS_BUCKET"] = "mapevent-avatars"
    $envVars["AWS_REGION"] = $REGION
    
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
        Write-Host "   - S3_AVATARS_BUCKET=mapevent-avatars" -ForegroundColor Gray
        Write-Host "   - AWS_REGION=$REGION" -ForegroundColor Gray
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
    Write-Host "   1. Le nom de la fonction Lambda est correct" -ForegroundColor Gray
    Write-Host "   2. Vous avez les permissions IAM nécessaires" -ForegroundColor Gray
    Write-Host "   3. La fonction Lambda existe dans la région $REGION" -ForegroundColor Gray
    exit 1
}

Write-Host "`n✅ Configuration terminée !" -ForegroundColor Green

