# Script pour créer la méthode POST avec intégration Lambda pour /api/user/oauth/google/complete
# API Gateway ID: j33osy4bvj
# Lambda Function: mapevent-backend

$ErrorActionPreference = "Stop"

$REST_API_ID = "j33osy4bvj"
$RESOURCE_ID = "rjh1m4"  # ID de /api/user/oauth/google/complete
$LAMBDA_FUNCTION_NAME = "mapevent-backend"
$REGION = "eu-west-1"
$API_PATH = "/api/user/oauth/google/complete"

Write-Host "Creation methode POST pour $API_PATH" -ForegroundColor Cyan
Write-Host ""

# Étape 1: Obtenir l'ARN de la fonction Lambda
Write-Host "Etape 1: Recherche fonction Lambda..." -ForegroundColor Yellow
$lambdaArn = aws lambda get-function --function-name $LAMBDA_FUNCTION_NAME --query "Configuration.FunctionArn" --output text --region $REGION

if (-not $lambdaArn) {
    Write-Host "  Erreur: Fonction Lambda '$LAMBDA_FUNCTION_NAME' non trouvee!" -ForegroundColor Red
    exit 1
}

Write-Host "  Fonction Lambda trouvee: $lambdaArn" -ForegroundColor Green
Write-Host ""

# Étape 2: Créer la méthode POST
Write-Host "Etape 2: Creation methode POST..." -ForegroundColor Yellow

try {
    aws apigateway put-method `
        --rest-api-id $REST_API_ID `
        --resource-id $RESOURCE_ID `
        --http-method POST `
        --authorization-type NONE `
        --no-api-key-required `
        --output json | Out-Null
    
    Write-Host "  Methode POST creee" -ForegroundColor Green
} catch {
    Write-Host "  Erreur lors de la creation de la methode POST: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Étape 3: Créer l'intégration Lambda
Write-Host "Etape 3: Creation integration Lambda..." -ForegroundColor Yellow

$lambdaUri = "arn:aws:apigateway:$REGION`:lambda:path/2015-03-31/functions/$lambdaArn/invocations"

try {
    aws apigateway put-integration `
        --rest-api-id $REST_API_ID `
        --resource-id $RESOURCE_ID `
        --http-method POST `
        --type AWS_PROXY `
        --integration-http-method POST `
        --uri $lambdaUri `
        --output json | Out-Null
    
    Write-Host "  Integration Lambda creee" -ForegroundColor Green
} catch {
    Write-Host "  Erreur lors de la creation de l'integration: $_" -ForegroundColor Red
    exit 1
}

Write-Host ""

# Étape 4: Ajouter la permission Lambda pour API Gateway
Write-Host "Etape 4: Ajout permission Lambda..." -ForegroundColor Yellow

$sourceArn = "arn:aws:execute-api:$REGION`:*:$REST_API_ID/*/POST$API_PATH"

try {
    # Vérifier si la permission existe déjà
    $existingPolicy = aws lambda get-policy --function-name $LAMBDA_FUNCTION_NAME --region $REGION --output json 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        $policy = $existingPolicy | ConvertFrom-Json
        $policyDoc = $policy.Policy | ConvertFrom-Json
        
        # Vérifier si la permission existe déjà
        $permissionExists = $false
        foreach ($statement in $policyDoc.Statement) {
            if ($statement.Condition.StringEquals.'AWS:SourceArn' -eq $sourceArn) {
                $permissionExists = $true
                break
            }
        }
        
        if (-not $permissionExists) {
            aws lambda add-permission `
                --function-name $LAMBDA_FUNCTION_NAME `
                --statement-id "apigateway-$(Get-Random)" `
                --action lambda:InvokeFunction `
                --principal apigateway.amazonaws.com `
                --source-arn $sourceArn `
                --region $REGION `
                --output json | Out-Null
            
            Write-Host "  Permission Lambda ajoutee" -ForegroundColor Green
        } else {
            Write-Host "  Permission Lambda existe deja" -ForegroundColor Green
        }
    } else {
        # Créer la permission si le policy n'existe pas
        aws lambda add-permission `
            --function-name $LAMBDA_FUNCTION_NAME `
            --statement-id "apigateway-$(Get-Random)" `
            --action lambda:InvokeFunction `
            --principal apigateway.amazonaws.com `
            --source-arn $sourceArn `
            --region $REGION `
            --output json | Out-Null
        
        Write-Host "  Permission Lambda ajoutee" -ForegroundColor Green
    }
} catch {
    Write-Host "  Avertissement: Erreur lors de l'ajout de la permission (peut-etre existe deja): $_" -ForegroundColor Yellow
}

Write-Host ""

# Étape 5: Configurer la réponse de méthode avec CORS
Write-Host "Etape 5: Configuration reponse methode avec CORS..." -ForegroundColor Yellow

try {
    aws apigateway put-method-response `
        --rest-api-id $REST_API_ID `
        --resource-id $RESOURCE_ID `
        --http-method POST `
        --status-code 200 `
        --response-parameters "method.response.header.Access-Control-Allow-Origin=false" `
        --output json | Out-Null
    
    Write-Host "  Reponse methode configuree" -ForegroundColor Green
} catch {
    Write-Host "  Avertissement: Erreur configuration reponse methode: $_" -ForegroundColor Yellow
}

Write-Host ""

# Étape 6: Configurer la réponse d'intégration avec CORS
Write-Host "Etape 6: Configuration reponse integration avec CORS..." -ForegroundColor Yellow

try {
    aws apigateway put-integration-response `
        --rest-api-id $REST_API_ID `
        --resource-id $RESOURCE_ID `
        --http-method POST `
        --status-code 200 `
        --response-parameters "method.response.header.Access-Control-Allow-Origin='https://mapevent.world'" `
        --output json | Out-Null
    
    Write-Host "  Reponse integration configuree avec CORS" -ForegroundColor Green
} catch {
    Write-Host "  Avertissement: Erreur configuration reponse integration: $_" -ForegroundColor Yellow
}

Write-Host ""

# Étape 7: Déployer l'API
Write-Host "Etape 7: Deploiement de l'API..." -ForegroundColor Yellow

try {
    $deployment = aws apigateway create-deployment `
        --rest-api-id $REST_API_ID `
        --stage-name default `
        --description "Creation methode POST pour /api/user/oauth/google/complete avec CORS" `
        --output json | ConvertFrom-Json
    
    if ($deployment.id) {
        Write-Host "  API deployee avec succes!" -ForegroundColor Green
        Write-Host "  Deployment ID: $($deployment.id)" -ForegroundColor Cyan
    }
} catch {
    Write-Host "  Erreur lors du deploiement: $_" -ForegroundColor Red
    Write-Host "  Vous devrez deployer manuellement depuis la console AWS" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Configuration terminee!" -ForegroundColor Green
Write-Host "Endpoint: https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default$API_PATH" -ForegroundColor Cyan
Write-Host ""
Write-Host "Testez avec:" -ForegroundColor Yellow
Write-Host "curl -X OPTIONS https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default$API_PATH -H 'Origin: https://mapevent.world' -v" -ForegroundColor Gray

