# Script PowerShell pour tester le modal de publication
# À exécuter dans PowerShell après avoir démarré le serveur

Write-Host "🧪 TEST DU MODAL DE PUBLICATION" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "📋 Instructions:" -ForegroundColor Yellow
Write-Host "1. Ouvrez votre navigateur et allez sur la page" -ForegroundColor White
Write-Host "2. Ouvrez la console (F12)" -ForegroundColor White
Write-Host "3. Copiez-collez le contenu de test-publish-modal.js dans la console" -ForegroundColor White
Write-Host "4. Appuyez sur Entrée" -ForegroundColor White
Write-Host ""

Write-Host "📋 Ou testez directement dans la console du navigateur:" -ForegroundColor Yellow
Write-Host ""
Write-Host "// Test rapide:" -ForegroundColor Green
Write-Host "console.log('Test 1:', typeof window.openPublishModal);" -ForegroundColor Green
Write-Host "console.log('Test 2:', document.getElementById('publish-modal-backdrop'));" -ForegroundColor Green
Write-Host "console.log('Test 3:', typeof currentUser !== 'undefined' ? currentUser.isLoggedIn : 'currentUser undefined');" -ForegroundColor Green
Write-Host "console.log('Test 4:', typeof currentMode);" -ForegroundColor Green
Write-Host "console.log('Test 5:', typeof window.t);" -ForegroundColor Green
Write-Host "console.log('Test 6:', typeof buildPublishFormHtml);" -ForegroundColor Green
Write-Host ""
Write-Host "// Tester l'ouverture:" -ForegroundColor Green
Write-Host "if (typeof window.openPublishModal === 'function') { window.openPublishModal(); }" -ForegroundColor Green
Write-Host ""

Write-Host "✅ Script de test créé: test-publish-modal.js" -ForegroundColor Green
Write-Host "📝 Ouvrez ce fichier et copiez son contenu dans la console du navigateur" -ForegroundColor Yellow
