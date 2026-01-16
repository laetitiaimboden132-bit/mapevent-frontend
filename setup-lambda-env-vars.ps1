# Script pour configurer les variables d'environnement Lambda
# Exécuter: .\setup-lambda-env-vars.ps1

$FUNCTION_NAME = "MapEventAI-Backend"  # À adapter selon votre nom de fonction Lambda
$REGION = "eu-west-1"

Write-Host "🔧 Configuration des variables d'environnement Lambda" -ForegroundColor Cyan
Write-Host ""

# Vérifier que AWS CLI est installé
if (-not (Get-Command aws -ErrorAction SilentlyContinue)) {
    Write-Host "❌ AWS CLI n'est pas installé" -ForegroundColor Red
    exit 1
}

# Variables d'environnement à ajouter
$envVars = @{
    "S3_AVATARS_BUCKET" = "mapevent-avatars"
    "AWS_REGION" = $REGION
}

Write-Host "📋 Variables à configurer:" -ForegroundColor Yellow
foreach ($key in $envVars.Keys) {
    Write-Host "   $key = $($envVars[$key])" -ForegroundColor White
}
Write-Host ""

# Récupérer les variables d'environnement existantes
Write-Host "📥 Récupération des variables d'environnement existantes..." -ForegroundColor Yellow
try {
    $currentConfig = aws lambda get-function-configuration --function-name $FUNCTION_NAME --region $REGION | ConvertFrom-Json
    $currentEnvVars = $currentConfig.Environment.Variables
    
    Write-Host "✅ Variables existantes récupérées" -ForegroundColor Green
    Write-Host ""
    
    # Fusionner avec les nouvelles variables
    $mergedEnvVars = @{}
    if ($currentEnvVars) {
        foreach ($key in $currentEnvVars.PSObject.Properties.Name) {
            $mergedEnvVars[$key] = $currentEnvVars.$key
        }
    }
    
    foreach ($key in $envVars.Keys) {
        $mergedEnvVars[$key] = $envVars[$key]
    }
    
    # Convertir en format JSON pour AWS CLI
    $envVarsJson = @{
        Variables = $mergedEnvVars
    } | ConvertTo-Json -Depth 10
    
    $envVarsFile = "lambda-env-vars.json"
    $envVarsJson | Out-File -FilePath $envVarsFile -Encoding UTF8
    
    # Mettre à jour la fonction Lambda
    Write-Host "🔄 Mise à jour de la fonction Lambda..." -ForegroundColor Yellow
    aws lambda update-function-configuration `
        --function-name $FUNCTION_NAME `
        --region $REGION `
        --environment "Variables=$($mergedEnvVars | ConvertTo-Json -Compress)"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Variables d'environnement mises à jour avec succès !" -ForegroundColor Green
    } else {
        Write-Host "❌ Erreur lors de la mise à jour" -ForegroundColor Red
        Write-Host ""
        Write-Host "💡 Vous pouvez configurer manuellement dans AWS Console:" -ForegroundColor Yellow
        Write-Host "   1. Allez dans Lambda > Fonctions > $FUNCTION_NAME" -ForegroundColor White
        Write-Host "   2. Configuration > Variables d'environnement" -ForegroundColor White
        Write-Host "   3. Ajoutez:" -ForegroundColor White
        foreach ($key in $envVars.Keys) {
            Write-Host "      - $key = $($envVars[$key])" -ForegroundColor Cyan
        }
    }
    
    Remove-Item $envVarsFile -ErrorAction SilentlyContinue
    
} catch {
    Write-Host "❌ Erreur: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Configuration manuelle requise:" -ForegroundColor Yellow
    Write-Host "   1. Allez dans AWS Console > Lambda > $FUNCTION_NAME" -ForegroundColor White
    Write-Host "   2. Configuration > Variables d'environnement" -ForegroundColor White
    Write-Host "   3. Ajoutez:" -ForegroundColor White
    foreach ($key in $envVars.Keys) {
        Write-Host "      - $key = $($envVars[$key])" -ForegroundColor Cyan
    }
}

Write-Host ""

