# Script pour créer un endpoint Lambda temporaire pour lister et supprimer les comptes
# Utilise Lambda Function URL (directement accessible sans API Gateway)

$functionName = "mapevent-backend"
$region = "eu-west-1"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "CREATION D'UN ENDPOINT TEMPORAIRE" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier si Function URL existe déjà
Write-Host "Verification de l'existence d'une Function URL..." -ForegroundColor Yellow
try {
    $existingUrl = aws lambda get-function-url-config --function-name $functionName --region $region 2>&1
    if ($LASTEXITCODE -eq 0) {
        $urlConfig = $existingUrl | ConvertFrom-Json
        Write-Host "Function URL existe deja:" -ForegroundColor Green
        Write-Host "  URL: $($urlConfig.FunctionUrl)" -ForegroundColor White
        Write-Host ""
        Write-Host "Vous pouvez utiliser cette URL pour appeler Lambda directement!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Exemple:" -ForegroundColor Yellow
        Write-Host "  $($urlConfig.FunctionUrl)api/admin/list-users" -ForegroundColor Gray
        exit 0
    }
} catch {
    Write-Host "Aucune Function URL trouvee. Creation..." -ForegroundColor Yellow
}

# Créer Function URL
Write-Host "Creation d'une Function URL..." -ForegroundColor Yellow
try {
    $corsJson = '{"AllowOrigins":["*"],"AllowMethods":["GET","POST","PUT","DELETE","OPTIONS"],"AllowHeaders":["Content-Type","Authorization","Origin","X-Requested-With","Accept"],"MaxAge":3600}'
    $urlConfig = aws lambda create-function-url-config --function-name $functionName --auth-type NONE --cors $corsJson --region $region 2>&1 | ConvertFrom-Json
    
    if ($urlConfig.FunctionUrl) {
        Write-Host ""
        Write-Host "Function URL creee avec succes!" -ForegroundColor Green
        Write-Host ""
        Write-Host "URL: $($urlConfig.FunctionUrl)" -ForegroundColor White
        Write-Host ""
        Write-Host "Maintenant, vous pouvez utiliser cette URL pour appeler Lambda directement!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Exemple:" -ForegroundColor Yellow
        Write-Host "  $($urlConfig.FunctionUrl)api/admin/list-users" -ForegroundColor Gray
        Write-Host ""
        
        # Sauvegarder l'URL dans un fichier
        $urlConfig.FunctionUrl | Out-File -FilePath "lambda-function-url.txt" -Encoding UTF8
        Write-Host "URL sauvegardee dans: lambda-function-url.txt" -ForegroundColor Gray
    } else {
        Write-Host "ERREUR: Impossible de creer la Function URL" -ForegroundColor Red
    }
} catch {
    Write-Host "ERREUR lors de la creation:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "Peut-etre que Lambda Function URLs ne sont pas disponibles pour cette fonction." -ForegroundColor Yellow
    Write-Host "Essayez d'activer Function URL manuellement dans AWS Console:" -ForegroundColor Yellow
    Write-Host "  1. Lambda > $functionName > Configuration > Function URL" -ForegroundColor White
    Write-Host "  2. Cliquez sur 'Create function URL'" -ForegroundColor White
    Write-Host "  3. Auth type: NONE" -ForegroundColor White
    Write-Host "  4. Configure CORS si necessaire" -ForegroundColor White
    Write-Host "  5. Cliquez sur 'Save'" -ForegroundColor White
}

