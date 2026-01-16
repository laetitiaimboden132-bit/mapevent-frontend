# Script pour créer une Lambda Layer avec bcrypt en téléchargeant directement le wheel Linux

$LAYER_NAME = "bcrypt-layer"
$LAYER_DIR = "layer-bcrypt"
$ZIP_FILE = "bcrypt-layer.zip"
$REGION = "eu-west-1"
$BCRYPT_VERSION = "4.1.2"
$PYTHON_VERSION = "3.12"

Write-Host "Création d'une Lambda Layer avec bcrypt (méthode directe)..." -ForegroundColor Cyan
Write-Host ""

# Nettoyer
Remove-Item -Path $LAYER_DIR -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path $ZIP_FILE -Force -ErrorAction SilentlyContinue

# Créer la structure
New-Item -ItemType Directory -Path "$LAYER_DIR/python" -Force | Out-Null

Write-Host "Téléchargement du wheel bcrypt pour Linux..." -ForegroundColor Yellow

$wheelFile = "bcrypt-$BCRYPT_VERSION-wheel.whl"
$tempDir = "temp-wheel"
$downloadDir = "downloads"

# Créer le répertoire de téléchargement
New-Item -ItemType Directory -Path $downloadDir -Force | Out-Null

try {
    # Utiliser pip download pour télécharger le wheel (si pip est disponible)
    Write-Host "Tentative de téléchargement avec pip download..." -ForegroundColor Gray
    $pipCmd = "pip download --only-binary=:all: --platform manylinux2014_x86_64 --python-version $PYTHON_VERSION --no-deps bcrypt==$BCRYPT_VERSION -d $downloadDir"
    
    try {
        Invoke-Expression $pipCmd 2>&1 | Out-Null
        $downloadedWheel = Get-ChildItem -Path $downloadDir -Filter "bcrypt-*.whl" | Select-Object -First 1
        
        if ($downloadedWheel) {
            Copy-Item -Path $downloadedWheel.FullName -Destination $wheelFile -Force
            Write-Host "✅ Wheel téléchargé: $wheelFile" -ForegroundColor Green
        } else {
            throw "Aucun wheel trouvé"
        }
    } catch {
        Write-Host "⚠️  pip download a échoué, tentative avec URL directe..." -ForegroundColor Yellow
        
        # URL alternative - utiliser PyPI API pour trouver le bon fichier
        $pypiUrl = "https://pypi.org/pypi/bcrypt/$BCRYPT_VERSION/json"
        $pypiResponse = Invoke-RestMethod -Uri $pypiUrl
        $wheelInfo = $pypiResponse.urls | Where-Object { 
            $_.filename -like "*manylinux*x86_64*" -and $_.python_version -eq "py3" 
        } | Select-Object -First 1
        
        if ($wheelInfo) {
            Write-Host "Téléchargement depuis: $($wheelInfo.url)" -ForegroundColor Gray
            Invoke-WebRequest -Uri $wheelInfo.url -OutFile $wheelFile -ErrorAction Stop
            Write-Host "✅ Wheel téléchargé: $wheelFile" -ForegroundColor Green
        } else {
            throw "Impossible de trouver le wheel approprié"
        }
    }
    
    # Extraire le wheel (c'est un ZIP, renommer temporairement)
    Write-Host "Extraction du wheel..." -ForegroundColor Yellow
    $zipFile = $wheelFile -replace '\.whl$', '.zip'
    Copy-Item -Path $wheelFile -Destination $zipFile -Force
    Expand-Archive -Path $zipFile -DestinationPath $tempDir -Force
    Remove-Item -Path $zipFile -Force -ErrorAction SilentlyContinue
    
    # Copier bcrypt dans la structure du layer
    if (Test-Path "$tempDir/bcrypt") {
        Copy-Item -Path "$tempDir/bcrypt" -Destination "$LAYER_DIR/python/bcrypt" -Recurse -Force
        Write-Host "✅ bcrypt copié dans layer" -ForegroundColor Green
        
        # Vérifier que _bcrypt existe et créer un lien si nécessaire
        $bcryptDir = "$LAYER_DIR/python/bcrypt"
        if (Test-Path "$bcryptDir/_bcrypt.so") {
            Write-Host "✅ Module _bcrypt.so trouvé" -ForegroundColor Green
        } else {
            Write-Host "⚠️  _bcrypt.so non trouvé, recherche..." -ForegroundColor Yellow
            $bcryptFiles = Get-ChildItem -Path $bcryptDir -Filter "*_bcrypt*"
            foreach ($file in $bcryptFiles) {
                Write-Host "   Trouvé: $($file.Name)" -ForegroundColor Gray
                # Si c'est _bcrypt.abi3.so, créer un lien vers _bcrypt.so
                if ($file.Name -like "*_bcrypt*.so" -and $file.Name -ne "_bcrypt.so") {
                    Write-Host "   Création d'un lien _bcrypt.so vers $($file.Name)..." -ForegroundColor Yellow
                    # Sur Windows, copier le fichier (pas de lien symbolique)
                    Copy-Item -Path $file.FullName -Destination "$bcryptDir/_bcrypt.so" -Force
                    Write-Host "   ✅ Lien créé" -ForegroundColor Green
                }
            }
        }
        
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
            Write-Host "Attachement à la fonction Lambda..." -ForegroundColor Yellow
            aws lambda update-function-configuration `
                --function-name mapevent-backend `
                --layers $layerArn `
                --region $REGION | Out-Null
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "✅ Layer attachée avec succès!" -ForegroundColor Green
            } else {
                Write-Host "⚠️  Erreur lors de l'attachement, faites-le manuellement:" -ForegroundColor Yellow
                Write-Host "   aws lambda update-function-configuration --function-name mapevent-backend --layers $layerArn --region $REGION" -ForegroundColor Gray
            }
        } else {
            Write-Host "❌ Erreur création layer: $layerArn" -ForegroundColor Red
        }
        
    } else {
        Write-Host "❌ Structure bcrypt non trouvée dans le wheel" -ForegroundColor Red
    }
    
} catch {
    Write-Host "❌ Erreur: $_" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
} finally {
    # Nettoyer
    Remove-Item -Path $LAYER_DIR -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item -Path $wheelFile -Force -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "=== FIN ===" -ForegroundColor Cyan
