# Script pour restaurer TOUTES les variables d'environnement Lambda
# Basé sur les valeurs récupérées plus tôt

$LAMBDA_FUNCTION_NAME = "mapevent-backend"
$REGION = "eu-west-1"

Write-Host "🔧 Restauration des variables d'environnement Lambda..." -ForegroundColor Yellow
Write-Host "⚠️ ATTENTION: Ce script restaure les variables depuis les valeurs connues" -ForegroundColor Red

# Variables récupérées depuis les logs précédents
$envVars = @{
    # RDS
    "RDS_HOST" = "mapevent-db.cr0mmuc0elm6.eu-west-1.rds.amazonaws.com"
    "RDS_PORT" = "5432"
    "RDS_DB" = "mapevent"
    "RDS_USER" = "postgres"
    "RDS_PASSWORD" = "666666Laeti69!"
    
    # Redis
    "REDIS_HOST" = "mapevent-cache-0001-001.mapevent-cache.jqxmjs.euw1.cache.amazonaws.com"
    "REDIS_PORT" = "6379"
    
    # Flask
    "FLASK_ENV" = "production"
    
    # S3
    "S3_AVATARS_BUCKET" = "mapevent-avatars"
    
    # Google Cloud Vision (vide si pas utilise)
    "GOOGLE_CLOUD_VISION_API_KEY" = ""
    
    # Stripe - ATTENTION: Il faut les vraies valeurs !
    # "STRIPE_SECRET_KEY" = "sk_test_..." # À RÉCUPÉRER MANUELLEMENT
    # "STRIPE_PUBLIC_KEY" = "pk_test_..." # À RÉCUPÉRER MANUELLEMENT  
    # "STRIPE_WEBHOOK_SECRET" = "whsec_..." # À RÉCUPÉRER MANUELLEMENT
}

Write-Host "`n📤 Mise à jour des variables..." -ForegroundColor Cyan

# Convertir en JSON
$json = ($envVars | ConvertTo-Json -Compress)

# Mettre à jour
try {
    aws lambda update-function-configuration `
        --function-name $LAMBDA_FUNCTION_NAME `
        --region $REGION `
        --environment "Variables=$json"
    
    Write-Host "✅ Variables restaurées !" -ForegroundColor Green
    Write-Host "⚠️ ATTENTION: Les clés Stripe doivent être ajoutées manuellement !" -ForegroundColor Yellow
    Write-Host "   - STRIPE_SECRET_KEY" -ForegroundColor Gray
    Write-Host "   - STRIPE_PUBLIC_KEY" -ForegroundColor Gray
    Write-Host "   - STRIPE_WEBHOOK_SECRET" -ForegroundColor Gray
} catch {
    Write-Host "❌ Erreur: $_" -ForegroundColor Red
    Write-Host "`n💡 Restaurez manuellement dans AWS Console:" -ForegroundColor Yellow
    Write-Host "   Lambda > $LAMBDA_FUNCTION_NAME > Configuration > Environment variables" -ForegroundColor Gray
}






