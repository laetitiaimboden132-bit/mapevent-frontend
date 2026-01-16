# Script ULTRA-SIMPLE pour supprimer TOUS les comptes via l'API
# Pas besoin de modifier RDS, pas besoin de pgAdmin, RIEN!

param(
    [string]$Confirm = "",
    [string]$ApiUrl = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"
)

Write-Host "============================================================" -ForegroundColor Red
Write-Host "SUPPRESSION DE TOUS LES COMPTES" -ForegroundColor Red
Write-Host "============================================================" -ForegroundColor Red
Write-Host ""
Write-Host "ATTENTION: Cette operation va supprimer TOUS les comptes!" -ForegroundColor Red
Write-Host "Cette operation est IRREVERSIBLE!" -ForegroundColor Red
Write-Host ""

if ($Confirm -ne "OUI") {
    Write-Host "Pour confirmer, executez avec le parametre -Confirm 'OUI':" -ForegroundColor Yellow
    Write-Host "  .\supprimer-comptes-api.ps1 -Confirm 'OUI'" -ForegroundColor White
    Write-Host ""
    exit 0
}

Write-Host "Suppression de TOUS les comptes en cours..." -ForegroundColor Yellow

# Appeler l'API
$body = @{
    confirm = "yes"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$ApiUrl/api/admin/delete-all-users-simple" `
        -Method POST `
        -ContentType "application/json" `
        -Body $body `
        -ErrorAction Stop
    
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host "SUCCES!" -ForegroundColor Green
    Write-Host "============================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Tous les comptes ont ete supprimes!" -ForegroundColor Green
    Write-Host "Nombre de comptes supprimes: $($response.deleted_count)" -ForegroundColor White
    Write-Host ""
    Write-Host "Vous pouvez maintenant creer de nouveaux comptes avec le nouveau systeme professionnel!" -ForegroundColor Cyan
    Write-Host ""
    
} catch {
    Write-Host ""
    Write-Host "ERREUR:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    
    if ($_.ErrorDetails.Message) {
        try {
            $errorJson = $_.ErrorDetails.Message | ConvertFrom-Json
            Write-Host "Details: $($errorJson.error)" -ForegroundColor Yellow
        } catch {
            Write-Host "Details: $($_.ErrorDetails.Message)" -ForegroundColor Yellow
        }
    }
    
    exit 1
}

