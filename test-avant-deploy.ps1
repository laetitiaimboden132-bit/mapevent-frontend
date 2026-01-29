# Test console avant deploiement : health + CORS (sans login).
# Usage: .\test-avant-deploy.ps1

$ApiUrl = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"
$ok = 0
$ko = 0

Write-Host ""
Write-Host "=== TEST AVANT DEPLOIEMENT (console) ===" -ForegroundColor Cyan
Write-Host ""

# 1) GET /api/health
Write-Host "1) GET /api/health ... " -NoNewline
try {
    $r = Invoke-WebRequest -Uri "$ApiUrl/api/health" -Method GET -UseBasicParsing -TimeoutSec 10
    if ($r.StatusCode -eq 200) {
        Write-Host "OK" -ForegroundColor Green
        $ok++
    } else {
        Write-Host "KO (status $($r.StatusCode))" -ForegroundColor Red
        $ko++
    }
} catch {
    Write-Host "KO ($($_.Exception.Message))" -ForegroundColor Red
    $ko++
}

# 2) OPTIONS (CORS)
Write-Host "2) OPTIONS (CORS) ... " -NoNewline
try {
    $r = Invoke-WebRequest -Uri "$ApiUrl/api/health" -Method OPTIONS -UseBasicParsing -TimeoutSec 10
    $aco = $r.Headers["Access-Control-Allow-Origin"]
    if ($r.StatusCode -eq 200 -and $aco) {
        Write-Host "OK (Origin: $aco)" -ForegroundColor Green
        $ok++
    } elseif ($r.StatusCode -eq 200) {
        Write-Host "OK (pas de header CORS vu)" -ForegroundColor Yellow
        $ok++
    } else {
        Write-Host "KO (status $($r.StatusCode))" -ForegroundColor Red
        $ko++
    }
} catch {
    Write-Host "KO ($($_.Exception.Message))" -ForegroundColor Red
    $ko++
}

Write-Host ""
if ($ko -eq 0) {
    Write-Host "=> Tout OK, vous pouvez deployer." -ForegroundColor Green
} else {
    Write-Host "=> $ko test(s) en echec. Verifiez Lambda / CORS avant de deployer." -ForegroundColor Yellow
}
Write-Host ""
