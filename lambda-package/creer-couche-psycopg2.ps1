# Script pour créer une couche Lambda avec psycopg2-binary
# Utilise Docker si disponible, sinon WSL, sinon erreur

$LAYER_NAME = "psycopg2-py312-mapevent"
$LAYER_DIR = "psycopg2-layer-temp"
$ZIP_FILE = "psycopg2-layer.zip"

Write-Host "`n=== Création couche Lambda psycopg2 ===" -ForegroundColor Cyan

# Nettoyer
Remove-Item -Path $LAYER_DIR -Recurse -ErrorAction SilentlyContinue
Remove-Item -Path $ZIP_FILE -ErrorAction SilentlyContinue

# Créer la structure
New-Item -ItemType Directory -Path "$LAYER_DIR\python\lib\python3.12\site-packages" -Force | Out-Null

Write-Host "`n1. Installation de psycopg2-binary..." -ForegroundColor Yellow

# Essayer Docker d'abord
$useDocker = $false
try {
    docker ps 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        $useDocker = $true
        Write-Host "   Utilisation de Docker..." -ForegroundColor Gray
        
        $workspacePath = (Get-Location).Path
        $dockerCmd = "docker run --rm -v `"${workspacePath}:C:/workspace`" -w C:/workspace/$LAYER_DIR python:3.12-slim pip install --no-cache-dir psycopg2-binary==2.9.9 -t python/lib/python3.12/site-packages"
        
        Invoke-Expression $dockerCmd 2>&1 | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ psycopg2-binary installé avec Docker" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️  Docker a échoué" -ForegroundColor Yellow
            $useDocker = $false
        }
    }
} catch {
    Write-Host "   ⚠️  Docker non disponible" -ForegroundColor Yellow
}

# Essayer WSL si Docker n'a pas fonctionné
if (-not $useDocker) {
    try {
        wsl --list | Out-Null
        Write-Host "   Utilisation de WSL..." -ForegroundColor Gray
        
        $wslPath = (Get-Location).Path -replace '\\', '/' -replace '^([A-Z]):', '/mnt/$1' -replace '([A-Z])', {$_.Value.ToLower()}
        $wslCmd = "wsl bash -c `"cd $wslPath/$LAYER_DIR && pip install --no-cache-dir psycopg2-binary==2.9.9 -t python/lib/python3.12/site-packages`""
        
        Invoke-Expression $wslCmd 2>&1 | Out-Null
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ psycopg2-binary installé avec WSL" -ForegroundColor Green
        } else {
            Write-Host "   ❌ WSL a échoué" -ForegroundColor Red
            Write-Host "`n❌ ERREUR: Impossible d'installer psycopg2-binary" -ForegroundColor Red
            Write-Host "   Solutions:" -ForegroundColor Yellow
            Write-Host "   1. Démarrer Docker Desktop et réessayer" -ForegroundColor White
            Write-Host "   2. Utiliser WSL et installer Python/pip dedans" -ForegroundColor White
            Write-Host "   3. Utiliser une couche Lambda publique (voir AJOUTER_COUCHE_PSYCOPG2.md)" -ForegroundColor White
            exit 1
        }
    } catch {
        Write-Host "   ❌ WSL non disponible" -ForegroundColor Red
        Write-Host "`n❌ ERREUR: Docker et WSL ne sont pas disponibles" -ForegroundColor Red
        Write-Host "   Solutions:" -ForegroundColor Yellow
        Write-Host "   1. Démarrer Docker Desktop" -ForegroundColor White
        Write-Host "   2. Installer WSL" -ForegroundColor White
        Write-Host "   3. Utiliser une couche Lambda publique (voir AJOUTER_COUCHE_PSYCOPG2.md)" -ForegroundColor White
        exit 1
    }
}

Write-Host "`n2. Création du ZIP..." -ForegroundColor Yellow
Set-Location $LAYER_DIR
Compress-Archive -Path python -DestinationPath "..\$ZIP_FILE" -Force
Set-Location ..

$SIZE = (Get-Item $ZIP_FILE).Length / 1MB
Write-Host "   ✅ ZIP créé: $ZIP_FILE ($([math]::Round($SIZE, 2)) MB)" -ForegroundColor Green

Write-Host "`n3. Publication de la couche Lambda..." -ForegroundColor Yellow
$layerArn = aws lambda publish-layer-version `
    --layer-name $LAYER_NAME `
    --zip-file "fileb://$ZIP_FILE" `
    --compatible-runtimes python3.12 `
    --region eu-west-1 `
    --output text `
    --query 'LayerVersionArn' 2>&1

if ($LASTEXITCODE -eq 0) {
    Write-Host "   ✅ Couche publiée: $layerArn" -ForegroundColor Green
    
    Write-Host "`n4. Ajout de la couche à la fonction Lambda..." -ForegroundColor Yellow
    aws lambda update-function-configuration `
        --function-name mapevent-backend `
        --layers $layerArn `
        --region eu-west-1 2>&1 | Out-Null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   ✅ Couche ajoutée à mapevent-backend" -ForegroundColor Green
        Write-Host "`n✅ SUCCÈS! La couche psycopg2 est maintenant configurée." -ForegroundColor Green
        Write-Host "`nProchaines étapes:" -ForegroundColor Cyan
        Write-Host "1. Retirer psycopg2-binary de requirements.txt (optionnel)" -ForegroundColor White
        Write-Host "2. Redéployer le code: .\deploy-lambda.ps1" -ForegroundColor White
        Write-Host "3. Tester la connexion" -ForegroundColor White
    } else {
        Write-Host "   ⚠️  Erreur lors de l'ajout de la couche" -ForegroundColor Yellow
        Write-Host "   ARN de la couche: $layerArn" -ForegroundColor Gray
        Write-Host "   Ajoutez-la manuellement dans AWS Console" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ❌ Erreur lors de la publication de la couche" -ForegroundColor Red
    Write-Host "   Sortie: $layerArn" -ForegroundColor Gray
}

# Nettoyer
Remove-Item -Path $LAYER_DIR -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "`n=== TERMINÉ ===" -ForegroundColor Cyan





