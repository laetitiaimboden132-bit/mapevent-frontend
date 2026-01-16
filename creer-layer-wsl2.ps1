# Script pour créer Lambda Layer avec WSL2 (Linux) - Plus simple que Docker !

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "CREATION LAMBDA LAYER AVEC WSL2 (Linux)" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Variables
$LAYER_NAME = "mapevent-python-dependencies"
$REGION = "eu-west-1"
$PYTHON_VERSION = "3.12"
$WSL_DISTRO = "Ubuntu"  # Utiliser Ubuntu qui est maintenant installé

# Aller dans le dossier lambda-package
Set-Location "lambda-package"

# Vérifier WSL2
Write-Host "1. Verification de WSL2..." -ForegroundColor Yellow
try {
    $wslVersion = wsl --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "WSL2 n'est pas disponible"
    }
    Write-Host "   OK: WSL2 est disponible" -ForegroundColor Green
} catch {
    Write-Host "ERREUR: WSL2 n'est pas disponible!" -ForegroundColor Red
    Write-Host "   Installez WSL2: wsl --install" -ForegroundColor Yellow
    exit 1
}

# Vérifier les distributions WSL2 disponibles
Write-Host "2. Verification des distributions WSL2 disponibles..." -ForegroundColor Yellow
try {
    $distrosList = wsl --list --verbose 2>&1 | Out-String
    Write-Host "   Distributions disponibles:" -ForegroundColor Gray
    
    # Chercher une distribution Ubuntu ou Debian
    $availableDistros = @()
    $distrosList -split "`n" | ForEach-Object {
        $line = $_.Trim()
        if ($line -match "^\s*(\S+)" -and $line -notmatch "NAME" -and $line -notmatch "^\s*$") {
            $distroName = $matches[1]
            if ($distroName -like "*ubuntu*" -or $distroName -like "*debian*" -or $distroName -like "*docker*") {
                $availableDistros += $distroName
                Write-Host "     - $distroName" -ForegroundColor Gray
            }
        }
    }
    
    if ($availableDistros.Count -eq 0) {
        Write-Host "   Aucune distribution Ubuntu/Debian trouvee, installation d'Ubuntu..." -ForegroundColor Yellow
        Write-Host "   Execution: wsl --install -d Ubuntu" -ForegroundColor Gray
        wsl --install -d Ubuntu 2>&1 | Out-Null
        Start-Sleep -Seconds 10
        $WSL_DISTRO = "Ubuntu"
    } else {
        $WSL_DISTRO = $availableDistros[0]
    }
    
    Write-Host "   Utilisation de la distribution: $WSL_DISTRO" -ForegroundColor Green
} catch {
    Write-Host "ERREUR: Impossible de lister les distributions WSL2" -ForegroundColor Red
    Write-Host "   Installation d'Ubuntu..." -ForegroundColor Yellow
    wsl --install -d Ubuntu 2>&1 | Out-Null
    $WSL_DISTRO = "Ubuntu"
}

# Nettoyer
Write-Host "3. Nettoyage..." -ForegroundColor Yellow
Remove-Item -Path "python-layer.zip" -Force -ErrorAction SilentlyContinue
Remove-Item -Path "lambda-layer-wsl2.zip" -Force -ErrorAction SilentlyContinue

# Créer un script bash pour installer les dépendances dans WSL2
Write-Host "4. Creation du script d'installation WSL2..." -ForegroundColor Yellow

$bashScript = @"
#!/bin/bash
set -e

# Variables
LAYER_DIR="/tmp/lambda-layer-build"
PYTHON_VER="$PYTHON_VERSION"
PYTHON_LIB_PATH="`$LAYER_DIR/python/lib/python`$PYTHON_VER/site-packages"

echo "Creation de la structure Lambda Layer..."
mkdir -p `$PYTHON_LIB_PATH

echo "Installation de Python `$PYTHON_VER si necessaire..."
if ! command -v python3.12 &> /dev/null; then
    echo "Installation de Python 3.12..."
    sudo apt-get update -qq
    sudo apt-get install -y python3.12 python3.12-venv python3-pip -qq
fi

echo "Installation des dependances Python (Linux)..."
python3.12 -m pip install --upgrade pip -q
python3.12 -m pip install -r /mnt/c/MapEventAI_NEW/frontend/lambda-package/backend/requirements.txt -t `$PYTHON_LIB_PATH --quiet --no-cache-dir

echo "Nettoyage des fichiers inutiles..."
find `$PYTHON_LIB_PATH -type d -name __pycache__ -exec rm -r {} + 2>/dev/null || true
find `$PYTHON_LIB_PATH -name "*.pyc" -delete
find `$PYTHON_LIB_PATH -name "*.pyo" -delete
find `$PYTHON_LIB_PATH -name "*.dist-info" -type d -exec rm -r {} + 2>/dev/null || true

echo "Creation du ZIP de la Layer..."
cd `$LAYER_DIR
zip -r /mnt/c/MapEventAI_NEW/frontend/lambda-package/lambda-layer-wsl2.zip python/ -q

echo "Nettoyage..."
rm -rf `$LAYER_DIR

echo "SUCCES: Lambda Layer creee dans lambda-layer-wsl2.zip"
"@

$bashScript | Out-File -FilePath "build-layer-wsl2.sh" -Encoding UTF8 -NoNewline

Write-Host "   OK: Script bash cree" -ForegroundColor Green

# Copier requirements.txt dans un emplacement accessible depuis WSL2
# (WSL2 peut accéder à C: via /mnt/c/)
Write-Host "5. Verification de requirements.txt..." -ForegroundColor Yellow
if (-not (Test-Path "backend\requirements.txt")) {
    Write-Host "ERREUR: backend\requirements.txt introuvable!" -ForegroundColor Red
    exit 1
}
Write-Host "   OK: requirements.txt trouve" -ForegroundColor Green

# Exécuter le script dans WSL2
Write-Host "6. Execution du script dans WSL2..." -ForegroundColor Yellow
Write-Host "   (Cela peut prendre plusieurs minutes la premiere fois)" -ForegroundColor Gray
Write-Host ""

try {
    # Changer les retours à la ligne pour Unix (LF)
    $bashScriptUnix = $bashScript -replace "`r`n", "`n"
    $bashScriptUnix | Out-File -FilePath "build-layer-wsl2.sh" -Encoding ASCII -NoNewline
    
    # Exécuter dans WSL2
    # Utiliser le chemin Windows directement (WSL2 peut accéder à /mnt/c/)
    $currentPath = (Get-Location).Path
    $wslPath = $currentPath.Replace("\", "/").Replace("C:", "/mnt/c")
    
    # Commande WSL2 pour exécuter le script
    $wslCommand = "cd '$wslPath' && bash build-layer-wsl2.sh"
    
    wsl -d $WSL_DISTRO bash -c $wslCommand 2>&1 | ForEach-Object {
        Write-Host $_ -ForegroundColor Gray
    }
    
    if ($LASTEXITCODE -ne 0) {
        throw "Erreur lors de l'execution dans WSL2 (code: $LASTEXITCODE)"
    }
    
    Write-Host ""
    Write-Host "   OK: Script execute avec succes" -ForegroundColor Green
} catch {
    Write-Host ""
    Write-Host "ERREUR lors de l'execution dans WSL2: $_" -ForegroundColor Red
    Remove-Item "build-layer-wsl2.sh" -Force -ErrorAction SilentlyContinue
    exit 1
}

# Vérifier que le ZIP a été créé
Write-Host "7. Verification du ZIP..." -ForegroundColor Yellow
if (-not (Test-Path "lambda-layer-wsl2.zip")) {
    Write-Host "ERREUR: lambda-layer-wsl2.zip non cree!" -ForegroundColor Red
    Remove-Item "build-layer-wsl2.sh" -Force -ErrorAction SilentlyContinue
    exit 1
}

$SIZE = (Get-Item "lambda-layer-wsl2.zip").Length / 1MB
Write-Host "   Taille du ZIP: $([math]::Round($SIZE, 2))MB" -ForegroundColor Cyan

# Renommer le ZIP pour cohérence
Rename-Item -Path "lambda-layer-wsl2.zip" -NewName "python-layer.zip" -Force
Write-Host "   OK: ZIP cree avec succes" -ForegroundColor Green

# Nettoyer le script bash
Remove-Item "build-layer-wsl2.sh" -Force -ErrorAction SilentlyContinue

# Publier la Layer
Write-Host "8. Publication de la Layer sur AWS..." -ForegroundColor Yellow

try {
    # Vérifier si la Layer existe déjà
    $existingLayers = aws lambda list-layers --region $REGION --query "Layers[?LayerName=='$LAYER_NAME']" 2>&1 | ConvertFrom-Json
    
    if ($existingLayers -and $existingLayers.Count -gt 0) {
        Write-Host "   Layer existe deja, creation d'une nouvelle version..." -ForegroundColor Gray
    } else {
        Write-Host "   Creation d'une nouvelle Layer..." -ForegroundColor Gray
    }
    
    $layerVersion = aws lambda publish-layer-version `
        --layer-name $LAYER_NAME `
        --zip-file "fileb://python-layer.zip" `
        --compatible-runtimes "python$PYTHON_VERSION" `
        --compatible-architectures x86_64 `
        --description "Dependances Python pour MapEventAI (Linux - via WSL2)" `
        --region $REGION 2>&1 | ConvertFrom-Json
    
    if ($layerVersion.LayerVersionArn) {
        Write-Host ""
        Write-Host "============================================================" -ForegroundColor Green
        Write-Host "SUCCES: Lambda Layer creee avec WSL2 !" -ForegroundColor Green
        Write-Host "============================================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "Layer ARN: $($layerVersion.LayerVersionArn)" -ForegroundColor White
        Write-Host "Version: $($layerVersion.Version)" -ForegroundColor White
        Write-Host ""
        
        # Sauvegarder l'ARN
        $layerVersion.LayerVersionArn | Out-File -FilePath "lambda-layer-arn-wsl2.txt" -Encoding UTF8
        Write-Host "ARN sauvegarde dans: lambda-layer-arn-wsl2.txt" -ForegroundColor Gray
        Write-Host ""
        
        Write-Host "Prochaine etape: Attacher cette nouvelle Layer a Lambda" -ForegroundColor Yellow
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

