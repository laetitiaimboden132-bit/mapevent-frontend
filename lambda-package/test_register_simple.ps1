# Test simple pour voir la réponse complète de /api/user/register

$API_BASE = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api"

Write-Host "=== TEST REGISTER SIMPLE ===" -ForegroundColor Cyan
Write-Host ""

$registerBody = @{
    email = "testjwt@example.com"
    password = "TestPassword123!"
    username = "testjwt"
    firstName = "Test"
    lastName = "JWT"
    addresses = @(
        @{
            street = "Rue de Test 1"
            city = "Lausanne"
            zip = "1000"
            country = "CH"
            lat = 46.5197
            lng = 6.6323
        }
    )
} | ConvertTo-Json -Depth 10

Write-Host "Body envoyé:" -ForegroundColor Yellow
Write-Host $registerBody
Write-Host ""

try {
    $response = Invoke-WebRequest -Uri "$API_BASE/user/register" `
        -Method POST `
        -Headers @{"Content-Type"="application/json"} `
        -Body $registerBody `
        -ErrorAction Stop
    
    Write-Host "✅ Succès: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Response Content:" -ForegroundColor Yellow
    Write-Host $response.Content
} catch {
    Write-Host "❌ Erreur: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "Status Code: $($_.Exception.Response.StatusCode.value__)" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        $reader.Close()
        Write-Host "Response Body:" -ForegroundColor Yellow
        Write-Host $responseBody
        Write-Host "Response Body Length: $($responseBody.Length)" -ForegroundColor Yellow
    }
}



