# Script ULTRA-SIMPLE pour supprimer les comptes via l'API
# Pas besoin d'installer quoi que ce soit!

param(
    [string]$EmailAGarder = "",
    [string]$ApiUrl = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"
)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "SUPPRESSION DES COMPTES - METHODE ULTRA-SIMPLE" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Étape 1: Lister les comptes via l'API
Write-Host "ETAPE 1: Liste de tous les comptes..." -ForegroundColor Yellow
Write-Host ""

try {
    $listResponse = Invoke-RestMethod -Uri "$ApiUrl/api/admin/list-users" -Method GET -ErrorAction Stop
    
    Write-Host "Nombre de comptes trouves: $($listResponse.count)" -ForegroundColor Cyan
    Write-Host ""
    
    if ($listResponse.count -eq 0) {
        Write-Host "Aucun compte trouve. Rien a supprimer." -ForegroundColor Green
        exit 0
    }
    
    Write-Host "LISTE DES COMPTES:" -ForegroundColor Cyan
    foreach ($user in $listResponse.users) {
        $role = if ($user.role) { $user.role } else { "user" }
        $roleColor = if ($role -eq "director" -or $role -eq "admin") { "Green" } else { "White" }
        Write-Host "  - $($user.email) (role: $role)" -ForegroundColor $roleColor
    }
    
} catch {
    Write-Host "ERREUR: Impossible de lister les comptes via l'API" -ForegroundColor Red
    Write-Host "  $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "L'API retourne une erreur. Utilisez la methode SQL directe:" -ForegroundColor Yellow
    Write-Host "  1. Installez PostgreSQL client: https://www.postgresql.org/download/windows/" -ForegroundColor White
    Write-Host "  2. Utilisez le script: .\supprimer-comptes-powershell.ps1" -ForegroundColor White
    exit 1
}

Write-Host ""

# Étape 2: Demander quel compte garder
if ([string]::IsNullOrWhiteSpace($EmailAGarder)) {
    Write-Host "Quel compte voulez-vous GARDER?" -ForegroundColor Cyan
    Write-Host "  (Tapez l'email du compte a garder)" -ForegroundColor Yellow
    Write-Host "  (Ou laissez vide pour supprimer TOUS les comptes)" -ForegroundColor Yellow
    Write-Host ""
    $EmailAGarder = Read-Host "Email du compte a garder (ou laissez vide)"
}

Write-Host ""
Write-Host "ATTENTION: Cette operation est IRREVERSIBLE!" -ForegroundColor Red
Write-Host ""

if ([string]::IsNullOrWhiteSpace($EmailAGarder)) {
    Write-Host "Vous allez supprimer TOUS les comptes!" -ForegroundColor Red
} else {
    Write-Host "Vous allez garder: $EmailAGarder" -ForegroundColor Green
    Write-Host "Tous les autres comptes seront supprimes!" -ForegroundColor Red
}

Write-Host ""
$confirmation = Read-Host "Tapez 'OUI' en majuscules pour confirmer"

if ($confirmation -ne "OUI") {
    Write-Host "Annule." -ForegroundColor Yellow
    exit 0
}

Write-Host ""
Write-Host "Suppression en cours..." -ForegroundColor Yellow

# Supprimer les comptes un par un via l'API
$deletedCount = 0
$keptCount = 0

foreach ($user in $listResponse.users) {
    if ($user.email -eq $EmailAGarder) {
        Write-Host "  GARDE: $($user.email)" -ForegroundColor Green
        $keptCount++
    } else {
        try {
            # Essayer de supprimer via l'endpoint admin/delete-user
            $deleteBody = @{
                email = $user.email
            } | ConvertTo-Json
            
            $deleteResponse = Invoke-RestMethod -Uri "$ApiUrl/api/admin/delete-user" `
                -Method POST `
                -ContentType "application/json" `
                -Body $deleteBody `
                -ErrorAction Stop
            
            Write-Host "  SUPPRIME: $($user.email)" -ForegroundColor Gray
            $deletedCount++
        } catch {
            Write-Host "  ERREUR pour $($user.email): $($_.Exception.Message)" -ForegroundColor Yellow
        }
    }
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "TERMINE!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host "  Comptes supprimes: $deletedCount" -ForegroundColor White
Write-Host "  Comptes gardes: $keptCount" -ForegroundColor White
Write-Host ""


