# Script pour créer le ZIP Lambda avec Docker (garantit les bonnes dépendances Linux)

$ZIP_FILE = "lambda-deploy-with-deps.zip"
$DOCKER_IMAGE = "lambda-builder:latest"

Write-Host "`n=== Création ZIP Lambda avec Docker ===" -ForegroundColor Cyan

# Vérifier si Docker est disponible
try {
    docker --version | Out-Null
    Write-Host "✅ Docker détecté" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker n'est pas disponible. Installation des dépendances Windows..." -ForegroundColor Red
    Write-Host "⚠️  ATTENTION: Les binaires Windows peuvent ne pas fonctionner sur Lambda" -ForegroundColor Yellow
    
    # Fallback vers méthode Windows
    $DEPS_DIR = "lambda-deps"
    Remove-Item -Path $ZIP_FILE -ErrorAction SilentlyContinue
    Remove-Item -Path $DEPS_DIR -Recurse -ErrorAction SilentlyContinue
    New-Item -ItemType Directory -Path $DEPS_DIR -Force | Out-Null
    
    Write-Host "`nInstallation des dépendances..." -ForegroundColor Yellow
    pip install -r backend/requirements.txt -t $DEPS_DIR 2>&1 | Out-Null
    
    Write-Host "Copie des fichiers source..." -ForegroundColor Yellow
    Copy-Item -Path "handler.py" -Destination $DEPS_DIR -Force
    Copy-Item -Path "backend" -Destination $DEPS_DIR -Recurse -Force
    
    Write-Host "Création du ZIP..." -ForegroundColor Yellow
    Set-Location $DEPS_DIR
    Compress-Archive -Path * -DestinationPath "..\$ZIP_FILE" -Force
    Set-Location ..
    Remove-Item -Path $DEPS_DIR -Recurse -Force
    
    $SIZE = (Get-Item $ZIP_FILE).Length / 1MB
    Write-Host "`n✅ ZIP créé: $ZIP_FILE ($([math]::Round($SIZE, 2)) MB)" -ForegroundColor Green
    Write-Host "`n⚠️  ATTENTION: Utilisez Docker pour garantir les bonnes dépendances Linux" -ForegroundColor Yellow
    exit
}

# Construire l'image Docker
Write-Host "`n1. Construction de l'image Docker..." -ForegroundColor Yellow
docker build -f Dockerfile.lambda -t $DOCKER_IMAGE . 2>&1 | Write-Host

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erreur lors de la construction de l'image Docker" -ForegroundColor Red
    exit 1
}

# Créer un conteneur et extraire le ZIP
Write-Host "`n2. Création du conteneur et extraction du ZIP..." -ForegroundColor Yellow
$CONTAINER_ID = docker create $DOCKER_IMAGE 2>&1 | Select-Object -Last 1

if (-not $CONTAINER_ID) {
    Write-Host "❌ Erreur lors de la création du conteneur" -ForegroundColor Red
    exit 1
}

# Copier le ZIP depuis le conteneur
docker cp "$CONTAINER_ID`:/tmp/lambda-deploy.zip" $ZIP_FILE 2>&1 | Out-Null

# Nettoyer
docker rm $CONTAINER_ID | Out-Null

if (Test-Path $ZIP_FILE) {
    $SIZE = (Get-Item $ZIP_FILE).Length / 1MB
    Write-Host "`n✅ ZIP créé avec Docker: $ZIP_FILE ($([math]::Round($SIZE, 2)) MB)" -ForegroundColor Green
} else {
    Write-Host "`n❌ Le fichier ZIP n'a pas été créé" -ForegroundColor Red
    exit 1
}





