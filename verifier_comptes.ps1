# Script pour vérifier les comptes restants
$API_BASE = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api"

Write-Host "=== VÉRIFICATION DES COMPTES ===" -ForegroundColor Cyan
Write-Host ""

try {
    $listResponse = Invoke-RestMethod -Uri "$API_BASE/admin/list-users" -Method GET -ErrorAction Stop
    
    $userCount = $listResponse.count
    Write-Host "Nombre de comptes: $userCount" -ForegroundColor Cyan
    
    if ($userCount -gt 0) {
        Write-Host ""
        Write-Host "Comptes existants:" -ForegroundColor Yellow
        foreach ($user in $listResponse.users) {
            $role = if ($user.role) { $user.role } else { "user" }
            Write-Host "  - $($user.email) ($($user.username)) [role: $role]" -ForegroundColor Gray
        }
    } else {
        Write-Host ""
        Write-Host "✅ Aucun compte dans la base de données!" -ForegroundColor Green
    }
    
} catch {
    Write-Host "❌ Erreur: $($_.Exception.Message)" -ForegroundColor Red
}
