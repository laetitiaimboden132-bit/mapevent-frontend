# Script PowerShell pour tester create-tables directement via Lambda
# Contourne API Gateway

Write-Host "🔧 Test direct de create-tables via Lambda" -ForegroundColor Cyan
Write-Host ""

# Remplacez par le nom de votre fonction Lambda
$lambdaFunctionName = "VOTRE_FONCTION_LAMBDA"

Write-Host "Fonction Lambda: $lambdaFunctionName" -ForegroundColor Yellow
Write-Host ""

# Créer le payload
$payload = @{
    path = "/api/admin/create-tables"
    httpMethod = "POST"
    headers = @{
        "Content-Type" = "application/json"
    }
    body = "{}"
} | ConvertTo-Json -Depth 10

Write-Host "📤 Envoi de la requête..." -ForegroundColor Green

try {
    # Appeler Lambda directement
    $response = aws lambda invoke `
        --function-name $lambdaFunctionName `
        --payload $payload `
        --region eu-west-1 `
        response.json
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Requête envoyée avec succès!" -ForegroundColor Green
        Write-Host ""
        Write-Host "📥 Réponse:" -ForegroundColor Cyan
        Get-Content response.json | ConvertFrom-Json | ConvertTo-Json -Depth 10
    } else {
        Write-Host "❌ Erreur lors de l'appel Lambda" -ForegroundColor Red
        Write-Host $response
    }
} catch {
    Write-Host "❌ Erreur: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Assurez-vous que:" -ForegroundColor Yellow
    Write-Host "   1. AWS CLI est installé" -ForegroundColor White
    Write-Host "   2. Vous êtes connecté (aws configure)" -ForegroundColor White
    Write-Host "   3. Le nom de la fonction Lambda est correct" -ForegroundColor White
}

