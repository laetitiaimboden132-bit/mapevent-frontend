# Script pour corriger l'integration Mock avec une reponse correcte
$API_ID = "j33osy4bvj"
$REGION = "eu-west-1"
$RESOURCE_ID = "rjh1m4"

Write-Host "Correction de l'integration Mock..." -ForegroundColor Cyan

# Supprimer l'integration existante
Write-Host "Suppression de l'integration existante..." -ForegroundColor Yellow
try {
    aws apigateway delete-integration `
        --rest-api-id $API_ID `
        --resource-id $RESOURCE_ID `
        --http-method OPTIONS `
        --region $REGION 2>&1 | Out-Null
    Start-Sleep -Seconds 2
} catch {
    Write-Host "Pas d'integration a supprimer" -ForegroundColor Gray
}

# Creer l'integration Mock avec une reponse correcte
Write-Host "Creation de l'integration Mock..." -ForegroundColor Yellow
aws apigateway put-integration `
    --rest-api-id $API_ID `
    --resource-id $RESOURCE_ID `
    --http-method OPTIONS `
    --type MOCK `
    --request-templates '{\"application/json\":\"{\\\"statusCode\\\":200}\"}' `
    --region $REGION 2>&1 | Out-Null

Write-Host "Integration Mock creee" -ForegroundColor Green

# Configurer la reponse d'integration avec un template de reponse vide
Write-Host "Configuration de la reponse d'integration..." -ForegroundColor Yellow
aws apigateway put-integration-response `
    --rest-api-id $API_ID `
    --resource-id $RESOURCE_ID `
    --http-method OPTIONS `
    --status-code 200 `
    --response-templates '{\"application/json\":\"\"}' `
    --response-parameters '{\"method.response.header.Access-Control-Allow-Origin\":\"'"'"'*'"'"'\",\"method.response.header.Access-Control-Allow-Headers\":\"'"'"'Content-Type,Authorization,Origin,X-Requested-With,Accept'"'"'\",\"method.response.header.Access-Control-Allow-Methods\":\"'"'"'POST,OPTIONS'"'"'\"}' `
    --region $REGION 2>&1 | Out-Null

Write-Host "Reponse d'integration configuree" -ForegroundColor Green

# Verifier que Method Response a les headers
Write-Host "Verification de Method Response..." -ForegroundColor Yellow
try {
    $methodResponse = aws apigateway get-method-response `
        --rest-api-id $API_ID `
        --resource-id $RESOURCE_ID `
        --http-method OPTIONS `
        --status-code 200 `
        --region $REGION 2>&1 | ConvertFrom-Json
    
    if (-not $methodResponse.responseParameters.'method.response.header.Access-Control-Allow-Origin') {
        Write-Host "Ajout des headers dans Method Response..." -ForegroundColor Yellow
        aws apigateway put-method-response `
            --rest-api-id $API_ID `
            --resource-id $RESOURCE_ID `
            --http-method OPTIONS `
            --status-code 200 `
            --response-parameters '{\"method.response.header.Access-Control-Allow-Origin\":true,\"method.response.header.Access-Control-Allow-Headers\":true,\"method.response.header.Access-Control-Allow-Methods\":true}' `
            --region $REGION 2>&1 | Out-Null
        Write-Host "Method Response configuree" -ForegroundColor Green
    } else {
        Write-Host "Method Response deja configuree" -ForegroundColor Green
    }
} catch {
    Write-Host "Erreur lors de la verification: $_" -ForegroundColor Yellow
}

# Deployer
Write-Host "`nDeploiement..." -ForegroundColor Cyan
aws apigateway create-deployment `
    --rest-api-id $API_ID `
    --stage-name default `
    --description "Fix Mock integration for OPTIONS" `
    --region $REGION 2>&1 | Out-Null

Write-Host "Deploiement termine !" -ForegroundColor Green
Write-Host "`nAttendez 10 secondes puis testez..." -ForegroundColor Yellow


