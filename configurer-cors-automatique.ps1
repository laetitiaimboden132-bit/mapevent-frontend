# Script automatique pour configurer CORS complet via AWS CLI
# Ce script configure CORS pour OPTIONS et POST sur les deux endpoints

$API_ID = "j33osy4bvj"
$STAGE = "default"
$REGION = "eu-west-1"
$ALLOWED_ORIGIN = "https://mapevent.world"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Configuration CORS automatique complete" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Endpoints a configurer
$endpoints = @{
    "/api/user/oauth/google" = "k70u2t"
    "/api/user/oauth/google/complete" = "rjh1m4"
}

foreach ($endpointPath in $endpoints.Keys) {
    $RESOURCE_ID = $endpoints[$endpointPath]
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host "Configuration: $endpointPath" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Yellow
    
    # ============================================
    # 1. CONFIGURER OPTIONS
    # ============================================
    Write-Host "1. Configuration methode OPTIONS..." -ForegroundColor Cyan
    
    # Verifier/Creer OPTIONS
    try {
        $method = aws apigateway get-method --rest-api-id $API_ID --resource-id $RESOURCE_ID --http-method OPTIONS --region $REGION 2>$null | ConvertFrom-Json
        Write-Host "   OK: OPTIONS existe" -ForegroundColor Green
    } catch {
        Write-Host "   Creation de OPTIONS..." -ForegroundColor Yellow
        aws apigateway put-method `
            --rest-api-id $API_ID `
            --resource-id $RESOURCE_ID `
            --http-method OPTIONS `
            --authorization-type NONE `
            --region $REGION `
            --no-api-key-required | Out-Null
    }
    
    # Configurer Integration Mock
    Write-Host "   Configuration integration Mock..." -ForegroundColor Gray
    $mockTemplate = '{\"application/json\":\"{\\\"statusCode\\\":200}\"}'
    aws apigateway put-integration `
        --rest-api-id $API_ID `
        --resource-id $RESOURCE_ID `
        --http-method OPTIONS `
        --type MOCK `
        --integration-http-method POST `
        --request-templates $mockTemplate `
        --region $REGION | Out-Null
    
    # Method Response pour OPTIONS
    Write-Host "   Configuration Method Response..." -ForegroundColor Gray
    $methodResponseParams = "method.response.header.Access-Control-Allow-Headers=false,method.response.header.Access-Control-Allow-Methods=false,method.response.header.Access-Control-Allow-Origin=false"
    
    try {
        aws apigateway put-method-response `
            --rest-api-id $API_ID `
            --resource-id $RESOURCE_ID `
            --http-method OPTIONS `
            --status-code 200 `
            --response-parameters $methodResponseParams `
            --region $REGION | Out-Null
        Write-Host "   OK: Method Response configuree" -ForegroundColor Green
    } catch {
        Write-Host "   ATTENTION: Method Response deja existe" -ForegroundColor Yellow
    }
    
    # Integration Response pour OPTIONS - Utiliser un fichier JSON temporaire
    Write-Host "   Configuration Integration Response..." -ForegroundColor Gray
    
    # Creer fichier JSON pour Integration Response
    $integrationResponseJson = @{
        statusCode = "200"
        responseParameters = @{
            "method.response.header.Access-Control-Allow-Origin" = "'$ALLOWED_ORIGIN'"
            "method.response.header.Access-Control-Allow-Methods" = "'POST,OPTIONS'"
            "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token'"
        }
        responseTemplates = @{
            "application/json" = ""
        }
    } | ConvertTo-Json -Depth 10 -Compress
    
    $tempFile = "temp-integration-response-$([System.Guid]::NewGuid().ToString('N').Substring(0,8)).json"
    $integrationResponseJson | Out-File -FilePath $tempFile -Encoding UTF8 -NoNewline
    
    try {
        # Essayer avec put-integration-response directement
        $responseParams = "method.response.header.Access-Control-Allow-Origin='$ALLOWED_ORIGIN',method.response.header.Access-Control-Allow-Methods='POST,OPTIONS',method.response.header.Access-Control-Allow-Headers='Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token'"
        $responseTemplates = '{\"application/json\":\"\"}'
        
        aws apigateway put-integration-response `
            --rest-api-id $API_ID `
            --resource-id $RESOURCE_ID `
            --http-method OPTIONS `
            --status-code 200 `
            --region $REGION `
            --response-parameters $responseParams `
            --response-templates $responseTemplates | Out-Null
        
        Write-Host "   OK: Integration Response configuree" -ForegroundColor Green
    } catch {
        Write-Host "   ATTENTION: Erreur Integration Response: $_" -ForegroundColor Yellow
        Write-Host "   Utilisez la console AWS pour configurer manuellement" -ForegroundColor Yellow
    } finally {
        if (Test-Path $tempFile) {
            Remove-Item $tempFile -Force
        }
    }
    
    # ============================================
    # 2. CONFIGURER POST
    # ============================================
    Write-Host ""
    Write-Host "2. Configuration methode POST..." -ForegroundColor Cyan
    
    # Obtenir les codes de statut existants pour POST
    try {
        $postMethod = aws apigateway get-method --rest-api-id $API_ID --resource-id $RESOURCE_ID --http-method POST --region $REGION | ConvertFrom-Json
        
        if ($postMethod.methodResponses) {
            $statusCodes = $postMethod.methodResponses.PSObject.Properties.Name
            
            foreach ($statusCode in $statusCodes) {
                Write-Host "   Configuration reponse $statusCode..." -ForegroundColor Gray
                
                # Method Response - Ajouter header
                try {
                    $methodResp = aws apigateway get-method-response --rest-api-id $API_ID --resource-id $RESOURCE_ID --http-method POST --status-code $statusCode --region $REGION | ConvertFrom-Json
                    
                    $methodParams = @{}
                    if ($methodResp.responseParameters) {
                        $methodResp.responseParameters.PSObject.Properties | ForEach-Object {
                            $methodParams[$_.Name] = $_.Value
                        }
                    }
                    
                    # Ajouter Access-Control-Allow-Origin si pas deja present
                    if (-not $methodParams.ContainsKey("method.response.header.Access-Control-Allow-Origin")) {
                        $methodParams["method.response.header.Access-Control-Allow-Origin"] = "false"
                        
                        $methodParamsString = ($methodParams.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join ","
                        
                        aws apigateway put-method-response `
                            --rest-api-id $API_ID `
                            --resource-id $RESOURCE_ID `
                            --http-method POST `
                            --status-code $statusCode `
                            --response-parameters $methodParamsString `
                            --region $REGION | Out-Null
                        
                        Write-Host "     OK: Method Response $statusCode mise a jour" -ForegroundColor Green
                    } else {
                        Write-Host "     OK: Method Response $statusCode deja configuree" -ForegroundColor Gray
                    }
                } catch {
                    Write-Host "     ATTENTION: Erreur Method Response $statusCode : $_" -ForegroundColor Yellow
                }
                
                # Integration Response - Ajouter mapping
                try {
                    $intResp = aws apigateway get-integration-response --rest-api-id $API_ID --resource-id $RESOURCE_ID --http-method POST --status-code $statusCode --region $REGION | ConvertFrom-Json
                    
                    $intParams = @{}
                    if ($intResp.responseParameters) {
                        $intResp.responseParameters.PSObject.Properties | ForEach-Object {
                            $intParams[$_.Name] = $_.Value
                        }
                    }
                    
                    # Ajouter Access-Control-Allow-Origin si pas deja present
                    if (-not $intParams.ContainsKey("method.response.header.Access-Control-Allow-Origin")) {
                        $intParams["method.response.header.Access-Control-Allow-Origin"] = "'$ALLOWED_ORIGIN'"
                        
                        $intParamsString = ($intParams.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join ","
                        
                        aws apigateway put-integration-response `
                            --rest-api-id $API_ID `
                            --resource-id $RESOURCE_ID `
                            --http-method POST `
                            --status-code $statusCode `
                            --response-parameters $intParamsString `
                            --region $REGION | Out-Null
                        
                        Write-Host "     OK: Integration Response $statusCode mise a jour" -ForegroundColor Green
                    } else {
                        Write-Host "     OK: Integration Response $statusCode deja configuree" -ForegroundColor Gray
                    }
                } catch {
                    Write-Host "     ATTENTION: Erreur Integration Response $statusCode : $_" -ForegroundColor Yellow
                    Write-Host "     (Peut etre normal si le code de statut n'a pas d'Integration Response)" -ForegroundColor Gray
                }
            }
        }
    } catch {
        Write-Host "   ATTENTION: Impossible de recuperer les codes de statut POST: $_" -ForegroundColor Yellow
        Write-Host "   Configuration POST sera faite manuellement dans la console" -ForegroundColor Yellow
    }
}

# ============================================
# 3. DEPLOYER
# ============================================
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
Write-Host ""
Write-Host "Si certaines configurations ont echoue, utilisez la console AWS pour" -ForegroundColor Yellow
Write-Host "les completer manuellement (voir GUIDE_CONFIGURATION_CORS_CONSOLE.md)" -ForegroundColor Yellow
Write-Host ""
Write-Host "Testez maintenant la connexion Google depuis https://mapevent.world" -ForegroundColor Cyan









