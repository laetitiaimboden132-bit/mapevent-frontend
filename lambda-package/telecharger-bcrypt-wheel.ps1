# Télécharge le wheel bcrypt pour Linux avec pip

$LAYER_DIR = "layer-bcrypt"
$ZIP_FILE = "bcrypt-layer.zip"
$REGION = "eu-west-1"
$LAYER_NAME = "bcrypt-layer"

Write-Host "Téléchargement de bcrypt wheel pour Linux..." -ForegroundColor Cyan

# Nettoyer
Remove-Item -Path $LAYER_DIR -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path $ZIP_FILE -Force -ErrorAction SilentlyContinue

# Créer la structure
New-Item -ItemType Directory -Path "$LAYER_DIR/python" -Force | Out-Null

# Essayer avec pip download (nécessite pip)
Write-Host "Téléchargement avec pip download..." -ForegroundColor Yellow

try {
    # Télécharger le wheel sans l'installer
    pip download --platform manylinux2014_x86_64 --only-binary=:all: --python-version 3.12 --abi cp312 bcrypt==4.1.2 -d $LAYER_DIR 2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        $wheelFile = Get-ChildItem -Path $LAYER_DIR -Filter "*.whl" | Select-Object -First 1
        
        if ($wheelFile) {
            Write-Host "✅ Wheel téléchargé: $($wheelFile.Name)" -ForegroundColor Green
            
            # Extraire le wheel (renommer en .zip car c'est un ZIP)
            Write-Host "Extraction..." -ForegroundColor Yellow
            $zipFile = $wheelFile.FullName -replace '\.whl$', '.zip'
            Copy-Item -Path $wheelFile.FullName -Destination $zipFile -Force
            Expand-Archive -Path $zipFile -DestinationPath "$LAYER_DIR/temp" -Force
            Remove-Item -Path $zipFile -Force
            
            # Déplacer bcrypt
            if (Test-Path "$LAYER_DIR/temp/bcrypt") {
                Move-Item -Path "$LAYER_DIR/temp/bcrypt" -Destination "$LAYER_DIR/python/bcrypt" -Force
                Get-ChildItem -Path "$LAYER_DIR/temp" -Filter "*.dist-info" | ForEach-Object {
                    Move-Item -Path $_.FullName -Destination "$LAYER_DIR/python/" -Force
                }
                
                Write-Host "✅ bcrypt extrait" -ForegroundColor Green
                
                # Créer le ZIP
                Write-Host "Création du ZIP..." -ForegroundColor Yellow
                Set-Location $LAYER_DIR
                Compress-Archive -Path python -DestinationPath "..\$ZIP_FILE" -Force
                Set-Location ..
                
                $sizeMB = (Get-Item $ZIP_FILE).Length / 1MB
                Write-Host "✅ ZIP créé: $ZIP_FILE ($([math]::Round($sizeMB, 2)) MB)" -ForegroundColor Green
                
                # Créer et attacher la layer
                Write-Host ""
                Write-Host "Création de la Lambda Layer..." -ForegroundColor Yellow
                $layerArn = aws lambda publish-layer-version `
                    --layer-name $LAYER_NAME `
                    --zip-file "fileb://$ZIP_FILE" `
                    --compatible-runtimes python3.12 `
                    --region $REGION `
                    --query 'LayerVersionArn' `
                    --output text 2>&1
                
                if ($LASTEXITCODE -eq 0 -and $layerArn -notmatch "error" -and -not [string]::IsNullOrWhiteSpace($layerArn)) {
                    Write-Host "✅ Layer créée: $layerArn" -ForegroundColor Green
                    
                    Write-Host "Attachement à Lambda..." -ForegroundColor Yellow
                    aws lambda update-function-configuration `
                        --function-name mapevent-backend `
                        --layers $layerArn `
                        --region $REGION 2>&1 | Out-Null
                    
                    if ($LASTEXITCODE -eq 0) {
                        Write-Host "✅ Layer attachée avec succès!" -ForegroundColor Green
                        Write-Host ""
                        Write-Host "Attendez 15 secondes puis testez:" -ForegroundColor Yellow
                        Write-Host "   cd .." -ForegroundColor Gray
                        Write-Host "   .\verifier-sendgrid-complet.ps1 -Email votre-email@gmail.com" -ForegroundColor Gray
                    } else {
                        Write-Host "⚠️  Attachement échoué, attachez manuellement avec:" -ForegroundColor Yellow
                        Write-Host "   .\attacher-layer-bcrypt.ps1" -ForegroundColor White
                    }
                } else {
                    Write-Host "❌ Erreur création layer" -ForegroundColor Red
                }
                
                # Nettoyer
                Remove-Item -Path "$LAYER_DIR/temp" -Recurse -Force -ErrorAction SilentlyContinue
            }
        } else {
            Write-Host "❌ Aucun wheel trouvé" -ForegroundColor Red
        }
    } else {
        Write-Host "❌ Échec téléchargement pip" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Erreur: $_" -ForegroundColor Red
}

# Nettoyer
Remove-Item -Path $LAYER_DIR -Recurse -Force -ErrorAction SilentlyContinue
