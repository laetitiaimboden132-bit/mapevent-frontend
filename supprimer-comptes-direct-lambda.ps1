# Script pour supprimer tous les comptes sauf un via Lambda directement (AWS CLI)
# Contourne le problème d'API Gateway

$functionName = "mapevent-backend"
$region = "eu-west-1"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "SUPPRESSION DES COMPTES - VIA LAMBDA DIRECT" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# ÉTAPE 1 : Lister tous les comptes
Write-Host "1. Liste de tous les comptes existants..." -ForegroundColor Yellow

    $listPayload = @{
        httpMethod = "GET"
        path = "/api/admin/list-users"
        rawPath = "/api/admin/list-users"
        headers = @{
            "Host" = "j33osy4bvj.execute-api.eu-west-1.amazonaws.com"
            "Content-Type" = "application/json"
        }
        queryStringParameters = $null
        body = $null
        requestContext = @{
            http = @{
                method = "GET"
                path = "/default/api/admin/list-users"
            }
        }
    } | ConvertTo-Json -Depth 10 -Compress

# Sauvegarder le payload dans un fichier temporaire
$listPayloadFile = "temp-list-payload.json"
$listPayload | Out-File -FilePath $listPayloadFile -Encoding UTF8

try {
    # Invoquer Lambda
    $invokeResult = aws lambda invoke `
        --function-name $functionName `
        --region $region `
        --payload file://$listPayloadFile `
        --cli-binary-format raw-in-base64-out `
        temp-list-response.json 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Erreur AWS CLI:" -ForegroundColor Red
        Write-Host $invokeResult -ForegroundColor Red
        throw "Erreur lors de l'invocation de Lambda (code: $LASTEXITCODE)"
    }
    
    # Lire la réponse
    $responseContent = Get-Content temp-list-response.json -Raw | ConvertFrom-Json
    
    # Lambda retourne la réponse dans responseContent.body (string JSON)
    if ($responseContent.body) {
        $bodyJson = $responseContent.body | ConvertFrom-Json
        
        if ($bodyJson.users -and $bodyJson.users.Count -gt 0) {
            Write-Host ""
            Write-Host "Comptes trouves : $($bodyJson.users.Count)" -ForegroundColor Green
            Write-Host ""
            
            foreach ($user in $bodyJson.users) {
                $email = if ($user.email) { $user.email } else { "(pas d'email)" }
                $username = if ($user.username) { $user.username } else { "(pas de username)" }
                $firstName = if ($user.first_name) { $user.first_name } else { "" }
                $lastName = if ($user.last_name) { $user.last_name } else { "" }
                
                Write-Host "  - Email: $email" -ForegroundColor White
                Write-Host "    Username: $username" -ForegroundColor Gray
                if ($firstName -or $lastName) {
                    Write-Host "    Nom: $firstName $lastName".Trim() -ForegroundColor Gray
                }
                Write-Host ""
            }
        } else {
            Write-Host "Aucun compte trouve." -ForegroundColor Yellow
            Remove-Item temp-list-payload.json -ErrorAction SilentlyContinue
            Remove-Item temp-list-response.json -ErrorAction SilentlyContinue
            exit 0
        }
    } else {
        Write-Host "ERREUR: Reponse invalide de Lambda" -ForegroundColor Red
        Write-Host "Reponse: $($responseContent | ConvertTo-Json -Depth 10)" -ForegroundColor Gray
        Remove-Item temp-list-payload.json -ErrorAction SilentlyContinue
        Remove-Item temp-list-response.json -ErrorAction SilentlyContinue
        exit 1
    }
} catch {
    Write-Host "ERREUR lors de la liste des comptes :" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Remove-Item temp-list-payload.json -ErrorAction SilentlyContinue
    Remove-Item temp-list-response.json -ErrorAction SilentlyContinue
    exit 1
}

# Nettoyer les fichiers temporaires
Remove-Item temp-list-payload.json -ErrorAction SilentlyContinue

# ÉTAPE 2 : Demander quel compte garder
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "2. Quel compte voulez-vous GARDER ?" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
$keepEmail = Read-Host "Entrez l'email du compte a garder (ou laissez vide pour tout supprimer)"

if ([string]::IsNullOrWhiteSpace($keepEmail)) {
    Write-Host ""
    Write-Host "ATTENTION: Vous allez supprimer TOUS les comptes !" -ForegroundColor Red
    $confirm = Read-Host "Confirmez en tapant 'OUI' en majuscules"
    
    if ($confirm -ne "OUI") {
        Write-Host "Operation annulee." -ForegroundColor Yellow
        Remove-Item temp-list-response.json -ErrorAction SilentlyContinue
        exit 0
    }
    
    # Supprimer tous les comptes
    Write-Host ""
    Write-Host "Suppression de TOUS les comptes..." -ForegroundColor Yellow
    
    $deleteAllPayload = @{
        httpMethod = "POST"
        path = "/api/admin/delete-all-users-simple"
        rawPath = "/api/admin/delete-all-users-simple"
        headers = @{
            "Host" = "j33osy4bvj.execute-api.eu-west-1.amazonaws.com"
            "Content-Type" = "application/json"
        }
        body = "{}"
        requestContext = @{
            http = @{
                method = "POST"
                path = "/default/api/admin/delete-all-users-simple"
            }
        }
    } | ConvertTo-Json -Depth 10 -Compress
    
    $deleteAllPayloadFile = "temp-delete-all-payload.json"
    $deleteAllPayload | Out-File -FilePath $deleteAllPayloadFile -Encoding UTF8
    
    try {
        aws lambda invoke `
            --function-name $functionName `
            --region $region `
            --payload file://$deleteAllPayloadFile `
            --cli-binary-format raw-in-base64-out `
            temp-delete-response.json 2>&1 | Out-Null
        
        $deleteResponse = Get-Content temp-delete-response.json -Raw | ConvertFrom-Json
        
        if ($deleteResponse.body) {
            $deleteBodyJson = $deleteResponse.body | ConvertFrom-Json
            
            if ($deleteBodyJson.success) {
                Write-Host ""
                Write-Host "SUCCES: Tous les comptes ont ete supprimes !" -ForegroundColor Green
                Write-Host "  Nombre supprime: $($deleteBodyJson.deleted_count)" -ForegroundColor Gray
            } else {
                Write-Host "ERREUR: $($deleteBodyJson.error)" -ForegroundColor Red
            }
        } else {
            Write-Host "ERREUR: Reponse invalide" -ForegroundColor Red
        }
    } catch {
        Write-Host "ERREUR lors de la suppression:" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
    } finally {
        Remove-Item temp-delete-all-payload.json -ErrorAction SilentlyContinue
        Remove-Item temp-delete-response.json -ErrorAction SilentlyContinue
    }
} else {
    # Supprimer tous sauf un
    Write-Host ""
    Write-Host "Suppression de tous les comptes SAUF: $keepEmail" -ForegroundColor Yellow
    $confirm = Read-Host "Confirmez en tapant 'OUI' en majuscules"
    
    if ($confirm -ne "OUI") {
        Write-Host "Operation annulee." -ForegroundColor Yellow
        Remove-Item temp-list-response.json -ErrorAction SilentlyContinue
        exit 0
    }
    
    Write-Host ""
    Write-Host "Suppression en cours..." -ForegroundColor Yellow
    
    $bodyObj = @{
        keepEmail = $keepEmail.ToLower()
    } | ConvertTo-Json -Compress
    
    $deleteExceptPayload = @{
        httpMethod = "POST"
        path = "/api/admin/delete-all-users-except"
        rawPath = "/api/admin/delete-all-users-except"
        headers = @{
            "Host" = "j33osy4bvj.execute-api.eu-west-1.amazonaws.com"
            "Content-Type" = "application/json"
        }
        body = $bodyObj
        requestContext = @{
            http = @{
                method = "POST"
                path = "/default/api/admin/delete-all-users-except"
            }
        }
    } | ConvertTo-Json -Depth 10 -Compress
    
    $deleteExceptPayloadFile = "temp-delete-except-payload.json"
    $deleteExceptPayload | Out-File -FilePath $deleteExceptPayloadFile -Encoding UTF8
    
    try {
        aws lambda invoke `
            --function-name $functionName `
            --region $region `
            --payload file://$deleteExceptPayloadFile `
            --cli-binary-format raw-in-base64-out `
            temp-delete-response.json 2>&1 | Out-Null
        
        $deleteResponse = Get-Content temp-delete-response.json -Raw | ConvertFrom-Json
        
        if ($deleteResponse.body) {
            $deleteBodyJson = $deleteResponse.body | ConvertFrom-Json
            
            if ($deleteBodyJson.success) {
                Write-Host ""
                Write-Host "SUCCES !" -ForegroundColor Green
                Write-Host "  Message: $($deleteBodyJson.message)" -ForegroundColor Gray
                Write-Host "  Nombre supprime: $($deleteBodyJson.deleted_count)" -ForegroundColor Gray
                Write-Host "  Compte garde: $($deleteBodyJson.kept_account.email)" -ForegroundColor Gray
                Write-Host ""
                
                # Vérifier le résultat
                Write-Host "Verification du resultat..." -ForegroundColor Yellow
                
                $verifyPayload = @{
                    httpMethod = "GET"
                    path = "/api/admin/list-users"
                    rawPath = "/api/admin/list-users"
                    headers = @{
                        "Host" = "j33osy4bvj.execute-api.eu-west-1.amazonaws.com"
                        "Content-Type" = "application/json"
                    }
                    queryStringParameters = $null
                    body = $null
                    requestContext = @{
                        http = @{
                            method = "GET"
                            path = "/default/api/admin/list-users"
                        }
                    }
                } | ConvertTo-Json -Depth 10 -Compress
                
                $verifyPayloadFile = "temp-verify-payload.json"
                $verifyPayload | Out-File -FilePath $verifyPayloadFile -Encoding UTF8
                
                aws lambda invoke `
                    --function-name $functionName `
                    --region $region `
                    --payload file://$verifyPayloadFile `
                    --cli-binary-format raw-in-base64-out `
                    temp-verify-response.json 2>&1 | Out-Null
                
                $verifyResponse = Get-Content temp-verify-response.json -Raw | ConvertFrom-Json
                
                if ($verifyResponse.body) {
                    $verifyBodyJson = $verifyResponse.body | ConvertFrom-Json
                    
                    if ($verifyBodyJson.users -and $verifyBodyJson.users.Count -eq 1) {
                        $remainingUser = $verifyBodyJson.users[0]
                        Write-Host ""
                        Write-Host "VERIFICATION OK: Un seul compte reste" -ForegroundColor Green
                        Write-Host "  Email: $($remainingUser.email)" -ForegroundColor White
                        Write-Host "  Username: $($remainingUser.username)" -ForegroundColor Gray
                    } else {
                        Write-Host ""
                        Write-Host "ATTENTION: Il reste $($verifyBodyJson.users.Count) comptes au lieu de 1" -ForegroundColor Red
                    }
                }
                
                Remove-Item temp-verify-payload.json -ErrorAction SilentlyContinue
                Remove-Item temp-verify-response.json -ErrorAction SilentlyContinue
            } else {
                Write-Host "ERREUR: $($deleteBodyJson.error)" -ForegroundColor Red
            }
        } else {
            Write-Host "ERREUR: Reponse invalide" -ForegroundColor Red
            Write-Host "Reponse: $($deleteResponse | ConvertTo-Json -Depth 10)" -ForegroundColor Gray
        }
    } catch {
        Write-Host "ERREUR lors de la suppression:" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
    } finally {
        Remove-Item temp-delete-except-payload.json -ErrorAction SilentlyContinue
        Remove-Item temp-delete-response.json -ErrorAction SilentlyContinue
    }
}

# Nettoyer tous les fichiers temporaires
Remove-Item temp-list-response.json -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "TERMINE" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

