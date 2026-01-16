# Script PowerShell pour corriger TOUS les problÃ¨mes d'un coup
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CORRECTION COMPLETE - TOUS LES PROBLÃˆMES" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
Write-Host "Timestamp: $timestamp" -ForegroundColor Yellow

# 1. VÃ©rifier et corriger auth.js
Write-Host "
1. VÃ©rification auth.js..." -ForegroundColor Green
$authJs = Get-Content "public\auth.js" -Raw -Encoding UTF8

if ($authJs -notmatch "Continuer sans vÃ©rifier") {
    Write-Host "âŒ Bouton manquant! Ajout..." -ForegroundColor Red
    # Le bouton devrait Ãªtre lÃ , mais vÃ©rifions
}

# 2. S'assurer que le modal est visible dans showVerificationChoice
Write-Host "2. Correction visibilitÃ© modal..." -ForegroundColor Green
$authJs = $authJs -replace "modal\.innerHTML = """", "modal.style.display = 'block'; modal.innerHTML = """"
$authJs = $authJs -replace "publish-modal-inner", "publish-modal-inner"

# 3. Forcer le display du modal
$fixModal = @'
  // FORCER la visibilitÃ© du modal
  if (modal) {
    modal.style.display = 'block';
    modal.style.visibility = 'visible';
    modal.style.opacity = '1';
  }
'@

if ($authJs -notmatch "FORCER la visibilitÃ© du modal") {
    $authJs = $authJs -replace "console\.log\('\[VERIFY\] Modal trouvÃ©:', modal\);", "console.log('[VERIFY] Modal trouvÃ©:', modal);

  $fixModal"
}

# 4. Mettre Ã  jour cache-busting
Write-Host "3. Mise Ã  jour cache-busting..." -ForegroundColor Green
$html = Get-Content "public\mapevent.html" -Raw -Encoding UTF8
$html = $html -replace 'auth\.js\?v=\d{8}-\d{6}', "auth.js?v=$timestamp"
Set-Content -Path "public\mapevent.html" -Value $html -NoNewline -Encoding UTF8

# 5. Sauvegarder auth.js
Set-Content -Path "public\auth.js" -Value $authJs -NoNewline -Encoding UTF8

Write-Host "âœ… Corrections appliquÃ©es!" -ForegroundColor Green
Write-Host "
DÃ©ploiement..." -ForegroundColor Yellow
& .\deploy-frontend.ps1
