# Script simplifie pour configurer CORS - Utilise la console AWS ou corrige les erreurs

$API_ID = "j33osy4bvj"
$STAGE = "default"
$ALLOWED_ORIGIN = "https://mapevent.world"
$REGION = "eu-west-1"

Write-Host "Configuration CORS pour les endpoints OAuth Google..." -ForegroundColor Cyan

# Endpoints
$endpoints = @{
    "/api/user/oauth/google" = "k70u2t"
    "/api/user/oauth/google/complete" = "rjh1m4"
}

foreach ($endpointPath in $endpoints.Keys) {
    $RESOURCE_ID = $endpoints[$endpointPath]
    
    Write-Host ""
    Write-Host "Configuration de: $endpointPath (Resource ID: $RESOURCE_ID)" -ForegroundColor Yellow
    
    # 1. Verifier/Creer OPTIONS
    Write-Host "  Verification methode OPTIONS..." -ForegroundColor Cyan
    try {
        $method = aws apigateway get-method --rest-api-id $API_ID --resource-id $RESOURCE_ID --http-method OPTIONS --region $REGION 2>$null | ConvertFrom-Json
        Write-Host "    OK: OPTIONS existe" -ForegroundColor Green
    } catch {
        Write-Host "    Creation de OPTIONS..." -ForegroundColor Yellow
        aws apigateway put-method `
            --rest-api-id $API_ID `
            --resource-id $RESOURCE_ID `
            --http-method OPTIONS `
            --authorization-type NONE `
            --region $REGION `
            --no-api-key-required | Out-Null
    }
    
    # 2. Configurer Integration Mock
    Write-Host "  Configuration integration Mock..." -ForegroundColor Cyan
    $mockJson = '{\"application/json\":\"{\\\"statusCode\\\":200}\"}'
    
    aws apigateway put-integration `
        --rest-api-id $API_ID `
        --resource-id $RESOURCE_ID `
        --http-method OPTIONS `
        --type MOCK `
        --integration-http-method POST `
        --request-templates $mockJson `
        --region $REGION | Out-Null
    
    Write-Host "    OK: Integration Mock configuree" -ForegroundColor Green
    
    # 3. Configurer Method Response
    Write-Host "  Configuration Method Response..." -ForegroundColor Cyan
    aws apigateway put-method-response `
        --rest-api-id $API_ID `
        --resource-id $RESOURCE_ID `
        --http-method OPTIONS `
        --status-code 200 `
        --response-parameters "method.response.header.Access-Control-Allow-Headers=false,method.response.header.Access-Control-Allow-Methods=false,method.response.header.Access-Control-Allow-Origin=false" `
        --region $REGION | Out-Null
    
    Write-Host "    OK: Method Response configuree" -ForegroundColor Green
    
    # 4. Configurer Integration Response - Format simple
    Write-Host "  Configuration Integration Response..." -ForegroundColor Cyan
    
    # Essayer avec un format simple d'abord
    $simpleParams = "method.response.header.Access-Control-Allow-Origin='$ALLOWED_ORIGIN',method.response.header.Access-Control-Allow-Methods='POST,OPTIONS',method.response.header.Access-Control-Allow-Headers='Content-Type,Authorization'"
    
    try {
        aws apigateway put-integration-response `
            --rest-api-id $API_ID `
            --resource-id $RESOURCE_ID `
            --http-method OPTIONS `
            --status-code 200 `
            --response-parameters $simpleParams `
            --region $REGION | Out-Null
        Write-Host "    OK: Integration Response configuree" -ForegroundColor Green
    } catch {
        Write-Host "    ATTENTION: Erreur avec format complet, essai format minimal..." -ForegroundColor Yellow
        $minimalParams = "method.response.header.Access-Control-Allow-Origin='$ALLOWED_ORIGIN'"
        try {
            aws apigateway put-integration-response `
                --rest-api-id $API_ID `
                --resource-id $RESOURCE_ID `
                --http-method OPTIONS `
                --status-code 200 `
                --response-parameters $minimalParams `
                --region $REGION | Out-Null
            Write-Host "    OK: Integration Response configuree (format minimal)" -ForegroundColor Green
        } catch {
            Write-Host "    ERREUR: Impossible de configurer Integration Response: $_" -ForegroundColor Red
        }
    }
}

# Deployer
Write-Host ""
Write-Host "Deploiement de l'API..." -ForegroundColor Cyan
$deploymentId = aws apigateway create-deployment --rest-api-id $API_ID --stage-name $STAGE --region $REGION --query 'id' --output text

Write-Host "OK: API deployee (ID: $deploymentId)" -ForegroundColor Green
Write-Host ""
Write-Host "Configuration terminee ! Testez maintenant." -ForegroundColor Green









