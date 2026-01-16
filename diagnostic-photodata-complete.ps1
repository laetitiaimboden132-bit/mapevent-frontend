# Script de diagnostic complet pour photoData
# Vérifie tout le flux et ajoute des logs pour tracer où photoData est perdu

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DIAGNOSTIC COMPLET PHOTODATA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 1. Vérifier où la photo est sauvegardée lors de l'upload
Write-Host "`n[1/7] Vérification upload photo..." -ForegroundColor Yellow
$mapLogicPath = "public\map_logic.js"
$content = Get-Content $mapLogicPath -Raw -Encoding UTF8

# Chercher la fonction qui gère l'upload de photo
if ($content -match "function.*handleProPhotoUpload|handleProPhotoUpload.*function|onchange.*handleProPhotoUpload") {
    Write-Host "  ✅ Fonction handleProPhotoUpload trouvée" -ForegroundColor Green
    # Chercher où registerData.profilePhoto ou registerData.photoData est défini
    if ($content -match "registerData\.profilePhoto\s*=|registerData\.photoData\s*=") {
        Write-Host "  ✅ registerData.profilePhoto/photoData trouvé" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️ registerData.profilePhoto/photoData non trouvé - problème probable ici" -ForegroundColor Yellow
    }
} else {
    Write-Host "  ⚠️ Fonction handleProPhotoUpload non trouvée" -ForegroundColor Yellow
}

# 2. Vérifier si photoData est dans pendingRegisterData
Write-Host "`n[2/7] Vérification pendingRegisterData..." -ForegroundColor Yellow
if ($content -match "pendingRegisterData.*photoData") {
    Write-Host "  ✅ photoData présent dans pendingRegisterData" -ForegroundColor Green
} else {
    Write-Host "  ❌ photoData absent de pendingRegisterData" -ForegroundColor Red
}

# 3. Vérifier si photoData est envoyé dans requestBody OAuth Google
Write-Host "`n[3/7] Vérification auth.js..." -ForegroundColor Yellow
$authJsPath = "public\auth.js"
$authContent = Get-Content $authJsPath -Raw -Encoding UTF8

if ($authContent -match "requestBody\.photoData\s*=") {
    Write-Host "  ✅ photoData présent dans requestBody OAuth Google" -ForegroundColor Green
} else {
    Write-Host "  ❌ photoData absent de requestBody OAuth Google" -ForegroundColor Red
    Write-Host "  → Ajout photoData dans requestBody..." -ForegroundColor Gray
    # Ajouter photoData dans requestBody
    $pattern = '(?s)(if \(pendingData\.selectedAddress.*?}\];\s*\}\s*)(console\.log\(''\[OAUTH\] Inscription avec Google)'
    $replacement = '$1        // INCLURE photoData si disponible (photo uploadée lors de la création du profil)
        if (pendingData.photoData && pendingData.photoData !== ''null'' && pendingData.photoData !== null) {
          requestBody.photoData = pendingData.photoData;
          console.log(''[OAUTH] ✅ photoData inclus dans la requête OAuth Google:'', pendingData.photoData.substring(0, 50) + ''...'');
        }
        $2'
    $authContent = $authContent -replace $pattern, $replacement
    [System.IO.File]::WriteAllText($authJsPath, $authContent, [System.Text.Encoding]::UTF8)
    Write-Host "  ✅ photoData ajouté dans requestBody" -ForegroundColor Green
}

# 4. Vérifier si photoData est sauvegardé dans slimUser après connexion
Write-Host "`n[4/7] Vérification sauvegarde photoData dans slimUser..." -ForegroundColor Yellow
if ($authContent -match "photoData:\s*(window\.pendingRegisterData|syncData\.user\.photoData|pendingData)") {
    Write-Host "  ✅ photoData sauvegardé dans slimUser" -ForegroundColor Green
} else {
    Write-Host "  ❌ photoData non sauvegardé dans slimUser" -ForegroundColor Red
    Write-Host "  → Correction sauvegarde photoData..." -ForegroundColor Gray
    # Corriger la sauvegarde dans slimUser (ligne 2161 et 2249)
    $pattern = '(?s)(photoData:\s*)(pendingData\?\.photoData|syncData\.user\.photoData)(\s*\|\|\s*null)'
    $replacement = '$1window.pendingRegisterData?.photoData || syncData.user?.photoData || null'
    $authContent = $authContent -replace $pattern, $replacement
    [System.IO.File]::WriteAllText($authJsPath, $authContent, [System.Text.Encoding]::UTF8)
    Write-Host "  ✅ Sauvegarde photoData corrigée" -ForegroundColor Green
}

# 5. Vérifier backend - traitement photoData
Write-Host "`n[5/7] Vérification backend..." -ForegroundColor Yellow
$mainPyPath = "lambda-package\backend\main.py"
$mainPyContent = Get-Content $mainPyPath -Raw -Encoding UTF8

if ($mainPyContent -match "photo_data_from_form\s*=\s*data\.get\('photoData'") {
    Write-Host "  ✅ Traitement photoData présent dans backend" -ForegroundColor Green
} else {
    Write-Host "  ❌ Traitement photoData absent du backend" -ForegroundColor Red
}

if ($mainPyContent -match "'photoData':.*photo_data_from_form") {
    Write-Host "  ✅ photoData retourné dans user_data_dict" -ForegroundColor Green
} else {
    Write-Host "  ❌ photoData non retourné dans user_data_dict" -ForegroundColor Red
}

if ($mainPyContent -match '"photoData":.*user_row_or_dict\.get\("photoData"\)') {
    Write-Host "  ✅ photoData retourné dans build_user_slim" -ForegroundColor Green
} else {
    Write-Host "  ❌ photoData non retourné dans build_user_slim" -ForegroundColor Red
}

# 6. Ajouter des logs de débogage complets
Write-Host "`n[6/7] Ajout logs de débogage..." -ForegroundColor Yellow

# Logs dans map_logic.js pour tracer registerData.profilePhoto
if ($content -notmatch "console\.log\('\[REGISTER\] registerData\.profilePhoto") {
    Write-Host "  → Ajout log registerData.profilePhoto..." -ForegroundColor Gray
    $pattern = '(?s)(// Récupérer photoData depuis registerData.*?\n    const photoData =)'
    $replacement = '$1
    console.log(''[REGISTER] registerData.profilePhoto:'', window.registerData?.profilePhoto ? (window.registerData.profilePhoto.substring(0, 50) + ''...'') : ''null'');
    console.log(''[REGISTER] registerData.photoData:'', window.registerData?.photoData ? (window.registerData.photoData.substring(0, 50) + ''...'') : ''null'');'
    $content = $content -replace $pattern, $replacement
    [System.IO.File]::WriteAllText($mapLogicPath, $content, [System.Text.Encoding]::UTF8)
    Write-Host "  ✅ Logs ajoutés dans map_logic.js" -ForegroundColor Green
}

# Logs dans auth.js pour tracer photoData dans tout le flux
if ($authContent -notmatch "console\.log\('\[OAUTH\] pendingRegisterData photoData") {
    Write-Host "  → Ajout logs OAuth photoData..." -ForegroundColor Gray
    # Log avant envoi requête
    $pattern = '(console\.log\(''\[OAUTH\] Envoi requete OAuth Google au backend''\))'
    $replacement = 'console.log(''[OAUTH] pendingRegisterData photoData:'', window.pendingRegisterData?.photoData ? (window.pendingRegisterData.photoData.substring(0, 50) + ''...'') : ''null'');
      console.log(''[OAUTH] requestBody photoData:'', requestBody.photoData ? (requestBody.photoData.substring(0, 50) + ''...'') : ''null'');
      $1'
    $authContent = $authContent -replace $pattern, $replacement
    
    # Log après réception réponse
    $pattern = '(const syncData = await syncResponse\.json\(\);)'
    $replacement = '$1
        console.log(''[OAUTH] Réponse backend photoData:'', syncData.user?.photoData ? (syncData.user.photoData.substring(0, 50) + ''...'') : ''null'');
        console.log(''[OAUTH] Réponse backend profile_photo_url:'', syncData.user?.profile_photo_url ? (syncData.user.profile_photo_url.substring(0, 50) + ''...'') : ''null'');'
    $authContent = $authContent -replace $pattern, $replacement
    
    # Log après sauvegarde dans slimUser
    $pattern = '(photoData:\s*window\.pendingRegisterData\?\.photoData.*?\n\s*avatarId:)'
    $replacement = '$1
              console.log(''[OAUTH] slimUser photoData sauvegardé:'', slimUser.photoData ? (slimUser.photoData.substring(0, 50) + ''...'') : ''null'');'
    $authContent = $authContent -replace $pattern, $replacement
    
    [System.IO.File]::WriteAllText($authJsPath, $authContent, [System.Text.Encoding]::UTF8)
    Write-Host "  ✅ Logs ajoutés dans auth.js" -ForegroundColor Green
}

# 7. Déploiement
Write-Host "`n[7/7] Déploiement..." -ForegroundColor Yellow
aws s3 cp public\auth.js s3://mapevent-frontend-laetibibi/auth.js --region eu-west-1 --content-type "application/javascript" --cache-control "no-cache, no-store, must-revalidate" 2>&1 | Out-Null
aws s3 cp public\map_logic.js s3://mapevent-frontend-laetibibi/map_logic.js --region eu-west-1 --content-type "application/javascript" --cache-control "no-cache, no-store, must-revalidate" 2>&1 | Out-Null

$invalidationId = aws cloudfront create-invalidation --distribution-id EMB53HDL7VFIJ --paths "/auth.js" "/auth.js*" "/map_logic.js" "/map_logic.js*" --query "Invalidation.Id" --output text 2>&1
Start-Sleep -Seconds 15

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "DIAGNOSTIC TERMINE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nPour tester:" -ForegroundColor Yellow
Write-Host "  1. Ouvrez la console du navigateur (F12)" -ForegroundColor White
Write-Host "  2. Créez un nouveau compte avec une photo" -ForegroundColor White
Write-Host "  3. Vérifiez les logs dans cet ordre:" -ForegroundColor White
Write-Host "     - [REGISTER] registerData.profilePhoto" -ForegroundColor Cyan
Write-Host "     - [REGISTER] photoData récupéré" -ForegroundColor Cyan
Write-Host "     - [REGISTER] pendingRegisterData créé avec photoData" -ForegroundColor Cyan
Write-Host "     - [OAUTH] pendingRegisterData photoData" -ForegroundColor Cyan
Write-Host "     - [OAUTH] requestBody photoData" -ForegroundColor Cyan
Write-Host "     - [OAUTH] Réponse backend photoData" -ForegroundColor Cyan
Write-Host "     - [OAUTH] slimUser photoData sauvegardé" -ForegroundColor Cyan
Write-Host "`nLe premier log qui affiche 'null' indique où photoData est perdu!" -ForegroundColor Yellow
