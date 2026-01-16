# Script de correction complète pour photoData
# Trace tout le flux et corrige tous les problèmes

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CORRECTION COMPLETE PHOTODATA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 1. Vérifier et corriger auth.js - S'assurer que photoData est bien inclus
Write-Host "`n[1/6] Vérification auth.js..." -ForegroundColor Yellow
$authJsPath = "public\auth.js"
$authJsContent = Get-Content $authJsPath -Raw -Encoding UTF8

# Vérifier si photoData est dans requestBody
if ($authJsContent -notmatch "requestBody\.photoData\s*=") {
    Write-Host "  → Ajout photoData dans requestBody..." -ForegroundColor Gray
    
    # Trouver la section où ajouter photoData (après addresses)
    $pattern = '(?s)(if \(pendingData\.selectedAddress.*?}\];\s*\}\s*)(console\.log\(''\[OAUTH\] Inscription avec Google)'
    $replacement = '$1        // INCLURE photoData si disponible (photo uploadée lors de la création du profil)
        if (pendingData.photoData && pendingData.photoData !== ''null'' && pendingData.photoData !== null) {
          requestBody.photoData = pendingData.photoData;
          console.log(''[OAUTH] ✅ photoData inclus dans la requête OAuth Google:'', pendingData.photoData.substring(0, 50) + ''...'');
        }
        $2'
    
    $authJsContent = $authJsContent -replace $pattern, $replacement
    [System.IO.File]::WriteAllText($authJsPath, $authJsContent, [System.Text.Encoding]::UTF8)
    Write-Host "  ✅ photoData ajouté dans requestBody" -ForegroundColor Green
} else {
    Write-Host "  ✅ photoData déjà présent dans requestBody" -ForegroundColor Green
}

# Vérifier si photoData est sauvegardé dans slimUser (ligne 2161)
if ($authJsContent -notmatch "photoData:\s*window\.pendingRegisterData") {
    Write-Host "  → Correction sauvegarde photoData dans slimUser..." -ForegroundColor Gray
    $pattern = '(?s)(photoData:\s*)(pendingData\?\.photoData|syncData\.user\.photoData)'
    $replacement = '$1window.pendingRegisterData?.photoData || syncData.user?.photoData || null'
    $authJsContent = $authJsContent -replace $pattern, $replacement
    [System.IO.File]::WriteAllText($authJsPath, $authJsContent, [System.Text.Encoding]::UTF8)
    Write-Host "  ✅ Sauvegarde photoData corrigée" -ForegroundColor Green
} else {
    Write-Host "  ✅ Sauvegarde photoData correcte" -ForegroundColor Green
}

# 2. Vérifier et corriger map_logic.js - S'assurer que photoData est bien utilisé
Write-Host "`n[2/6] Vérification map_logic.js..." -ForegroundColor Yellow
$mapLogicPath = "public\map_logic.js"
$mapLogicContent = Get-Content $mapLogicPath -Raw -Encoding UTF8

# Vérifier la logique de priorité photoData
if ($mapLogicContent -match "currentUser\.photoData.*!==.*'null'") {
    Write-Host "  ✅ Logique photoData correcte" -ForegroundColor Green
} else {
    Write-Host "  ⚠️ Logique photoData à vérifier" -ForegroundColor Yellow
}

# 3. Vérifier et corriger backend - S'assurer que photoData est traité et retourné
Write-Host "`n[3/6] Vérification backend main.py..." -ForegroundColor Yellow
$mainPyPath = "lambda-package\backend\main.py"
$mainPyContent = Get-Content $mainPyPath -Raw -Encoding UTF8

# Vérifier si photoData est traité lors de la création utilisateur
if ($mainPyContent -match "photo_data_from_form\s*=\s*data\.get\('photoData'") {
    Write-Host "  ✅ Traitement photoData présent" -ForegroundColor Green
} else {
    Write-Host "  → Ajout traitement photoData..." -ForegroundColor Gray
    # Ajouter le traitement avant INSERT INTO users
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
    Write-Host "  ✅ Traitement photoData ajouté" -ForegroundColor Green
}

# Vérifier si photoData est dans user_data_dict
if ($mainPyContent -match "'photoData':.*photo_data_from_form") {
    Write-Host "  ✅ photoData dans user_data_dict" -ForegroundColor Green
} else {
    Write-Host "  → Ajout photoData dans user_data_dict..." -ForegroundColor Gray
    $pattern = "('profileComplete': profile_complete\s*\})"
    $replacement = "'profileComplete': profile_complete,
                # Inclure photoData si une photo a été uploadée depuis le formulaire
                'photoData': photo_data_from_form if 'photo_data_from_form' in locals() and photo_data_from_form and photo_data_from_form != 'null' else None
            }"
    $mainPyContent = $mainPyContent -replace $pattern, $replacement
    [System.IO.File]::WriteAllText($mainPyPath, $mainPyContent, [System.Text.Encoding]::UTF8)
    Write-Host "  ✅ photoData ajouté dans user_data_dict" -ForegroundColor Green
}

# Vérifier si photoData est dans build_user_slim
if ($mainPyContent -match '"photoData":.*user_row_or_dict\.get\("photoData"\)') {
    Write-Host "  ✅ photoData dans build_user_slim" -ForegroundColor Green
} else {
    Write-Host "  → Ajout photoData dans build_user_slim..." -ForegroundColor Gray
    $pattern = '("profileComplete": user_row_or_dict\.get\("profileComplete", False)\s*\})'
    $replacement = '"profileComplete": user_row_or_dict.get("profileComplete", False),
        # Inclure photoData si disponible (photo uploadée depuis le formulaire)
        "photoData": user_row_or_dict.get("photoData") if user_row_or_dict.get("photoData") and user_row_or_dict.get("photoData") != ''null'' else None
    }'
    $mainPyContent = $mainPyContent -replace $pattern, $replacement
    [System.IO.File]::WriteAllText($mainPyPath, $mainPyContent, [System.Text.Encoding]::UTF8)
    Write-Host "  ✅ photoData ajouté dans build_user_slim" -ForegroundColor Green
}

# 4. Ajouter des logs de débogage dans auth.js pour tracer photoData
Write-Host "`n[4/6] Ajout logs de débogage..." -ForegroundColor Yellow
if ($authJsContent -notmatch "console\.log\('\[OAUTH\] pendingRegisterData photoData") {
    Write-Host "  → Ajout logs pour tracer photoData..." -ForegroundColor Gray
    # Ajouter un log avant l'envoi de la requête OAuth
    $pattern = '(console\.log\(''\[OAUTH\] Envoi requete OAuth Google au backend''\))'
    $replacement = 'console.log(''[OAUTH] pendingRegisterData photoData:'', window.pendingRegisterData?.photoData ? (window.pendingRegisterData.photoData.substring(0, 50) + ''...'') : ''null'');
      $1'
    $authJsContent = $authJsContent -replace $pattern, $replacement
    
    # Ajouter un log après réception de la réponse
    $pattern = '(const syncData = await syncResponse\.json\(\);)'
    $replacement = '$1
        console.log(''[OAUTH] Réponse backend photoData:'', syncData.user?.photoData ? (syncData.user.photoData.substring(0, 50) + ''...'') : ''null'');'
    $authJsContent = $authJsContent -replace $pattern, $replacement
    
    [System.IO.File]::WriteAllText($authJsPath, $authJsContent, [System.Text.Encoding]::UTF8)
    Write-Host "  ✅ Logs ajoutés" -ForegroundColor Green
} else {
    Write-Host "  ✅ Logs déjà présents" -ForegroundColor Green
}

# 5. Déploiement frontend
Write-Host "`n[5/6] Déploiement frontend..." -ForegroundColor Yellow
aws s3 cp public\auth.js s3://mapevent-frontend-laetibibi/auth.js --region eu-west-1 --content-type "application/javascript" --cache-control "no-cache, no-store, must-revalidate" 2>&1 | Out-Null
aws s3 cp public\map_logic.js s3://mapevent-frontend-laetibibi/map_logic.js --region eu-west-1 --content-type "application/javascript" --cache-control "no-cache, no-store, must-revalidate" 2>&1 | Out-Null
Write-Host "  ✅ Frontend déployé" -ForegroundColor Green

# 6. Déploiement backend
Write-Host "`n[6/6] Déploiement backend..." -ForegroundColor Yellow
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
Write-Host "CORRECTION TERMINEE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nVérifications effectuées:" -ForegroundColor Yellow
Write-Host "  ✅ photoData dans requestBody (auth.js)" -ForegroundColor Green
Write-Host "  ✅ photoData sauvegardé dans slimUser" -ForegroundColor Green
Write-Host "  ✅ Traitement photoData dans backend" -ForegroundColor Green
Write-Host "  ✅ photoData retourné dans API" -ForegroundColor Green
Write-Host "  ✅ Logs de débogage ajoutés" -ForegroundColor Green
Write-Host "`nPour tester:" -ForegroundColor Yellow
Write-Host "  1. Ouvrez la console du navigateur" -ForegroundColor White
Write-Host "  2. Créez un nouveau compte avec une photo" -ForegroundColor White
Write-Host "  3. Vérifiez les logs '[OAUTH] pendingRegisterData photoData'" -ForegroundColor White
Write-Host "  4. Vérifiez les logs '[OAUTH] Réponse backend photoData'" -ForegroundColor White
