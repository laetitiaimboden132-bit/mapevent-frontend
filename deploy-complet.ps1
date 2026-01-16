# Déploiement complet avec vérification

$ErrorActionPreference = "Stop"

Write-Host "Deploiement complet du backend..." -ForegroundColor Cyan

# Variables
$FUNCTION_NAME = "mapevent-backend"
$REGION = "eu-west-1"
$ZIP_FILE = "lambda-deploy-complet.zip"

# Aller dans le dossier lambda-package
Set-Location "lambda-package"

# Nettoyer
Write-Host "Nettoyage..." -ForegroundColor Yellow
Remove-Item -Path $ZIP_FILE -ErrorAction SilentlyContinue
Get-ChildItem -Path . -Recurse -Include __pycache__,*.pyc | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue

# Vérifier que les fichiers existent
Write-Host "Verification des fichiers..." -ForegroundColor Yellow
if (-not (Test-Path "backend\main.py")) {
    Write-Host "ERREUR: backend\main.py introuvable!" -ForegroundColor Red
    exit 1
}
if (-not (Test-Path "handler.py")) {
    Write-Host "ERREUR: handler.py introuvable!" -ForegroundColor Red
    exit 1
}

Write-Host "  OK: Fichiers trouves" -ForegroundColor Green

# Créer le ZIP avec TOUS les fichiers nécessaires
Write-Host "Creation du package..." -ForegroundColor Yellow

# Créer un dossier temporaire
$TEMP_DIR = "temp-deploy-complet"
Remove-Item -Path $TEMP_DIR -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Path $TEMP_DIR | Out-Null

# Installer les dépendances Python (Lambda utilise Linux, mais pip trouvera automatiquement les bons binaires)
Write-Host "  Installation des dependances Python..." -ForegroundColor Gray
if (Test-Path "backend\requirements.txt") {
    $ErrorActionPreferenceBackup = $ErrorActionPreference
    $ErrorActionPreference = "Continue"
    try {
        # Forcer l'installation pour Linux (Lambda utilise Linux, pas Windows)
        # Utiliser --platform pour forcer Linux manylinux
        $env:PIP_ONLY_BINARY = "all"
        & pip install -r backend\requirements.txt -t $TEMP_DIR --platform manylinux2014_x86_64 --implementation cp --python-version 3.12 --only-binary=:all: --quiet --disable-pip-version-check 2>&1 | Out-Null
        # Si ça ne marche pas (certains packages n'ont pas de wheels), installer normalement
        if ($LASTEXITCODE -ne 0) {
            Write-Host "      Installation normale (certains packages sans wheels Linux)..." -ForegroundColor Gray
            Remove-Item Env:\PIP_ONLY_BINARY -ErrorAction SilentlyContinue
            & pip install -r backend\requirements.txt -t $TEMP_DIR --quiet --disable-pip-version-check 2>&1 | Out-Null
        } else {
            Remove-Item Env:\PIP_ONLY_BINARY -ErrorAction SilentlyContinue
        }
        # Vérifier que les packages critiques sont installés
        $criticalPackages = @("flask", "bcrypt", "werkzeug", "psycopg2")
        $missingPackages = @()
        foreach ($pkg in $criticalPackages) {
            $found = Get-ChildItem -Path $TEMP_DIR -Filter "$pkg*" -Directory -ErrorAction SilentlyContinue | Where-Object { $_.Name -like "$pkg*" }
            if (-not $found) {
                $missingPackages += $pkg
            }
        }
        if ($missingPackages.Count -eq 0) {
            Write-Host "    OK: Toutes les dependances critiques installees" -ForegroundColor Green
        } else {
            Write-Host "    ATTENTION: Packages manquants: $($missingPackages -join ', ')" -ForegroundColor Yellow
            foreach ($pkg in $missingPackages) {
                Write-Host "      Installation de $pkg..." -ForegroundColor Gray
                & pip install $pkg -t $TEMP_DIR --quiet --disable-pip-version-check 2>&1 | Out-Null
            }
            Write-Host "    OK: Packages manquants installes" -ForegroundColor Green
        }
    } catch {
        Write-Host "    ATTENTION: Erreur lors de l'installation: $_" -ForegroundColor Yellow
        Write-Host "    Continuons quand meme..." -ForegroundColor Gray
    } finally {
        $ErrorActionPreference = $ErrorActionPreferenceBackup
    }
} else {
    Write-Host "    ATTENTION: requirements.txt introuvable!" -ForegroundColor Yellow
}

# Copier TOUS les fichiers nécessaires
Write-Host "  Copie de backend..." -ForegroundColor Gray
Copy-Item -Path "backend" -Destination "$TEMP_DIR\backend" -Recurse -Force

Write-Host "  Copie de services..." -ForegroundColor Gray
if (Test-Path "services") {
    Copy-Item -Path "services" -Destination "$TEMP_DIR\services" -Recurse -Force
}

Write-Host "  Copie de handler.py..." -ForegroundColor Gray
Copy-Item -Path "handler.py" -Destination "$TEMP_DIR\handler.py" -Force

Write-Host "  Copie de lambda_function.py..." -ForegroundColor Gray
if (Test-Path "lambda_function.py") {
    Copy-Item -Path "lambda_function.py" -Destination "$TEMP_DIR\lambda_function.py" -Force
}

Write-Host "  Copie de lambda.env..." -ForegroundColor Gray
if (Test-Path "lambda.env") {
    Copy-Item -Path "lambda.env" -Destination "$TEMP_DIR\lambda.env" -Force
}

# Vérifier que le nouveau endpoint est bien dans main.py
Write-Host "  Verification de l'endpoint..." -ForegroundColor Gray
$mainContent = Get-Content "$TEMP_DIR\backend\main.py" -Raw
if ($mainContent -notmatch "delete-all-users-simple") {
    Write-Host "  ATTENTION: L'endpoint delete-all-users-simple n'est pas trouve dans main.py!" -ForegroundColor Yellow
} else {
    Write-Host "  OK: Endpoint trouve" -ForegroundColor Green
}

# Créer le ZIP
Write-Host "  Compression..." -ForegroundColor Gray
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

Write-Host "Attente de la mise a jour (30 secondes)..." -ForegroundColor Yellow
Start-Sleep -Seconds 30

Write-Host "Deploiement termine!" -ForegroundColor Green
Write-Host ""
Write-Host "Vous pouvez maintenant tester avec:" -ForegroundColor Cyan
Write-Host "  .\supprimer-comptes-api.ps1 -Confirm 'OUI'" -ForegroundColor White

# Retourner au dossier parent
Set-Location ..

