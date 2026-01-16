# Script PowerShell pour supprimer TOUS les comptes SAUF votre email principal
# Usage: .\supprimer_comptes_test.ps1

$API_BASE = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api"

Write-Host "=== SUPPRESSION DES COMPTES DE TEST ===" -ForegroundColor Cyan
Write-Host ""

# ⚠️ MODIFIEZ CETTE ADRESSE EMAIL AVANT DE LANCER LE SCRIPT ⚠️
# C'est l'email que vous voulez GARDER (tous les autres seront supprimés)
$emailAGarder = "laetitia.imboden132@gmail.com"

Write-Host "Mode: Supprimer TOUS les comptes SAUF cet email:" -ForegroundColor Yellow
Write-Host "  📧 $emailAGarder" -ForegroundColor Cyan
Write-Host ""
Write-Host "⚠️  ATTENTION: Cette action est IRRÉVERSIBLE!" -ForegroundColor Red
Write-Host "   Tous les comptes seront supprimés sauf: $emailAGarder" -ForegroundColor Yellow
Write-Host ""

$confirm = Read-Host "Tapez 'OUI' en majuscules pour confirmer"

if ($confirm -ne "OUI") {
    Write-Host "❌ Opération annulée" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Suppression en cours..." -ForegroundColor Yellow

$body = @{
    keepEmail = $emailAGarder
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "$API_BASE/admin/delete-all-users-except" `
        -Method POST `
        -Headers @{"Content-Type"="application/json"} `
        -Body $body `
        -ErrorAction Stop
    
    $result = $response.Content | ConvertFrom-Json
    
    Write-Host ""
    Write-Host "✅ SUCCÈS!" -ForegroundColor Green
    Write-Host "   Nombre de comptes supprimés: $($result.deleted_count)" -ForegroundColor Gray
    Write-Host "   Compte conservé: $($result.kept_account.email) ($($result.kept_account.username))" -ForegroundColor Gray
    Write-Host ""
    Write-Host "✅ Tous les comptes de test ont été supprimés!" -ForegroundColor Green
    
} catch {
    Write-Host ""
    Write-Host "❌ ERREUR lors de la suppression:" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        
        Write-Host "   Code: $statusCode" -ForegroundColor Red
        Write-Host "   Réponse: $responseBody" -ForegroundColor Red
        
        try {
            $errorData = $responseBody | ConvertFrom-Json
            if ($errorData.error) {
                Write-Host "   Erreur: $($errorData.error)" -ForegroundColor Red
            }
        } catch {
            Write-Host "   Réponse brute: $responseBody" -ForegroundColor Red
        }
    } else {
        Write-Host "   $($_.Exception.Message)" -ForegroundColor Red
    }
    
    exit 1
}
