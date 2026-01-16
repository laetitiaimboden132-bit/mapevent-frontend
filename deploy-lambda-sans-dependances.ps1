# Redéploiement de Lambda SANS les dépendances (elles sont dans la Layer)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "DEPLOIEMENT LAMBDA SANS DEPENDANCES (Layer contient tout)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Variables
$FUNCTION_NAME = "mapevent-backend"
$REGION = "eu-west-1"
$ZIP_FILE = "lambda-deploy-leger.zip"

# Aller dans le dossier lambda-package
Set-Location "lambda-package"

# Nettoyer
Write-Host "1. Nettoyage..." -ForegroundColor Yellow
Remove-Item -Path $ZIP_FILE -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Recurse -Include __pycache__,*.pyc | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# Vérifier que les fichiers existent
Write-Host "2. Verification des fichiers..." -ForegroundColor Yellow
if (-not (Test-Path "backend\main.py")) {
    Write-Host "ERREUR: backend\main.py introuvable!" -ForegroundColor Red
    exit 1
}
if (-not (Test-Path "handler.py")) {
    Write-Host "ERREUR: handler.py introuvable!" -ForegroundColor Red
    exit 1
}

Write-Host "   OK: Fichiers trouves" -ForegroundColor Green

# Créer le ZIP SANS les dépendances (juste le code)
Write-Host "3. Creation du package (SANS dependances)..." -ForegroundColor Yellow

# Créer un dossier temporaire
$TEMP_DIR = "temp-deploy-leger"
Remove-Item -Path $TEMP_DIR -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $TEMP_DIR | Out-Null

# Copier SEULEMENT le code (pas les dépendances)
Write-Host "   Copie de backend..." -ForegroundColor Gray
Copy-Item -Path "backend" -Destination "$TEMP_DIR\backend" -Recurse -Force

Write-Host "   Copie de services..." -ForegroundColor Gray
if (Test-Path "services") {
    Copy-Item -Path "services" -Destination "$TEMP_DIR\services" -Recurse -Force
}

Write-Host "   Copie de handler.py..." -ForegroundColor Gray
Copy-Item -Path "handler.py" -Destination "$TEMP_DIR\handler.py" -Force

Write-Host "   Copie de lambda_function.py..." -ForegroundColor Gray
if (Test-Path "lambda_function.py") {
    Copy-Item -Path "lambda_function.py" -Destination "$TEMP_DIR\lambda_function.py" -Force
}

Write-Host "   Copie de lambda.env..." -ForegroundColor Gray
if (Test-Path "lambda.env") {
    Copy-Item -Path "lambda.env" -Destination "$TEMP_DIR\lambda.env" -Force
}

# Vérifier que l'endpoint existe
Write-Host "   Verification de l'endpoint..." -ForegroundColor Gray
$mainContent = Get-Content "$TEMP_DIR\backend\main.py" -Raw
if ($mainContent -notmatch "delete-all-users-simple") {
    Write-Host "   ATTENTION: L'endpoint delete-all-users-simple n'est pas trouve!" -ForegroundColor Yellow
} else {
    Write-Host "   OK: Endpoint trouve" -ForegroundColor Green
}

# Créer le ZIP
Write-Host "   Compression..." -ForegroundColor Gray
Compress-Archive -Path "$TEMP_DIR\*" -DestinationPath $ZIP_FILE -Force

# Nettoyer le dossier temporaire
Remove-Item -Path $TEMP_DIR -Recurse -Force

# Vérifier la taille (devrait être beaucoup plus petite maintenant)
$SIZE = (Get-Item $ZIP_FILE).Length / 1MB
Write-Host "   Taille du package: $([math]::Round($SIZE, 2))MB (devrait etre < 5MB)" -ForegroundColor Cyan

# Déployer
Write-Host "4. Deploiement sur AWS Lambda..." -ForegroundColor Yellow
aws lambda update-function-code `
    --function-name $FUNCTION_NAME `
    --zip-file "fileb://$ZIP_FILE" `
    --region $REGION

Write-Host ""
Write-Host "Attente de la mise a jour (30 secondes)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "DEPLOIEMENT TERMINE !" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Vous pouvez maintenant tester la suppression des comptes:" -ForegroundColor Cyan
Write-Host "  .\supprimer-tous-comptes.ps1" -ForegroundColor White
Write-Host ""

# Retourner au dossier parent
Set-Location ..

