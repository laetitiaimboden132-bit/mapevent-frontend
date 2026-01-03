# Test de la route create-tables via API Gateway

Write-Host "Test de la route create-tables..." -ForegroundColor Cyan
Write-Host ""

$uri = "https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/api/admin/create-tables"

try {
    $response = Invoke-WebRequest -Uri $uri -Method POST -Headers @{"Content-Type"="application/json"} -Body "{}"
    
    Write-Host "Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host ""
    Write-Host "Reponse:" -ForegroundColor Cyan
    $response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10
    
} catch {
    Write-Host "Erreur: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "Reponse serveur: $responseBody" -ForegroundColor Yellow
    }
}

