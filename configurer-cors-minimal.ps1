# Configuration CORS minimale - Access-Control-Allow-Origin seulement

$API_ID = "j33osy4bvj"
$STAGE = "default"
$ALLOWED_ORIGIN = "https://mapevent.world"
$REGION = "eu-west-1"

Write-Host "Configuration CORS minimale (Access-Control-Allow-Origin)..." -ForegroundColor Cyan

# Endpoints
$endpoints = @{
    "/api/user/oauth/google" = "k70u2t"
    "/api/user/oauth/google/complete" = "rjh1m4"
}

foreach ($endpointPath in $endpoints.Keys) {
    $RESOURCE_ID = $endpoints[$endpointPath]
    
    Write-Host ""
    Write-Host "Configuration: $endpointPath" -ForegroundColor Yellow
    
    # Configurer seulement Access-Control-Allow-Origin
    $responseParams = "method.response.header.Access-Control-Allow-Origin='$ALLOWED_ORIGIN'"
    $responseTemplates = '{\"application/json\":\"\"}'
    
    Write-Host "  Configuration Integration Response OPTIONS..." -ForegroundColor Cyan
    
    try {
        # Supprimer l'Integration Response existante si elle existe
        try {
            aws apigateway delete-integration-response --rest-api-id $API_ID --resource-id $RESOURCE_ID --http-method OPTIONS --status-code 200 --region $REGION 2>$null
        } catch {}
        
        aws apigateway put-integration-response `
            --rest-api-id $API_ID `
            --resource-id $RESOURCE_ID `
            --http-method OPTIONS `
            --status-code 200 `
            --region $REGION `
            --response-parameters $responseParams `
            --response-templates $responseTemplates | Out-Null
        
        Write-Host "  OK: Integration Response configuree" -ForegroundColor Green
    } catch {
        Write-Host "  ERREUR: $_" -ForegroundColor Red
    }
}

# Deployer
Write-Host ""
Write-Host "Deploiement..." -ForegroundColor Cyan
$deploymentId = aws apigateway create-deployment --rest-api-id $API_ID --stage-name $STAGE --region $REGION --query 'id' --output text

Write-Host "OK: Deploye (ID: $deploymentId)" -ForegroundColor Green
Write-Host ""
Write-Host "NOTE: Access-Control-Allow-Origin est configure." -ForegroundColor Yellow
Write-Host "Pour une configuration CORS complete, ajoutez manuellement dans AWS Console:" -ForegroundColor Yellow
Write-Host "- Access-Control-Allow-Methods: POST,OPTIONS" -ForegroundColor White
Write-Host "- Access-Control-Allow-Headers: Content-Type,Authorization" -ForegroundColor White









