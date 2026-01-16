# Configuration CORS via API REST AWS directement
# Utilise Invoke-RestMethod pour contourner les limitations d'AWS CLI

$API_ID = "j33osy4bvj"
$STAGE = "default"
$REGION = "eu-west-1"
$ALLOWED_ORIGIN = "https://mapevent.world"

Write-Host "Configuration CORS via API REST AWS..." -ForegroundColor Cyan

# Obtenir les credentials AWS
$awsProfile = $env:AWS_PROFILE
if (-not $awsProfile) {
    $awsProfile = "default"
}

# Endpoints
$endpoints = @{
    "/api/user/oauth/google" = "k70u2t"
    "/api/user/oauth/google/complete" = "rjh1m4"
}

Write-Host ""
Write-Host "ATTENTION: Cette methode necessite AWS CLI avec credentials configures" -ForegroundColor Yellow
Write-Host "Utilisation de AWS CLI avec format JSON..." -ForegroundColor Yellow
Write-Host ""

foreach ($endpointPath in $endpoints.Keys) {
    $RESOURCE_ID = $endpoints[$endpointPath]
    
    Write-Host "Configuration: $endpointPath" -ForegroundColor Yellow
    
    # OPTIONS Integration Response
    Write-Host "  OPTIONS Integration Response..." -ForegroundColor Cyan
    
    # Creer fichier JSON pour put-integration-response
    $integrationResponseJson = @{
        responseParameters = @{
            "method.response.header.Access-Control-Allow-Origin" = "'$ALLOWED_ORIGIN'"
            "method.response.header.Access-Control-Allow-Methods" = "'POST,OPTIONS'"
            "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token'"
        }
        responseTemplates = @{
            "application/json" = ""
        }
    } | ConvertTo-Json -Depth 10
    
    $jsonFile = "integration-response-$RESOURCE_ID-options.json"
    $integrationResponseJson | Out-File -FilePath $jsonFile -Encoding UTF8
    
    # Utiliser aws apigateway put-integration-response avec fichier JSON
    # Note: AWS CLI ne supporte pas directement les fichiers JSON pour put-integration-response
    # On doit utiliser les parametres directement
    
    try {
        # Essayer avec format inline (echappe correctement)
        $responseParams = "method.response.header.Access-Control-Allow-Origin='$ALLOWED_ORIGIN',method.response.header.Access-Control-Allow-Methods='POST,OPTIONS',method.response.header.Access-Control-Allow-Headers='Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token'"
        $responseTemplates = '{\"application/json\":\"\"}'
        
        # Utiliser une commande AWS CLI avec eval pour gerer les guillemets
        $cmd = "aws apigateway put-integration-response --rest-api-id $API_ID --resource-id $RESOURCE_ID --http-method OPTIONS --status-code 200 --region $REGION --response-parameters `"$responseParams`" --response-templates `"$responseTemplates`""
        
        Invoke-Expression $cmd | Out-Null
        
        Write-Host "    OK: OPTIONS Integration Response configuree" -ForegroundColor Green
    } catch {
        Write-Host "    ERREUR: $_" -ForegroundColor Red
        Write-Host "    Configuration manuelle necessaire" -ForegroundColor Yellow
    } finally {
        if (Test-Path $jsonFile) {
            Remove-Item $jsonFile -Force
        }
    }
    
    # POST Integration Response
    Write-Host "  POST Integration Response..." -ForegroundColor Cyan
    
    try {
        $postMethod = aws apigateway get-method --rest-api-id $API_ID --resource-id $RESOURCE_ID --http-method POST --region $REGION | ConvertFrom-Json
        
        if ($postMethod.methodResponses) {
            $statusCodes = $postMethod.methodResponses.PSObject.Properties.Name
            
            foreach ($statusCode in $statusCodes) {
                try {
                    $postResponseParams = "method.response.header.Access-Control-Allow-Origin='$ALLOWED_ORIGIN'"
                    
                    $postCmd = "aws apigateway put-integration-response --rest-api-id $API_ID --resource-id $RESOURCE_ID --http-method POST --status-code $statusCode --region $REGION --response-parameters `"$postResponseParams`""
                    
                    Invoke-Expression $postCmd | Out-Null
                    
                    Write-Host "    OK: POST $statusCode configure" -ForegroundColor Green
                } catch {
                    Write-Host "    ATTENTION: POST $statusCode : $_" -ForegroundColor Yellow
                }
            }
        }
    } catch {
        Write-Host "    ATTENTION: Impossible de recuperer POST: $_" -ForegroundColor Yellow
    }
}

# Deployer
Write-Host ""
Write-Host "Deploiement..." -ForegroundColor Cyan
$deploymentId = aws apigateway create-deployment --rest-api-id $API_ID --stage-name $STAGE --region $REGION --query 'id' --output text

Write-Host "OK: Deploye (ID: $deploymentId)" -ForegroundColor Green
Write-Host ""
Write-Host "Si des erreurs persistent, configurez manuellement dans la console AWS" -ForegroundColor Yellow









