# Script pour créer une Lambda Layer avec toutes les dépendances Python (Linux)
# Cette Layer résoudra le problème des binaires Windows vs Linux

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "CREATION DE LAMBDA LAYER AVEC DEPENDANCES PYTHON" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Variables
$LAYER_NAME = "mapevent-python-dependencies"
$REGION = "eu-west-1"
$PYTHON_VERSION = "3.12"
$LAYER_DIR = "lambda-layer-build"

# Aller dans le dossier lambda-package
Set-Location "lambda-package"

# Nettoyer
Write-Host "1. Nettoyage..." -ForegroundColor Yellow
Remove-Item -Path $LAYER_DIR -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "python-layer.zip" -Force -ErrorAction SilentlyContinue

# Créer la structure de la Layer
Write-Host "2. Creation de la structure de la Layer..." -ForegroundColor Yellow
New-Item -ItemType Directory -Path "$LAYER_DIR\python" -Force | Out-Null

# Installer les dépendances pour Linux (manylinux)
Write-Host "3. Installation des dependances Python (Linux manylinux)..." -ForegroundColor Yellow

if (-not (Test-Path "backend\requirements.txt")) {
    Write-Host "ERREUR: backend\requirements.txt introuvable!" -ForegroundColor Red
    exit 1
}

# Installer les dépendances directement dans le dossier python/
# Lambda Layer attend les packages Python dans python/lib/pythonX.Y/site-packages/
$pythonLibPath = "$LAYER_DIR\python\lib\python$($PYTHON_VERSION -replace '\.', '')\site-packages"
New-Item -ItemType Directory -Path $pythonLibPath -Force | Out-Null

# Méthode 1: Installer avec --platform manylinux2014_x86_64 (pour Linux)
Write-Host "   Installation pour Linux (manylinux2014_x86_64)..." -ForegroundColor Gray
$ErrorActionPreferenceBackup = $ErrorActionPreference
$ErrorActionPreference = "Continue"

try {
    # Installer les dépendances pour Linux
    # Utiliser --platform pour forcer Linux, mais sans --only-binary pour permettre les sources si nécessaire
    & pip install -r backend\requirements.txt `
        -t $pythonLibPath `
        --platform manylinux2014_x86_64 `
        --implementation cp `
        --python-version $($PYTHON_VERSION -replace '\.', '') `
        --only-binary=:all: `
        --no-deps `
        --quiet `
        --disable-pip-version-check 2>&1 | Out-Null
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "   Méthode 1 échouée, utilisation méthode 2 (installation normale)..." -ForegroundColor Yellow
        
        # Méthode 2: Installer normalement (pip téléchargera automatiquement les binaires Linux)
        Remove-Item -Path $pythonLibPath -Recurse -Force -ErrorAction SilentlyContinue
        New-Item -ItemType Directory -Path $pythonLibPath -Force | Out-Null
        
        & pip install -r backend\requirements.txt `
            -t $pythonLibPath `
            --quiet `
            --disable-pip-version-check 2>&1 | Out-Null
    }
    
    # Installer les dépendances manquantes
    & pip install -r backend\requirements.txt `
        -t $pythonLibPath `
        --quiet `
        --disable-pip-version-check 2>&1 | Out-Null
    
    Write-Host "   OK: Dependances installees" -ForegroundColor Green
    
    # Vérifier que les packages critiques sont installés
    $criticalPackages = @("flask", "bcrypt", "werkzeug")
    $missingPackages = @()
    foreach ($pkg in $criticalPackages) {
        $found = Get-ChildItem -Path $pythonLibPath -Filter "$pkg*" -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -like "$pkg*" }
        if (-not $found) {
            $missingPackages += $pkg
        }
    }
    
    if ($missingPackages.Count -gt 0) {
        Write-Host "   Installation des packages manquants: $($missingPackages -join ', ')" -ForegroundColor Yellow
        foreach ($pkg in $missingPackages) {
            & pip install $pkg -t $pythonLibPath --quiet --disable-pip-version-check 2>&1 | Out-Null
        }
    }
    
    Write-Host "   OK: Tous les packages critiques sont installes" -ForegroundColor Green
    
} catch {
    Write-Host "   ERREUR lors de l'installation: $_" -ForegroundColor Red
    $ErrorActionPreference = $ErrorActionPreferenceBackup
    exit 1
} finally {
    $ErrorActionPreference = $ErrorActionPreferenceBackup
}

# Nettoyer les fichiers inutiles
Write-Host "4. Nettoyage des fichiers inutiles..." -ForegroundColor Yellow
Get-ChildItem -Path $pythonLibPath -Recurse -Include __pycache__,*.pyc,*.dist-info,*.egg-info | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# Créer le ZIP de la Layer
Write-Host "5. Creation du ZIP de la Layer..." -ForegroundColor Yellow
Compress-Archive -Path "$LAYER_DIR\python" -DestinationPath "python-layer.zip" -Force

# Vérifier la taille
$SIZE = (Get-Item "python-layer.zip").Length / 1MB
Write-Host "   Taille du ZIP: $([math]::Round($SIZE, 2))MB" -ForegroundColor Cyan

if ($SIZE -gt 50) {
    Write-Host "   ATTENTION: La Layer depasse 50MB (taille max non compressee). Optimisation..." -ForegroundColor Yellow
    # Supprimer les packages non essentiels si nécessaire
}

# Publier la Layer
Write-Host "6. Publication de la Layer sur AWS..." -ForegroundColor Yellow

try {
    # Vérifier si la Layer existe déjà
    $existingLayers = aws lambda list-layers --region $REGION --query "Layers[?LayerName=='$LAYER_NAME']" 2>&1 | ConvertFrom-Json
    
    if ($existingLayers -and $existingLayers.Count -gt 0) {
        Write-Host "   Layer existe deja, creation d'une nouvelle version..." -ForegroundColor Gray
        $layerVersion = aws lambda publish-layer-version `
            --layer-name $LAYER_NAME `
            --zip-file "fileb://python-layer.zip" `
            --compatible-runtimes "python$PYTHON_VERSION" `
            --compatible-architectures x86_64 `
            --region $REGION 2>&1 | ConvertFrom-Json
        
        if ($layerVersion.LayerVersionArn) {
            Write-Host ""
            Write-Host "============================================================" -ForegroundColor Green
            Write-Host "SUCCES: Lambda Layer creee !" -ForegroundColor Green
            Write-Host "============================================================" -ForegroundColor Green
            Write-Host ""
            Write-Host "Layer ARN: $($layerVersion.LayerVersionArn)" -ForegroundColor White
            Write-Host "Version: $($layerVersion.Version)" -ForegroundColor White
            Write-Host ""
            
            # Sauvegarder l'ARN pour référence future
            $layerVersion.LayerVersionArn | Out-File -FilePath "lambda-layer-arn.txt" -Encoding UTF8
            Write-Host "ARN sauvegarde dans: lambda-layer-arn.txt" -ForegroundColor Gray
            Write-Host ""
            
            Write-Host "Prochaine etape: Attacher cette Layer a la fonction Lambda" -ForegroundColor Yellow
            Write-Host "  .\attacher-layer-lambda.ps1" -ForegroundColor White
            Write-Host ""
        } else {
            Write-Host "ERREUR: Impossible de creer la Layer" -ForegroundColor Red
            exit 1
        }
    } else {
        Write-Host "   Creation d'une nouvelle Layer..." -ForegroundColor Gray
        $layerVersion = aws lambda publish-layer-version `
            --layer-name $LAYER_NAME `
            --zip-file "fileb://python-layer.zip" `
            --compatible-runtimes "python$PYTHON_VERSION" `
            --compatible-architectures x86_64 `
            --description "Dependances Python pour MapEventAI (Flask, bcrypt, werkzeug, etc.)" `
            --region $REGION 2>&1 | ConvertFrom-Json
        
        if ($layerVersion.LayerVersionArn) {
            Write-Host ""
            Write-Host "============================================================" -ForegroundColor Green
            Write-Host "SUCCES: Lambda Layer creee !" -ForegroundColor Green
            Write-Host "============================================================" -ForegroundColor Green
            Write-Host ""
            Write-Host "Layer ARN: $($layerVersion.LayerVersionArn)" -ForegroundColor White
            Write-Host "Version: $($layerVersion.Version)" -ForegroundColor White
            Write-Host ""
            
            # Sauvegarder l'ARN
            $layerVersion.LayerVersionArn | Out-File -FilePath "lambda-layer-arn.txt" -Encoding UTF8
            Write-Host "ARN sauvegarde dans: lambda-layer-arn.txt" -ForegroundColor Gray
            Write-Host ""
            
            Write-Host "Prochaine etape: Attacher cette Layer a la fonction Lambda" -ForegroundColor Yellow
            Write-Host "  .\attacher-layer-lambda.ps1" -ForegroundColor White
            Write-Host ""
        } else {
            Write-Host "ERREUR: Impossible de creer la Layer" -ForegroundColor Red
            exit 1
        }
    }
} catch {
    Write-Host "ERREUR lors de la creation de la Layer: $_" -ForegroundColor Red
    exit 1
}

# Nettoyer le dossier temporaire (garder le ZIP pour référence)
# Remove-Item -Path $LAYER_DIR -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "Termine !" -ForegroundColor Green
Write-Host ""

# Retourner au dossier parent
Set-Location ..

