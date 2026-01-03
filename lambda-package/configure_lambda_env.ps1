# Script de configuration des variables d'environnement Lambda
# Utilise le script Python configure_lambda_env.py pour éviter les problèmes d'échappement PowerShell

Write-Host "Configuration des variables d'environnement Lambda..." -ForegroundColor Cyan
Write-Host ""

# Vérifier si Python est disponible
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    $pythonCmd = Get-Command python3 -ErrorAction SilentlyContinue
}

if (-not $pythonCmd) {
    Write-Host "ERREUR: Python n'est pas installe!" -ForegroundColor Red
    Write-Host "Installez Python et relancez le script." -ForegroundColor Yellow
    exit 1
}

# Vérifier si boto3 est installé
$boto3Check = python -c "import boto3" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installation de boto3..." -ForegroundColor Yellow
    pip install boto3 --quiet
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERREUR: Impossible d'installer boto3!" -ForegroundColor Red
        exit 1
    }
}

# Exécuter le script Python
$scriptPath = Join-Path $PSScriptRoot "configure_lambda_env.py"
if (-not (Test-Path $scriptPath)) {
    Write-Host "ERREUR: Script Python non trouve: $scriptPath" -ForegroundColor Red
    exit 1
}

Write-Host "Execution du script Python..." -ForegroundColor Yellow
python $scriptPath

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERREUR lors de la configuration Lambda" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Configuration terminee!" -ForegroundColor Green
exit 0

Write-Host "Configuration des variables d'environnement Lambda..." -ForegroundColor Cyan
Write-Host ""

# Lire les valeurs depuis un fichier .env ou les demander
$envFile = "lambda.env"
$envVars = @{}

if (Test-Path $envFile) {
    Write-Host "Lecture du fichier $envFile..." -ForegroundColor Yellow
    Get-Content $envFile | ForEach-Object {
        if ($_ -match '^\s*([^#][^=]+)=(.*)$') {
            $key = $matches[1].Trim()
            $value = $matches[2].Trim()
            $envVars[$key] = $value
        }
    }
} else {
    Write-Host "Fichier $envFile non trouve. Creation d'un template..." -ForegroundColor Yellow
    @"
# Configuration Lambda MapEventAI
# Remplissez ces valeurs et relancez le script

# Base de donnees PostgreSQL (RDS)
RDS_HOST=votre-rds-host.region.rds.amazonaws.com
RDS_PORT=5432
RDS_DB=mapevent
RDS_USER=votre_user
RDS_PASSWORD=votre_password

# Redis
REDIS_HOST=votre-redis-host.cache.amazonaws.com
REDIS_PORT=6379

# Google Cloud Vision API (pour moderation images)
GOOGLE_CLOUD_VISION_API_KEY=votre_cle_api_google

# AWS Region (pour Rekognition fallback)
AWS_REGION=eu-west-1

# Stripe
STRIPE_SECRET_KEY=votre_cle_stripe_secrete
STRIPE_PUBLIC_KEY=votre_cle_stripe_publique
STRIPE_WEBHOOK_SECRET=votre_webhook_secret

# Environnement
FLASK_ENV=production
"@ | Out-File -FilePath $envFile -Encoding UTF8
    
    Write-Host "Template cree: $envFile" -ForegroundColor Green
    Write-Host "Remplissez les valeurs et relancez le script." -ForegroundColor Yellow
    exit
}

# Vérifier que toutes les variables essentielles sont présentes
$requiredVars = @('RDS_HOST', 'RDS_USER', 'RDS_PASSWORD', 'REDIS_HOST')
$missingVars = @()

foreach ($var in $requiredVars) {
    if (-not $envVars.ContainsKey($var) -or [string]::IsNullOrWhiteSpace($envVars[$var])) {
        $missingVars += $var
    }
}

if ($missingVars.Count -gt 0) {
    Write-Host "ERREUR: Variables manquantes dans $envFile :" -ForegroundColor Red
    $missingVars | ForEach-Object { Write-Host "  - $_" -ForegroundColor Red }
    exit 1
}

# Construire la chaîne JSON pour les variables d'environnement
# Utiliser ConvertTo-Json pour créer un JSON valide
$envJson = @{}
foreach ($key in $envVars.Keys) {
    $envJson[$key] = $envVars[$key]
}

Write-Host "Mise a jour des variables d'environnement..." -ForegroundColor Yellow
Write-Host "Fonction Lambda: $FUNCTION_NAME" -ForegroundColor Gray
Write-Host "Region: $REGION" -ForegroundColor Gray

# Créer un fichier JSON temporaire dans le répertoire courant
# Utiliser Out-File avec -NoNewline pour éviter les problèmes d'encodage
$cliInputFile = Join-Path (Get-Location) "lambda-env-temp.json"
$cliInputJson = @{
    FunctionName = $FUNCTION_NAME
    Environment = @{
        Variables = $envJson
    }
}

# Générer le JSON et l'écrire dans le fichier
$jsonContent = $cliInputJson | ConvertTo-Json -Depth 10
# Utiliser [System.IO.File]::WriteAllText pour éviter l'interprétation PowerShell
[System.IO.File]::WriteAllText($cliInputFile, $jsonContent, [System.Text.Encoding]::UTF8)

Write-Host "Fichier de configuration: $cliInputFile" -ForegroundColor Gray

# Mettre à jour les variables d'environnement
try {
    $filePath = (Resolve-Path $cliInputFile).Path
    $success = $false
    
    # Utiliser le fichier JSON complet avec --cli-input-json
    # Sur Windows, certaines versions d'AWS CLI acceptent les chemins Windows directs
    Write-Host "Mise à jour Lambda avec fichier JSON..." -ForegroundColor Gray
    
    # Essayer avec le chemin Windows natif (sans file://)
    # Certaines versions d'AWS CLI sur Windows acceptent cela
    $result = aws lambda update-function-configuration `
        --cli-input-json $cliInputFile `
        --region $REGION `
        --output json 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        # Si ça ne fonctionne pas, utiliser file:// avec le chemin converti
        Write-Host "Tentative avec file://..." -ForegroundColor Yellow
        $filePathUnix = $filePath -replace '\\', '/'
        $fileUri = "file://$filePathUnix"
        
        $result = aws lambda update-function-configuration `
            --cli-input-json $fileUri `
            --region $REGION `
            --output json 2>&1
    }
    
    # Nettoyer le fichier temporaire
    Remove-Item $cliInputFile -ErrorAction SilentlyContinue
    
    if ($LASTEXITCODE -eq 0) {
        $success = $true
        $result | ConvertFrom-Json | Select-Object FunctionName, LastUpdateStatus | Format-Table
    } else {
        Write-Host "ERREUR AWS CLI:" -ForegroundColor Red
        Write-Host $result -ForegroundColor Red
        Write-Host ""
        Write-Host "Le JSON Environment généré:" -ForegroundColor Yellow
        Write-Host $envJsonString -ForegroundColor Gray
        throw "Échec de la mise à jour Lambda"
    }
    
    # Nettoyer le fichier temporaire
    Remove-Item $cliInputFile -ErrorAction SilentlyContinue
    
    if (-not $success) {
        throw "Échec de la mise à jour Lambda"
    }
    
    Write-Host ""
    Write-Host "Variables d'environnement configurees avec succes!" -ForegroundColor Green
    
    # Afficher les variables configurées (masquer les valeurs sensibles)
    Write-Host ""
    Write-Host "Variables configurees:" -ForegroundColor Cyan
    foreach ($key in $envVars.Keys) {
        $value = $envVars[$key]
        if ($key -match 'PASSWORD|SECRET|KEY') {
            $displayValue = "***" + $value.Substring([Math]::Max(0, $value.Length - 4))
        } else {
            $displayValue = $value
        }
        Write-Host "  $key = $displayValue" -ForegroundColor Gray
    }
    
} catch {
    Write-Host "ERREUR lors de la mise a jour:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Configuration terminee!" -ForegroundColor Green


