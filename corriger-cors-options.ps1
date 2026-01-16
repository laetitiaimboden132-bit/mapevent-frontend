# Script pour corriger l'integration OPTIONS
$API_ID = "j33osy4bvj"
$REGION = "eu-west-1"
$RESOURCE_ID = "rjh1m4"  # ID trouve par le script precedent

Write-Host "Correction de l'integration OPTIONS..." -ForegroundColor Cyan

# Verifier si OPTIONS existe
Write-Host "Verification de la methode OPTIONS..." -ForegroundColor Yellow
try {
    $method = aws apigateway get-method `
        --rest-api-id $API_ID `
        --resource-id $RESOURCE_ID `
        --http-method OPTIONS `
        --region $REGION 2>&1 | ConvertFrom-Json
    
    Write-Host "Methode OPTIONS trouvee" -ForegroundColor Green
} catch {
    Write-Host "Creation de la methode OPTIONS..." -ForegroundColor Yellow
    aws apigateway put-method `
        --rest-api-id $API_ID `
        --resource-id $RESOURCE_ID `
        --http-method OPTIONS `
        --authorization-type NONE `
        --region $REGION 2>&1 | Out-Null
    Write-Host "Methode OPTIONS creee" -ForegroundColor Green
}

# Configurer l'integration Mock
Write-Host "Configuration de l'integration Mock..." -ForegroundColor Yellow
aws apigateway put-integration `
    --rest-api-id $API_ID `
    --resource-id $RESOURCE_ID `
    --http-method OPTIONS `
    --type MOCK `
    --request-templates '{\"application/json\":\"{\\\"statusCode\\\":200}\"}' `
    --region $REGION 2>&1 | Out-Null

Write-Host "Integration Mock configuree" -ForegroundColor Green

# Configurer la reponse de methode
Write-Host "Configuration de la reponse de methode..." -ForegroundColor Yellow
aws apigateway put-method-response `
    --rest-api-id $API_ID `
    --resource-id $RESOURCE_ID `
    --http-method OPTIONS `
    --status-code 200 `
    --response-parameters '{\"method.response.header.Access-Control-Allow-Origin\":true,\"method.response.header.Access-Control-Allow-Headers\":true,\"method.response.header.Access-Control-Allow-Methods\":true}' `
    --region $REGION 2>&1 | Out-Null

Write-Host "Reponse de methode configuree" -ForegroundColor Green

# Configurer la reponse d'integration
Write-Host "Configuration de la reponse d'integration..." -ForegroundColor Yellow
aws apigateway put-integration-response `
    --rest-api-id $API_ID `
    --resource-id $RESOURCE_ID `
    --http-method OPTIONS `
    --status-code 200 `
    --response-parameters '{\"method.response.header.Access-Control-Allow-Origin\":\"'"'"'*'"'"'\",\"method.response.header.Access-Control-Allow-Headers\":\"'"'"'Content-Type,Authorization,Origin,X-Requested-With,Accept'"'"'\",\"method.response.header.Access-Control-Allow-Methods\":\"'"'"'POST,OPTIONS'"'"'\"}' `
    --region $REGION 2>&1 | Out-Null

Write-Host "Reponse d'integration configuree" -ForegroundColor Green

# Deployer
Write-Host "`nDeploiement de l'API..." -ForegroundColor Cyan
aws apigateway create-deployment `
    --rest-api-id $API_ID `
    --stage-name default `
    --description "CORS OPTIONS configuration" `
    --region $REGION 2>&1 | ConvertFrom-Json | Out-Null

Write-Host "Deploiement termine !" -ForegroundColor Green
Write-Host "`nTestez maintenant le formulaire sur https://mapevent.world" -ForegroundColor Cyan









