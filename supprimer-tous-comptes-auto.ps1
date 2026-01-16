# Script PowerShell pour supprimer TOUS les comptes AUTOMATIQUEMENT
# ATTENTION: Cette opération est IRRÉVERSIBLE

$API_BASE = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api"

Write-Host "=== SUPPRESSION AUTOMATIQUE DE TOUS LES COMPTES ===" -ForegroundColor Red
Write-Host ""

# Afficher le nombre de comptes avant suppression
try {
    Write-Host "Vérification du nombre de comptes..." -ForegroundColor Yellow
    $listResponse = Invoke-RestMethod -Uri "$API_BASE/admin/list-users" -Method GET -ErrorAction Stop
    
    $userCount = $listResponse.count
    Write-Host ""
    Write-Host "Nombre de comptes à supprimer: $userCount" -ForegroundColor Cyan
    
    if ($userCount -gt 0) {
        Write-Host ""
        Write-Host "Comptes qui seront supprimés:" -ForegroundColor Yellow
        foreach ($user in $listResponse.users) {
            $role = if ($user.role) { $user.role } else { "user" }
            Write-Host "  - $($user.email) ($($user.username)) [role: $role]" -ForegroundColor Gray
        }
    } else {
        Write-Host ""
        Write-Host "Aucun compte à supprimer." -ForegroundColor Green
        exit 0
    }
    
} catch {
    Write-Host "⚠️  Impossible de lister les comptes, continuation..." -ForegroundColor Yellow
    Write-Host "   Erreur: $($_.Exception.Message)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Suppression de tous les comptes en cours..." -ForegroundColor Yellow

$body = @{
    confirm = "yes"
} | ConvertTo-Json

try {
    $response = Invoke-RestMethod -Uri "$API_BASE/admin/delete-all-users-simple" `
        -Method POST `
        -ContentType "application/json" `
        -Body $body `
        -ErrorAction Stop
    
    Write-Host ""
    Write-Host "✅ SUCCÈS!" -ForegroundColor Green
    Write-Host "   Tous les comptes ont été supprimés avec succès" -ForegroundColor Green
    Write-Host "   Nombre de comptes supprimés: $($response.deleted_count)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "⚠️  ATTENTION: Il ne reste plus aucun compte dans la base de données." -ForegroundColor Yellow
    Write-Host "   Les nouveaux comptes créés seront automatiquement supprimés après création (mode test)." -ForegroundColor Yellow
    
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
            if ($errorData.warning) {
                Write-Host "   Avertissement: $($errorData.warning)" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "   Réponse brute: $responseBody" -ForegroundColor Red
        }
    } else {
        Write-Host "   $($_.Exception.Message)" -ForegroundColor Red
    }
    
    exit 1
}

Write-Host ""
Write-Host "=== FIN DE L'OPÉRATION ===" -ForegroundColor Cyan
