# Test simple de /health
$url = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/health"
Write-Host "Test GET $url"

try {
    $response = Invoke-WebRequest -Uri $url -Method GET -ErrorAction Stop
    Write-Host "SUCCESS Status: $($response.StatusCode)" -ForegroundColor Green
    Write-Host "Response: $($response.Content)"
} catch {
    Write-Host "ERROR: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response) {
        Write-Host "Status Code: $($_.Exception.Response.StatusCode.value__)"
        try {
            $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
            $responseBody = $reader.ReadToEnd()
            $reader.Close()
            Write-Host "Response Body: $responseBody"
        } catch {
            Write-Host "Could not read response body"
        }
    }
}



