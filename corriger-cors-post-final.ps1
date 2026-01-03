# Script pour corriger CORS sur la methode POST de /api/user/oauth/google/complete

$API_ID = "j33osy4bvj"
$RESOURCE_ID = "rjh1m4"
$ALLOWED_ORIGIN = "https://mapevent.world"
$STAGE = "default"

Write-Host "Correction CORS pour POST..." -ForegroundColor Cyan

# Recuperer la reponse d'integration existante pour POST 200
$integrationResponse = aws apigateway get-integration-response --rest-api-id $API_ID --resource-id $RESOURCE_ID --http-method POST --status-code 200 --region eu-west-1 | ConvertFrom-Json

# Construire les nouveaux response-parameters
$existingParams = @{}
if ($integrationResponse.responseParameters) {
    $integrationResponse.responseParameters.PSObject.Properties | ForEach-Object {
        $existingParams[$_.Name] = $_.Value
    }
}
$existingParams["method.response.header.Access-Control-Allow-Origin"] = "'$ALLOWED_ORIGIN'"

# Convertir en format AWS CLI
$paramsString = ($existingParams.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join ","

Write-Host "Parametres: $paramsString" -ForegroundColor Yellow

# Mettre a jour Integration Response
aws apigateway put-integration-response `
    --rest-api-id $API_ID `
    --resource-id $RESOURCE_ID `
    --http-method POST `
    --status-code 200 `
    --response-parameters $paramsString `
    --region eu-west-1 | Out-Null

Write-Host "OK: Integration Response mise a jour" -ForegroundColor Green

# Verifier que Method Response a le header
$methodResponse = aws apigateway get-method-response --rest-api-id $API_ID --resource-id $RESOURCE_ID --http-method POST --status-code 200 --region eu-west-1 | ConvertFrom-Json

$methodParams = @{}
if ($methodResponse.responseParameters) {
    $methodResponse.responseParameters.PSObject.Properties | ForEach-Object {
        $methodParams[$_.Name] = $_.Value
    }
}
$methodParams["method.response.header.Access-Control-Allow-Origin"] = "false"

$methodParamsString = ($methodParams.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join ","

aws apigateway put-method-response `
    --rest-api-id $API_ID `
    --resource-id $RESOURCE_ID `
    --http-method POST `
    --status-code 200 `
    --response-parameters $methodParamsString `
    --region eu-west-1 | Out-Null

Write-Host "OK: Method Response mise a jour" -ForegroundColor Green

# Deployer
$deploymentId = aws apigateway create-deployment --rest-api-id $API_ID --stage-name $STAGE --region eu-west-1 --query 'id' --output text

Write-Host "OK: API deployee (ID: $deploymentId)" -ForegroundColor Green
Write-Host "Testez maintenant la creation de compte" -ForegroundColor Cyan
