# Script de deploiement Lambda avec support S3

$ErrorActionPreference = "Stop"

Write-Host "Deploiement Lambda MapEventAI Backend..." -ForegroundColor Cyan

# Variables
$FUNCTION_NAME = "mapevent-backend"
$REGION = "eu-west-1"
$ZIP_FILE = "lambda-deploy.zip"

# Nettoyer les anciens fichiers
Write-Host "Nettoyage..." -ForegroundColor Yellow
Remove-Item -Path $ZIP_FILE -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Recurse -Include __pycache__,*.pyc | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# Installer les dependances
Write-Host "Installation des dependances..." -ForegroundColor Yellow
pip install -r backend/requirements.txt -t . --upgrade --quiet

# Creer le fichier ZIP (methode compatible)
Write-Host "Creation du package ZIP..." -ForegroundColor Yellow
$filesToExclude = @("*.git*", "*.pyc", "__pycache__", "*.zip", "deploy.*", "test_*.py", "*.md", ".git")
Get-ChildItem -Path . -File | Where-Object { $filesToExclude -notcontains $_.Extension } | Compress-Archive -DestinationPath $ZIP_FILE -Force
Get-ChildItem -Path . -Directory | Where-Object { $filesToExclude -notcontains $_.Name } | Compress-Archive -DestinationPath $ZIP_FILE -Update -Force

# Verifier la taille
$SIZE = (Get-Item $ZIP_FILE).Length / 1MB
Write-Host "Taille du package: $([math]::Round($SIZE, 2))MB" -ForegroundColor Cyan

# Deployer
Write-Host "Deploiement sur AWS Lambda..." -ForegroundColor Yellow
aws lambda update-function-code `
    --function-name $FUNCTION_NAME `
    --zip-file "fileb://$ZIP_FILE" `
    --region $REGION

Write-Host "Attente de la finalisation..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host "Deploiement termine avec succes!" -ForegroundColor Green






