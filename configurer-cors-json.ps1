# Configuration CORS avec fichiers JSON

$API_ID = "j33osy4bvj"
$STAGE = "default"
$REGION = "eu-west-1"

Write-Host "Configuration CORS avec fichiers JSON..." -ForegroundColor Cyan

# Endpoints
$endpoints = @{
    "/api/user/oauth/google" = "k70u2t"
    "/api/user/oauth/google/complete" = "rjh1m4"
}

foreach ($endpointPath in $endpoints.Keys) {
    $RESOURCE_ID = $endpoints[$endpointPath]
    
    Write-Host ""
    Write-Host "Configuration: $endpointPath" -ForegroundColor Yellow
    
    # Lire le fichier JSON
    $jsonConfig = Get-Content "integration-response-options.json" -Raw | ConvertFrom-Json
    
    # Convertir responseParameters en format AWS CLI
    $paramsArray = @()
    foreach ($key in $jsonConfig.responseParameters.PSObject.Properties.Name) {
        $value = $jsonConfig.responseParameters.$key
        $paramsArray += "$key=$value"
    }
    $paramsString = $paramsArray -join ","
    
    # Convertir responseTemplates en format AWS CLI
    $templatesString = ($jsonConfig.responseTemplates | ConvertTo-Json -Compress).Replace('"', '\"')
    
    Write-Host "  Parametres: $paramsString" -ForegroundColor Gray
    
    try {
        aws apigateway put-integration-response `
            --rest-api-id $API_ID `
            --resource-id $RESOURCE_ID `
            --http-method OPTIONS `
            --status-code 200 `
            --region $REGION `
            --response-parameters $paramsString `
            --response-templates $templatesString | Out-Null
        
        Write-Host "  OK: Integration Response configuree" -ForegroundColor Green
    } catch {
        Write-Host "  ERREUR: $_" -ForegroundColor Red
        
        # Essayer avec seulement Access-Control-Allow-Origin
        Write-Host "  Essai avec format minimal..." -ForegroundColor Yellow
        try {
            aws apigateway put-integration-response `
                --rest-api-id $API_ID `
                --resource-id $RESOURCE_ID `
                --http-method OPTIONS `
                --status-code 200 `
                --region $REGION `
                --response-parameters "method.response.header.Access-Control-Allow-Origin='https://mapevent.world'" `
                --response-templates $templatesString | Out-Null
            Write-Host "  OK: Integration Response configuree (minimal)" -ForegroundColor Green
        } catch {
            Write-Host "  ERREUR: Impossible de configurer: $_" -ForegroundColor Red
        }
    }
}

# Deployer
Write-Host ""
Write-Host "Deploiement..." -ForegroundColor Cyan
$deploymentId = aws apigateway create-deployment --rest-api-id $API_ID --stage-name $STAGE --region $REGION --query 'id' --output text

Write-Host "OK: Deploye (ID: $deploymentId)" -ForegroundColor Green









