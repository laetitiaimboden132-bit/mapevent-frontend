# Script complet pour configurer CORS sur /api/user/oauth/google et /api/user/oauth/google/complete

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Configuration CORS complete pour OAuth Google" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$API_ID = "j33osy4bvj"
$STAGE = "default"
$ALLOWED_ORIGIN = "https://mapevent.world"
$REGION = "eu-west-1"

# Endpoints a configurer
$endpoints = @(
    "/api/user/oauth/google",
    "/api/user/oauth/google/complete"
)

foreach ($endpointPath in $endpoints) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host "Configuration de: $endpointPath" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Yellow
    
    # 1. Trouver le Resource ID
    Write-Host "Recherche du Resource ID..." -ForegroundColor Cyan
    $resourcesJson = aws apigateway get-resources --rest-api-id $API_ID --region $REGION
    $resources = $resourcesJson | ConvertFrom-Json
    
    $targetResource = $null
    foreach ($resource in $resources.items) {
        if ($resource.path -eq $endpointPath) {
            $targetResource = $resource
            break
        }
    }
    
    if (-not $targetResource) {
        Write-Host "ERREUR: Resource non trouve: $endpointPath" -ForegroundColor Red
        Write-Host "Resources disponibles:" -ForegroundColor Yellow
        foreach ($resource in $resources.items) {
            Write-Host "  - $($resource.path)" -ForegroundColor Gray
        }
        continue
    }
    
    $RESOURCE_ID = $targetResource.id
    Write-Host "OK: Resource ID trouve: $RESOURCE_ID" -ForegroundColor Green
    
    # 2. Creer/Verifier la methode OPTIONS
    Write-Host "Configuration de la methode OPTIONS..." -ForegroundColor Cyan
    
    try {
        $existingMethods = aws apigateway get-resource --rest-api-id $API_ID --resource-id $RESOURCE_ID --region $REGION | ConvertFrom-Json
        $hasOptions = $existingMethods.resourceMethods.PSObject.Properties.Name -contains "OPTIONS"
        
        if (-not $hasOptions) {
            Write-Host "Creation de la methode OPTIONS..." -ForegroundColor Yellow
            aws apigateway put-method `
                --rest-api-id $API_ID `
                --resource-id $RESOURCE_ID `
                --http-method OPTIONS `
                --authorization-type NONE `
                --region $REGION `
                --no-api-key-required | Out-Null
            Write-Host "OK: Methode OPTIONS creee" -ForegroundColor Green
        } else {
            Write-Host "OK: Methode OPTIONS existe deja" -ForegroundColor Green
        }
    } catch {
        Write-Host "ATTENTION: Erreur lors de la creation de OPTIONS: $_" -ForegroundColor Yellow
        aws apigateway put-method `
            --rest-api-id $API_ID `
            --resource-id $RESOURCE_ID `
            --http-method OPTIONS `
            --authorization-type NONE `
            --region $REGION `
            --no-api-key-required | Out-Null
    }
    
    # 3. Configurer l'integration Mock pour OPTIONS
    Write-Host "Configuration de l'integration Mock..." -ForegroundColor Cyan
    
    $mockTemplate = '{\"statusCode\":200}'
    
    aws apigateway put-integration `
        --rest-api-id $API_ID `
        --resource-id $RESOURCE_ID `
        --http-method OPTIONS `
        --type MOCK `
        --integration-http-method POST `
        --request-templates "{\"application/json\":$mockTemplate}" `
        --region $REGION | Out-Null
    
    Write-Host "OK: Integration Mock configuree" -ForegroundColor Green
    
    # 4. Configurer Method Response pour OPTIONS
    Write-Host "Configuration Method Response pour OPTIONS..." -ForegroundColor Cyan
    
    try {
        aws apigateway delete-method-response --rest-api-id $API_ID --resource-id $RESOURCE_ID --http-method OPTIONS --status-code 200 --region $REGION 2>$null
    } catch {}
    
    aws apigateway put-method-response `
        --rest-api-id $API_ID `
        --resource-id $RESOURCE_ID `
        --http-method OPTIONS `
        --status-code 200 `
        --response-parameters "method.response.header.Access-Control-Allow-Headers=false,method.response.header.Access-Control-Allow-Methods=false,method.response.header.Access-Control-Allow-Origin=false" `
        --region $REGION | Out-Null
    
    Write-Host "OK: Method Response configuree" -ForegroundColor Green
    
    # 5. Configurer Integration Response pour OPTIONS
    Write-Host "Configuration Integration Response pour OPTIONS..." -ForegroundColor Cyan
    
    # Utiliser un format simple sans guillemets autour de POST,OPTIONS
    $responseParams = "method.response.header.Access-Control-Allow-Headers='Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',method.response.header.Access-Control-Allow-Methods='POST,OPTIONS',method.response.header.Access-Control-Allow-Origin='$ALLOWED_ORIGIN'"
    
    # Creer un fichier JSON temporaire pour response-templates
    $tempTemplates = @"
{"application/json":""}
"@
    $tempFile = "temp-templates-$([System.Guid]::NewGuid().ToString('N').Substring(0,8)).json"
    $tempTemplates | Out-File -FilePath $tempFile -Encoding UTF8 -NoNewline
    
    try {
        aws apigateway put-integration-response `
            --rest-api-id $API_ID `
            --resource-id $RESOURCE_ID `
            --http-method OPTIONS `
            --status-code 200 `
            --region $REGION `
            --response-parameters $responseParams `
            --response-templates "file://$tempFile" | Out-Null
        Write-Host "OK: Integration Response configuree" -ForegroundColor Green
    } catch {
        Write-Host "ATTENTION: Erreur Integration Response: $_" -ForegroundColor Yellow
        Write-Host "Tentative avec format simplifie..." -ForegroundColor Yellow
        
        # Essayer avec un format encore plus simple
        $simpleParams = "method.response.header.Access-Control-Allow-Origin='$ALLOWED_ORIGIN'"
        try {
            aws apigateway put-integration-response `
                --rest-api-id $API_ID `
                --resource-id $RESOURCE_ID `
                --http-method OPTIONS `
                --status-code 200 `
                --region $REGION `
                --response-parameters $simpleParams `
                --response-templates "file://$tempFile" | Out-Null
            Write-Host "OK: Integration Response configuree (format simplifie)" -ForegroundColor Green
        } catch {
            Write-Host "ERREUR: Impossible de configurer Integration Response" -ForegroundColor Red
        }
    } finally {
        if (Test-Path $tempFile) {
            Remove-Item $tempFile -Force
        }
    }
    
    # 6. Ajouter CORS headers a POST si existe
    Write-Host "Ajout des headers CORS a la methode POST..." -ForegroundColor Cyan
    
    try {
        $postMethod = aws apigateway get-method --rest-api-id $API_ID --resource-id $RESOURCE_ID --http-method POST --region $REGION | ConvertFrom-Json
        
        if ($postMethod.methodResponses) {
            $statusCodes = $postMethod.methodResponses.PSObject.Properties.Name
            
            foreach ($statusCode in $statusCodes) {
                Write-Host "  Configuration de la reponse $statusCode..." -ForegroundColor Gray
                
                # Ajouter header a Method Response
                try {
                    $methodResp = aws apigateway get-method-response --rest-api-id $API_ID --resource-id $RESOURCE_ID --http-method POST --status-code $statusCode --region $REGION | ConvertFrom-Json
                    
                    $methodParams = @{}
                    if ($methodResp.responseParameters) {
                        $methodResp.responseParameters.PSObject.Properties | ForEach-Object {
                            $methodParams[$_.Name] = $_.Value
                        }
                    }
                    $methodParams["method.response.header.Access-Control-Allow-Origin"] = "false"
                    
                    $methodParamsString = ($methodParams.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join ","
                    
                    aws apigateway put-method-response `
                        --rest-api-id $API_ID `
                        --resource-id $RESOURCE_ID `
                        --http-method POST `
                        --status-code $statusCode `
                        --response-parameters $methodParamsString `
                        --region $REGION | Out-Null
                } catch {
                    Write-Host "    ATTENTION: Erreur Method Response: $_" -ForegroundColor Yellow
                }
                
                # Ajouter header a Integration Response
                try {
                    $intResp = aws apigateway get-integration-response --rest-api-id $API_ID --resource-id $RESOURCE_ID --http-method POST --status-code $statusCode --region $REGION | ConvertFrom-Json
                    
                    $intParams = @{}
                    if ($intResp.responseParameters) {
                        $intResp.responseParameters.PSObject.Properties | ForEach-Object {
                            $intParams[$_.Name] = $_.Value
                        }
                    }
                    $intParams["method.response.header.Access-Control-Allow-Origin"] = "'$ALLOWED_ORIGIN'"
                    
                    $intParamsString = ($intParams.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join ","
                    
                    aws apigateway put-integration-response `
                        --rest-api-id $API_ID `
                        --resource-id $RESOURCE_ID `
                        --http-method POST `
                        --status-code $statusCode `
                        --response-parameters $intParamsString `
                        --region $REGION | Out-Null
                    
                    Write-Host "    OK: Header CORS ajoute a la reponse $statusCode" -ForegroundColor Green
                } catch {
                    Write-Host "    ATTENTION: Erreur Integration Response: $_" -ForegroundColor Yellow
                }
            }
        }
    } catch {
        Write-Host "ATTENTION: Methode POST non trouvee ou erreur: $_" -ForegroundColor Yellow
    }
}

# 7. Deployer l'API
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Deploiement de l'API..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$deploymentId = aws apigateway create-deployment `
    --rest-api-id $API_ID `
    --stage-name $STAGE `
    --region $REGION `
    --query 'id' `
    --output text

if ($deploymentId) {
    Write-Host "OK: API deployee avec succes (Deployment ID: $deploymentId)" -ForegroundColor Green
} else {
    Write-Host "ERREUR: Echec du deploiement" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Configuration CORS terminee !" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host "Testez maintenant la connexion Google depuis https://mapevent.world" -ForegroundColor Cyan


