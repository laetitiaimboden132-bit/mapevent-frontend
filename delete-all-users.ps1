# Script PowerShell pour supprimer TOUS les comptes utilisateurs
# ATTENTION: Cette opération est IRRÉVERSIBLE

Write-Host "=" -NoNewline
Write-Host ("=" * 59) -ForegroundColor Red
Write-Host "🗑️  SUPPRESSION DE TOUS LES COMPTES UTILISATEURS" -ForegroundColor Red
Write-Host "=" -NoNewline
Write-Host ("=" * 59) -ForegroundColor Red
Write-Host ""
Write-Host "⚠️  ATTENTION: Cette opération est IRRÉVERSIBLE!" -ForegroundColor Yellow
Write-Host "   Tous les comptes utilisateurs et leurs données seront supprimés." -ForegroundColor Yellow
Write-Host ""

# Demander confirmation
$confirmation = Read-Host "Tapez 'OUI' pour confirmer la suppression de TOUS les comptes"

if ($confirmation -ne "OUI") {
    Write-Host "❌ Suppression annulée." -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "🔄 Définition de la variable d'environnement CONFIRM_DELETE_ALL=yes..." -ForegroundColor Cyan
$env:CONFIRM_DELETE_ALL = "yes"

Write-Host "🔄 Exécution du script Python..." -ForegroundColor Cyan
Write-Host ""

# Exécuter le script Python
python lambda-package/delete_all_users.py

$exitCode = $LASTEXITCODE

if ($exitCode -eq 0) {
    Write-Host ""
    Write-Host "✅ Tous les comptes utilisateurs ont été supprimés avec succès!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "❌ Erreur lors de la suppression des comptes." -ForegroundColor Red
    exit $exitCode
}



