# Script pour creer une Lambda Function URL (contourne la limite 29s d'API Gateway)

$functionName = "mapevent-backend"
$region = "eu-west-1"

Write-Host "`n=== Creation Lambda Function URL ===" -ForegroundColor Cyan
Write-Host "Fonction: $functionName" -ForegroundColor Yellow
Write-Host "Region: $region" -ForegroundColor Yellow

Write-Host "`n1. Verification si Function URL existe deja..." -ForegroundColor Yellow
try {
    $existing = aws lambda get-function-url-config --function-name $functionName --region $region 2>&1 | ConvertFrom-Json
    if ($existing) {
        Write-Host "Function URL existe deja:" -ForegroundColor Green
        Write-Host "  URL: $($existing.FunctionUrl)" -ForegroundColor White
        Write-Host "  CORS: $($existing.Cors.AllowOrigins -join ', ')" -ForegroundColor White
        Write-Host "`nPour recreer, supprimez d'abord l'existante" -ForegroundColor Yellow
        exit 0
    }
} catch {
    Write-Host "Function URL n'existe pas encore" -ForegroundColor Gray
}

Write-Host "`n2. Creation de la Function URL..." -ForegroundColor Yellow
try {
    $corsJson = '{"AllowOrigins":["https://mapevent.world","http://localhost:3000","http://localhost:8000"],"AllowMethods":["GET","POST","PUT","DELETE","OPTIONS","PATCH"],"AllowHeaders":["Content-Type","Authorization","Origin","X-Requested-With","Accept"],"MaxAge":3600}'
    $urlConfig = aws lambda create-function-url-config --function-name $functionName --auth-type NONE --cors $corsJson --region $region 2>&1 | ConvertFrom-Json
    
    if ($urlConfig.FunctionUrl) {
        Write-Host "Function URL creee avec succes!" -ForegroundColor Green
        Write-Host "`nInformations:" -ForegroundColor Cyan
        Write-Host "  URL: $($urlConfig.FunctionUrl)" -ForegroundColor White
        Write-Host "  Auth: NONE (public)" -ForegroundColor White
        Write-Host "  CORS: Configure pour mapevent.world" -ForegroundColor White
        Write-Host "`nIMPORTANT: Mettez a jour API_BASE_URL dans le frontend!" -ForegroundColor Yellow
        Write-Host "  Ancien: https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default" -ForegroundColor Gray
        Write-Host "  Nouveau: $($urlConfig.FunctionUrl)" -ForegroundColor Green
    } else {
        Write-Host "Erreur lors de la creation" -ForegroundColor Red
    }
} catch {
    Write-Host "Erreur: $_" -ForegroundColor Red
}
