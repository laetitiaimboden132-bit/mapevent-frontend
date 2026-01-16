# Script pour créer une Lambda Layer avec bcrypt pour Linux

$LAYER_NAME = "bcrypt-layer"
$LAYER_DIR = "layer-bcrypt"
$ZIP_FILE = "bcrypt-layer.zip"
$REGION = "eu-west-1"

Write-Host "Création d'une Lambda Layer avec bcrypt..." -ForegroundColor Cyan
Write-Host ""

# Nettoyer
Remove-Item -Path $LAYER_DIR -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path $ZIP_FILE -Force -ErrorAction SilentlyContinue

# Créer la structure
New-Item -ItemType Directory -Path "$LAYER_DIR/python" -Force | Out-Null

Write-Host "Installation de bcrypt avec Docker (Linux)..." -ForegroundColor Yellow

$workspacePath = (Get-Location).Path
$dockerCmd = "docker run --rm -v `"${workspacePath}:/workspace`" -w /workspace python:3.12-slim pip install --no-cache-dir bcrypt==4.1.2 -t $LAYER_DIR/python"

try {
    Invoke-Expression $dockerCmd 2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0 -and (Test-Path "$LAYER_DIR/python/bcrypt")) {
        Write-Host "✅ bcrypt installé avec succès" -ForegroundColor Green
        
        # Créer le ZIP
        Write-Host "Création du ZIP..." -ForegroundColor Yellow
        Set-Location $LAYER_DIR
        Compress-Archive -Path python -DestinationPath "..\$ZIP_FILE" -Force
        Set-Location ..
        
        $sizeMB = (Get-Item $ZIP_FILE).Length / 1MB
        Write-Host "✅ ZIP créé: $ZIP_FILE ($([math]::Round($sizeMB, 2)) MB)" -ForegroundColor Green
        
        # Créer la layer dans Lambda
        Write-Host ""
        Write-Host "Création de la Lambda Layer..." -ForegroundColor Yellow
        $layerArn = aws lambda publish-layer-version `
            --layer-name $LAYER_NAME `
            --zip-file "fileb://$ZIP_FILE" `
            --compatible-runtimes python3.12 `
            --region $REGION `
            --query 'LayerVersionArn' `
            --output text 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Layer créée: $layerArn" -ForegroundColor Green
            Write-Host ""
            Write-Host "PROCHAINES ÉTAPES:" -ForegroundColor Cyan
            Write-Host "1. Attachez cette layer à votre fonction Lambda:" -ForegroundColor White
            Write-Host "   aws lambda update-function-configuration --function-name mapevent-backend --layers $layerArn --region $REGION" -ForegroundColor Gray
            Write-Host ""
            Write-Host "2. Ou via la console AWS:" -ForegroundColor White
            Write-Host "   Lambda > mapevent-backend > Layers > Add a layer" -ForegroundColor Gray
            Write-Host "   Sélectionnez: Custom layers > $LAYER_NAME" -ForegroundColor Gray
        } else {
            Write-Host "❌ Erreur création layer: $layerArn" -ForegroundColor Red
        }
        
    } else {
        Write-Host "❌ Échec installation bcrypt" -ForegroundColor Red
        Write-Host ""
        Write-Host "SOLUTION ALTERNATIVE:" -ForegroundColor Yellow
        Write-Host "Téléchargez bcrypt wheel pour Linux depuis:" -ForegroundColor White
        Write-Host "https://pypi.org/project/bcrypt/#files" -ForegroundColor Gray
        Write-Host "Cherchez: bcrypt-4.1.2-cp312-cp312-manylinux_*" -ForegroundColor Gray
    }
} catch {
    Write-Host "❌ Erreur: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Docker n'est pas disponible. Utilisez une alternative:" -ForegroundColor Yellow
    Write-Host "1. Téléchargez bcrypt wheel pour Linux" -ForegroundColor White
    Write-Host "2. Extrayez-le dans $LAYER_DIR/python/" -ForegroundColor White
    Write-Host "3. Créez le ZIP manuellement" -ForegroundColor White
}

# Nettoyer
Remove-Item -Path $LAYER_DIR -Recurse -Force -ErrorAction SilentlyContinue
