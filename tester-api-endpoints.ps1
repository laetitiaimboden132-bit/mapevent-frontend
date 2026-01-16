# Script pour tester les endpoints API disponibles
$apiBaseUrl = "https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "TEST DES ENDPOINTS API" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Tester différents endpoints
$endpoints = @(
    "/api/admin/list-users",
    "/api/admin/delete-all-users-except",
    "/api/admin/delete-all-users-simple",
    "/api/user/register",
    "/api/health"
)

foreach ($endpoint in $endpoints) {
    Write-Host "Test: $endpoint" -ForegroundColor Yellow
    try {
        if ($endpoint -like "*delete*") {
            # Pour les endpoints POST
            $body = @{} | ConvertTo-Json
            $response = Invoke-WebRequest -Uri "$apiBaseUrl$endpoint" -Method POST -Body $body -ContentType "application/json" -UseBasicParsing -ErrorAction Stop
        } else {
            # Pour les endpoints GET
            $response = Invoke-WebRequest -Uri "$apiBaseUrl$endpoint" -Method GET -UseBasicParsing -ErrorAction Stop
        }
        
        Write-Host "  Status: $($response.StatusCode) - OK" -ForegroundColor Green
        if ($response.Content) {
            $content = $response.Content | ConvertFrom-Json -ErrorAction SilentlyContinue
            if ($content) {
                Write-Host "  Response: $($content | ConvertTo-Json -Depth 2 -Compress)" -ForegroundColor Gray
            }
        }
    } catch {
        Write-Host "  Status: $($_.Exception.Response.StatusCode.value__) - ERREUR" -ForegroundColor Red
        Write-Host "  Message: $($_.Exception.Message)" -ForegroundColor Gray
        if ($_.ErrorDetails.Message) {
            $errorDetails = $_.ErrorDetails.Message | ConvertFrom-Json -ErrorAction SilentlyContinue
            if ($errorDetails.message) {
                Write-Host "  Details: $($errorDetails.message)" -ForegroundColor Gray
            }
        }
    }
    Write-Host ""
}

