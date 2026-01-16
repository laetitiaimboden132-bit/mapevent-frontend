# Script PowerShell pour supprimer TOUS les comptes (y compris les admins)
# Usage: .\supprimer_tous_comptes.ps1

$API_BASE = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api"

Write-Host "=== SUPPRESSION DE TOUS LES COMPTES ===" -ForegroundColor Red
Write-Host ""

Write-Host "⚠️  ATTENTION ULTRA-IMPORTANTE:" -ForegroundColor Red
Write-Host "   Cette action va supprimer TOUS les comptes utilisateurs" -ForegroundColor Yellow
Write-Host "   y compris les comptes ADMIN et DIRECTOR!" -ForegroundColor Yellow
Write-Host "   Cette opération est COMPLÈTEMENT IRRÉVERSIBLE!" -ForegroundColor Red
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
Write-Host "============================================================" -ForegroundColor Red
Write-Host ""

$confirm1 = Read-Host "Êtes-vous ABSOLUMENT SÛR ? Tapez 'OUI' pour confirmer"

if ($confirm1 -ne "OUI") {
    Write-Host "❌ Opération annulée" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Dernière confirmation..." -ForegroundColor Red
$confirm2 = Read-Host "Tapez 'SUPPRIMER TOUT' en majuscules pour confirmer définitivement"

if ($confirm2 -ne "SUPPRIMER TOUT") {
    Write-Host "❌ Opération annulée" -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Suppression de tous les comptes en cours..." -ForegroundColor Yellow

$body = @{
    confirm = "yes"
} | ConvertTo-Json

try {
    $response = Invoke-WebRequest -Uri "$API_BASE/admin/delete-all-users-simple" `
        -Method POST `
        -Headers @{"Content-Type"="application/json"} `
        -Body $body `
        -ErrorAction Stop
    
    $result = $response.Content | ConvertFrom-Json
    
    Write-Host ""
    Write-Host "✅ SUCCÈS!" -ForegroundColor Green
    Write-Host "   Tous les comptes ont été supprimés avec succès" -ForegroundColor Green
    Write-Host "   Nombre de comptes supprimés: $($result.deleted_count)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "⚠️  ATTENTION: Il ne reste plus aucun compte dans la base de données." -ForegroundColor Yellow
    Write-Host "   Vous devrez créer un nouveau compte pour continuer à utiliser l'application." -ForegroundColor Yellow
    
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
