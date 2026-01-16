# Script pour ajouter les variables S3 à Lambda

$LAMBDA_FUNCTION_NAME = "mapevent-backend"
$REGION = "eu-west-1"

Write-Host "🔧 Ajout des variables S3 à Lambda..." -ForegroundColor Yellow

# Récupérer les variables actuelles
$currentEnv = aws lambda get-function-configuration --function-name $LAMBDA_FUNCTION_NAME --region $REGION --query "Environment.Variables" --output json | ConvertFrom-Json

# Ajouter les nouvelles variables
$currentEnv | Add-Member -NotePropertyName "S3_AVATARS_BUCKET" -NotePropertyValue "mapevent-avatars" -Force
$currentEnv | Add-Member -NotePropertyName "AWS_REGION" -NotePropertyValue $REGION -Force

# Convertir en JSON compact (sans espaces)
$envJson = ($currentEnv | ConvertTo-Json -Compress -Depth 10).Replace('"', '\"')

# Mettre à jour
Write-Host "📤 Mise à jour de la configuration..." -ForegroundColor Cyan
aws lambda update-function-configuration `
    --function-name $LAMBDA_FUNCTION_NAME `
    --region $REGION `
    --environment "Variables={$envJson}"

Write-Host "✅ Variables S3 ajoutées !" -ForegroundColor Green
Write-Host "   - S3_AVATARS_BUCKET=mapevent-avatars" -ForegroundColor Gray
Write-Host "   - AWS_REGION=$REGION" -ForegroundColor Gray






