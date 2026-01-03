# Script PowerShell pour configurer CORS dans API Gateway
# Endpoint: /api/user/oauth/google/complete

Write-Host "Configuration CORS pour API Gateway..." -ForegroundColor Cyan

# Configuration
$API_ID = "j33osy4bvj"  # ID de l'API depuis l'URL
$REGION = "eu-west-1"
$STAGE = "default"
$RESOURCE_PATH = "/api/user/oauth/google/complete"
$ORIGIN = "https://mapevent.world"

Write-Host "API ID: $API_ID" -ForegroundColor Yellow
Write-Host "Region: $REGION" -ForegroundColor Yellow
Write-Host "Resource: $RESOURCE_PATH" -ForegroundColor Yellow

# Vérifier que AWS CLI est installé
try {
    $awsVersion = aws --version 2>&1
    Write-Host "AWS CLI detecte: $awsVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ AWS CLI n'est pas installé ou pas dans le PATH" -ForegroundColor Red
    Write-Host "Installez AWS CLI depuis: https://aws.amazon.com/cli/" -ForegroundColor Yellow
    exit 1
}

# Vérifier les credentials AWS
try {
    $identity = aws sts get-caller-identity 2>&1 | ConvertFrom-Json
    Write-Host "Credentials AWS OK - Account: $($identity.Account)" -ForegroundColor Green
} catch {
    Write-Host "❌ Erreur credentials AWS. Configurez avec: aws configure" -ForegroundColor Red
    exit 1
}

Write-Host "`nRecherche de l'API Gateway..." -ForegroundColor Cyan

# Lister les APIs pour trouver la bonne
try {
    $apis = aws apigateway get-rest-apis --region $REGION 2>&1 | ConvertFrom-Json
    $api = $apis.items | Where-Object { $_.id -eq $API_ID -or $_.name -like "*mapevent*" } | Select-Object -First 1
    
    if (-not $api) {
        Write-Host "⚠️  API non trouvée avec ID $API_ID. Liste des APIs disponibles:" -ForegroundColor Yellow
        $apis.items | ForEach-Object { Write-Host "  - $($_.name) (ID: $($_.id))" -ForegroundColor Gray }
        
        # Demander à l'utilisateur
        $apiIdInput = Read-Host "Entrez l'ID de l'API Gateway"
        $api = $apis.items | Where-Object { $_.id -eq $apiIdInput } | Select-Object -First 1
    }
    
    if ($api) {
        $API_ID = $api.id
        Write-Host "API trouvee: $($api.name) (ID: $API_ID)" -ForegroundColor Green
    } else {
        Write-Host "❌ API non trouvée" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Erreur lors de la recherche de l'API: $_" -ForegroundColor Red
    exit 1
}

Write-Host "`nRecherche de la ressource $RESOURCE_PATH..." -ForegroundColor Cyan

# Trouver la ressource
try {
    $resources = aws apigateway get-resources --rest-api-id $API_ID --region $REGION 2>&1 | ConvertFrom-Json
    $targetResource = $resources.items | Where-Object { $_.path -eq $RESOURCE_PATH } | Select-Object -First 1
    
    if (-not $targetResource) {
        Write-Host "⚠️  Ressource $RESOURCE_PATH non trouvée. Création..." -ForegroundColor Yellow
        
        # Essayer de créer la ressource (nécessite de trouver le parent)
        $parentPath = "/api/user/oauth/google"
        $parentResource = $resources.items | Where-Object { $_.path -eq $parentPath } | Select-Object -First 1
        
        if (-not $parentResource) {
            Write-Host "❌ Ressource parente $parentPath non trouvée" -ForegroundColor Red
            Write-Host "Veuillez créer la ressource manuellement dans la console AWS" -ForegroundColor Yellow
            exit 1
        }
        
        # Créer la ressource
        $newResource = aws apigateway create-resource `
            --rest-api-id $API_ID `
            --parent-id $parentResource.id `
            --path-part "complete" `
            --region $REGION 2>&1 | ConvertFrom-Json
        
        $targetResource = $newResource
        Write-Host "Ressource creee (ID: $($targetResource.id))" -ForegroundColor Green
    } else {
        Write-Host "Ressource trouvee (ID: $($targetResource.id))" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Erreur lors de la recherche/création de la ressource: $_" -ForegroundColor Red
    Write-Host "Veuillez créer la ressource manuellement dans la console AWS" -ForegroundColor Yellow
    exit 1
}

$RESOURCE_ID = $targetResource.id

Write-Host "`nConfiguration de la methode OPTIONS..." -ForegroundColor Cyan

# Vérifier si OPTIONS existe déjà
try {
    $methods = aws apigateway get-resource --rest-api-id $API_ID --resource-id $RESOURCE_ID --region $REGION 2>&1 | ConvertFrom-Json
    $hasOptions = $methods.resourceMethods.PSObject.Properties.Name -contains "OPTIONS"
    
    if (-not $hasOptions) {
        Write-Host "Création de la méthode OPTIONS..." -ForegroundColor Yellow
        
        # Créer la méthode OPTIONS
        aws apigateway put-method `
            --rest-api-id $API_ID `
            --resource-id $RESOURCE_ID `
            --http-method OPTIONS `
            --authorization-type NONE `
            --region $REGION 2>&1 | Out-Null
        
        Write-Host "Methode OPTIONS creee" -ForegroundColor Green
    } else {
        Write-Host "Methode OPTIONS existe deja" -ForegroundColor Green
    }
} catch {
    Write-Host "⚠️  Erreur lors de la création de OPTIONS: $_" -ForegroundColor Yellow
    Write-Host "Tentative de continuer..." -ForegroundColor Yellow
}

# Configurer l'intégration Mock pour OPTIONS
Write-Host "Configuration de l'intégration Mock..." -ForegroundColor Yellow

try {
    aws apigateway put-integration `
        --rest-api-id $API_ID `
        --resource-id $RESOURCE_ID `
        --http-method OPTIONS `
        --type MOCK `
        --request-templates '{"application/json":"{\"statusCode\":200}"}' `
        --region $REGION 2>&1 | Out-Null
    
    Write-Host "Integration Mock configuree" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Erreur lors de la configuration de l'intégration: $_" -ForegroundColor Yellow
}

# Configurer la réponse d'intégration
Write-Host "Configuration de la réponse d'intégration..." -ForegroundColor Yellow

try {
    aws apigateway put-integration-response `
        --rest-api-id $API_ID `
        --resource-id $RESOURCE_ID `
        --http-method OPTIONS `
        --status-code 200 `
        --response-parameters '{"method.response.header.Access-Control-Allow-Origin":"'"'"'*'"'"'","method.response.header.Access-Control-Allow-Headers":"'"'"'Content-Type,Authorization,Origin,X-Requested-With,Accept'"'"'","method.response.header.Access-Control-Allow-Methods":"'"'"'POST,OPTIONS'"'"'"}' `
        --region $REGION 2>&1 | Out-Null
    
    Write-Host "Reponse d'integration configuree" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Erreur lors de la configuration de la réponse: $_" -ForegroundColor Yellow
}

# Configurer la réponse de méthode
Write-Host "Configuration de la réponse de méthode..." -ForegroundColor Yellow

try {
    # Ajouter les headers dans Method Response
    aws apigateway put-method-response `
        --rest-api-id $API_ID `
        --resource-id $RESOURCE_ID `
        --http-method OPTIONS `
        --status-code 200 `
        --response-parameters '{"method.response.header.Access-Control-Allow-Origin":true,"method.response.header.Access-Control-Allow-Headers":true,"method.response.header.Access-Control-Allow-Methods":true}' `
        --region $REGION 2>&1 | Out-Null
    
    Write-Host "Reponse de methode configuree" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Erreur lors de la configuration de la réponse de méthode: $_" -ForegroundColor Yellow
}

# Configurer CORS pour POST aussi
Write-Host "`nConfiguration CORS pour POST..." -ForegroundColor Cyan

try {
    # Vérifier si POST existe
    $methods = aws apigateway get-resource --rest-api-id $API_ID --resource-id $RESOURCE_ID --region $REGION 2>&1 | ConvertFrom-Json
    $hasPost = $methods.resourceMethods.PSObject.Properties.Name -contains "POST"
    
    if ($hasPost) {
        # Ajouter les headers CORS à la réponse POST
        Write-Host "Ajout des headers CORS à POST..." -ForegroundColor Yellow
        
        # Method Response pour POST
        try {
            $postResponse = aws apigateway get-method-response `
                --rest-api-id $API_ID `
                --resource-id $RESOURCE_ID `
                --http-method POST `
                --status-code 200 `
                --region $REGION 2>&1 | ConvertFrom-Json
            
            $responseParams = @{
                "method.response.header.Access-Control-Allow-Origin" = $true
                "method.response.header.Access-Control-Allow-Headers" = $true
                "method.response.header.Access-Control-Allow-Methods" = $true
            }
            
            # Merger avec les paramètres existants
            if ($postResponse.responseParameters) {
                foreach ($key in $postResponse.responseParameters.PSObject.Properties.Name) {
                    $responseParams[$key] = $postResponse.responseParameters.$key
                }
            }
            
            $paramsJson = ($responseParams.GetEnumerator() | ForEach-Object { """$($_.Key)"":$($_.Value.ToString().ToLower())" }) -join ","
            $paramsJson = "{$paramsJson}"
            
            aws apigateway put-method-response `
                --rest-api-id $API_ID `
                --resource-id $RESOURCE_ID `
                --http-method POST `
                --status-code 200 `
                --response-parameters $paramsJson `
                --region $REGION 2>&1 | Out-Null
            
            Write-Host "Headers CORS ajoutes a POST" -ForegroundColor Green
        } catch {
            Write-Host "⚠️  Erreur lors de l'ajout des headers à POST: $_" -ForegroundColor Yellow
        }
        
        # Integration Response pour POST
        try {
            $integrationResponse = aws apigateway get-integration-response `
                --rest-api-id $API_ID `
                --resource-id $RESOURCE_ID `
                --http-method POST `
                --status-code 200 `
                --region $REGION 2>&1 | ConvertFrom-Json
            
            $integrationParams = @{
                "method.response.header.Access-Control-Allow-Origin" = "'*'"
                "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,Authorization,Origin,X-Requested-With,Accept'"
                "method.response.header.Access-Control-Allow-Methods" = "'POST,OPTIONS'"
            }
            
            # Merger avec les paramètres existants
            if ($integrationResponse.responseParameters) {
                foreach ($key in $integrationResponse.responseParameters.PSObject.Properties.Name) {
                    $integrationParams[$key] = $integrationResponse.responseParameters.$key
                }
            }
            
            $intParamsJson = ($integrationParams.GetEnumerator() | ForEach-Object { """$($_.Key)"":""$($_.Value)""" }) -join ","
            $intParamsJson = "{$intParamsJson}"
            
            aws apigateway put-integration-response `
                --rest-api-id $API_ID `
                --resource-id $RESOURCE_ID `
                --http-method POST `
                --status-code 200 `
                --response-parameters $intParamsJson `
                --region $REGION 2>&1 | Out-Null
            
            Write-Host "Headers CORS ajoutes a l'integration POST" -ForegroundColor Green
        } catch {
            Write-Host "⚠️  Erreur lors de l'ajout des headers à l'intégration POST: $_" -ForegroundColor Yellow
        }
    } else {
        Write-Host "Methode POST non trouvee sur cette ressource" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️  Erreur lors de la configuration CORS pour POST: $_" -ForegroundColor Yellow
}

# Deployer l'API
Write-Host "`nDeploiement de l'API..." -ForegroundColor Cyan

try {
    $deployment = aws apigateway create-deployment `
        --rest-api-id $API_ID `
        --stage-name $STAGE `
        --description "CORS configuration for /api/user/oauth/google/complete" `
        --region $REGION 2>&1 | ConvertFrom-Json
    
    Write-Host "API deployee avec succes (Deployment ID: $($deployment.id))" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Erreur lors du déploiement: $_" -ForegroundColor Yellow
    Write-Host "Vous pouvez déployer manuellement depuis la console AWS" -ForegroundColor Yellow
}

Write-Host "`nConfiguration CORS terminee !" -ForegroundColor Green
Write-Host "`nTestez avec:" -ForegroundColor Cyan
Write-Host "curl -X OPTIONS https://$API_ID.execute-api.$REGION.amazonaws.com/$STAGE$RESOURCE_PATH -H Origin: $ORIGIN -v" -ForegroundColor Gray

