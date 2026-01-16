# Script pour vérifier l'état actuel des comptes utilisateurs

param(
    [string]$ApiUrl = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"
)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "VERIFICATION DE L'ETAT DES COMPTES UTILISATEURS" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Vérifier que l'API est accessible
Write-Host "Test 1: Verification de l'accessibilite de l'API..." -ForegroundColor Yellow
try {
    $testResponse = Invoke-WebRequest -Uri "$ApiUrl/api/user/exists?email=test@test.com" -Method GET -ErrorAction SilentlyContinue
    Write-Host "  OK: L'API est accessible" -ForegroundColor Green
} catch {
    Write-Host "  ATTENTION: L'API ne semble pas accessible" -ForegroundColor Red
    Write-Host "  URL testee: $ApiUrl" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Voulez-vous continuer quand meme? (O/N)" -ForegroundColor Yellow
    $continue = Read-Host
    if ($continue -ne "O" -and $continue -ne "o") {
        exit 1
    }
}

Write-Host ""

# Test 2: Lister les utilisateurs (si endpoint admin existe)
Write-Host "Test 2: Tentative de lister les utilisateurs..." -ForegroundColor Yellow
try {
    $listResponse = Invoke-RestMethod -Uri "$ApiUrl/api/admin/list-users" -Method GET -ErrorAction Stop
    Write-Host "  SUCCES: Liste des utilisateurs obtenue" -ForegroundColor Green
    Write-Host ""
    Write-Host "Nombre d'utilisateurs trouves: $($listResponse.count)" -ForegroundColor Cyan
    Write-Host ""
    
    if ($listResponse.count -eq 0) {
        Write-Host "  AUCUN COMPTE UTILISATEUR TROUVE" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "  ACTION REQUISE:" -ForegroundColor Cyan
        Write-Host "  Vous devez creer un compte administrateur avant de pouvoir supprimer les comptes." -ForegroundColor Yellow
        Write-Host "  (Ou les comptes ont deja ete supprimes)" -ForegroundColor Gray
    } else {
        Write-Host "  LISTE DES UTILISATEURS:" -ForegroundColor Cyan
        Write-Host ""
        foreach ($user in $listResponse.users) {
            $role = if ($user.role) { $user.role } else { "user" }
            $roleColor = if ($role -eq "director" -or $role -eq "admin") { "Green" } else { "White" }
            Write-Host "  - Email: $($user.email)" -ForegroundColor White
            Write-Host "    Username: $($user.username)" -ForegroundColor Gray
            Write-Host "    Role: $role" -ForegroundColor $roleColor
            Write-Host "    Cree le: $($user.created_at)" -ForegroundColor Gray
            Write-Host ""
        }
        
        # Vérifier s'il y a un administrateur
        $admins = $listResponse.users | Where-Object { $_.role -eq "director" -or $_.role -eq "admin" }
        if ($admins.Count -eq 0) {
            Write-Host "  ATTENTION: AUCUN ADMINISTRATEUR TROUVE" -ForegroundColor Red
            Write-Host ""
            Write-Host "  ACTION REQUISE:" -ForegroundColor Cyan
            Write-Host "  Vous devez creer un compte avec le role 'director' ou 'admin' pour pouvoir supprimer les comptes." -ForegroundColor Yellow
        } else {
            Write-Host "  ADMINISTRATEURS TROUVES: $($admins.Count)" -ForegroundColor Green
            Write-Host ""
            Write-Host "  Vous pouvez utiliser l'un de ces comptes pour supprimer tous les comptes:" -ForegroundColor Cyan
            foreach ($admin in $admins) {
                Write-Host "    - $($admin.email) (role: $($admin.role))" -ForegroundColor Green
            }
        }
    }
    
} catch {
    Write-Host "  ATTENTION: Impossible de lister les utilisateurs" -ForegroundColor Yellow
    Write-Host "  (L'endpoint /api/admin/list-users peut ne pas exister ou ne pas etre accessible)" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  Erreur: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "RESUME" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

if ($listResponse -and $listResponse.count -gt 0) {
    $admins = $listResponse.users | Where-Object { $_.role -eq "director" -or $_.role -eq "admin" }
    
    if ($admins.Count -gt 0) {
        Write-Host "STATUT: Comptes trouves, administrateurs disponibles" -ForegroundColor Green
        Write-Host ""
        Write-Host "PROCHAINE ETAPE:" -ForegroundColor Cyan
        Write-Host "  Utilisez l'un des comptes administrateur pour supprimer tous les comptes:" -ForegroundColor Yellow
        Write-Host "  .\supprimer-tous-comptes.ps1 -Email 'email-admin@example.com' -Password 'motdepasse' -Confirm 'OUI'" -ForegroundColor White
    } else {
        Write-Host "STATUT: Comptes trouves, MAIS aucun administrateur" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "PROCHAINE ETAPE:" -ForegroundColor Cyan
        Write-Host "  Vous devez d'abord creer un compte administrateur ou modifier le role d'un compte existant." -ForegroundColor Yellow
    }
} else {
    Write-Host "STATUT: Aucun compte trouve (ou endpoint non accessible)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "PROCHAINE ETAPE:" -ForegroundColor Cyan
    Write-Host "  Soit les comptes ont deja ete supprimes, soit vous devez creer un compte administrateur." -ForegroundColor Yellow
}

Write-Host ""



