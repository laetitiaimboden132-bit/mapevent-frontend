# Configuration CORS finale avec fichiers JSON

$API_ID = "j33osy4bvj"
$STAGE = "default"
$ALLOWED_ORIGIN = "https://mapevent.world"
$REGION = "eu-west-1"

# Creer fichier JSON pour response-templates
$templatesJson = '{"application/json":""}'
$templatesFile = "templates-options.json"
$templatesJson | Out-File -FilePath $templatesFile -Encoding UTF8 -NoNewline

Write-Host "Configuration CORS finale..." -ForegroundColor Cyan

# Endpoints
$endpoints = @{
    "/api/user/oauth/google" = "k70u2t"
    "/api/user/oauth/google/complete" = "rjh1m4"
}

foreach ($endpointPath in $endpoints.Keys) {
    $RESOURCE_ID = $endpoints[$endpointPath]
    
    Write-Host ""
    Write-Host "Configuration: $endpointPath" -ForegroundColor Yellow
    
    # Configurer Integration Response avec seulement Access-Control-Allow-Origin
    $responseParams = "method.response.header.Access-Control-Allow-Origin='$ALLOWED_ORIGIN'"
    
    Write-Host "  Configuration Integration Response OPTIONS..." -ForegroundColor Cyan
    
    try {
        aws apigateway put-integration-response `
            --rest-api-id $API_ID `
            --resource-id $RESOURCE_ID `
            --http-method OPTIONS `
            --status-code 200 `
            --region $REGION `
            --response-parameters $responseParams `
            --response-templates "file://$templatesFile" | Out-Null
        
        Write-Host "    OK: Integration Response configuree" -ForegroundColor Green
    } catch {
        Write-Host "    ERREUR: $_" -ForegroundColor Red
    }
}

# Nettoyer
if (Test-Path $templatesFile) {
    Remove-Item $templatesFile -Force
}

# Deployer
Write-Host ""
Write-Host "Deploiement..." -ForegroundColor Cyan
$deploymentId = aws apigateway create-deployment --rest-api-id $API_ID --stage-name $STAGE --region $REGION --query 'id' --output text

Write-Host "OK: Deploye (ID: $deploymentId)" -ForegroundColor Green
Write-Host ""
Write-Host "IMPORTANT: Les headers Access-Control-Allow-Methods et Access-Control-Allow-Headers" -ForegroundColor Yellow
Write-Host "doivent etre ajoutes manuellement dans la console AWS API Gateway car AWS CLI" -ForegroundColor Yellow
Write-Host "a des problemes avec le format 'POST,OPTIONS'." -ForegroundColor Yellow
Write-Host ""
Write-Host "Pour completer la configuration:" -ForegroundColor Cyan
Write-Host "1. Allez dans AWS API Gateway Console" -ForegroundColor White
Write-Host "2. Pour chaque endpoint (/api/user/oauth/google et /api/user/oauth/google/complete):" -ForegroundColor White
Write-Host "   - Cliquez sur OPTIONS > Integration Response > 200" -ForegroundColor White
Write-Host "   - Ajoutez: method.response.header.Access-Control-Allow-Methods = 'POST,OPTIONS'" -ForegroundColor White
Write-Host "   - Ajoutez: method.response.header.Access-Control-Allow-Headers = 'Content-Type,Authorization'" -ForegroundColor White
Write-Host "3. Deployez l'API" -ForegroundColor White


