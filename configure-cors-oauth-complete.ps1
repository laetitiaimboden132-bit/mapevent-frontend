# Script pour configurer CORS sur /api/user/oauth/google/complete
# API Gateway ID: j33osy4bvj

$REST_API_ID = "j33osy4bvj"
$API_PATH = "/api/user/oauth/google/complete"

Write-Host "Configuration CORS pour $API_PATH" -ForegroundColor Cyan

# Fonction pour obtenir l'ID d'une ressource par son chemin
function Get-ResourceIdByPath {
    param($RestApiId, $Path)
    
    $resources = aws apigateway get-resources --rest-api-id $RestApiId --output json | ConvertFrom-Json
    
    foreach ($item in $resources.items) {
        if ($item.path -eq $Path) {
            return $item.id
        }
    }
    return $null
}

# Fonction pour créer une ressource récursivement
function Create-ResourcePath {
    param($RestApiId, $ParentId, $PathParts, $Index = 0)
    
    if ($Index -ge $PathParts.Length) {
        return $ParentId
    }
    
    $currentPath = "/" + ($PathParts[0..$Index] -join "/")
    $currentPart = $PathParts[$Index]
    
    Write-Host "  Verification: $currentPath" -ForegroundColor Yellow
    
    # Verifier si la ressource existe deja
    $existingId = Get-ResourceIdByPath -RestApiId $RestApiId -Path $currentPath
    
    if ($existingId) {
        Write-Host "  Ressource existe: $currentPath (ID: $existingId)" -ForegroundColor Green
        return Create-ResourcePath -RestApiId $RestApiId -ParentId $existingId -PathParts $PathParts -Index ($Index + 1)
    }
    
    # Creer la ressource
    Write-Host "  Creation ressource: $currentPart" -ForegroundColor Yellow
    $createResult = aws apigateway create-resource `
        --rest-api-id $RestApiId `
        --parent-id $ParentId `
        --path-part $currentPart `
        --output json | ConvertFrom-Json
    
    if ($createResult.id) {
        Write-Host "  Ressource creee: $currentPath (ID: $createResult.id)" -ForegroundColor Green
        return Create-ResourcePath -RestApiId $RestApiId -ParentId $createResult.id -PathParts $PathParts -Index ($Index + 1)
    }
    
    return $null
}

# Etape 1: Trouver ou creer la ressource
Write-Host ""
Write-Host "Etape 1: Recherche/Creation de la ressource..." -ForegroundColor Cyan

$resourceId = Get-ResourceIdByPath -RestApiId $REST_API_ID -Path $API_PATH

if (-not $resourceId) {
    Write-Host "  Ressource non trouvee, creation..." -ForegroundColor Yellow
    
    # Trouver /api/user
    $userResourceId = Get-ResourceIdByPath -RestApiId $REST_API_ID -Path "/api/user"
    
    if (-not $userResourceId) {
        Write-Host "  /api/user non trouve!" -ForegroundColor Red
        exit 1
    }
    
    # Creer le chemin oauth/google/complete
    $pathParts = @("oauth", "google", "complete")
    $resourceId = Create-ResourcePath -RestApiId $REST_API_ID -ParentId $userResourceId -PathParts $pathParts
    
    if (-not $resourceId) {
        Write-Host "  Echec creation ressource!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "  Ressource trouvee: $API_PATH (ID: $resourceId)" -ForegroundColor Green
}

# Etape 2: Verifier/Creer la methode OPTIONS
Write-Host ""
Write-Host "Etape 2: Configuration methode OPTIONS..." -ForegroundColor Cyan

$optionsExists = aws apigateway get-method --rest-api-id $REST_API_ID --resource-id $resourceId --http-method OPTIONS --output json 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "  Creation methode OPTIONS..." -ForegroundColor Yellow
    
    # Creer la methode OPTIONS
    aws apigateway put-method `
        --rest-api-id $REST_API_ID `
        --resource-id $resourceId `
        --http-method OPTIONS `
        --authorization-type NONE `
        --no-api-key-required `
        --output json | Out-Null
    
    Write-Host "  Methode OPTIONS creee" -ForegroundColor Green
    
    # Configurer la reponse de methode
    aws apigateway put-method-response `
        --rest-api-id $REST_API_ID `
        --resource-id $resourceId `
        --http-method OPTIONS `
        --status-code 200 `
        --response-parameters "method.response.header.Access-Control-Allow-Headers=false,method.response.header.Access-Control-Allow-Methods=false,method.response.header.Access-Control-Allow-Origin=false" `
        --output json | Out-Null
    
    # Configurer l'integration MOCK
    aws apigateway put-integration `
        --rest-api-id $REST_API_ID `
        --resource-id $resourceId `
        --http-method OPTIONS `
        --type MOCK `
        --request-templates "{\"application/json\": \"{\\\"statusCode\\\": 200}\"}" `
        --output json | Out-Null
    
    # Configurer la reponse d'integration avec headers CORS
    aws apigateway put-integration-response `
        --rest-api-id $REST_API_ID `
        --resource-id $resourceId `
        --http-method OPTIONS `
        --status-code 200 `
        --response-parameters "method.response.header.Access-Control-Allow-Headers='Content-Type,Authorization,Origin,X-Requested-With,Accept',method.response.header.Access-Control-Allow-Methods='POST,OPTIONS',method.response.header.Access-Control-Allow-Origin='https://mapevent.world'" `
        --output json | Out-Null
    
    Write-Host "  Methode OPTIONS configuree avec CORS" -ForegroundColor Green
} else {
    Write-Host "  Methode OPTIONS existe deja" -ForegroundColor Green
}

# Etape 3: Verifier/Creer la methode POST avec CORS
Write-Host ""
Write-Host "Etape 3: Configuration methode POST..." -ForegroundColor Cyan

$postExists = aws apigateway get-method --rest-api-id $REST_API_ID --resource-id $resourceId --http-method POST --output json 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "  Methode POST n'existe pas encore" -ForegroundColor Yellow
    Write-Host "  Vous devrez creer la methode POST manuellement dans la console AWS" -ForegroundColor Yellow
    Write-Host "  Ou utiliser AWS CLI pour creer l'integration Lambda" -ForegroundColor Yellow
} else {
    Write-Host "  Methode POST existe" -ForegroundColor Green
    
    # Ajouter les headers CORS a la reponse POST
    Write-Host "  Ajout headers CORS a POST..." -ForegroundColor Yellow
    
    # Verifier si la reponse 200 existe
    $methodResponse = aws apigateway get-method-response `
        --rest-api-id $REST_API_ID `
        --resource-id $resourceId `
        --http-method POST `
        --status-code 200 `
        --output json 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        # Creer la reponse de methode avec headers CORS
        aws apigateway put-method-response `
            --rest-api-id $REST_API_ID `
            --resource-id $resourceId `
            --http-method POST `
            --status-code 200 `
            --response-parameters "method.response.header.Access-Control-Allow-Origin=false" `
            --output json | Out-Null
    } else {
        # Mettre a jour la reponse existante
        $responseParams = "method.response.header.Access-Control-Allow-Origin=false"
        aws apigateway put-method-response `
            --rest-api-id $REST_API_ID `
            --resource-id $resourceId `
            --http-method POST `
            --status-code 200 `
            --response-parameters $responseParams `
            --output json | Out-Null
    }
    
    # Ajouter les headers CORS a l'integration
    $integration = aws apigateway get-integration `
        --rest-api-id $REST_API_ID `
        --resource-id $resourceId `
        --http-method POST `
        --output json | ConvertFrom-Json
    
    if ($integration.integrationResponses.'200') {
        $existingParams = $integration.integrationResponses.'200'.responseParameters
        $corsParams = "method.response.header.Access-Control-Allow-Origin='https://mapevent.world'"
        
        if ($existingParams) {
            $corsParams = ($existingParams | ConvertTo-Json -Compress) + "," + $corsParams
        }
        
        aws apigateway put-integration-response `
            --rest-api-id $REST_API_ID `
            --resource-id $resourceId `
            --http-method POST `
            --status-code 200 `
            --response-parameters $corsParams `
            --output json | Out-Null
        
        Write-Host "  Headers CORS ajoutes a POST" -ForegroundColor Green
    }
}

# Etape 4: Deployer l'API
Write-Host ""
Write-Host "Etape 4: Deploiement de l'API..." -ForegroundColor Cyan

$deployment = aws apigateway create-deployment `
    --rest-api-id $REST_API_ID `
    --stage-name default `
    --description "CORS configuration for /api/user/oauth/google/complete" `
    --output json | ConvertFrom-Json

if ($deployment.id) {
    Write-Host "  API deployee avec succes!" -ForegroundColor Green
    Write-Host "  Deployment ID: $($deployment.id)" -ForegroundColor Cyan
} else {
    Write-Host "  Echec du deploiement" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Configuration CORS terminee!" -ForegroundColor Green
Write-Host "Testez l'endpoint: https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default$API_PATH" -ForegroundColor Cyan

