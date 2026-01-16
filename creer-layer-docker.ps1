# Script pour créer Lambda Layer avec Docker (garantit les binaires Linux)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "CREATION LAMBDA LAYER AVEC DOCKER (Linux)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier que Docker est installé
Write-Host "1. Verification de Docker..." -ForegroundColor Yellow
try {
    $dockerVersion = docker --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Docker n'est pas installe"
    }
    Write-Host "   OK: $dockerVersion" -ForegroundColor Green
} catch {
    Write-Host "ERREUR: Docker n'est pas installe ou n'est pas demarre!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Installez Docker Desktop:" -ForegroundColor Yellow
    Write-Host "  https://www.docker.com/products/docker-desktop" -ForegroundColor White
    Write-Host ""
    exit 1
}

# Variables
$LAYER_NAME = "mapevent-python-dependencies"
$REGION = "eu-west-1"

# Aller dans le dossier lambda-package
Set-Location "lambda-package"

# Vérifier que Dockerfile existe
if (-not (Test-Path "Dockerfile.lambda-layer")) {
    Write-Host "ERREUR: Dockerfile.lambda-layer introuvable!" -ForegroundColor Red
    exit 1
}

# Nettoyer
Write-Host "2. Nettoyage..." -ForegroundColor Yellow
Remove-Item -Path "python-layer.zip" -Force -ErrorAction SilentlyContinue

# Construire l'image Docker
Write-Host "3. Construction de l'image Docker..." -ForegroundColor Yellow
Write-Host "   (Cela peut prendre plusieurs minutes la premiere fois)" -ForegroundColor Gray

try {
    docker build -f Dockerfile.lambda-layer -t lambda-layer-builder:latest . 2>&1 | Out-Null
    
    if ($LASTEXITCODE -ne 0) {
        throw "Erreur lors de la construction de l'image Docker"
    }
    
    Write-Host "   OK: Image Docker construite" -ForegroundColor Green
} catch {
    Write-Host "ERREUR lors de la construction: $_" -ForegroundColor Red
    exit 1
}

# Exécuter le conteneur pour créer le ZIP
Write-Host "4. Creation du ZIP de la Layer..." -ForegroundColor Yellow

try {
    # Créer un dossier temporaire pour recevoir le ZIP
    $tempDir = "temp-docker-output"
    Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue
    New-Item -ItemType Directory -Path $tempDir | Out-Null
    
    # Exécuter le conteneur et copier le ZIP
    docker run --rm `
        -v "${PWD}\$tempDir:/output" `
        lambda-layer-builder:latest `
        sh -c "cp /layer-build/python-layer.zip /output/" 2>&1 | Out-Null
    
    if ($LASTEXITCODE -ne 0) {
        throw "Erreur lors de l'execution du conteneur Docker"
    }
    
    # Vérifier que le ZIP a été créé
    if (Test-Path "$tempDir\python-layer.zip") {
        Move-Item -Path "$tempDir\python-layer.zip" -Destination "python-layer.zip" -Force
        Remove-Item -Path $tempDir -Recurse -Force
        Write-Host "   OK: ZIP cree" -ForegroundColor Green
    } else {
        throw "Le ZIP n'a pas ete cree dans le conteneur"
    }
} catch {
    Write-Host "ERREUR lors de la creation du ZIP: $_" -ForegroundColor Red
    Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue
    exit 1
}

# Vérifier la taille
$SIZE = (Get-Item "python-layer.zip").Length / 1MB
Write-Host "   Taille du ZIP: $([math]::Round($SIZE, 2))MB" -ForegroundColor Cyan

# Publier la Layer
Write-Host "5. Publication de la Layer sur AWS..." -ForegroundColor Yellow

try {
    $layerVersion = aws lambda publish-layer-version `
        --layer-name $LAYER_NAME `
        --zip-file "fileb://python-layer.zip" `
        --compatible-runtimes "python3.12" `
        --compatible-architectures x86_64 `
        --description "Dependances Python pour MapEventAI (Linux - via Docker)" `
        --region $REGION 2>&1 | ConvertFrom-Json
    
    if ($layerVersion.LayerVersionArn) {
        Write-Host ""
        Write-Host "============================================================" -ForegroundColor Green
        Write-Host "SUCCES: Lambda Layer creee avec Docker !" -ForegroundColor Green
        Write-Host "============================================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Layer ARN: $($layerVersion.LayerVersionArn)" -ForegroundColor White
        Write-Host "Version: $($layerVersion.Version)" -ForegroundColor White
        Write-Host ""
        
        # Sauvegarder l'ARN
        $layerVersion.LayerVersionArn | Out-File -FilePath "lambda-layer-arn-docker.txt" -Encoding UTF8
        
        Write-Host "Prochaine etape: Attacher cette Layer et redeployer Lambda" -ForegroundColor Yellow
        Write-Host "  .\attacher-layer-lambda.ps1" -ForegroundColor White
        Write-Host ""
    } else {
        Write-Host "ERREUR: Impossible de creer la Layer" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "ERREUR lors de la publication: $_" -ForegroundColor Red
    exit 1
}

# Retourner au dossier parent
Set-Location ..

Write-Host "Termine !" -ForegroundColor Green
Write-Host ""

