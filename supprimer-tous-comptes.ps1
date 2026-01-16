# Script final pour supprimer tous les comptes via Lambda

$functionName = "mapevent-backend"
$region = "eu-west-1"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "SUPPRESSION DE TOUS LES COMPTES UTILISATEURS" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Créer le payload
$payload = @{
    httpMethod = "POST"
    path = "/api/admin/delete-all-users-simple"
    rawPath = "/api/admin/delete-all-users-simple"
    headers = @{
        "Host" = "j33osy4bvj.execute-api.eu-west-1.amazonaws.com"
        "Content-Type" = "application/json"
    }
    body = '{"confirm": "yes"}'
    requestContext = @{
        http = @{
            method = "POST"
            path = "/default/api/admin/delete-all-users-simple"
        }
    }
} | ConvertTo-Json -Depth 10 -Compress

$payloadFile = "supprimer-tous-payload.json"
$payload | Out-File -FilePath $payloadFile -Encoding UTF8

Write-Host "Suppression en cours..." -ForegroundColor Yellow

try {
    aws lambda invoke `
        --function-name $functionName `
        --region $region `
        --payload file://$payloadFile `
        --cli-binary-format raw-in-base64-out `
        supprimer-tous-response.json 2>&1 | Out-Null
    
    if (Test-Path supprimer-tous-response.json) {
        $response = Get-Content supprimer-tous-response.json -Raw | ConvertFrom-Json
        
        if ($response.body) {
            $bodyJson = $response.body | ConvertFrom-Json
            
            if ($bodyJson.success) {
                Write-Host ""
                Write-Host "============================================================" -ForegroundColor Green
                Write-Host "  SUCCES: TOUS LES COMPTES ONT ETE SUPPRIMES !" -ForegroundColor Green
                Write-Host "============================================================" -ForegroundColor Green
                Write-Host ""
                Write-Host "Nombre de comptes supprimes: $($bodyJson.deleted_count)" -ForegroundColor White
                Write-Host ""
            } else {
                Write-Host ""
                Write-Host "ERREUR:" -ForegroundColor Red
                $bodyJson | ConvertTo-Json -Depth 10
            }
        } else {
            Write-Host ""
            Write-Host "ERREUR: Pas de body dans la reponse" -ForegroundColor Red
            $response | ConvertTo-Json -Depth 10
        }
    } else {
        Write-Host ""
        Write-Host "ERREUR: Fichier de reponse non cree" -ForegroundColor Red
    }
} catch {
    Write-Host ""
    Write-Host "ERREUR: $_" -ForegroundColor Red
} finally {
    Remove-Item $payloadFile -ErrorAction SilentlyContinue
    Remove-Item supprimer-tous-response.json -ErrorAction SilentlyContinue
}

Write-Host ""
