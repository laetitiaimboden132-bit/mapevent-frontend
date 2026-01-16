# Script PowerShell pour supprimer les comptes de test
# Usage: .\delete_test_accounts.ps1

$API_BASE = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api"

Write-Host "=== SUPPRESSION COMPTES DE TEST - MapEventAI ===" -ForegroundColor Cyan
Write-Host ""

# ============================================
# CONFIGURATION
# ============================================

# OPTION 1 : Supprimer des emails spécifiques
# MODIFIEZ CETTE LISTE avec vos emails de test
$testEmails = @(
    # Ajoutez ici vos emails de test...
    # Exemple:
    # "test1@gmail.com",
    # "test2@gmail.com",
    # "test3@outlook.com"
)

# OPTION 2 : Supprimer TOUS les comptes SAUF un email (PLUS SÛR)
# Mettre $deleteAllExcept = $true pour activer cette option
$deleteAllExcept = $false  # Mettre à $true pour activer
$keepEmail = "votre.email.principal@example.com"  # Garder SEULEMENT cet email

Write-Host "Mode: " -NoNewline
if ($deleteAllExcept) {
    Write-Host "Supprimer TOUS les comptes SAUF un email" -ForegroundColor Yellow
    Write-Host "Email à garder: $keepEmail" -ForegroundColor Gray
} else {
    Write-Host "Supprimer des emails spécifiques" -ForegroundColor Yellow
    if ($testEmails.Count -eq 0) {
        Write-Host "⚠️  AUCUN EMAIL DÉFINI dans `$testEmails !" -ForegroundColor Red
        Write-Host "   Modifiez le script pour ajouter vos emails de test." -ForegroundColor Yellow
        exit 1
    }
    Write-Host "Nombre d'emails à supprimer: $($testEmails.Count)" -ForegroundColor Gray
    Write-Host "Emails: $($testEmails -join ', ')" -ForegroundColor DarkGray
}

Write-Host ""
Write-Host "⚠️  ATTENTION: Cette action est IRRÉVERSIBLE!" -ForegroundColor Red
$confirm = Read-Host "Tapez 'OUI' pour confirmer"

if ($confirm -ne "OUI") {
    Write-Host "❌ Opération annulée" -ForegroundColor Yellow
    exit 0
}

Write-Host ""

if ($deleteAllExcept) {
    # Mode: Supprimer tous SAUF certains
    Write-Host "[MODE] Suppression de tous les comptes SAUF ceux spécifiés..." -ForegroundColor Yellow
    
    $body = @{
        keepEmail = $keepEmail
    } | ConvertTo-Json
    
    try {
        $response = Invoke-WebRequest -Uri "$API_BASE/admin/delete-all-users-except" `
            -Method POST `
            -Headers @{"Content-Type"="application/json"} `
            -Body $body `
            -ErrorAction Stop
        
        $result = $response.Content | ConvertFrom-Json
        Write-Host "✅ Tous les comptes supprimés SAUF: $keepEmail" -ForegroundColor Green
        Write-Host "   Nombre de comptes supprimés: $($result.deleted_count)" -ForegroundColor Gray
        Write-Host "   Compte conservé: $($result.kept_account.email) ($($result.kept_account.username))" -ForegroundColor Gray
        
    } catch {
        Write-Host "❌ Erreur lors de la suppression:" -ForegroundColor Red
        if ($_.Exception.Response) {
            $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
            $responseBody = $reader.ReadToEnd()
            Write-Host "   $responseBody" -ForegroundColor Red
        } else {
            Write-Host "   $($_.Exception.Message)" -ForegroundColor Red
        }
        exit 1
    }
    
} else {
    # Mode: Supprimer des emails spécifiques
    Write-Host "[MODE] Suppression de comptes spécifiques..." -ForegroundColor Yellow
    Write-Host ""
    
    $successCount = 0
    $errorCount = 0
    $notFoundCount = 0
    
    foreach ($email in $testEmails) {
        Write-Host "Suppression de: $email..." -NoNewline -ForegroundColor Gray
        
        $body = @{
            email = $email
        } | ConvertTo-Json
        
        try {
            # NOTE: Si l'endpoint nécessite un token admin, ajoutez-le ici :
            # -Headers @{
            #     "Authorization" = "Bearer VOTRE_TOKEN_ADMIN"
            #     "Content-Type" = "application/json"
            # }
            
            $response = Invoke-WebRequest -Uri "$API_BASE/admin/delete-user" `
                -Method POST `
                -Headers @{"Content-Type"="application/json"} `
                -Body $body `
                -ErrorAction Stop
            
            $result = $response.Content | ConvertFrom-Json
            
            Write-Host " ✅ Supprimé" -ForegroundColor Green
            Write-Host "   ID: $($result.deleted_user.id), Username: $($result.deleted_user.username)" -ForegroundColor DarkGray
            Write-Host "   Données supprimées: $($result.deleted_data.likes) likes, $($result.deleted_data.favorites) favs" -ForegroundColor DarkGray
            $successCount++
            
        } catch {
            if ($_.Exception.Response.StatusCode -eq 404) {
                Write-Host " ⚠️  Non trouvé" -ForegroundColor Yellow
                $notFoundCount++
            } else {
                Write-Host " ❌ Erreur" -ForegroundColor Red
                if ($_.Exception.Response) {
                    $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
                    $responseBody = $reader.ReadToEnd()
                    Write-Host "   $responseBody" -ForegroundColor Red
                } else {
                    Write-Host "   $($_.Exception.Message)" -ForegroundColor Red
                }
                $errorCount++
            }
        }
        
        # Petite pause entre les suppressions
        Start-Sleep -Milliseconds 200
    }
    
    Write-Host ""
    Write-Host "=== RÉSUMÉ ===" -ForegroundColor Cyan
    Write-Host "✅ Supprimés: $successCount" -ForegroundColor Green
    Write-Host "⚠️  Non trouvés: $notFoundCount" -ForegroundColor Yellow
    Write-Host "❌ Erreurs: $errorCount" -ForegroundColor Red
}

Write-Host ""
Write-Host "✅ Opération terminée!" -ForegroundColor Green
