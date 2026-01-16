# Script pour supprimer un compte par email

param(
    [Parameter(Mandatory=$true)]
    [string]$Email
)

$API_BASE = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api"

Write-Host "Suppression du compte avec email: $Email" -ForegroundColor Cyan
Write-Host ""

# D'abord, lister tous les comptes pour trouver celui avec cet email
try {
    Write-Host "Recherche du compte..." -ForegroundColor Yellow
    $listResponse = Invoke-RestMethod -Uri "$API_BASE/admin/list-users" -Method GET -ErrorAction Stop
    
    $userToDelete = $listResponse.users | Where-Object { $_.email -eq $Email }
    
    if ($userToDelete) {
        Write-Host "Compte trouve:" -ForegroundColor Green
        Write-Host "   ID: $($userToDelete.id)" -ForegroundColor White
        Write-Host "   Email: $($userToDelete.email)" -ForegroundColor White
        Write-Host "   Username: $($userToDelete.username)" -ForegroundColor White
        Write-Host ""
        
        # Supprimer via l'endpoint admin
        $deleteBody = @{
            user_id = $userToDelete.id
        } | ConvertTo-Json
        
        Write-Host "Suppression en cours..." -ForegroundColor Yellow
        $deleteResponse = Invoke-RestMethod -Uri "$API_BASE/admin/delete-user" `
            -Method POST `
            -ContentType "application/json" `
            -Body $deleteBody `
            -ErrorAction Stop
        
        Write-Host "OK - Compte supprime avec succes!" -ForegroundColor Green
        Write-Host "   $($deleteResponse.message)" -ForegroundColor White
        
    } else {
        Write-Host "Aucun compte trouve avec cet email: $Email" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Comptes existants:" -ForegroundColor Cyan
        foreach ($user in $listResponse.users) {
            Write-Host "   - $($user.email) ($($user.username))" -ForegroundColor Gray
        }
    }
    
} catch {
    Write-Host "ERREUR:" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode.value__
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        $reader.Close()
        
        Write-Host "   Code HTTP: $statusCode" -ForegroundColor Red
        Write-Host "   Response: $responseBody" -ForegroundColor Red
    } else {
        Write-Host "   $($_.Exception.Message)" -ForegroundColor Red
    }
}
