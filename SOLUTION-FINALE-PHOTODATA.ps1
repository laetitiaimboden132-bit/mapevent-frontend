# SOLUTION FINALE COMPLETE POUR PHOTODATA
# Corrige TOUT le flux de A à Z en une seule fois

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SOLUTION FINALE PHOTODATA" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$mapLogicPath = "public\map_logic.js"
$authJsPath = "public\auth.js"
$mainPyPath = "lambda-package\backend\main.py"

$mapContent = [System.IO.File]::ReadAllText($mapLogicPath, [System.Text.Encoding]::UTF8)
$authContent = [System.IO.File]::ReadAllText($authJsPath, [System.Text.Encoding]::UTF8)
$mainPyContent = [System.IO.File]::ReadAllText($mainPyPath, [System.Text.Encoding]::UTF8)

$corrections = 0

# ========================================
# 1. CORRECTION handleProPhotoUpload
# ========================================
Write-Host "`n[1/6] Correction handleProPhotoUpload..." -ForegroundColor Yellow

# Vérifier si la fonction existe et sauvegarde photoData
if ($mapContent -match "function handleProPhotoUpload|window\.handleProPhotoUpload\s*=") {
    Write-Host "  ✅ Fonction handleProPhotoUpload trouvée" -ForegroundColor Green
    
    # Vérifier si photoData est sauvegardé
    if ($mapContent -match "registerData\.photoData\s*=\s*base64") {
        Write-Host "  ✅ registerData.photoData sauvegardé" -ForegroundColor Green
    } else {
        Write-Host "  ❌ registerData.photoData non sauvegardé - CORRECTION..." -ForegroundColor Red
        $pattern = '(?s)(registerData\.profilePhoto\s*=\s*base64;)'
        $replacement = '$1
    window.registerData.photoData = base64; // AUSSI dans photoData pour compatibilité
    console.log(''[PHOTO] ✅ Photo sauvegardée dans registerData.profilePhoto ET registerData.photoData, longueur:'', base64.length);'
        $mapContent = $mapContent -replace $pattern, $replacement
        $corrections++
    }
} else {
    Write-Host "  ❌ Fonction handleProPhotoUpload NON TROUVEE - CREATION..." -ForegroundColor Red
    # Créer la fonction complète
    $functionCode = @"

// Gestion de l'upload de photo de profil
function handleProPhotoUpload(event) {
  const file = event.target.files[0];
  if (!file) {
    console.log('[PHOTO] Aucun fichier sélectionné');
    return;
  }

  // Vérifier la taille (max 5MB)
  if (file.size > 5 * 1024 * 1024) {
    showError('pro-photo-error', 'La photo est trop grande (max 5MB)');
    console.error('[PHOTO] Fichier trop grand:', file.size);
    return;
  }

  // Vérifier le type
  if (!file.type.startsWith('image/')) {
    showError('pro-photo-error', 'Veuillez sélectionner une image');
    console.error('[PHOTO] Type de fichier invalide:', file.type);
    return;
  }

  console.log('[PHOTO] Fichier sélectionné:', { name: file.name, size: file.size, type: file.type });

  // Lire et convertir en Base64
  const reader = new FileReader();
  reader.onload = function(e) {
    const base64 = e.target.result;
    console.log('[PHOTO] Photo convertie en base64, longueur:', base64.length);
    
    // Sauvegarder dans registerData.profilePhoto ET registerData.photoData
    if (!window.registerData) {
      window.registerData = {};
    }
    window.registerData.profilePhoto = base64;
    window.registerData.photoData = base64; // AUSSI dans photoData pour compatibilité
    console.log('[PHOTO] ✅ Photo sauvegardée dans registerData.profilePhoto ET registerData.photoData');
    
    // Afficher la preview
    const preview = document.getElementById('pro-photo-preview');
    const placeholder = document.getElementById('pro-photo-placeholder');
    const photoText = document.querySelector('.pro-register-photo-text');
    
    if (preview) {
      preview.src = base64;
      preview.style.display = 'block';
      preview.classList.add('show');
      console.log('[PHOTO] ✅ Preview mise à jour');
    }
    if (placeholder) {
      placeholder.style.display = 'none';
    }
    if (photoText) {
      photoText.textContent = 'Cliquez pour changer la photo';
    }
    
    // Cacher l'erreur
    showError('pro-photo-error', '');
  };
  
  reader.onerror = function(error) {
    console.error('[PHOTO] ❌ Erreur lors de la lecture du fichier:', error);
    showError('pro-photo-error', 'Erreur lors de la lecture de la photo');
  };
  
  reader.readAsDataURL(file);
}

// Exposer globalement
window.handleProPhotoUpload = handleProPhotoUpload;

"@
    # Insérer après showProRegisterForm
    $pattern = '(?s)(function showProRegisterForm\(\) \{.*?\n\})'
    if ($mapContent -match $pattern) {
        $mapContent = $mapContent -replace $pattern, "`$1`n$functionCode"
        $corrections++
        Write-Host "  ✅ Fonction handleProPhotoUpload créée" -ForegroundColor Green
    } else {
        # Insérer avant les fonctions globales
        $pattern = '(?s)(// Fonctions globales pour éviter les erreurs)'
        $mapContent = $mapContent -replace $pattern, "$functionCode`n`$1"
        $corrections++
        Write-Host "  ✅ Fonction handleProPhotoUpload créée" -ForegroundColor Green
    }
}

# ========================================
# 2. CORRECTION pendingRegisterData
# ========================================
Write-Host "`n[2/6] Correction pendingRegisterData..." -ForegroundColor Yellow

# Vérifier que photoData est bien récupéré depuis registerData
if ($mapContent -match "const photoData = window\.registerData\.photoData.*window\.registerData\.profilePhoto") {
    Write-Host "  ✅ photoData récupéré correctement" -ForegroundColor Green
} else {
    Write-Host "  ❌ photoData mal récupéré - CORRECTION..." -ForegroundColor Red
    $pattern = '(?s)(// Récupérer photoData depuis registerData.*?\n    const photoData =)([^;]*;)'
    $replacement = '$1 window.registerData.photoData || window.registerData.profilePhoto || null;
    console.log(''[REGISTER] registerData.photoData:'', window.registerData?.photoData ? (window.registerData.photoData.substring(0, 50) + ''...'') : ''null'');
    console.log(''[REGISTER] registerData.profilePhoto:'', window.registerData?.profilePhoto ? (window.registerData.profilePhoto.substring(0, 50) + ''...'') : ''null'');'
    $mapContent = $mapContent -replace $pattern, $replacement
    $corrections++
}

# Vérifier qu'il n'y a pas de duplication
if (([regex]::Matches($mapContent, '(?s)pendingRegisterData\s*=\s*\{[^}]*photoData:[^}]*\}').Value | Select-String -Pattern 'photoData:' -AllMatches).Matches.Count -gt 1) {
    Write-Host "  ❌ Duplication photoData détectée - SUPPRESSION..." -ForegroundColor Red
    $pattern = '(?s)(photoData:\s*photoData[^,]*,\s*photoLater:[^,]*,\s*addressLater:[^,]*,\s*selectedAddress:[^,]*,\s*)photoData:[^,]*,\s*'
    $mapContent = $mapContent -replace $pattern, '$1'
    $corrections++
    Write-Host "  ✅ Duplication supprimée" -ForegroundColor Green
}

# ========================================
# 3. CORRECTION auth.js - requestBody
# ========================================
Write-Host "`n[3/6] Correction auth.js requestBody..." -ForegroundColor Yellow

if ($authContent -match "requestBody\.photoData\s*=") {
    Write-Host "  ✅ photoData dans requestBody" -ForegroundColor Green
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
    $corrections++
    Write-Host "  ✅ Correction appliquée" -ForegroundColor Green
}

# Ajouter logs avant envoi
if ($authContent -notmatch "console\.log\('\[OAUTH\] pendingRegisterData photoData") {
    $pattern = '(console\.log\(''\[OAUTH\] Envoi requete OAuth Google au backend''\))'
    $replacement = 'console.log(''[OAUTH] pendingRegisterData photoData:'', window.pendingRegisterData?.photoData ? (window.pendingRegisterData.photoData.substring(0, 50) + ''...'') : ''null'');
      console.log(''[OAUTH] requestBody photoData:'', requestBody.photoData ? (requestBody.photoData.substring(0, 50) + ''...'') : ''null'');
      $1'
    $authContent = $authContent -replace $pattern, $replacement
    $corrections++
}

# Ajouter logs après réception
if ($authContent -notmatch "console\.log\('\[OAUTH\] Réponse backend photoData") {
    $pattern = '(const syncData = await syncResponse\.json\(\);)'
    $replacement = '$1
        console.log(''[OAUTH] Réponse backend photoData:'', syncData.user?.photoData ? (syncData.user.photoData.substring(0, 50) + ''...'') : ''null'');
        console.log(''[OAUTH] Réponse backend profile_photo_url:'', syncData.user?.profile_photo_url ? (syncData.user.profile_photo_url.substring(0, 50) + ''...'') : ''null'');'
    $authContent = $authContent -replace $pattern, $replacement
    $corrections++
}

# ========================================
# 4. CORRECTION sauvegarde dans slimUser
# ========================================
Write-Host "`n[4/6] Correction sauvegarde slimUser..." -ForegroundColor Yellow

# Ligne 2161 (nouveau compte)
if ($authContent -match "photoData:\s*window\.pendingRegisterData\?\.photoData.*\|\|.*null") {
    Write-Host "  ✅ photoData sauvegardé dans slimUser (nouveau compte)" -ForegroundColor Green
} else {
    Write-Host "  ❌ photoData non sauvegardé (nouveau compte) - CORRECTION..." -ForegroundColor Red
    $pattern = '(?s)(photoData:\s*)(pendingData\?\.photoData|syncData\.user\.photoData)(\s*\|\|\s*null)'
    $replacement = '$1window.pendingRegisterData?.photoData || syncData.user?.photoData || null'
    $authContent = $authContent -replace $pattern, $replacement
    $corrections++
}

# Ligne 2249 (compte existant)
if ($authContent -match "photoData:\s*syncData\.user\.photoData.*\|\|.*null") {
    Write-Host "  ✅ photoData sauvegardé dans slimUser (compte existant)" -ForegroundColor Green
} else {
    Write-Host "  ⚠️ Vérification sauvegarde compte existant..." -ForegroundColor Yellow
}

# ========================================
# 5. CORRECTION backend
# ========================================
Write-Host "`n[5/6] Correction backend..." -ForegroundColor Yellow

# Vérifier traitement photoData
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
    $corrections++
}

# Vérifier retour dans user_data_dict
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
    $corrections++
}

# Vérifier retour dans build_user_slim
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
    $corrections++
}

# ========================================
# 6. SAUVEGARDE ET DEPLOIEMENT
# ========================================
Write-Host "`n[6/6] Sauvegarde et déploiement..." -ForegroundColor Yellow

if ($corrections -gt 0) {
    Write-Host "  → $corrections correction(s) appliquée(s)" -ForegroundColor Cyan
    [System.IO.File]::WriteAllText($mapLogicPath, $mapContent, [System.Text.Encoding]::UTF8)
    [System.IO.File]::WriteAllText($authJsPath, $authContent, [System.Text.Encoding]::UTF8)
    [System.IO.File]::WriteAllText($mainPyPath, $mainPyContent, [System.Text.Encoding]::UTF8)
    Write-Host "  ✅ Fichiers sauvegardés" -ForegroundColor Green
} else {
    Write-Host "  ✅ Aucune correction nécessaire" -ForegroundColor Green
}

# Déploiement frontend
Write-Host "  → Déploiement frontend..." -ForegroundColor Gray
aws s3 cp public\auth.js s3://mapevent-frontend-laetibibi/auth.js --region eu-west-1 --content-type "application/javascript" --cache-control "no-cache, no-store, must-revalidate" 2>&1 | Out-Null
aws s3 cp public\map_logic.js s3://mapevent-frontend-laetibibi/map_logic.js --region eu-west-1 --content-type "application/javascript" --cache-control "no-cache, no-store, must-revalidate" 2>&1 | Out-Null
Write-Host "  ✅ Frontend déployé" -ForegroundColor Green

# Déploiement backend
Write-Host "  → Déploiement backend..." -ForegroundColor Gray
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
Write-Host "  → Invalidation CloudFront..." -ForegroundColor Gray
$invalidationId = aws cloudfront create-invalidation --distribution-id EMB53HDL7VFIJ --paths "/auth.js" "/auth.js*" "/map_logic.js" "/map_logic.js*" --query "Invalidation.Id" --output text 2>&1
Start-Sleep -Seconds 15
Write-Host "  ✅ CloudFront invalidé" -ForegroundColor Green

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "SOLUTION APPLIQUEE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nCorrections appliquées: $corrections" -ForegroundColor Yellow
Write-Host "`nTESTEZ MAINTENANT:" -ForegroundColor Yellow
Write-Host "  1. Ouvrez la console (F12)" -ForegroundColor White
Write-Host "  2. Créez un compte et UPLOADEZ une photo" -ForegroundColor White
Write-Host "  3. Vérifiez les logs dans cet ordre:" -ForegroundColor White
Write-Host "     [PHOTO] ✅ Photo sauvegardée..." -ForegroundColor Cyan
Write-Host "     [REGISTER] registerData.photoData..." -ForegroundColor Cyan
Write-Host "     [REGISTER] pendingRegisterData créé avec photoData..." -ForegroundColor Cyan
Write-Host "     [OAUTH] pendingRegisterData photoData..." -ForegroundColor Cyan
Write-Host "     [OAUTH] requestBody photoData..." -ForegroundColor Cyan
Write-Host "     [OAUTH] Réponse backend photoData..." -ForegroundColor Cyan
Write-Host "`nLe premier log qui affiche 'null' indique où photoData est perdu!" -ForegroundColor Yellow
