# Script automatique pour deployer Lambda (depuis la racine du projet)

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  DEPLOY AUTOMATIQUE LAMBDA" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Aller dans le dossier lambda-package
Push-Location lambda-package

try {
    # Executer le script de deploy
    & .\deploy-lambda.ps1
} finally {
    # Retourner au dossier racine
    Pop-Location
}






