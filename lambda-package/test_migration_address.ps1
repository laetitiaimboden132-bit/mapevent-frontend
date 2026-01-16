# Script PowerShell pour tester la migration des champs d'adresse
# Usage: .\test_migration_address.ps1

$LAMBDA_URL = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"

Write-Host "========================================"
Write-Host "TEST MIGRATION CHAMPS ADRESSE"
Write-Host "========================================"
Write-Host ""

Write-Host "[ETAPE 1] Execution de la migration..."
try {
    $response = Invoke-RestMethod -Uri "$LAMBDA_URL/api/admin/migrate-address-fields" -Method POST -Headers @{
        "Content-Type" = "application/json"
    } -ErrorAction Stop
    
    Write-Host "[OK] Migration executee avec succes!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Resultats:" -ForegroundColor Cyan
    foreach ($result in $response.results) {
        Write-Host "  - $result" -ForegroundColor Gray
    }
    Write-Host ""
    
    if ($response.success) {
        Write-Host "[SUCCES] Migration terminee!" -ForegroundColor Green
    } else {
        Write-Host "[ERREUR] Migration echouee" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "[ERREUR] Impossible d'executer la migration:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host $_.ErrorDetails.Message -ForegroundColor Red
    }
    exit 1
}

Write-Host ""
Write-Host "========================================"
Write-Host "MIGRATION TERMINEE"
Write-Host "========================================"



