# Script PowerShell pour créer toutes les colonnes nécessaires dans la table users
# Ce script se connecte à votre base de données RDS et exécute le script SQL

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Creation des colonnes users pour OAuth" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Récupérer les informations de la base de données
Write-Host "[1/3] Recuperation des informations RDS..." -ForegroundColor Yellow

$dbEndpoint = aws rds describe-db-instances --region eu-west-1 --query "DBInstances[?DBName=='mapevent'].Endpoint.Address" --output text
$dbName = "mapevent"
$dbUser = "postgres"

Write-Host "   Endpoint: $dbEndpoint" -ForegroundColor Green
Write-Host "   Database: $dbName" -ForegroundColor Green
Write-Host "   User: $dbUser" -ForegroundColor Green
Write-Host ""

# Récupérer le mot de passe depuis lambda.env
Write-Host "[1.5/3] Recuperation du mot de passe depuis lambda.env..." -ForegroundColor Yellow

$lambdaEnvPath = "lambda-package\lambda.env"
if (Test-Path $lambdaEnvPath) {
    $lambdaEnvContent = Get-Content $lambdaEnvPath
    $rdsPasswordLine = $lambdaEnvContent | Select-String "RDS_PASSWORD="
    if ($rdsPasswordLine) {
        $dbPasswordPlain = ($rdsPasswordLine.ToString() -replace "RDS_PASSWORD=", "").Trim()
        Write-Host "   Mot de passe trouve dans lambda.env" -ForegroundColor Green
    } else {
        Write-Host "   ERREUR: RDS_PASSWORD non trouve dans lambda.env!" -ForegroundColor Red
        $dbPassword = Read-Host "Entrez le mot de passe de la base de données" -AsSecureString
        $dbPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($dbPassword))
    }
} else {
    Write-Host "   lambda.env non trouve, demande du mot de passe..." -ForegroundColor Yellow
    $dbPassword = Read-Host "Entrez le mot de passe de la base de données" -AsSecureString
    $dbPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($dbPassword))
}

Write-Host ""
Write-Host "[2/3] Lecture du script SQL..." -ForegroundColor Yellow

$sqlScript = Get-Content "CREER_COLONNES_USERS.sql" -Raw

if (-not $sqlScript) {
    Write-Host "   ERREUR: Fichier CREER_COLONNES_USERS.sql introuvable!" -ForegroundColor Red
    exit 1
}

Write-Host "   Script SQL charge: $($sqlScript.Length) caracteres" -ForegroundColor Green
Write-Host ""

# Vérifier si psql est disponible
Write-Host "[3/3] Execution du script SQL..." -ForegroundColor Yellow

$psqlPath = Get-Command psql -ErrorAction SilentlyContinue

if (-not $psqlPath) {
    Write-Host "   ERREUR: psql non trouve!" -ForegroundColor Red
    Write-Host "   Installez PostgreSQL Client ou utilisez un autre outil SQL" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   Alternative: Utilisez pgAdmin ou DBeaver pour executer CREER_COLONNES_USERS.sql manuellement" -ForegroundColor Yellow
    exit 1
}

# Exécuter le script SQL
$env:PGPASSWORD = $dbPasswordPlain

try {
    $sqlScript | & psql -h $dbEndpoint -U $dbUser -d $dbName -f -
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "SUCCES: Colonnes creees avec succes!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Red
        Write-Host "ERREUR: Echec de l'execution SQL" -ForegroundColor Red
        Write-Host "========================================" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host ""
    Write-Host "ERREUR: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
} finally {
    Remove-Item Env:\PGPASSWORD
}

Write-Host ""
Write-Host "Prochaines etapes:" -ForegroundColor Cyan
Write-Host "  1. Publiez votre application Google OAuth en mode Production" -ForegroundColor White
Write-Host "  2. Testez la connexion Google sur https://mapevent.world" -ForegroundColor White
Write-Host "  3. Le formulaire d'inscription devrait s'afficher automatiquement" -ForegroundColor White

