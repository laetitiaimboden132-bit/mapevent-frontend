# Script de déploiement Lambda pour MapEventAI Backend (PowerShell)

$ErrorActionPreference = "Stop"

Write-Host "🚀 Déploiement Lambda MapEventAI Backend..." -ForegroundColor Cyan

# Variables
$FUNCTION_NAME = "mapevent-backend"
$REGION = "eu-west-1"
$ZIP_FILE = "lambda-deploy.zip"

# Nettoyer les anciens fichiers
Write-Host "🧹 Nettoyage..." -ForegroundColor Yellow
Remove-Item -Path $ZIP_FILE -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Recurse -Include __pycache__,*.pyc | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# Installer les dépendances dans un dossier local
Write-Host "📦 Installation des dépendances..." -ForegroundColor Yellow
pip install -r backend/requirements.txt -t . --upgrade --quiet

# Créer le fichier ZIP
Write-Host "📦 Création du package..." -ForegroundColor Yellow
Compress-Archive -Path * -DestinationPath $ZIP_FILE -Force -Exclude "*.git*","*.pyc","__pycache__","*.zip","deploy.*","test_*.py","*.md"

# Vérifier la taille du package
$SIZE = (Get-Item $ZIP_FILE).Length / 1MB
if ($SIZE -gt 50) {
    Write-Host "⚠️  Attention: Le package fait $([math]::Round($SIZE, 2))MB (limite: 50MB)" -ForegroundColor Yellow
}

# Déployer sur Lambda
Write-Host "☁️  Déploiement sur AWS Lambda..." -ForegroundColor Yellow
aws lambda update-function-code `
    --function-name $FUNCTION_NAME `
    --zip-file "fileb://$ZIP_FILE" `
    --region $REGION

# Attendre que le déploiement soit terminé
Write-Host "⏳ Attente de la mise à jour..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "✅ Déploiement terminé avec succès!" -ForegroundColor Green
Write-Host "📊 Informations de la fonction:" -ForegroundColor Cyan
aws lambda get-function `
    --function-name $FUNCTION_NAME `
    --region $REGION `
    --query 'Configuration.[FunctionName,Runtime,LastModified,CodeSize]' `
    --output table





