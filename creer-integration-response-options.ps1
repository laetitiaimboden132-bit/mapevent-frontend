# Creer Integration Response pour OPTIONS

$API_ID = "j33osy4bvj"
$RESOURCE_ID = "rjh1m4"
$ALLOWED_ORIGIN = "https://mapevent.world"

$responseParams = "method.response.header.Access-Control-Allow-Headers='Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',method.response.header.Access-Control-Allow-Methods='POST,OPTIONS',method.response.header.Access-Control-Allow-Origin='$ALLOWED_ORIGIN'"

$responseTemplates = '{\"application/json\":\"\"}'

Write-Host "Creation Integration Response pour OPTIONS..." -ForegroundColor Cyan
Write-Host "Parametres: $responseParams" -ForegroundColor Yellow

aws apigateway put-integration-response `
    --rest-api-id $API_ID `
    --resource-id $RESOURCE_ID `
    --http-method OPTIONS `
    --status-code 200 `
    --region eu-west-1 `
    --response-parameters $responseParams `
    --response-templates $responseTemplates

Write-Host "OK: Integration Response creee" -ForegroundColor Green

# Deployer
$deploymentId = aws apigateway create-deployment --rest-api-id $API_ID --stage-name default --region eu-west-1 --query 'id' --output text

Write-Host "OK: API deployee (ID: $deploymentId)" -ForegroundColor Green


