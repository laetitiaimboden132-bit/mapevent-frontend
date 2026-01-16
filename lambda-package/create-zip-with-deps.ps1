# Script pour creer le ZIP Lambda avec toutes les dependances

$ZIP_FILE = "lambda-deploy-with-deps.zip"
$DEPS_DIR = "lambda-deps"

Write-Host "`n=== Creation ZIP Lambda avec dependances ===" -ForegroundColor Cyan

# Nettoyer
Remove-Item -Path $ZIP_FILE -ErrorAction SilentlyContinue
Remove-Item -Path $DEPS_DIR -Recurse -ErrorAction SilentlyContinue

# Creer le dossier pour les dependances
New-Item -ItemType Directory -Path $DEPS_DIR -Force | Out-Null

Write-Host "`n1. Installation des dependances Python..." -ForegroundColor Yellow
pip install -r backend/requirements.txt -t $DEPS_DIR --platform manylinux2014_x86_64 --only-binary=:all: --python-version 3.12 --no-deps 2>&1 | Out-Null
pip install -r backend/requirements.txt -t $DEPS_DIR --no-deps 2>&1 | Out-Null

Write-Host "2. Copie des fichiers source..." -ForegroundColor Yellow
Copy-Item -Path "lambda_function.py" -Destination $DEPS_DIR -Force
Copy-Item -Path "handler.py" -Destination $DEPS_DIR -Force
Copy-Item -Path "backend" -Destination $DEPS_DIR -Recurse -Force

Write-Host "3. Creation du ZIP..." -ForegroundColor Yellow
Set-Location $DEPS_DIR
Compress-Archive -Path * -DestinationPath "..\$ZIP_FILE" -Force
Set-Location ..

Write-Host "4. Nettoyage..." -ForegroundColor Yellow
Remove-Item -Path $DEPS_DIR -Recurse -Force

$SIZE = (Get-Item $ZIP_FILE).Length / 1MB
Write-Host "`n✅ ZIP cree: $ZIP_FILE ($([math]::Round($SIZE, 2)) MB)" -ForegroundColor Green
Write-Host "`n⚠️  ATTENTION: Le ZIP peut etre volumineux (>50MB)" -ForegroundColor Yellow
Write-Host "   Lambda limite a 250MB (deploy) ou 50MB (direct upload)" -ForegroundColor Yellow
Write-Host "   Si >50MB, utilisez S3 pour uploader le ZIP" -ForegroundColor Yellow






