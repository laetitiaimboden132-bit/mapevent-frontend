# Script pour verifier CORS
$API_ID = "j33osy4bvj"
$REGION = "eu-west-1"
$RESOURCE_ID = "rjh1m4"
$ENDPOINT = "https://$API_ID.execute-api.$REGION.amazonaws.com/default/api/user/oauth/google/complete"

Write-Host "Verification CORS pour OPTIONS..." -ForegroundColor Cyan

try {
    $response = Invoke-WebRequest -Uri $ENDPOINT -Method OPTIONS -Headers @{
        "Origin" = "https://mapevent.world"
        "Access-Control-Request-Method" = "POST"
        "Access-Control-Request-Headers" = "Content-Type"
    } -UseBasicParsing
    
    Write-Host "Status Code: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Headers CORS:" -ForegroundColor Yellow
    $response.Headers | ForEach-Object {
        if ($_.Key -like "*Access-Control*") {
            Write-Host "  $($_.Key): $($_.Value -join ', ')" -ForegroundColor Green
        }
    }
    
    if ($response.Headers['Access-Control-Allow-Origin']) {
        Write-Host "`nCORS configure correctement !" -ForegroundColor Green
    } else {
        Write-Host "`nCORS non configure - headers manquants" -ForegroundColor Red
    }
} catch {
    Write-Host "Erreur: $_" -ForegroundColor Red
    Write-Host "Details: $($_.Exception.Message)" -ForegroundColor Yellow
}


