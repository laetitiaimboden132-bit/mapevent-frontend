# Script pour tester DIRECTEMENT la clé API SendGrid
# Nécessite que SENDGRID_API_KEY soit disponible localement

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "TEST DIRECT DE LA CLÉ API SENDGRID" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier si la clé est disponible dans les variables d'environnement
$sendgridKey = $env:SENDGRID_API_KEY

if ([string]::IsNullOrWhiteSpace($sendgridKey)) {
    Write-Host "⚠️  SENDGRID_API_KEY non trouvée dans les variables d'environnement" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Options:" -ForegroundColor Cyan
    Write-Host "   1. Définir temporairement: `$env:SENDGRID_API_KEY = 'votre-clé'" -ForegroundColor White
    Write-Host "   2. Ou tester via l'API Lambda (utilisez tester-sendgrid.ps1)" -ForegroundColor White
    Write-Host ""
    
    $useLambda = Read-Host "Voulez-vous tester via l'API Lambda à la place ? (O/N)"
    if ($useLambda -eq "O" -or $useLambda -eq "o") {
        Write-Host ""
        Write-Host "Exécution de tester-sendgrid.ps1..." -ForegroundColor Cyan
        & .\tester-sendgrid.ps1
        exit
    } else {
        Write-Host ""
        Write-Host "Pour tester directement SendGrid, vous devez avoir la clé API." -ForegroundColor Yellow
        Write-Host "Vous pouvez la récupérer depuis:" -ForegroundColor White
        Write-Host "   - AWS Lambda > Variables d'environnement" -ForegroundColor White
        Write-Host "   - SendGrid Dashboard > Settings > API Keys" -ForegroundColor White
        exit 1
    }
}

Write-Host "✅ Clé API SendGrid trouvée (longueur: $($sendgridKey.Length) caractères)" -ForegroundColor Green
Write-Host ""

# Tester la clé en appelant l'API SendGrid
Write-Host "[TEST] Vérification de la validité de la clé API..." -ForegroundColor Yellow
Write-Host ""

try {
    # Appel simple à l'API SendGrid pour vérifier la clé
    $headers = @{
        "Authorization" = "Bearer $sendgridKey"
        "Content-Type" = "application/json"
    }
    
    # Test 1: Vérifier les informations du compte
    Write-Host "Test 1: Vérification du compte SendGrid..." -ForegroundColor Cyan
    $userResponse = Invoke-RestMethod -Uri "https://api.sendgrid.com/v3/user/profile" `
        -Method GET `
        -Headers $headers `
        -ErrorAction Stop
    
    Write-Host "✅ Clé API VALIDE!" -ForegroundColor Green
    Write-Host "   Email du compte: $($userResponse.email)" -ForegroundColor White
    Write-Host "   Nom: $($userResponse.first_name) $($userResponse.last_name)" -ForegroundColor White
    Write-Host ""
    
    # Test 2: Envoyer un email de test
    Write-Host "Test 2: Envoi d'un email de test..." -ForegroundColor Cyan
    $testEmail = Read-Host "Entrez votre adresse email pour recevoir le test (ou appuyez sur Entrée pour annuler)"
    
    if (-not [string]::IsNullOrWhiteSpace($testEmail)) {
        $emailBody = @{
            personalizations = @(
                @{
                    to = @(
                        @{
                            email = $testEmail
                        }
                    )
                }
            )
            from = @{
                email = "noreply@mapevent.world"
                name = "MapEvent Test"
            }
            subject = "Test SendGrid - MapEventAI"
            content = @(
                @{
                    type = "text/plain"
                    value = "Ceci est un email de test depuis MapEventAI. Si vous recevez ce message, SendGrid est correctement configuré!"
                }
            )
        } | ConvertTo-Json -Depth 10
        
        $sendResponse = Invoke-RestMethod -Uri "https://api.sendgrid.com/v3/mail/send" `
            -Method POST `
            -Headers $headers `
            -Body $emailBody `
            -ErrorAction Stop
        
        Write-Host "✅ Email de test envoyé avec succès!" -ForegroundColor Green
        Write-Host "   Vérifiez votre boîte email: $testEmail" -ForegroundColor White
        Write-Host "   (Vérifiez aussi les spams)" -ForegroundColor Gray
    } else {
        Write-Host "⚠️  Test d'envoi annulé" -ForegroundColor Yellow
    }
    
} catch {
    Write-Host ""
    Write-Host "❌ ERREUR lors du test:" -ForegroundColor Red
    
    if ($_.Exception.Response) {
        $statusCode = $_.Exception.Response.StatusCode.value__
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        
        Write-Host "   Code HTTP: $statusCode" -ForegroundColor Red
        
        if ($statusCode -eq 401) {
            Write-Host "   ❌ Clé API INVALIDE ou EXPIRÉE" -ForegroundColor Red
            Write-Host "   Vérifiez que la clé API est correcte dans SendGrid" -ForegroundColor Yellow
        } elseif ($statusCode -eq 403) {
            Write-Host "   ❌ Permissions insuffisantes" -ForegroundColor Red
            Write-Host "   La clé API n'a pas les permissions nécessaires" -ForegroundColor Yellow
        } else {
            Write-Host "   Réponse: $responseBody" -ForegroundColor Red
        }
    } else {
        Write-Host "   $($_.Exception.Message)" -ForegroundColor Red
    }
    
    exit 1
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "FIN DU TEST" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
