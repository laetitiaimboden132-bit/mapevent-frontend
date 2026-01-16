# Script PowerShell pour supprimer TOUS les comptes automatiquement
# Usage: .\supprimer_tout_auto.ps1

$API_BASE = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api"

Write-Host "=== SUPPRESSION DE TOUS LES COMPTES ===" -ForegroundColor Red
Write-Host ""

# Lister les comptes avant suppression
try {
    Write-Host "Vérification des comptes..." -ForegroundColor Yellow
    $listResponse = Invoke-RestMethod -Uri "$API_BASE/admin/list-users" -Method GET -ErrorAction Stop
    
    $userCount = $listResponse.count
    Write-Host "Nombre de comptes trouvés: $userCount" -ForegroundColor Cyan
    
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
}

Write-Host ""
Write-Host "Suppression en cours..." -ForegroundColor Yellow

# Supprimer tous les comptes
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
    Write-Host "⚠️  Il ne reste plus aucun compte dans la base de données." -ForegroundColor Yellow
    Write-Host "   Vous devrez créer un nouveau compte pour continuer." -ForegroundColor Yellow
    
} catch {
    Write-Host ""
    Write-Host "❌ ERREUR lors de la suppression:" -ForegroundColor Red
    Write-Host "   Message: $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        try {
            $statusCode = $_.Exception.Response.StatusCode
            Write-Host "   Code HTTP: $statusCode" -ForegroundColor Red
            
            $stream = $_.Exception.Response.GetResponseStream()
            $reader = New-Object System.IO.StreamReader($stream)
            $responseBody = $reader.ReadToEnd()
            $reader.Close()
            $stream.Close()
            
            Write-Host "   Réponse: $responseBody" -ForegroundColor Red
            
            try {
                $errorData = $responseBody | ConvertFrom-Json
                if ($errorData.error) {
                    Write-Host "   Erreur détaillée: $($errorData.error)" -ForegroundColor Red
                }
            } catch {
                # Pas un JSON, afficher tel quel
            }
        } catch {
            Write-Host "   Impossible de lire la réponse détaillée" -ForegroundColor Red
        }
    }
    
    Write-Host ""
    Write-Host "Stack trace:" -ForegroundColor DarkGray
    Write-Host $_.Exception.StackTrace -ForegroundColor DarkGray
    
    exit 1
}

Write-Host ""
Write-Host "=== FIN ===" -ForegroundColor Cyan
