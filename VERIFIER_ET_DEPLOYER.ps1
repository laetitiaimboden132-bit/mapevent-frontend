# Script pour vérifier la syntaxe et déployer
# Usage: .\VERIFIER_ET_DEPLOYER.ps1

Write-Host "=== VÉRIFICATION ET DÉPLOIEMENT ===" -ForegroundColor Cyan
Write-Host ""

# Vérifier que les fichiers existent
$mapLogic = "public\map_logic.js"
$auth = "public\auth.js"
$html = "public\mapevent.html"

if (-not (Test-Path $mapLogic)) {
    Write-Host "❌ ERREUR: $mapLogic introuvable!" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $auth)) {
    Write-Host "❌ ERREUR: $auth introuvable!" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $html)) {
    Write-Host "❌ ERREUR: $html introuvable!" -ForegroundColor Red
    exit 1
}

Write-Host "✅ Fichiers trouvés" -ForegroundColor Green
Write-Host ""

# Vérifier les versions dans le HTML
Write-Host "Vérification des versions dans mapevent.html..." -ForegroundColor Yellow
$htmlContent = Get-Content $html -Raw
if ($htmlContent -match 'map_logic\.js\?v=([^"]+)') {
    $mapLogicVersion = $matches[1]
    Write-Host "  map_logic.js: v=$mapLogicVersion" -ForegroundColor Cyan
} else {
    Write-Host "  ⚠️ Version de map_logic.js non trouvée" -ForegroundColor Yellow
}

if ($htmlContent -match 'auth\.js\?v=([^"]+)') {
    $authVersion = $matches[1]
    Write-Host "  auth.js: v=$authVersion" -ForegroundColor Cyan
} else {
    Write-Host "  ⚠️ Version de auth.js non trouvée" -ForegroundColor Yellow
}

Write-Host ""

# Vérifier la ligne 2562 de map_logic.js
Write-Host "Vérification de la ligne 2562 de map_logic.js..." -ForegroundColor Yellow
$mapLogicLines = Get-Content $mapLogic
if ($mapLogicLines.Count -ge 2562) {
    $line2562 = $mapLogicLines[2561]  # Index 0-based
    Write-Host "  Ligne 2562: $line2562" -ForegroundColor Gray
    
    # Vérifier si la ligne contient des caractères suspects
    if ($line2562 -match '^\s*\}\s*\)\s*;\s*$') {
        Write-Host "  ✅ Syntaxe correcte: fermeture de callback" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️ Ligne 2562 ne correspond pas au pattern attendu" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ⚠️ Le fichier a moins de 2562 lignes ($($mapLogicLines.Count) lignes)" -ForegroundColor Yellow
}

Write-Host ""

# Demander confirmation pour déployer
Write-Host "Le serveur charge encore v=20260107-56 (ancienne version)" -ForegroundColor Red
Write-Host "Il faut redéployer les fichiers pour corriger l'erreur." -ForegroundColor Yellow
Write-Host ""
$confirm = Read-Host "Voulez-vous déployer maintenant? (O/N)"

if ($confirm -eq "O" -or $confirm -eq "o" -or $confirm -eq "Oui" -or $confirm -eq "oui") {
    Write-Host ""
    Write-Host "Déploiement en cours..." -ForegroundColor Yellow
    Write-Host ""
    
    if (Test-Path "deploy-force-cache-bust.ps1") {
        & ".\deploy-force-cache-bust.ps1"
    } elseif (Test-Path "deploy-frontend.ps1") {
        & ".\deploy-frontend.ps1"
    } else {
        Write-Host "❌ Script de déploiement introuvable!" -ForegroundColor Red
        Write-Host "   Cherchez: deploy-force-cache-bust.ps1 ou deploy-frontend.ps1" -ForegroundColor Yellow
        exit 1
    }
} else {
    Write-Host ""
    Write-Host "Déploiement annulé." -ForegroundColor Yellow
    Write-Host "Pour déployer plus tard, exécutez: .\deploy-force-cache-bust.ps1" -ForegroundColor Cyan
}
