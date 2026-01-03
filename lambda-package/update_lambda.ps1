# Script simple pour mettre à jour Lambda après modification de lambda.env
# Usage: .\update_lambda.ps1

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  MISE A JOUR LAMBDA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier que lambda.env existe
if (-not (Test-Path "lambda.env")) {
    Write-Host "ERREUR: Fichier lambda.env non trouve!" -ForegroundColor Red
    Write-Host "Assurez-vous d'etre dans le repertoire lambda-package" -ForegroundColor Yellow
    exit 1
}

# Vérifier Python
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    $pythonCmd = Get-Command python3 -ErrorAction SilentlyContinue
}

if (-not $pythonCmd) {
    Write-Host "ERREUR: Python n'est pas installe!" -ForegroundColor Red
    Write-Host "Installez Python depuis https://www.python.org/" -ForegroundColor Yellow
    exit 1
}

Write-Host "Lecture de lambda.env..." -ForegroundColor Yellow
Write-Host ""

# Afficher le mot de passe RDS actuel (masqué)
$rdsPassword = (Get-Content lambda.env | Select-String "RDS_PASSWORD").ToString() -replace "RDS_PASSWORD=", ""
if ($rdsPassword) {
    $maskedPassword = "***" + $rdsPassword.Substring([Math]::Max(0, $rdsPassword.Length - 4))
    Write-Host "Mot de passe RDS configure: $maskedPassword" -ForegroundColor Gray
} else {
    Write-Host "ATTENTION: RDS_PASSWORD non trouve dans lambda.env!" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Mise a jour des variables d'environnement Lambda..." -ForegroundColor Yellow
Write-Host ""

# Exécuter le script Python
python configure_lambda_env.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "[OK] Lambda mis a jour avec succes!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Les variables d'environnement Lambda ont ete synchronisees avec lambda.env" -ForegroundColor Gray
} else {
    Write-Host ""
    Write-Host "ERREUR lors de la mise a jour Lambda" -ForegroundColor Red
    exit 1
}




