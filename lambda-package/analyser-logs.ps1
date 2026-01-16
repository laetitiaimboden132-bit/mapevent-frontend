# Script pour analyser automatiquement les logs CloudWatch

param(
    [int]$Minutes = 10,
    [switch]$ShowAll = $false
)

Write-Host "`n=== Analyse automatique des logs CloudWatch ===" -ForegroundColor Cyan
Write-Host "`nRécupération des logs des $Minutes dernières minutes..." -ForegroundColor Yellow

# Récupérer les logs avec gestion d'encodage
$env:AWS_PAGER = ""
$logFile = "cloudwatch-logs-latest.txt"

try {
    # Récupérer les logs et rediriger vers un fichier directement
    aws logs tail /aws/lambda/mapevent-backend --since ${Minutes}m --region eu-west-1 > $logFile 2>&1
    
    if (-not (Test-Path $logFile) -or (Get-Item $logFile).Length -eq 0) {
        Write-Host "ERREUR: Aucun log trouve" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "ERREUR lors de la recuperation des logs: $_" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Logs récupérés et sauvegardés dans $logFile" -ForegroundColor Green

# Analyser les erreurs
Write-Host "`n=== Analyse des erreurs ===" -ForegroundColor Cyan

$errors = @()
$warnings = @()
$success = @()

$content = Get-Content $logFile -Raw

# Rechercher les erreurs
if ($content -match 'ERROR|ERREUR|Exception|Traceback|NameError|ImportError|psycopg2') {
    Write-Host "`nErreurs trouvees:" -ForegroundColor Red
    $errorLines = $content | Select-String -Pattern 'ERROR|ERREUR|Exception|Traceback|NameError|ImportError' -Context 1
    $errorLines | Select-Object -Last 20 | ForEach-Object {
        Write-Host "  $_" -ForegroundColor Red
    }
}

# Rechercher les warnings
if ($content -match 'WARNING|warning') {
    Write-Host "`nAvertissements:" -ForegroundColor Yellow
    $warningLines = $content | Select-String -Pattern 'WARNING|warning' -Context 0 | Select-Object -Last 10
    $warningLines | ForEach-Object {
        Write-Host "  $_" -ForegroundColor Yellow
    }
}

# Rechercher les succes
if ($content -match 'SUCCESS|Application Flask creee|Connexion RDS reussie') {
    Write-Host "`nSucces:" -ForegroundColor Green
    $successLines = $content | Select-String -Pattern 'SUCCESS|Application Flask creee|Connexion RDS reussie' -Context 0 | Select-Object -Last 10
    $successLines | ForEach-Object {
        Write-Host "  $_" -ForegroundColor Green
    }
}

# Analyse specifique
Write-Host "`n=== Analyse detaillee ===" -ForegroundColor Cyan

# psycopg2
if ($content -match 'psycopg2') {
    if ($content -match 'psycopg2.*trouve|psycopg2.*trouve') {
        Write-Host "OK psycopg2: OK" -ForegroundColor Green
    } else {
        Write-Host "ERREUR psycopg2: Probleme detecte" -ForegroundColor Red
    }
} else {
    Write-Host "INFO psycopg2: Pas de mention" -ForegroundColor Gray
}

# Application Flask
if ($content -match 'Application Flask creee|create_app.*importe') {
    Write-Host "OK Application Flask: OK" -ForegroundColor Green
} else {
    Write-Host "ERREUR Application Flask: Non creee" -ForegroundColor Red
}

# Connexion RDS
if ($content -match 'Connexion RDS reussie') {
    Write-Host "OK Connexion RDS: OK" -ForegroundColor Green
} else {
    Write-Host "ATTENTION Connexion RDS: Pas de confirmation" -ForegroundColor Yellow
}

# Photo profil
if ($content -match 'profile_photo|avatar.*S3|URL photo') {
    Write-Host "Photo profil: Mentionnee dans les logs" -ForegroundColor Gray
    $photoLines = $content | Select-String -Pattern 'profile_photo|avatar.*S3|URL photo' -Context 0 | Select-Object -Last 5
    $photoLines | ForEach-Object {
        Write-Host "  $_" -ForegroundColor Gray
    }
}

# Afficher les dernieres lignes si demande
if ($ShowAll) {
    Write-Host "`n=== Dernieres lignes des logs ===" -ForegroundColor Cyan
    Get-Content $logFile | Select-Object -Last 50
}

Write-Host "`n=== Fin de l'analyse ===" -ForegroundColor Cyan
Write-Host "`nPour voir tous les logs: Get-Content $logFile" -ForegroundColor Gray

