# Script pour attacher la layer bcrypt à la fonction Lambda

$FUNCTION_NAME = "mapevent-backend"
$LAYER_NAME = "bcrypt-layer"
$REGION = "eu-west-1"

Write-Host "Recherche de la layer $LAYER_NAME..." -ForegroundColor Cyan

# Trouver la dernière version de la layer
$layerArn = aws lambda list-layer-versions `
    --layer-name $LAYER_NAME `
    --region $REGION `
    --query 'LayerVersions[0].LayerVersionArn' `
    --output text 2>&1

if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($layerArn) -or $layerArn -match "None") {
    Write-Host "❌ Layer $LAYER_NAME non trouvée" -ForegroundColor Red
    Write-Host ""
    Write-Host "Créez d'abord la layer avec:" -ForegroundColor Yellow
    Write-Host "   .\creer-layer-bcrypt.ps1" -ForegroundColor White
    exit 1
}

Write-Host "✅ Layer trouvée: $layerArn" -ForegroundColor Green
Write-Host ""

# Récupérer les layers existantes
Write-Host "Récupération des layers actuelles..." -ForegroundColor Yellow
$currentLayers = aws lambda get-function-configuration `
    --function-name $FUNCTION_NAME `
    --region $REGION `
    --query 'Layers[*].Arn' `
    --output text 2>&1

$layers = @()
if ($currentLayers -and -not ($currentLayers -match "None")) {
    $layers = $currentLayers -split "`t"
    Write-Host "Layers existantes: $($layers.Count)" -ForegroundColor Gray
}

# Ajouter la nouvelle layer (si pas déjà présente)
if ($layers -notcontains $layerArn) {
    $layers += $layerArn
    Write-Host "Ajout de la layer bcrypt..." -ForegroundColor Yellow
    
    $layersParam = $layers -join " "
    $result = aws lambda update-function-configuration `
        --function-name $FUNCTION_NAME `
        --layers $layersParam `
        --region $REGION 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Layer bcrypt attachée avec succès!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Attendez 10-15 secondes que Lambda se mette à jour..." -ForegroundColor Yellow
    } else {
        Write-Host "❌ Erreur: $result" -ForegroundColor Red
    }
} else {
    Write-Host "✅ Layer bcrypt déjà attachée" -ForegroundColor Green
}
