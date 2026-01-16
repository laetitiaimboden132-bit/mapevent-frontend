# Script pour créer un compte administrateur directement

param(
    [string]$Email = "",
    [string]$Password = "",
    [string]$Username = "",
    [string]$FirstName = "",
    [string]$LastName = "",
    [string]$ApiUrl = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"
)

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "CREATION D'UN COMPTE ADMINISTRATEUR" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier les paramètres
if ([string]::IsNullOrWhiteSpace($Email)) {
    Write-Host "ERREUR: Email requis" -ForegroundColor Red
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\creer-compte-admin.ps1 -Email 'admin@example.com' -Password 'MotDePasse123!@#' -Username 'admin' -FirstName 'Admin' -LastName 'User'" -ForegroundColor White
    exit 1
}

if ([string]::IsNullOrWhiteSpace($Password)) {
    Write-Host "ERREUR: Mot de passe requis" -ForegroundColor Red
    Write-Host ""
    Write-Host "Le mot de passe doit contenir:" -ForegroundColor Yellow
    Write-Host "  - Au moins 12 caracteres" -ForegroundColor White
    Write-Host "  - Au moins une majuscule" -ForegroundColor White
    Write-Host "  - Au moins une minuscule" -ForegroundColor White
    Write-Host "  - Au moins un chiffre" -ForegroundColor White
    Write-Host "  - Au moins un caractere special (!@#`$%^&*...)" -ForegroundColor White
    exit 1
}

if ([string]::IsNullOrWhiteSpace($Username)) {
    $Username = $Email.Split('@')[0]
    Write-Host "Username non fourni, utilisation de: $Username" -ForegroundColor Yellow
}

if ([string]::IsNullOrWhiteSpace($FirstName)) {
    $FirstName = "Admin"
    Write-Host "Prenom non fourni, utilisation de: $FirstName" -ForegroundColor Yellow
}

if ([string]::IsNullOrWhiteSpace($LastName)) {
    $LastName = "User"
    Write-Host "Nom non fourni, utilisation de: $LastName" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Creation du compte administrateur..." -ForegroundColor Cyan
Write-Host "  Email: $Email" -ForegroundColor White
Write-Host "  Username: $Username" -ForegroundColor White
Write-Host "  Nom: $FirstName $LastName" -ForegroundColor White
Write-Host ""

# Étape 1: Envoyer le code de vérification email
Write-Host "Etape 1: Envoi du code de verification email..." -ForegroundColor Yellow
try {
    $verifyBody = @{
        email = $Email
    } | ConvertTo-Json
    
    $verifyResponse = Invoke-RestMethod -Uri "$ApiUrl/api/user/send-verification-code" `
        -Method POST `
        -ContentType "application/json" `
        -Body $verifyBody `
        -ErrorAction Stop
    
    Write-Host "  Code de verification envoye!" -ForegroundColor Green
    Write-Host ""
    Write-Host "  IMPORTANT: Vous devez recuperer le code de verification depuis:" -ForegroundColor Yellow
    Write-Host "  - Votre email" -ForegroundColor White
    Write-Host "  - Ou Redis (si vous y avez acces)" -ForegroundColor White
    Write-Host ""
    Write-Host "  Le code est a 6 chiffres et est valide pendant quelques minutes." -ForegroundColor Gray
    Write-Host ""
    
    $verificationCode = Read-Host "Entrez le code de verification (6 chiffres)"
    
} catch {
    Write-Host "  ERREUR: Impossible d'envoyer le code de verification" -ForegroundColor Red
    Write-Host "  $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "  NOTE: Si vous avez deja un compte, vous pouvez essayer de vous connecter directement." -ForegroundColor Yellow
    Write-Host "  Ou si Redis n'est pas accessible, vous devrez peut-etre creer le compte via l'interface web." -ForegroundColor Yellow
    exit 1
}

# Étape 2: Créer le compte
Write-Host ""
Write-Host "Etape 2: Creation du compte..." -ForegroundColor Yellow
try {
    $registerBody = @{
        email = $Email
        username = $Username
        password = $Password
        firstName = $FirstName
        lastName = $LastName
        avatarId = 1
        avatarEmoji = "👤"
        verificationCode = $verificationCode
        addresses = @()
    } | ConvertTo-Json
    
    $registerResponse = Invoke-RestMethod -Uri "$ApiUrl/api/user/register" `
        -Method POST `
        -ContentType "application/json" `
        -Body $registerBody `
        -ErrorAction Stop
    
    Write-Host "  SUCCES: Compte cree!" -ForegroundColor Green
    Write-Host "  User ID: $($registerResponse.userId)" -ForegroundColor Gray
    Write-Host ""
    
    # Étape 3: Modifier le rôle en "director" (nécessite un endpoint admin ou accès direct à la DB)
    Write-Host "Etape 3: Modification du role en 'director'..." -ForegroundColor Yellow
    Write-Host "  ATTENTION: Cette etape necessite un acces admin ou a la base de donnees." -ForegroundColor Yellow
    Write-Host "  Le compte a ete cree mais avec le role 'user' par defaut." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "  Pour le mettre en 'director', vous devez:" -ForegroundColor Cyan
    Write-Host "  1. Vous connecter avec ce compte" -ForegroundColor White
    Write-Host "  2. Modifier le role dans la base de donnees directement" -ForegroundColor White
    Write-Host "     UPDATE users SET role = 'director' WHERE email = '$Email';" -ForegroundColor Gray
    Write-Host ""
    Write-Host "  OU utiliser un compte existant avec le role 'director' pour modifier ce compte." -ForegroundColor White
    
} catch {
    Write-Host "  ERREUR: Impossible de creer le compte" -ForegroundColor Red
    Write-Host "  $($_.Exception.Message)" -ForegroundColor Red
    
    if ($_.ErrorDetails.Message) {
        try {
            $errorJson = $_.ErrorDetails.Message | ConvertFrom-Json
            Write-Host "  Details: $($errorJson.error)" -ForegroundColor Yellow
            if ($errorJson.code -eq "EMAIL_ALREADY_EXISTS") {
                Write-Host ""
                Write-Host "  Le compte existe deja! Vous pouvez essayer de vous connecter:" -ForegroundColor Yellow
                Write-Host "  .\test-connexion-api.ps1 -Email '$Email' -Password 'votre-mot-de-passe'" -ForegroundColor White
            }
        } catch {
            Write-Host "  Details bruts: $($_.ErrorDetails.Message)" -ForegroundColor Yellow
        }
    }
    
    exit 1
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "COMPTE CREE AVEC SUCCES" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "PROCHAINES ETAPES:" -ForegroundColor Cyan
Write-Host "  1. Modifier le role en 'director' dans la base de donnees" -ForegroundColor Yellow
Write-Host "  2. Vous connecter avec ce compte" -ForegroundColor Yellow
Write-Host "  3. Supprimer tous les comptes si necessaire" -ForegroundColor Yellow
Write-Host ""



