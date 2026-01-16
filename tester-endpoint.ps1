# Test simple de l'endpoint

$ApiUrl = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"
$body = @{
    confirm = "yes"
} | ConvertTo-Json

Write-Host "Test de l'endpoint..." -ForegroundColor Cyan
Write-Host "URL: $ApiUrl/api/admin/delete-all-users-simple" -ForegroundColor Yellow
Write-Host "Body: $body" -ForegroundColor Yellow
Write-Host ""

try {
    $response = Invoke-RestMethod -Uri "$ApiUrl/api/admin/delete-all-users-simple" `
        -Method POST `
        -ContentType "application/json" `
        -Body $body `
        -ErrorAction Stop
    
    Write-Host "SUCCES!" -ForegroundColor Green
    $response | ConvertTo-Json
    
} catch {
    Write-Host "ERREUR:" -ForegroundColor Red
    Write-Host "Status: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Red
    Write-Host "Message: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.ErrorDetails.Message) {
        Write-Host "Details: $($_.ErrorDetails.Message)" -ForegroundColor Yellow
    }
}


