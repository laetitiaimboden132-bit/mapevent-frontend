# Configurer les methodes OPTIONS pour utiliser AWS_PROXY au lieu de MOCK

$API_ID = "j33osy4bvj"
$STAGE = "default"
$REGION = "eu-west-1"
$LAMBDA_ARN = "arn:aws:lambda:eu-west-1:818127249940:function:mapevent-backend"

Write-Host "Configuration des methodes OPTIONS pour utiliser AWS_PROXY..." -ForegroundColor Cyan

# Endpoints
$endpoints = @{
    "/api/user/oauth/google" = "k70u2t"
    "/api/user/oauth/google/complete" = "rjh1m4"
}

foreach ($endpointPath in $endpoints.Keys) {
    $RESOURCE_ID = $endpoints[$endpointPath]
    
    Write-Host ""
    Write-Host "Configuration: $endpointPath" -ForegroundColor Yellow
    
    # Verifier que OPTIONS existe
    try {
        $method = aws apigateway get-method --rest-api-id $API_ID --resource-id $RESOURCE_ID --http-method OPTIONS --region $REGION | ConvertFrom-Json
        Write-Host "  OK: Methode OPTIONS existe" -ForegroundColor Green
    } catch {
        Write-Host "  Creation de la methode OPTIONS..." -ForegroundColor Yellow
        aws apigateway put-method `
            --rest-api-id $API_ID `
            --resource-id $RESOURCE_ID `
            --http-method OPTIONS `
            --authorization-type NONE `
            --region $REGION `
            --no-api-key-required | Out-Null
    }
    
    # Configurer l'integration AWS_PROXY pour OPTIONS
    Write-Host "  Configuration integration AWS_PROXY..." -ForegroundColor Cyan
    
    aws apigateway put-integration `
        --rest-api-id $API_ID `
        --resource-id $RESOURCE_ID `
        --http-method OPTIONS `
        --type AWS_PROXY `
        --integration-http-method POST `
        --uri "arn:aws:apigateway:$REGION`:lambda:path/2015-03-31/functions/$LAMBDA_ARN/invocations" `
        --region $REGION | Out-Null
    
    Write-Host "  OK: Integration AWS_PROXY configuree" -ForegroundColor Green
    
    # Supprimer les Integration Response existantes (AWS_PROXY n'en a pas besoin)
    try {
        aws apigateway delete-integration-response --rest-api-id $API_ID --resource-id $RESOURCE_ID --http-method OPTIONS --status-code 200 --region $REGION 2>$null
    } catch {}
    
    # Supprimer les Method Response existantes (AWS_PROXY les gere automatiquement)
    try {
        aws apigateway delete-method-response --rest-api-id $API_ID --resource-id $RESOURCE_ID --http-method OPTIONS --status-code 200 --region $REGION 2>$null
    } catch {}
}

# Deployer
Write-Host ""
Write-Host "Deploiement..." -ForegroundColor Cyan
$deploymentId = aws apigateway create-deployment --rest-api-id $API_ID --stage-name $STAGE --region $REGION --query 'id' --output text

Write-Host "OK: Deploye (ID: $deploymentId)" -ForegroundColor Green
Write-Host ""
Write-Host "Les requetes OPTIONS seront maintenant gerees par Lambda qui retourne les headers CORS." -ForegroundColor Green









