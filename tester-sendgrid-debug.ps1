# Script de debug pour SendGrid avec affichage detaille des erreurs

$API_BASE = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api"
$email = "laetitia.imboden132@gmail.com"
$code = (Get-Random -Minimum 100000 -Maximum 999999).ToString()

$body = @{
    email = $email
    username = "Test User"
    code = $code
} | ConvertTo-Json

Write-Host "Test SendGrid Debug" -ForegroundColor Cyan
Write-Host "Email: $email" -ForegroundColor White
Write-Host "Code: $code" -ForegroundColor White
Write-Host "Body: $body" -ForegroundColor Gray
Write-Host ""

try {
    $response = Invoke-WebRequest -Uri "$API_BASE/user/send-verification-code" `
        -Method POST `
        -ContentType "application/json" `
        -Body $body `
        -ErrorAction Stop
    
    Write-Host "SUCCESS - Code HTTP: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Response:" -ForegroundColor Cyan
    $response.Content | ConvertFrom-Json | ConvertTo-Json -Depth 10 | Write-Host
    
} catch {
    Write-Host "ERREUR:" -ForegroundColor Red
    Write-Host "  Message: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode.value__
        Write-Host "  Code HTTP: $statusCode" -ForegroundColor Red
        
        try {
            $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
            $responseBody = $reader.ReadToEnd()
            $reader.Close()
            
            Write-Host "  Response Body:" -ForegroundColor Yellow
            Write-Host $responseBody -ForegroundColor White
            
            if ($responseBody) {
                try {
                    $errorData = $responseBody | ConvertFrom-Json
                    Write-Host ""
                    Write-Host "  Error Details:" -ForegroundColor Yellow
                    $errorData | ConvertTo-Json -Depth 10 | Write-Host
                } catch {
                    Write-Host "  (Response n'est pas du JSON)" -ForegroundColor Gray
                }
            }
        } catch {
            Write-Host "  (Impossible de lire la response)" -ForegroundColor Gray
        }
    }
    
    Write-Host ""
    Write-Host "Stack Trace:" -ForegroundColor Gray
    Write-Host $_.ScriptStackTrace -ForegroundColor Gray
}
