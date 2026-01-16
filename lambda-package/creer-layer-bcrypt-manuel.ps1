# Script pour créer une Lambda Layer avec bcrypt (sans Docker)

$LAYER_NAME = "bcrypt-layer"
$LAYER_DIR = "layer-bcrypt"
$ZIP_FILE = "bcrypt-layer.zip"
$REGION = "eu-west-1"
$BCRYPT_VERSION = "4.1.2"
$PYTHON_VERSION = "3.12"

Write-Host "Création d'une Lambda Layer avec bcrypt (méthode manuelle)..." -ForegroundColor Cyan
Write-Host ""

# Nettoyer
Remove-Item -Path $LAYER_DIR -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path $ZIP_FILE -Force -ErrorAction SilentlyContinue

# Créer la structure
New-Item -ItemType Directory -Path "$LAYER_DIR/python" -Force | Out-Null

Write-Host "Téléchargement de bcrypt wheel pour Linux..." -ForegroundColor Yellow

# URL du wheel bcrypt pour Linux (manylinux)
$wheelUrl = "https://files.pythonhosted.org/packages/6a/2f/3aac40d4e6356b96349eb49c1bdaf1127e7b5b28738b5500321455d05562e/bcrypt-4.1.2-cp312-cp312-manylinux_2_28_x86_64.whl"

$wheelFile = "bcrypt-4.1.2-cp312-cp312-manylinux_2_28_x86_64.whl"
$wheelPath = "$LAYER_DIR\$wheelFile"

try {
    Write-Host "Téléchargement depuis PyPI..." -ForegroundColor Gray
    Invoke-WebRequest -Uri $wheelUrl -OutFile $wheelPath -ErrorAction Stop
    
    Write-Host "✅ Téléchargement réussi" -ForegroundColor Green
    Write-Host ""
    Write-Host "Extraction du wheel..." -ForegroundColor Yellow
    
    # Extraire le wheel (c'est un ZIP)
    Expand-Archive -Path $wheelPath -DestinationPath "$LAYER_DIR/temp" -Force
    
    # Déplacer bcrypt dans python/
    if (Test-Path "$LAYER_DIR/temp/bcrypt") {
        Move-Item -Path "$LAYER_DIR/temp/bcrypt" -Destination "$LAYER_DIR/python/bcrypt" -Force
        Move-Item -Path "$LAYER_DIR/temp/bcrypt-4.1.2.dist-info" -Destination "$LAYER_DIR/python/bcrypt-4.1.2.dist-info" -Force -ErrorAction SilentlyContinue
        
        Write-Host "✅ bcrypt extrait" -ForegroundColor Green
        
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
        
        if ($LASTEXITCODE -eq 0 -and $layerArn -notmatch "error") {
            Write-Host "✅ Layer créée: $layerArn" -ForegroundColor Green
            Write-Host ""
            Write-Host "Attachement automatique à la fonction Lambda..." -ForegroundColor Yellow
            
            # Attacher automatiquement
            $attachResult = aws lambda update-function-configuration `
                --function-name mapevent-backend `
                --layers $layerArn `
                --region $REGION 2>&1
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Layer attachée avec succès!" -ForegroundColor Green
                Write-Host ""
                Write-Host "Attendez 10-15 secondes que Lambda se mette à jour..." -ForegroundColor Yellow
            } else {
                Write-Host "⚠️  Layer créée mais attachement échoué: $attachResult" -ForegroundColor Yellow
                Write-Host ""
                Write-Host "Attachez manuellement avec:" -ForegroundColor Cyan
                Write-Host "   .\attacher-layer-bcrypt.ps1" -ForegroundColor White
            }
        } else {
            Write-Host "❌ Erreur création layer: $layerArn" -ForegroundColor Red
        }
        
    } else {
        Write-Host "❌ Structure du wheel incorrecte" -ForegroundColor Red
    }
    
    # Nettoyer
    Remove-Item -Path "$LAYER_DIR/temp" -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path $wheelPath -Force -ErrorAction SilentlyContinue
    
} catch {
    Write-Host "❌ Erreur: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Téléchargement manuel:" -ForegroundColor Yellow
    Write-Host "1. Allez sur: https://pypi.org/project/bcrypt/#files" -ForegroundColor White
    Write-Host "2. Téléchargez: bcrypt-4.1.2-cp312-cp312-manylinux_2_28_x86_64.whl" -ForegroundColor White
    Write-Host "3. Extrayez-le et placez bcrypt/ dans $LAYER_DIR/python/" -ForegroundColor White
}

# Nettoyer
Remove-Item -Path $LAYER_DIR -Recurse -Force -ErrorAction SilentlyContinue
