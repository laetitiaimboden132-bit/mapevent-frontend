# Script pour lancer le scraper d'événements Valais
# Usage: .\run_scraper.ps1

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  SCRAPER EVENEMENTS VALAIS - MapEventAI" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier Python
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Erreur: Python n'est pas installé!" -ForegroundColor Red
    exit 1
}
Write-Host "Python détecté: $pythonVersion" -ForegroundColor Green

# Installer les dépendances
Write-Host ""
Write-Host "Installation des dépendances..." -ForegroundColor Yellow
pip install -r requirements.txt -q

if ($LASTEXITCODE -ne 0) {
    Write-Host "Erreur lors de l'installation des dépendances!" -ForegroundColor Red
    exit 1
}
Write-Host "Dépendances OK" -ForegroundColor Green

# Lancer le scraper
Write-Host ""
Write-Host "Lancement du scraper..." -ForegroundColor Yellow
Write-Host "(Ctrl+C pour arrêter et sauvegarder les événements collectés)" -ForegroundColor Gray
Write-Host ""

python valais_scraper.py

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  SCRAPING TERMINE" -ForegroundColor Cyan  
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Fichiers generés:" -ForegroundColor Green
Write-Host "  - valais_events.json (pour inspection)" -ForegroundColor White
Write-Host "  - valais_events.sql (pour import en base)" -ForegroundColor White
Write-Host ""
Write-Host "Pour importer en base PostgreSQL:" -ForegroundColor Yellow
Write-Host "  psql -h <host> -U <user> -d <database> -f valais_events.sql" -ForegroundColor Gray
