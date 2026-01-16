# Script pour supprimer tous les comptes sauf un via l'API Lambda
# Utilise les endpoints existants qui sont dans le même VPC que RDS

$apiBaseUrl = "https://j33osy4bvj.execute-api.eu-west-1.amazonaws.com/default"

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "SUPPRESSION DES COMPTES - VIA API LAMBDA" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# ÉTAPE 1 : Lister tous les comptes
Write-Host "1. Liste de tous les comptes existants..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$apiBaseUrl/api/admin/list-users" -Method GET -ContentType "application/json"
    
    if ($response.users -and $response.users.Count -gt 0) {
        Write-Host ""
        Write-Host "Comptes trouves : $($response.users.Count)" -ForegroundColor Green
        Write-Host ""
        
        foreach ($user in $response.users) {
            $role = if ($user.role) { $user.role } else { "user" }
            $email = if ($user.email) { $user.email } else { "(pas d'email)" }
            $username = if ($user.username) { $user.username } else { "(pas de username)" }
            
            Write-Host "  - Email: $email" -ForegroundColor White
            Write-Host "    Username: $username" -ForegroundColor Gray
            Write-Host "    Role: $role" -ForegroundColor Gray
            Write-Host ""
        }
    } else {
        Write-Host "Aucun compte trouve." -ForegroundColor Yellow
        exit 0
    }
} catch {
    Write-Host "ERREUR lors de la liste des comptes :" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    
    if ($_.ErrorDetails.Message) {
        Write-Host "Details :" -ForegroundColor Yellow
        Write-Host $_.ErrorDetails.Message -ForegroundColor Gray
    }
    exit 1
}

# ÉTAPE 2 : Demander quel compte garder
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "2. Quel compte voulez-vous GARDER ?" -ForegroundColor Yellow
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
$keepEmail = Read-Host "Entrez l'email du compte a garder (ou laissez vide pour tout supprimer)"

if ([string]::IsNullOrWhiteSpace($keepEmail)) {
    Write-Host ""
    Write-Host "ATTENTION: Vous allez supprimer TOUS les comptes !" -ForegroundColor Red
    $confirm = Read-Host "Confirmez en tapant 'OUI' en majuscules"
    
    if ($confirm -ne "OUI") {
        Write-Host "Operation annulee." -ForegroundColor Yellow
        exit 0
    }
    
    # Supprimer tous les comptes
    Write-Host ""
    Write-Host "Suppression de TOUS les comptes..." -ForegroundColor Yellow
    try {
        $body = @{} | ConvertTo-Json
        $response = Invoke-RestMethod -Uri "$apiBaseUrl/api/admin/delete-all-users-simple" -Method POST -Body $body -ContentType "application/json"
        
        if ($response.success) {
            Write-Host ""
            Write-Host "SUCCES: Tous les comptes ont ete supprimes !" -ForegroundColor Green
            Write-Host "  Nombre supprime: $($response.deleted_count)" -ForegroundColor Gray
        } else {
            Write-Host "ERREUR: $($response.error)" -ForegroundColor Red
        }
    } catch {
        Write-Host "ERREUR lors de la suppression:" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        if ($_.ErrorDetails.Message) {
            Write-Host "Details: $($_.ErrorDetails.Message)" -ForegroundColor Gray
        }
    }
} else {
    # Supprimer tous sauf un
    Write-Host ""
    Write-Host "Suppression de tous les comptes SAUF: $keepEmail" -ForegroundColor Yellow
    $confirm = Read-Host "Confirmez en tapant 'OUI' en majuscules"
    
    if ($confirm -ne "OUI") {
        Write-Host "Operation annulee." -ForegroundColor Yellow
        exit 0
    }
    
    try {
        $body = @{
            keepEmail = $keepEmail
        } | ConvertTo-Json
        
        $response = Invoke-RestMethod -Uri "$apiBaseUrl/api/admin/delete-all-users-except" -Method POST -Body $body -ContentType "application/json"
        
        if ($response.success) {
            Write-Host ""
            Write-Host "SUCCES !" -ForegroundColor Green
            Write-Host "  Message: $($response.message)" -ForegroundColor Gray
            Write-Host "  Nombre supprime: $($response.deleted_count)" -ForegroundColor Gray
            Write-Host "  Compte garde: $($response.kept_account.email)" -ForegroundColor Gray
            Write-Host ""
            
            # Vérifier le résultat
            Write-Host "Verification du resultat..." -ForegroundColor Yellow
            $verifyResponse = Invoke-RestMethod -Uri "$apiBaseUrl/api/admin/list-users" -Method GET -ContentType "application/json"
            
            if ($verifyResponse.users -and $verifyResponse.users.Count -eq 1) {
                $remainingUser = $verifyResponse.users[0]
                Write-Host ""
                Write-Host "VERIFICATION OK: Un seul compte reste" -ForegroundColor Green
                Write-Host "  Email: $($remainingUser.email)" -ForegroundColor White
                Write-Host "  Username: $($remainingUser.username)" -ForegroundColor Gray
                Write-Host "  Role: $($remainingUser.role)" -ForegroundColor Gray
            } else {
                Write-Host ""
                Write-Host "ATTENTION: Il reste $($verifyResponse.users.Count) comptes au lieu de 1" -ForegroundColor Red
            }
        } else {
            Write-Host "ERREUR: $($response.error)" -ForegroundColor Red
        }
    } catch {
        Write-Host "ERREUR lors de la suppression:" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor Red
        if ($_.ErrorDetails.Message) {
            Write-Host "Details: $($_.ErrorDetails.Message)" -ForegroundColor Gray
        }
    }
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "TERMINE" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

