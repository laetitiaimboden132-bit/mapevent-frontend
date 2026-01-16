# Script automatique pour deployer Lambda (depuis la racine)

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  DEPLOY AUTOMATIQUE LAMBDA" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Aller dans le dossier lambda-package
Push-Location lambda-package

try {
    # Executer le script de deploy
    & .\deploy-lambda.ps1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ DEPLOY REUSSI!" -ForegroundColor Green
    } else {
        Write-Host "`n❌ ERREUR LORS DU DEPLOY" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "`n❌ ERREUR: $_" -ForegroundColor Red
    exit 1
} finally {
    # Retourner au dossier racine
    Pop-Location
}






