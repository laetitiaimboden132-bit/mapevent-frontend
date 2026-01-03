# Ajouter les permissions Lambda pour OPTIONS sur les endpoints OAuth

$FUNCTION_NAME = "mapevent-backend"
$API_ID = "j33osy4bvj"
$ACCOUNT_ID = "818127249940"
$REGION = "eu-west-1"

Write-Host "Ajout des permissions Lambda pour OPTIONS..." -ForegroundColor Cyan

# Endpoints OAuth
$endpoints = @(
    "/api/user/oauth/google",
    "/api/user/oauth/google/complete"
)

foreach ($endpointPath in $endpoints) {
    $sourceArn = "arn:aws:execute-api:$REGION`:$ACCOUNT_ID`:$API_ID`/*/OPTIONS$endpointPath"
    
    Write-Host ""
    Write-Host "Ajout permission pour: OPTIONS $endpointPath" -ForegroundColor Yellow
    Write-Host "Source ARN: $sourceArn" -ForegroundColor Gray
    
    try {
        aws lambda add-permission `
            --function-name $FUNCTION_NAME `
            --statement-id "allow-options-$($endpointPath.Replace('/','-').Replace('_','-'))-$(Get-Date -Format 'yyyyMMddHHmmss')" `
            --action "lambda:InvokeFunction" `
            --principal "apigateway.amazonaws.com" `
            --source-arn $sourceArn `
            --region $REGION | Out-Null
        
        Write-Host "  OK: Permission ajoutee" -ForegroundColor Green
    } catch {
        $errorMsg = $_.Exception.Message
        if ($errorMsg -like "*already exists*") {
            Write-Host "  INFO: Permission existe deja" -ForegroundColor Yellow
        } else {
            Write-Host "  ERREUR: $errorMsg" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "Permissions ajoutees avec succes !" -ForegroundColor Green

