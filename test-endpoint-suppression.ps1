# Script pour tester l'endpoint de suppression des comptes

$ApiUrl = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "TEST ENDPOINT DE SUPPRESSION" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "API URL: $ApiUrl" -ForegroundColor Yellow
Write-Host ""

# D'abord, vérifier l'état actuel des comptes (avec l'endpoint list-users)
Write-Host "1. Verification de l'endpoint list-users..." -ForegroundColor Yellow
try {
    $listResponse = Invoke-RestMethod -Uri "$ApiUrl/api/admin/list-users" `
        -Method GET `
        -ErrorAction Stop 2>&1
    
    Write-Host "   Reponse:" -ForegroundColor Gray
    $listResponse | ConvertTo-Json -Depth 10 | Write-Host
    
} catch {
    Write-Host "   ERREUR lors de l'appel list-users:" -ForegroundColor Red
    Write-Host "   $($_.Exception.Message)" -ForegroundColor Red
    if ($_.ErrorDetails.Message) {
        Write-Host "   Details: $($_.ErrorDetails.Message)" -ForegroundColor Yellow
    }
    Write-Host ""
}

Write-Host ""
Write-Host "2. Test de l'endpoint delete-all-users-simple (SANS confirmation)..." -ForegroundColor Yellow
Write-Host "   (Cet appel devrait echouer car nous n'envoyons pas confirm=yes)" -ForegroundColor Gray
try {
    $testResponse = Invoke-RestMethod -Uri "$ApiUrl/api/admin/delete-all-users-simple" `
        -Method POST `
        -ContentType "application/json" `
        -Body '{}' `
        -ErrorAction Stop 2>&1
    
    Write-Host "   Reponse inattendue:" -ForegroundColor Yellow
    $testResponse | ConvertTo-Json -Depth 10 | Write-Host
    
} catch {
    $statusCode = $_.Exception.Response.StatusCode.value__
    if ($statusCode -eq 400) {
        Write-Host "   OK: Erreur 400 attendue (confirmation requise)" -ForegroundColor Green
        if ($_.ErrorDetails.Message) {
            try {
                $errorJson = $_.ErrorDetails.Message | ConvertFrom-Json
                Write-Host "   Message: $($errorJson.error)" -ForegroundColor Gray
            } catch {
                Write-Host "   Message: $($_.ErrorDetails.Message)" -ForegroundColor Gray
            }
        }
    } else {
        Write-Host "   ERREUR inattendue (code: $statusCode):" -ForegroundColor Red
        Write-Host "   $($_.Exception.Message)" -ForegroundColor Red
        if ($_.ErrorDetails.Message) {
            Write-Host "   Details: $($_.ErrorDetails.Message)" -ForegroundColor Yellow
        }
    }
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "TEST TERMINE" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Si les tests sont OK, vous pouvez executer:" -ForegroundColor Yellow
Write-Host "  .\supprimer-comptes-api.ps1 -Confirm 'OUI'" -ForegroundColor White
Write-Host ""
