# Script PowerShell pour creer les tables directement via Lambda

Write-Host "Creation des tables via Lambda..." -ForegroundColor Cyan
Write-Host ""

$lambdaFunctionName = "mapevent-backend"

# Creer le payload JSON sur une seule ligne
$payload = '{"path":"/api/admin/create-tables","httpMethod":"POST","headers":{"Content-Type":"application/json"},"body":"{}"}'

Write-Host "Envoi de la requete a Lambda..." -ForegroundColor Yellow
Write-Host "Fonction: $lambdaFunctionName" -ForegroundColor Gray
Write-Host ""

try {
    $null = aws lambda invoke --function-name $lambdaFunctionName --payload $payload --region eu-west-1 --cli-binary-format raw-in-base64-out response.json 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Requete envoyee avec succes!" -ForegroundColor Green
        Write-Host ""
        Write-Host "Reponse:" -ForegroundColor Cyan
        
        if (Test-Path "response.json") {
            $responseContent = Get-Content "response.json" -Raw | ConvertFrom-Json
            
            if ($responseContent.statusCode) {
                $statusColor = if ($responseContent.statusCode -eq 200) { "Green" } else { "Red" }
                Write-Host "Status: $($responseContent.statusCode)" -ForegroundColor $statusColor
            }
            
            if ($responseContent.body) {
                try {
                    $bodyObj = $responseContent.body | ConvertFrom-Json
                    Write-Host ""
                    Write-Host ($bodyObj | ConvertTo-Json -Depth 10) -ForegroundColor White
                } catch {
                    Write-Host $responseContent.body -ForegroundColor White
                }
            } else {
                Write-Host ($responseContent | ConvertTo-Json -Depth 10) -ForegroundColor White
            }
            
            Remove-Item "response.json" -ErrorAction SilentlyContinue
        }
        
        Write-Host ""
        Write-Host "Tables creees avec succes !" -ForegroundColor Green
        
    } else {
        Write-Host "Erreur lors de l'appel Lambda" -ForegroundColor Red
        Write-Host ""
        Write-Host "Verifiez que AWS CLI est installe et configure:" -ForegroundColor Yellow
        Write-Host "  1. Telechargez AWS CLI depuis: https://aws.amazon.com/cli/" -ForegroundColor White
        Write-Host "  2. Installez-le" -ForegroundColor White
        Write-Host "  3. Configurez avec: aws configure" -ForegroundColor White
    }
} catch {
    Write-Host "Erreur: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Assurez-vous que:" -ForegroundColor Yellow
    Write-Host "   1. AWS CLI est installe" -ForegroundColor White
    Write-Host "   2. Vous etes connecte (aws configure)" -ForegroundColor White
    Write-Host "   3. Le nom de la fonction Lambda est correct: $lambdaFunctionName" -ForegroundColor White
}
