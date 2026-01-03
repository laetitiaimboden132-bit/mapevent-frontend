# Configuration CORS pour /api/user/oauth/google

$API_ID = "j33osy4bvj"
$RESOURCE_ID = "k70u2t"
$ALLOWED_ORIGIN = "https://mapevent.world"
$STAGE = "default"

Write-Host "Configuration CORS pour /api/user/oauth/google..." -ForegroundColor Cyan

# Verifier si OPTIONS existe
$method = aws apigateway get-method --rest-api-id $API_ID --resource-id $RESOURCE_ID --http-method OPTIONS --region eu-west-1 2>$null

if (-not $method) {
    Write-Host "Creation de la methode OPTIONS..." -ForegroundColor Yellow
    aws apigateway put-method `
        --rest-api-id $API_ID `
        --resource-id $RESOURCE_ID `
        --http-method OPTIONS `
        --authorization-type NONE `
        --region eu-west-1 `
        --no-api-key-required | Out-Null
    Write-Host "OK: Methode OPTIONS creee" -ForegroundColor Green
} else {
    Write-Host "OK: Methode OPTIONS existe deja" -ForegroundColor Green
}

# Configurer Integration Mock
Write-Host "Configuration Integration Mock..." -ForegroundColor Yellow
aws apigateway put-integration `
    --rest-api-id $API_ID `
    --resource-id $RESOURCE_ID `
    --http-method OPTIONS `
    --type MOCK `
    --integration-http-method POST `
    --request-templates '{\"application/json\":\"{\\\"statusCode\\\":200}\"}' `
    --region eu-west-1 | Out-Null

# Configurer Method Response
Write-Host "Configuration Method Response..." -ForegroundColor Yellow
aws apigateway put-method-response `
    --rest-api-id $API_ID `
    --resource-id $RESOURCE_ID `
    --http-method OPTIONS `
    --status-code 200 `
    --response-parameters "method.response.header.Access-Control-Allow-Headers=false,method.response.header.Access-Control-Allow-Methods=false,method.response.header.Access-Control-Allow-Origin=false" `
    --region eu-west-1 | Out-Null

# Configurer Integration Response
Write-Host "Configuration Integration Response..." -ForegroundColor Yellow
$responseParams = "method.response.header.Access-Control-Allow-Headers='Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',method.response.header.Access-Control-Allow-Methods='POST,OPTIONS',method.response.header.Access-Control-Allow-Origin='$ALLOWED_ORIGIN'"

aws apigateway put-integration-response `
    --rest-api-id $API_ID `
    --resource-id $RESOURCE_ID `
    --http-method OPTIONS `
    --status-code 200 `
    --region eu-west-1 `
    --response-parameters $responseParams `
    --response-templates file://response-templates.json | Out-Null

Write-Host "OK: Integration Response configuree" -ForegroundColor Green

# Deployer
Write-Host "Deploiement de l'API..." -ForegroundColor Yellow
$deploymentId = aws apigateway create-deployment --rest-api-id $API_ID --stage-name $STAGE --region eu-west-1 --query 'id' --output text

Write-Host "OK: API deployee (ID: $deploymentId)" -ForegroundColor Green
Write-Host "Testez maintenant la connexion Google" -ForegroundColor Cyan

