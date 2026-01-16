# Script pour ajouter les headers CORS a POST
$API_ID = "j33osy4bvj"
$REGION = "eu-west-1"
$RESOURCE_ID = "rjh1m4"

Write-Host "Ajout des headers CORS a POST..." -ForegroundColor Cyan

# Verifier si POST existe
try {
    $postMethod = aws apigateway get-method `
        --rest-api-id $API_ID `
        --resource-id $RESOURCE_ID `
        --http-method POST `
        --region $REGION 2>&1 | ConvertFrom-Json
    
    Write-Host "Methode POST trouvee" -ForegroundColor Green
    
    # Ajouter les headers dans Method Response (200)
    Write-Host "Ajout des headers dans Method Response..." -ForegroundColor Yellow
    
    # Recuperer les parametres existants
    $existingParams = @{}
    if ($postMethod.methodResponses.'200'.responseParameters) {
        foreach ($key in $postMethod.methodResponses.'200'.responseParameters.PSObject.Properties.Name) {
            $existingParams[$key] = $postMethod.methodResponses.'200'.responseParameters.$key
        }
    }
    
    # Ajouter les headers CORS
    $existingParams['method.response.header.Access-Control-Allow-Origin'] = $true
    $existingParams['method.response.header.Access-Control-Allow-Headers'] = $true
    $existingParams['method.response.header.Access-Control-Allow-Methods'] = $true
    
    # Convertir en JSON
    $paramsJson = ($existingParams.GetEnumerator() | ForEach-Object { """$($_.Key)"":$($_.Value.ToString().ToLower())" }) -join ","
    $paramsJson = "{$paramsJson}"
    
    aws apigateway put-method-response `
        --rest-api-id $API_ID `
        --resource-id $RESOURCE_ID `
        --http-method POST `
        --status-code 200 `
        --response-parameters $paramsJson `
        --region $REGION 2>&1 | Out-Null
    
    Write-Host "Method Response configuree" -ForegroundColor Green
    
    # Ajouter les headers dans Integration Response
    Write-Host "Ajout des headers dans Integration Response..." -ForegroundColor Yellow
    
    try {
        $intResponse = aws apigateway get-integration-response `
            --rest-api-id $API_ID `
            --resource-id $RESOURCE_ID `
            --http-method POST `
            --status-code 200 `
            --region $REGION 2>&1 | ConvertFrom-Json
        
        $existingIntParams = @{}
        if ($intResponse.responseParameters) {
            foreach ($key in $intResponse.responseParameters.PSObject.Properties.Name) {
                $existingIntParams[$key] = $intResponse.responseParameters.$key
            }
        }
        
        # Ajouter les headers CORS
        $existingIntParams['method.response.header.Access-Control-Allow-Origin'] = "'*'"
        $existingIntParams['method.response.header.Access-Control-Allow-Headers'] = "'Content-Type,Authorization,Origin,X-Requested-With,Accept'"
        $existingIntParams['method.response.header.Access-Control-Allow-Methods'] = "'POST,OPTIONS'"
        
        # Convertir en JSON
        $intParamsJson = ($existingIntParams.GetEnumerator() | ForEach-Object { """$($_.Key)"":""$($_.Value)""" }) -join ","
        $intParamsJson = "{$intParamsJson}"
        
        aws apigateway put-integration-response `
            --rest-api-id $API_ID `
            --resource-id $RESOURCE_ID `
            --http-method POST `
            --status-code 200 `
            --response-parameters $intParamsJson `
            --region $REGION 2>&1 | Out-Null
        
        Write-Host "Integration Response configuree" -ForegroundColor Green
    } catch {
        Write-Host "Erreur lors de la configuration Integration Response: $_" -ForegroundColor Yellow
        Write-Host "Vous devrez peut-etre le faire manuellement dans la console AWS" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host "Methode POST non trouvee ou erreur: $_" -ForegroundColor Red
    Write-Host "Assurez-vous que POST existe sur cette ressource" -ForegroundColor Yellow
    exit 1
}

# Deployer
Write-Host "`nDeploiement..." -ForegroundColor Cyan
aws apigateway create-deployment `
    --rest-api-id $API_ID `
    --stage-name default `
    --description "Add CORS headers to POST" `
    --region $REGION 2>&1 | Out-Null

Write-Host "Deploiement termine !" -ForegroundColor Green









