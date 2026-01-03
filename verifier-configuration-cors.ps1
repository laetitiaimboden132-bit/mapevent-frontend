# Script pour verifier la configuration CORS dans API Gateway

$API_ID = "j33osy4bvj"
$STAGE = "default"
$REGION = "eu-west-1"

Write-Host "Verification de la configuration CORS..." -ForegroundColor Cyan

# Endpoints a verifier
$endpoints = @{
    "/api/user/oauth/google" = "k70u2t"
    "/api/user/oauth/google/complete" = "rjh1m4"
}

foreach ($endpointPath in $endpoints.Keys) {
    $RESOURCE_ID = $endpoints[$endpointPath]
    
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Yellow
    Write-Host "Verification: $endpointPath" -ForegroundColor Yellow
    Write-Host "========================================" -ForegroundColor Yellow
    
    # Verifier OPTIONS
    Write-Host "Methode OPTIONS:" -ForegroundColor Cyan
    try {
        $optionsMethod = aws apigateway get-method --rest-api-id $API_ID --resource-id $RESOURCE_ID --http-method OPTIONS --region $REGION | ConvertFrom-Json
        Write-Host "  OK: Methode OPTIONS existe" -ForegroundColor Green
        
        # Verifier Method Response
        $optionsMethodResp = aws apigateway get-method-response --rest-api-id $API_ID --resource-id $RESOURCE_ID --http-method OPTIONS --status-code 200 --region $REGION | ConvertFrom-Json
        Write-Host "  Method Response 200:" -ForegroundColor Gray
        if ($optionsMethodResp.responseParameters) {
            foreach ($header in $optionsMethodResp.responseParameters.PSObject.Properties.Name) {
                Write-Host "    - $header" -ForegroundColor Green
            }
        } else {
            Write-Host "    Aucun header trouve" -ForegroundColor Red
        }
        
        # Verifier Integration Response
        $optionsIntResp = aws apigateway get-integration-response --rest-api-id $API_ID --resource-id $RESOURCE_ID --http-method OPTIONS --status-code 200 --region $REGION | ConvertFrom-Json
        Write-Host "  Integration Response 200:" -ForegroundColor Gray
        if ($optionsIntResp.responseParameters) {
            foreach ($header in $optionsIntResp.responseParameters.PSObject.Properties.Name) {
                $value = $optionsIntResp.responseParameters.$header
                Write-Host "    - $header = $value" -ForegroundColor Green
            }
        } else {
            Write-Host "    Aucun mapping trouve" -ForegroundColor Red
        }
        
    } catch {
        Write-Host "  ERREUR: $_" -ForegroundColor Red
    }
    
    # Verifier POST
    Write-Host ""
    Write-Host "Methode POST:" -ForegroundColor Cyan
    try {
        $postMethod = aws apigateway get-method --rest-api-id $API_ID --resource-id $RESOURCE_ID --http-method POST --region $REGION | ConvertFrom-Json
        Write-Host "  OK: Methode POST existe" -ForegroundColor Green
        
        # Verifier les codes de statut
        if ($postMethod.methodResponses) {
            $statusCodes = $postMethod.methodResponses.PSObject.Properties.Name
            Write-Host "  Codes de statut trouves: $($statusCodes -join ', ')" -ForegroundColor Gray
            
            foreach ($statusCode in $statusCodes) {
                Write-Host "  Status $statusCode:" -ForegroundColor Gray
                try {
                    $methodResp = aws apigateway get-method-response --rest-api-id $API_ID --resource-id $RESOURCE_ID --http-method POST --status-code $statusCode --region $REGION | ConvertFrom-Json
                    if ($methodResp.responseParameters -and $methodResp.responseParameters.'method.response.header.Access-Control-Allow-Origin') {
                        Write-Host "    Method Response: Access-Control-Allow-Origin present" -ForegroundColor Green
                    } else {
                        Write-Host "    Method Response: Access-Control-Allow-Origin MANQUANT" -ForegroundColor Red
                    }
                    
                    $intResp = aws apigateway get-integration-response --rest-api-id $API_ID --resource-id $RESOURCE_ID --http-method POST --status-code $statusCode --region $REGION | ConvertFrom-Json
                    if ($intResp.responseParameters -and $intResp.responseParameters.'method.response.header.Access-Control-Allow-Origin') {
                        $value = $intResp.responseParameters.'method.response.header.Access-Control-Allow-Origin'
                        Write-Host "    Integration Response: Access-Control-Allow-Origin = $value" -ForegroundColor Green
                    } else {
                        Write-Host "    Integration Response: Access-Control-Allow-Origin MANQUANT" -ForegroundColor Red
                    }
                } catch {
                    Write-Host "    ERREUR: $_" -ForegroundColor Red
                }
            }
        }
        
    } catch {
        Write-Host "  ERREUR: $_" -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "Verification terminee!" -ForegroundColor Cyan

