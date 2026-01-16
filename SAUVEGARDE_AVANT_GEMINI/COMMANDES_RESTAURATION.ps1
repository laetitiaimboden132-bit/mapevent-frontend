# 🔄 SCRIPT DE RESTAURATION - SAUVEGARDE AVANT GEMINI
# Utilisez ce script si Gemini a cassé quelque chose

Write-Host "🔄 RESTAURATION DE LA SAUVEGARDE..." -ForegroundColor Yellow
Write-Host ""

# Vérifier que la sauvegarde existe
if (-not (Test-Path "SAUVEGARDE_AVANT_GEMINI")) {
    Write-Host "❌ ERREUR : Le dossier SAUVEGARDE_AVANT_GEMINI n'existe pas !" -ForegroundColor Red
    exit 1
}

Write-Host "📁 Restauration du Frontend..." -ForegroundColor Cyan
Copy-Item -Path "SAUVEGARDE_AVANT_GEMINI\mapevent.html" -Destination "public\mapevent.html" -Force
Copy-Item -Path "SAUVEGARDE_AVANT_GEMINI\map_logic.js" -Destination "public\map_logic.js" -Force
Write-Host "✅ Frontend restauré" -ForegroundColor Green

Write-Host ""
Write-Host "📁 Restauration du Backend..." -ForegroundColor Cyan
Copy-Item -Path "SAUVEGARDE_AVANT_GEMINI\handler.py" -Destination "lambda-package\handler.py" -Force
Copy-Item -Path "SAUVEGARDE_AVANT_GEMINI\lambda_function.py" -Destination "lambda-package\lambda_function.py" -Force
Copy-Item -Path "SAUVEGARDE_AVANT_GEMINI\backend_main.py" -Destination "lambda-package\backend\main.py" -Force
Copy-Item -Path "SAUVEGARDE_AVANT_GEMINI\requirements.txt" -Destination "lambda-package\backend\requirements.txt" -Force
Copy-Item -Path "SAUVEGARDE_AVANT_GEMINI\deploy_backend.py" -Destination "lambda-package\deploy_backend.py" -Force
Write-Host "✅ Backend restauré" -ForegroundColor Green

Write-Host ""
Write-Host "🚀 Redéploiement du backend Lambda..." -ForegroundColor Cyan
cd lambda-package
python deploy_backend.py
cd ..

Write-Host ""
Write-Host "✅ RESTAURATION TERMINÉE !" -ForegroundColor Green
Write-Host "⚠️ N'oubliez pas de tester le site : https://mapevent.world" -ForegroundColor Yellow







