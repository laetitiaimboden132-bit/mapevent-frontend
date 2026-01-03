# Script pour configurer CORS pour /api/user/oauth/google/complete
# API Gateway ID et Resource ID doivent être identifiés

Write-Host "Configuration CORS pour /api/user/oauth/google/complete..." -ForegroundColor Cyan

# Configuration
$API_ID = "j33osy4bvj"  # ID de l'API (extrait de l'URL)
$STAGE = "default"
$RESOURCE_PATH = "/api/user/oauth/google/complete"
$ALLOWED_ORIGIN = "https://mapevent.world"

Write-Host "API ID: $API_ID" -ForegroundColor Yellow
Write-Host "Stage: $STAGE" -ForegroundColor Yellow
Write-Host "Resource: $RESOURCE_PATH" -ForegroundColor Yellow
Write-Host "Origin: $ALLOWED_ORIGIN" -ForegroundColor Yellow

# Étape 1: Trouver le Resource ID
Write-Host ""
Write-Host "Recherche du Resource ID pour $RESOURCE_PATH..." -ForegroundColor Cyan
$resourcesJson = aws apigateway get-resources --rest-api-id $API_ID --region eu-west-1
$resources = $resourcesJson | ConvertFrom-Json

$targetResource = $null
foreach ($resource in $resources.items) {
    if ($resource.path -eq $RESOURCE_PATH) {
        $targetResource = $resource
        break
    }
}

if (-not $targetResource) {
    Write-Host "ERREUR: Resource non trouve: $RESOURCE_PATH" -ForegroundColor Red
    Write-Host "Resources disponibles:" -ForegroundColor Yellow
    foreach ($resource in $resources.items) {
        Write-Host "  - $($resource.path) (ID: $($resource.id))" -ForegroundColor Gray
    }
    exit 1
}

$RESOURCE_ID = $targetResource.id
Write-Host "OK: Resource ID trouve: $RESOURCE_ID" -ForegroundColor Green

# Étape 2: Créer la méthode OPTIONS si elle n'existe pas
Write-Host ""
Write-Host "Configuration de la methode OPTIONS..." -ForegroundColor Cyan

try {
    $existingMethods = aws apigateway get-resource --rest-api-id $API_ID --resource-id $RESOURCE_ID --region eu-west-1 | ConvertFrom-Json
    $hasOptions = $existingMethods.resourceMethods.PSObject.Properties.Name -contains "OPTIONS"
    
    if (-not $hasOptions) {
        Write-Host "Création de la méthode OPTIONS..." -ForegroundColor Yellow
        aws apigateway put-method `
            --rest-api-id $API_ID `
            --resource-id $RESOURCE_ID `
            --http-method OPTIONS `
            --authorization-type NONE `
            --region eu-west-1 `
            --no-api-key-required | Out-Null
        Write-Host "✅ Méthode OPTIONS créée" -ForegroundColor Green
    } else {
        Write-Host "✅ Méthode OPTIONS existe déjà" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️ Erreur lors de la création de OPTIONS: $_" -ForegroundColor Yellow
    Write-Host "Tentative de création..." -ForegroundColor Yellow
    aws apigateway put-method `
        --rest-api-id $API_ID `
        --resource-id $RESOURCE_ID `
        --http-method OPTIONS `
        --authorization-type NONE `
        --region eu-west-1 `
        --no-api-key-required | Out-Null
}

# Étape 3: Configurer l'intégration Mock pour OPTIONS
Write-Host ""
Write-Host "Configuration de l'integration Mock pour OPTIONS..." -ForegroundColor Cyan

$requestTemplatesJson = '{\"application/json\":\"{\\\"statusCode\\\":200}\"}'

aws apigateway put-integration `
    --rest-api-id $API_ID `
    --resource-id $RESOURCE_ID `
    --http-method OPTIONS `
    --type MOCK `
    --integration-http-method POST `
    --request-templates $requestTemplatesJson `
    --region eu-west-1 | Out-Null

Write-Host "✅ Intégration Mock configurée" -ForegroundColor Green

# Étape 4: Configurer Method Response pour OPTIONS
Write-Host ""
Write-Host "Configuration Method Response pour OPTIONS..." -ForegroundColor Cyan

# Supprimer les réponses existantes si elles existent
try {
    aws apigateway delete-method-response --rest-api-id $API_ID --resource-id $RESOURCE_ID --http-method OPTIONS --status-code 200 --region eu-west-1 2>$null
} catch {}

# Créer la réponse 200 avec les headers CORS
aws apigateway put-method-response `
    --rest-api-id $API_ID `
    --resource-id $RESOURCE_ID `
    --http-method OPTIONS `
    --status-code 200 `
    --response-parameters "method.response.header.Access-Control-Allow-Headers=false,method.response.header.Access-Control-Allow-Methods=false,method.response.header.Access-Control-Allow-Origin=false" `
    --region eu-west-1 | Out-Null

Write-Host "✅ Method Response configurée" -ForegroundColor Green

# Étape 5: Configurer Integration Response pour OPTIONS
Write-Host ""
Write-Host "Configuration Integration Response pour OPTIONS..." -ForegroundColor Cyan

$responseParamsJson = "method.response.header.Access-Control-Allow-Headers='Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',method.response.header.Access-Control-Allow-Methods='POST,OPTIONS',method.response.header.Access-Control-Allow-Origin='$ALLOWED_ORIGIN'"

aws apigateway put-integration-response `
    --rest-api-id $API_ID `
    --resource-id $RESOURCE_ID `
    --http-method OPTIONS `
    --status-code 200 `
    --response-parameters $responseParamsJson `
    --region eu-west-1 | Out-Null

Write-Host "✅ Integration Response configurée" -ForegroundColor Green

# Étape 6: Ajouter les headers CORS à la méthode POST
Write-Host ""
Write-Host "Ajout des headers CORS a la methode POST..." -ForegroundColor Cyan

# Vérifier si POST existe
$hasPost = $existingMethods.resourceMethods.PSObject.Properties.Name -contains "POST"

if ($hasPost) {
    # Ajouter les headers à Integration Response de POST
    $postResponseParams = @{
        "method.response.header.Access-Control-Allow-Origin" = "'$ALLOWED_ORIGIN'"
    } | ConvertTo-Json -Compress
    
    # Récupérer les réponses existantes de POST
    try {
        $postResponses = aws apigateway get-method --rest-api-id $API_ID --resource-id $RESOURCE_ID --http-method POST --region eu-west-1 | ConvertFrom-Json
        $statusCodes = $postResponses.methodResponses.PSObject.Properties.Name
        
        foreach ($statusCode in $statusCodes) {
            Write-Host "  Configuration de la réponse $statusCode..." -ForegroundColor Gray
            
            # Ajouter le header à Method Response
            try {
                $methodResponse = aws apigateway get-method-response --rest-api-id $API_ID --resource-id $RESOURCE_ID --http-method POST --status-code $statusCode --region eu-west-1 | ConvertFrom-Json
                $existingHeaders = $methodResponse.responseParameters.PSObject.Properties.Name -join ","
                
                if ($existingHeaders -notmatch "Access-Control-Allow-Origin") {
                    aws apigateway update-method-response `
                        --rest-api-id $API_ID `
                        --resource-id $RESOURCE_ID `
                        --http-method POST `
                        --status-code $statusCode `
                        --patch-ops op=add,path="/responseParameters/method.response.header.Access-Control-Allow-Origin",value="false" `
                        --region eu-west-1 | Out-Null
                }
            } catch {
                Write-Host "    ⚠️ Erreur Method Response: $_" -ForegroundColor Yellow
            }
            
            # Ajouter le header à Integration Response
            try {
                aws apigateway update-integration-response `
                    --rest-api-id $API_ID `
                    --resource-id $RESOURCE_ID `
                    --http-method POST `
                    --status-code $statusCode `
                    --patch-ops op=add,path="/responseParameters/method.response.header.Access-Control-Allow-Origin",value="'$ALLOWED_ORIGIN'" `
                    --region eu-west-1 | Out-Null
                Write-Host "    ✅ Header CORS ajouté à la réponse $statusCode" -ForegroundColor Green
            } catch {
                Write-Host "    ⚠️ Erreur Integration Response: $_" -ForegroundColor Yellow
            }
        }
    } catch {
        Write-Host "⚠️ Erreur lors de la configuration POST: $_" -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️ Méthode POST non trouvée" -ForegroundColor Yellow
}

# Étape 7: Déployer l'API
Write-Host ""
Write-Host "Deploiement de l'API..." -ForegroundColor Cyan

$deploymentId = aws apigateway create-deployment `
    --rest-api-id $API_ID `
    --stage-name $STAGE `
    --region eu-west-1 `
    --query 'id' `
    --output text

if ($deploymentId) {
    Write-Host "✅ API déployée avec succès (Deployment ID: $deploymentId)" -ForegroundColor Green
} else {
    Write-Host "❌ Erreur lors du déploiement" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "OK: Configuration CORS terminee !" -ForegroundColor Green
Write-Host "Testez maintenant la creation de compte depuis https://mapevent.world" -ForegroundColor Cyan

