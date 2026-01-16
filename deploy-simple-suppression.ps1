# Script simple pour déployer le nouveau endpoint de suppression

$ErrorActionPreference = "Stop"

Write-Host "Deploiement du nouveau endpoint de suppression..." -ForegroundColor Cyan

# Variables
$FUNCTION_NAME = "mapevent-backend"
$REGION = "eu-west-1"
$ZIP_FILE = "lambda-deploy.zip"

# Aller dans le dossier lambda-package
Set-Location "lambda-package"

# Nettoyer
Write-Host "Nettoyage..." -ForegroundColor Yellow
Remove-Item -Path $ZIP_FILE -ErrorAction SilentlyContinue

# Créer le ZIP avec seulement le code (sans dépendances car elles sont dans les Layers)
Write-Host "Creation du package..." -ForegroundColor Yellow

# Créer un dossier temporaire
$TEMP_DIR = "temp-deploy"
Remove-Item -Path $TEMP_DIR -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $TEMP_DIR | Out-Null

# Copier les fichiers nécessaires
Copy-Item -Path "backend" -Destination "$TEMP_DIR\backend" -Recurse -Force
Copy-Item -Path "services" -Destination "$TEMP_DIR\services" -Recurse -Force -ErrorAction SilentlyContinue
Copy-Item -Path "handler.py" -Destination "$TEMP_DIR\handler.py" -Force -ErrorAction SilentlyContinue
Copy-Item -Path "lambda.env" -Destination "$TEMP_DIR\lambda.env" -Force -ErrorAction SilentlyContinue

# Créer le ZIP
Compress-Archive -Path "$TEMP_DIR\*" -DestinationPath $ZIP_FILE -Force

# Nettoyer le dossier temporaire
Remove-Item -Path $TEMP_DIR -Recurse -Force

# Vérifier la taille
$SIZE = (Get-Item $ZIP_FILE).Length / 1MB
Write-Host "Taille du package: $([math]::Round($SIZE, 2))MB" -ForegroundColor Cyan

# Déployer
Write-Host "Deploiement sur AWS Lambda..." -ForegroundColor Yellow
aws lambda update-function-code `
    --function-name $FUNCTION_NAME `
    --zip-file "fileb://$ZIP_FILE" `
    --region $REGION

Write-Host "Attente de la mise a jour..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host "Deploiement termine avec succes!" -ForegroundColor Green

# Retourner au dossier parent
Set-Location ..


