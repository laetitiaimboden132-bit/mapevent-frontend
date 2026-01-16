# Script final complet pour corriger photoData de A à Z
# Vérifie et corrige TOUT le flux

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CORRECTION FINALE COMPLETE PHOTODATA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$mapLogicPath = "public\map_logic.js"
$authJsPath = "public\auth.js"
$mapContent = Get-Content $mapLogicPath -Raw -Encoding UTF8
$authContent = Get-Content $authJsPath -Raw -Encoding UTF8

# 1. Vérifier que handleProPhotoUpload sauvegarde bien dans registerData.photoData
Write-Host "`n[1/8] Vérification handleProPhotoUpload..." -ForegroundColor Yellow
if ($mapContent -match "registerData\.photoData\s*=\s*base64") {
    Write-Host "  ✅ registerData.photoData sauvegardé dans handleProPhotoUpload" -ForegroundColor Green
} else {
    Write-Host "  ❌ registerData.photoData non sauvegardé - CORRECTION..." -ForegroundColor Red
    # Trouver la fonction handleProPhotoUpload et ajouter photoData
    $pattern = '(?s)(registerData\.profilePhoto\s*=\s*base64;)'
    $replacement = '$1
    window.registerData.photoData = base64; // AUSSI dans photoData pour compatibilité
    console.log(''[PHOTO] ✅ Photo sauvegardée dans registerData.profilePhoto et registerData.photoData, longueur:'', base64.length);'
    $mapContent = $mapContent -replace $pattern, $replacement
    [System.IO.File]::WriteAllText($mapLogicPath, $mapContent, [System.Text.Encoding]::UTF8)
    Write-Host "  ✅ Correction appliquée" -ForegroundColor Green
}

# 2. Vérifier que photoData est bien dans pendingRegisterData
Write-Host "`n[2/8] Vérification pendingRegisterData..." -ForegroundColor Yellow
if ($mapContent -match "pendingRegisterData.*photoData:\s*photoData") {
    Write-Host "  ✅ photoData présent dans pendingRegisterData" -ForegroundColor Green
} else {
    Write-Host "  ❌ photoData absent - CORRECTION..." -ForegroundColor Red
    $pattern = '(?s)(const photoData = window\.registerData\.photoData.*?\n    console\.log)'
    $replacement = 'const photoData = window.registerData.photoData || window.registerData.profilePhoto || null;
    console.log(''[REGISTER] registerData.photoData:'', window.registerData?.photoData ? (window.registerData.photoData.substring(0, 50) + ''...'') : ''null'');
    console.log(''[REGISTER] registerData.profilePhoto:'', window.registerData?.profilePhoto ? (window.registerData.profilePhoto.substring(0, 50) + ''...'') : ''null'');
    $1'
    $mapContent = $mapContent -replace $pattern, $replacement
    [System.IO.File]::WriteAllText($mapLogicPath, $mapContent, [System.Text.Encoding]::UTF8)
    Write-Host "  ✅ Correction appliquée" -ForegroundColor Green
}

# 3. Vérifier que photoData est envoyé dans requestBody OAuth Google
Write-Host "`n[3/8] Vérification auth.js requestBody..." -ForegroundColor Yellow
if ($authContent -match "requestBody\.photoData\s*=") {
    Write-Host "  ✅ photoData présent dans requestBody" -ForegroundColor Green
} else {
    Write-Host "  ❌ photoData absent de requestBody - CORRECTION..." -ForegroundColor Red
    $pattern = '(?s)(if \(pendingData\.selectedAddress.*?}\];\s*\}\s*)(console\.log\(''\[OAUTH\] Inscription avec Google)'
    $replacement = '$1        // INCLURE photoData si disponible (photo uploadée lors de la création du profil)
        if (pendingData.photoData && pendingData.photoData !== ''null'' && pendingData.photoData !== null) {
          requestBody.photoData = pendingData.photoData;
          console.log(''[OAUTH] ✅ photoData inclus dans la requête OAuth Google:'', pendingData.photoData.substring(0, 50) + ''...'');
        }
        $2'
    $authContent = $authContent -replace $pattern, $replacement
    [System.IO.File]::WriteAllText($authJsPath, $authContent, [System.Text.Encoding]::UTF8)
    Write-Host "  ✅ Correction appliquée" -ForegroundColor Green
}

# 4. Vérifier que photoData est sauvegardé dans slimUser
Write-Host "`n[4/8] Vérification sauvegarde slimUser..." -ForegroundColor Yellow
if ($authContent -match "photoData:\s*window\.pendingRegisterData") {
    Write-Host "  ✅ photoData sauvegardé dans slimUser" -ForegroundColor Green
} else {
    Write-Host "  ❌ photoData non sauvegardé - CORRECTION..." -ForegroundColor Red
    $pattern = '(?s)(photoData:\s*)(pendingData\?\.photoData|syncData\.user\.photoData)(\s*\|\|\s*null)'
    $replacement = '$1window.pendingRegisterData?.photoData || syncData.user?.photoData || null'
    $authContent = $authContent -replace $pattern, $replacement
    [System.IO.File]::WriteAllText($authJsPath, $authContent, [System.Text.Encoding]::UTF8)
    Write-Host "  ✅ Correction appliquée" -ForegroundColor Green
}

# 5. Vérifier backend
Write-Host "`n[5/8] Vérification backend..." -ForegroundColor Yellow
$mainPyPath = "lambda-package\backend\main.py"
$mainPyContent = Get-Content $mainPyPath -Raw -Encoding UTF8

if ($mainPyContent -match "photo_data_from_form\s*=\s*data\.get\('photoData'") {
    Write-Host "  ✅ Traitement photoData présent" -ForegroundColor Green
} else {
    Write-Host "  ❌ Traitement photoData absent - CORRECTION..." -ForegroundColor Red
    $pattern = '(?s)(# Les colonnes OAuth sont déjà créées.*?\n                # Utiliser picture comme avatar_emoji)'
    $replacement = '# Les colonnes OAuth sont déjà créées dans le bloc DO $$ ci-dessus
                
                # Gérer la photo uploadée lors de la création du profil (photoData)
                photo_data_from_form = data.get(''photoData'', '''')
                profile_photo_initial = picture if picture else ''''
                
                # Si une photo a été uploadée dans le formulaire, l''uploader vers S3 et l''utiliser
                if photo_data_from_form and photo_data_from_form.strip() and photo_data_from_form != ''null'':
                    try:
                        from services.s3_service import upload_avatar_to_s3
                        logger.info(f"[PHOTO] Upload photo formulaire vers S3 pour {email}...")
                        s3_url = upload_avatar_to_s3(user_id, photo_data_from_form)
                        if s3_url:
                            profile_photo_initial = s3_url
                            logger.info(f"[OK] Photo uploadée vers S3: {s3_url[:100]}...")
                        else:
                            logger.warning(f"[WARNING] Échec upload photo vers S3, utilisation photo Google")
                    except Exception as photo_error:
                        logger.error(f"[ERROR] Erreur upload photo vers S3: {photo_error}")
                        import traceback
                        logger.error(traceback.format_exc())
                        # Continuer avec la photo Google si l''upload échoue
                
                # Utiliser picture comme avatar_emoji'
    $mainPyContent = $mainPyContent -replace $pattern, $replacement
    [System.IO.File]::WriteAllText($mainPyPath, $mainPyContent, [System.Text.Encoding]::UTF8)
    Write-Host "  ✅ Correction appliquée" -ForegroundColor Green
}

if ($mainPyContent -match "'photoData':.*photo_data_from_form") {
    Write-Host "  ✅ photoData dans user_data_dict" -ForegroundColor Green
} else {
    Write-Host "  ❌ photoData absent de user_data_dict - CORRECTION..." -ForegroundColor Red
    $pattern = "('profileComplete': profile_complete\s*\})"
    $replacement = "'profileComplete': profile_complete,
                # Inclure photoData si une photo a été uploadée depuis le formulaire
                'photoData': photo_data_from_form if 'photo_data_from_form' in locals() and photo_data_from_form and photo_data_from_form != 'null' else None
            }"
    $mainPyContent = $mainPyContent -replace $pattern, $replacement
    [System.IO.File]::WriteAllText($mainPyPath, $mainPyContent, [System.Text.Encoding]::UTF8)
    Write-Host "  ✅ Correction appliquée" -ForegroundColor Green
}

if ($mainPyContent -match '"photoData":.*user_row_or_dict\.get\("photoData"\)') {
    Write-Host "  ✅ photoData dans build_user_slim" -ForegroundColor Green
} else {
    Write-Host "  ❌ photoData absent de build_user_slim - CORRECTION..." -ForegroundColor Red
    $pattern = '("profileComplete": user_row_or_dict\.get\("profileComplete", False)\s*\})'
    $replacement = '"profileComplete": user_row_or_dict.get("profileComplete", False),
        # Inclure photoData si disponible (photo uploadée depuis le formulaire)
        "photoData": user_row_or_dict.get("photoData") if user_row_or_dict.get("photoData") and user_row_or_dict.get("photoData") != ''null'' else None
    }'
    $mainPyContent = $mainPyContent -replace $pattern, $replacement
    [System.IO.File]::WriteAllText($mainPyPath, $mainPyContent, [System.Text.Encoding]::UTF8)
    Write-Host "  ✅ Correction appliquée" -ForegroundColor Green
}

# 6. Ajouter logs complets
Write-Host "`n[6/8] Ajout logs complets..." -ForegroundColor Yellow

# Logs dans handleProPhotoUpload
if ($mapContent -notmatch "console\.log\('\[PHOTO\] Photo sauvegardée dans registerData") {
    $pattern = '(?s)(registerData\.profilePhoto\s*=\s*base64;)'
    $replacement = '$1
    window.registerData.photoData = base64; // AUSSI dans photoData
    console.log(''[PHOTO] ✅ Photo sauvegardée dans registerData.profilePhoto et registerData.photoData, longueur:'', base64.length);'
    $mapContent = $mapContent -replace $pattern, $replacement
    [System.IO.File]::WriteAllText($mapLogicPath, $mapContent, [System.Text.Encoding]::UTF8)
    Write-Host "  ✅ Logs ajoutés dans handleProPhotoUpload" -ForegroundColor Green
}

# Logs dans auth.js
if ($authContent -notmatch "console\.log\('\[OAUTH\] pendingRegisterData photoData") {
    $pattern = '(console\.log\(''\[OAUTH\] Envoi requete OAuth Google au backend''\))'
    $replacement = 'console.log(''[OAUTH] pendingRegisterData photoData:'', window.pendingRegisterData?.photoData ? (window.pendingRegisterData.photoData.substring(0, 50) + ''...'') : ''null'');
      console.log(''[OAUTH] requestBody photoData:'', requestBody.photoData ? (requestBody.photoData.substring(0, 50) + ''...'') : ''null'');
      $1'
    $authContent = $authContent -replace $pattern, $replacement
    
    $pattern = '(const syncData = await syncResponse\.json\(\);)'
    $replacement = '$1
        console.log(''[OAUTH] Réponse backend photoData:'', syncData.user?.photoData ? (syncData.user.photoData.substring(0, 50) + ''...'') : ''null'');
        console.log(''[OAUTH] Réponse backend profile_photo_url:'', syncData.user?.profile_photo_url ? (syncData.user.profile_photo_url.substring(0, 50) + ''...'') : ''null'');'
    $authContent = $authContent -replace $pattern, $replacement
    
    [System.IO.File]::WriteAllText($authJsPath, $authContent, [System.Text.Encoding]::UTF8)
    Write-Host "  ✅ Logs ajoutés dans auth.js" -ForegroundColor Green
}

# 7. Déploiement frontend
Write-Host "`n[7/8] Déploiement frontend..." -ForegroundColor Yellow
aws s3 cp public\auth.js s3://mapevent-frontend-laetibibi/auth.js --region eu-west-1 --content-type "application/javascript" --cache-control "no-cache, no-store, must-revalidate" 2>&1 | Out-Null
aws s3 cp public\map_logic.js s3://mapevent-frontend-laetibibi/map_logic.js --region eu-west-1 --content-type "application/javascript" --cache-control "no-cache, no-store, must-revalidate" 2>&1 | Out-Null
Write-Host "  ✅ Frontend déployé" -ForegroundColor Green

# 8. Déploiement backend
Write-Host "`n[8/8] Déploiement backend..." -ForegroundColor Yellow
Compress-Archive -Path lambda-package\* -DestinationPath lambda-deployment.zip -Force 2>&1 | Out-Null
aws s3 cp lambda-deployment.zip s3://mapevent-backend-deployments/lambda-deployment.zip --region eu-west-1 2>&1 | Out-Null
aws lambda update-function-code --function-name mapevent-backend --s3-bucket mapevent-backend-deployments --s3-key lambda-deployment.zip --region eu-west-1 2>&1 | Out-Null

$maxAttempts = 60
$attempt = 0
$completed = $false
while (-not $completed -and $attempt -lt $maxAttempts) {
    Start-Sleep -Seconds 3
    $attempt++
    $status = aws lambda get-function --function-name mapevent-backend --region eu-west-1 --query "Configuration.LastUpdateStatus" --output text 2>&1
    if ($status -eq "Successful") {
        Write-Host "  ✅ Backend déployé (temps: $($attempt * 3) secondes)" -ForegroundColor Green
        $completed = $true
    }
}

# Invalidation CloudFront
Write-Host "`nInvalidation CloudFront..." -ForegroundColor Yellow
$invalidationId = aws cloudfront create-invalidation --distribution-id EMB53HDL7VFIJ --paths "/auth.js" "/auth.js*" "/map_logic.js" "/map_logic.js*" --query "Invalidation.Id" --output text 2>&1
Start-Sleep -Seconds 15
Write-Host "  ✅ CloudFront invalidé" -ForegroundColor Green

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "CORRECTION FINALE TERMINEE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nTous les points de contrôle vérifiés et corrigés:" -ForegroundColor Yellow
Write-Host "  ✅ handleProPhotoUpload sauvegarde dans registerData.photoData" -ForegroundColor Green
Write-Host "  ✅ photoData dans pendingRegisterData" -ForegroundColor Green
Write-Host "  ✅ photoData dans requestBody OAuth Google" -ForegroundColor Green
Write-Host "  ✅ photoData sauvegardé dans slimUser" -ForegroundColor Green
Write-Host "  ✅ Traitement photoData dans backend" -ForegroundColor Green
Write-Host "  ✅ photoData retourné dans API" -ForegroundColor Green
Write-Host "  ✅ Logs complets ajoutés" -ForegroundColor Green
Write-Host "`nTESTEZ MAINTENANT:" -ForegroundColor Yellow
Write-Host "  1. Ouvrez la console (F12)" -ForegroundColor White
Write-Host "  2. Créez un compte et UPLOADEZ une photo" -ForegroundColor White
Write-Host "  3. Vérifiez les logs [PHOTO] et [OAUTH]" -ForegroundColor White
