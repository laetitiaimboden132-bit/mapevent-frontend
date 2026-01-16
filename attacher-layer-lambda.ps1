# Script pour attacher la Lambda Layer à la fonction Lambda

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "ATTACHER LAMBDA LAYER A LA FONCTION LAMBDA" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Variables
$FUNCTION_NAME = "mapevent-backend"
$REGION = "eu-west-1"
$LAYER_ARN_FILE = "lambda-package\lambda-layer-arn.txt"

# Vérifier si le fichier ARN existe
if (-not (Test-Path $LAYER_ARN_FILE)) {
    Write-Host "ERREUR: Fichier lambda-layer-arn.txt introuvable!" -ForegroundColor Red
    Write-Host "Executez d'abord: .\creer-lambda-layer.ps1" -ForegroundColor Yellow
    exit 1
}

# Lire l'ARN de la Layer
$LAYER_ARN = Get-Content $LAYER_ARN_FILE -Raw | ForEach-Object { $_.Trim() }

if ([string]::IsNullOrWhiteSpace($LAYER_ARN)) {
    Write-Host "ERREUR: ARN de la Layer vide!" -ForegroundColor Red
    exit 1
}

Write-Host "Layer ARN: $LAYER_ARN" -ForegroundColor White
Write-Host ""

# Récupérer les Layers actuels de la fonction
Write-Host "1. Recuperation des Layers actuels..." -ForegroundColor Yellow
try {
    $functionConfig = aws lambda get-function-configuration `
        --function-name $FUNCTION_NAME `
        --region $REGION 2>&1 | ConvertFrom-Json
    
    $currentLayers = $functionConfig.Layers | ForEach-Object { $_.Arn }
    
    Write-Host "   Layers actuels:" -ForegroundColor Gray
    foreach ($layer in $currentLayers) {
        if ($layer -like "*psycopg2*") {
            Write-Host "     - $layer (psycopg2 - a garder)" -ForegroundColor Green
        } else {
            Write-Host "     - $layer" -ForegroundColor Gray
        }
    }
} catch {
    Write-Host "ERREUR: Impossible de recuperer la configuration de la fonction" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

# Construire la liste des Layers à attacher
# Garder psycopg2 Layer (si présente) et ajouter notre nouvelle Layer
$layersToAttach = @()
foreach ($layer in $currentLayers) {
    if ($layer -like "*psycopg2*") {
        $layersToAttach += $layer
    }
}
$layersToAttach += $LAYER_ARN

Write-Host ""
Write-Host "2. Attachement de la Layer..." -ForegroundColor Yellow
Write-Host "   Layers a attacher:" -ForegroundColor Gray
foreach ($layer in $layersToAttach) {
    if ($layer -like "*psycopg2*") {
        Write-Host "     - $layer (psycopg2)" -ForegroundColor Green
    } elseif ($layer -eq $LAYER_ARN) {
        Write-Host "     - $layer (nouvelles dependances Python)" -ForegroundColor Cyan
    } else {
        Write-Host "     - $layer" -ForegroundColor Gray
    }
}

try {
    # Construire le paramètre --layers correctement (liste séparée par des espaces)
    $layersArg = $layersToAttach -join " "
    
    # Utiliser Invoke-Expression ou appeler directement
    $updateResult = aws lambda update-function-configuration `
        --function-name $FUNCTION_NAME `
        --layers $layersArg `
        --region $REGION 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERREUR: $updateResult" -ForegroundColor Red
        throw "Erreur lors de l'attachement de la Layer"
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "============================================================" -ForegroundColor Green
        Write-Host "SUCCES: Layer attachee avec succes !" -ForegroundColor Green
        Write-Host "============================================================" -ForegroundColor Green
        Write-Host ""
        
        Write-Host "Attente de 10 secondes pour que Lambda se mette a jour..." -ForegroundColor Yellow
        Start-Sleep -Seconds 10
        
        Write-Host ""
        Write-Host "Prochaine etape: Redeployer Lambda SANS dependances" -ForegroundColor Yellow
        Write-Host "  .\deploy-lambda-sans-dependances.ps1" -ForegroundColor White
        Write-Host ""
    } else {
        Write-Host "ERREUR: Impossible d'attacher la Layer (code: $LASTEXITCODE)" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "ERREUR lors de l'attachement: $_" -ForegroundColor Red
    exit 1
}

