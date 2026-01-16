# Script PowerShell pour forcer le déploiement de auth.js avec cache-busting unique
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "FORCE DEPLOY AUTH.JS - CACHE BUSTING" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Générer un timestamp unique
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
Write-Host "Timestamp: $timestamp" -ForegroundColor Yellow

# Vérifier que le bouton est présent dans auth.js
Write-Host "`nVérification du contenu de auth.js..." -ForegroundColor Green
$authJsPath = "public\auth.js"
if (Test-Path $authJsPath) {
    $content = Get-Content $authJsPath -Raw
    if ($content -match "Continuer sans vérifier") {
        Write-Host "✅ Bouton 'Continuer sans vérifier' trouvé dans auth.js" -ForegroundColor Green
    } else {
        Write-Host "❌ Bouton 'Continuer sans vérifier' NON trouvé dans auth.js!" -ForegroundColor Red
        exit 1
    }
    
    if ($content -match "handleVerificationChoice\('skip'\)") {
        Write-Host "✅ Fonction handleVerificationChoice('skip') trouvée" -ForegroundColor Green
    } else {
        Write-Host "❌ Fonction handleVerificationChoice('skip') NON trouvée!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "❌ Fichier auth.js non trouvé!" -ForegroundColor Red
    exit 1
}

# Mettre à jour le cache-busting dans mapevent.html
Write-Host "`nMise à jour du cache-busting dans mapevent.html..." -ForegroundColor Green
$htmlPath = "public\mapevent.html"
if (Test-Path $htmlPath) {
    $htmlContent = Get-Content $htmlPath -Raw
    $htmlContent = $htmlContent -replace 'auth\.js\?v=\d{8}-\d{6}', "auth.js?v=$timestamp"
    Set-Content -Path $htmlPath -Value $htmlContent -NoNewline
    Write-Host "✅ Cache-busting mis à jour: auth.js?v=$timestamp" -ForegroundColor Green
} else {
    Write-Host "❌ Fichier mapevent.html non trouvé!" -ForegroundColor Red
    exit 1
}

# Déployer avec deploy-frontend.ps1
Write-Host "`nDéploiement en cours..." -ForegroundColor Green
if (Test-Path ".\deploy-frontend.ps1") {
    & .\deploy-frontend.ps1
} else {
    Write-Host "❌ Script deploy-frontend.ps1 non trouvé!" -ForegroundColor Red
    exit 1
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "TERMINÉ!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "URL de test: https://mapevent.world/auth.js?v=$timestamp" -ForegroundColor Yellow
Write-Host "`nVidez le cache de votre navigateur (Ctrl+Shift+Delete)" -ForegroundColor Yellow
Write-Host "ou utilisez une fenêtre privée (Ctrl+Shift+N)" -ForegroundColor Yellow
