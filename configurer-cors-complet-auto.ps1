# Script automatique complet pour configurer CORS via AWS CLI
# Utilise l'API REST directement pour éviter les problèmes de format

$API_ID = "j33osy4bvj"
$STAGE = "default"
$REGION = "eu-west-1"
$ALLOWED_ORIGIN = "https://mapevent.world"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Configuration CORS automatique COMPLETE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# Endpoints
$endpoints = @{
    "/api/user/oauth/google" = "k70u2t"
    "/api/user/oauth/google/complete" = "rjh1m4"
}

foreach ($endpointPath in $endpoints.Keys) {
    $RESOURCE_ID = $endpoints[$endpointPath]
    
    Write-Host ""
    Write-Host "Configuration: $endpointPath" -ForegroundColor Yellow
    
    # ============================================
    # OPTIONS - Integration Response avec patch JSON
    # ============================================
    Write-Host "  Configuration OPTIONS Integration Response..." -ForegroundColor Cyan
    
    # Creer un fichier patch JSON pour Integration Response
    $patchJson = @"
[
  {
    "op": "replace",
    "path": "/responseParameters/method.response.header.Access-Control-Allow-Origin",
    "value": "'$ALLOWED_ORIGIN'"
  },
  {
    "op": "replace",
    "path": "/responseParameters/method.response.header.Access-Control-Allow-Methods",
    "value": "'POST,OPTIONS'"
  },
  {
    "op": "replace",
    "path": "/responseParameters/method.response.header.Access-Control-Allow-Headers",
    "value": "'Content-Type,Authorization,X-Amz-Date,X-Api-Key,X-Amz-Security-Token'"
  },
  {
    "op": "replace",
    "path": "/responseTemplates/application~1json",
    "value": ""
  }
]
"@
    
    $patchFile = "patch-options-$RESOURCE_ID.json"
    $patchJson | Out-File -FilePath $patchFile -Encoding UTF8 -NoNewline
    
    try {
        # Essayer avec update-integration-response
        aws apigateway update-integration-response `
            --rest-api-id $API_ID `
            --resource-id $RESOURCE_ID `
            --http-method OPTIONS `
            --status-code 200 `
            --region $REGION `
            --patch-ops file://$patchFile | Out-Null
        
        Write-Host "    OK: Integration Response OPTIONS configuree" -ForegroundColor Green
    } catch {
        Write-Host "    Tentative avec put-integration-response..." -ForegroundColor Yellow
        
        # Si update ne fonctionne pas, essayer put avec format simple
        try {
            $responseParams = "method.response.header.Access-Control-Allow-Origin='$ALLOWED_ORIGIN'"
            $responseTemplates = '{\"application/json\":\"\"}'
            
            aws apigateway put-integration-response `
                --rest-api-id $API_ID `
                --resource-id $RESOURCE_ID `
                --http-method OPTIONS `
                --status-code 200 `
                --region $REGION `
                --response-parameters $responseParams `
                --response-templates $responseTemplates | Out-Null
            
            Write-Host "    OK: Integration Response OPTIONS configuree (format simple)" -ForegroundColor Green
        } catch {
            Write-Host "    ERREUR: $_" -ForegroundColor Red
            Write-Host "    Configuration manuelle necessaire dans la console AWS" -ForegroundColor Yellow
        }
    } finally {
        if (Test-Path $patchFile) {
            Remove-Item $patchFile -Force
        }
    }
    
    # ============================================
    # POST - Integration Response pour chaque code de statut
    # ============================================
    Write-Host "  Configuration POST Integration Response..." -ForegroundColor Cyan
    
    try {
        $postMethod = aws apigateway get-method --rest-api-id $API_ID --resource-id $RESOURCE_ID --http-method POST --region $REGION | ConvertFrom-Json
        
        if ($postMethod.methodResponses) {
            $statusCodes = $postMethod.methodResponses.PSObject.Properties.Name
            
            foreach ($statusCode in $statusCodes) {
                Write-Host "    Configuration reponse $statusCode..." -ForegroundColor Gray
                
                # Creer patch pour POST Integration Response
                $postPatchJson = @"
[
  {
    "op": "replace",
    "path": "/responseParameters/method.response.header.Access-Control-Allow-Origin",
    "value": "'$ALLOWED_ORIGIN'"
  }
]
"@
                
                $postPatchFile = "patch-post-$RESOURCE_ID-$statusCode.json"
                $postPatchJson | Out-File -FilePath $postPatchFile -Encoding UTF8 -NoNewline
                
                try {
                    # Essayer update-integration-response
                    aws apigateway update-integration-response `
                        --rest-api-id $API_ID `
                        --resource-id $RESOURCE_ID `
                        --http-method POST `
                        --status-code $statusCode `
                        --region $REGION `
                        --patch-ops file://$postPatchFile | Out-Null
                    
                    Write-Host "      OK: Integration Response POST $statusCode configuree" -ForegroundColor Green
                } catch {
                    # Si update ne fonctionne pas, essayer put
                    try {
                        $postResponseParams = "method.response.header.Access-Control-Allow-Origin='$ALLOWED_ORIGIN'"
                        
                        aws apigateway put-integration-response `
                            --rest-api-id $API_ID `
                            --resource-id $RESOURCE_ID `
                            --http-method POST `
                            --status-code $statusCode `
                            --region $REGION `
                            --response-parameters $postResponseParams | Out-Null
                        
                        Write-Host "      OK: Integration Response POST $statusCode configuree (put)" -ForegroundColor Green
                    } catch {
                        Write-Host "      ATTENTION: Impossible de configurer $statusCode : $_" -ForegroundColor Yellow
                    }
                } finally {
                    if (Test-Path $postPatchFile) {
                        Remove-Item $postPatchFile -Force
                    }
                }
            }
        }
    } catch {
        Write-Host "    ATTENTION: Impossible de recuperer les codes de statut POST: $_" -ForegroundColor Yellow
    }
}

# Deployer
Write-Host ""
Write-Host "Deploiement de l'API..." -ForegroundColor Cyan
$deploymentId = aws apigateway create-deployment `
    --rest-api-id $API_ID `
    --stage-name $STAGE `
    --region $REGION `
    --query 'id' `
    --output text

if ($deploymentId) {
    Write-Host "OK: API deployee (ID: $deploymentId)" -ForegroundColor Green
} else {
    Write-Host "ERREUR: Echec du deploiement" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "Configuration terminee !" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Testez maintenant la connexion Google depuis https://mapevent.world" -ForegroundColor Cyan


