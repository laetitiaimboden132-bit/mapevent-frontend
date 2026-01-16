# Script pour corriger l'integration Mock pour OPTIONS
$API_ID = "j33osy4bvj"
$REGION = "eu-west-1"
$RESOURCE_ID = "rjh1m4"

Write-Host "Correction de l'integration Mock pour OPTIONS..." -ForegroundColor Cyan

# Supprimer l'integration existante si elle existe
Write-Host "Suppression de l'integration existante..." -ForegroundColor Yellow
try {
    aws apigateway delete-integration `
        --rest-api-id $API_ID `
        --resource-id $RESOURCE_ID `
        --http-method OPTIONS `
        --region $REGION 2>&1 | Out-Null
    Write-Host "Integration existante supprimee" -ForegroundColor Green
} catch {
    Write-Host "Pas d'integration existante a supprimer" -ForegroundColor Gray
}

# Creer une nouvelle integration Mock simple
Write-Host "Creation de l'integration Mock..." -ForegroundColor Yellow
aws apigateway put-integration `
    --rest-api-id $API_ID `
    --resource-id $RESOURCE_ID `
    --http-method OPTIONS `
    --type MOCK `
    --request-templates '{\"application/json\":\"{\\\"statusCode\\\":200}\"}' `
    --region $REGION 2>&1 | Out-Null

Write-Host "Integration Mock creee" -ForegroundColor Green

# Supprimer et recreer la reponse d'integration
Write-Host "Configuration de la reponse d'integration..." -ForegroundColor Yellow
try {
    aws apigateway delete-integration-response `
        --rest-api-id $API_ID `
        --resource-id $RESOURCE_ID `
        --http-method OPTIONS `
        --status-code 200 `
        --region $REGION 2>&1 | Out-Null
} catch {
    # Ignorer si n'existe pas
}

aws apigateway put-integration-response `
    --rest-api-id $API_ID `
    --resource-id $RESOURCE_ID `
    --http-method OPTIONS `
    --status-code 200 `
    --response-templates '{\"application/json\":\"\"}' `
    --response-parameters '{\"method.response.header.Access-Control-Allow-Origin\":\"'"'"'*'"'"'\",\"method.response.header.Access-Control-Allow-Headers\":\"'"'"'Content-Type,Authorization,Origin,X-Requested-With,Accept'"'"'\",\"method.response.header.Access-Control-Allow-Methods\":\"'"'"'POST,OPTIONS'"'"'\"}' `
    --region $REGION 2>&1 | Out-Null

Write-Host "Reponse d'integration configuree" -ForegroundColor Green

# Deployer
Write-Host "`nDeploiement..." -ForegroundColor Cyan
$deployment = aws apigateway create-deployment `
    --rest-api-id $API_ID `
    --stage-name default `
    --description "Fix CORS OPTIONS Mock integration" `
    --region $REGION 2>&1 | ConvertFrom-Json

Write-Host "Deploiement termine (ID: $($deployment.id))" -ForegroundColor Green
Write-Host "`nAttendez 10 secondes puis testez le formulaire..." -ForegroundColor Yellow









