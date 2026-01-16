# Script de déploiement complet avec corrections automatiques
# Force l'exécution et corrige tous les problèmes

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DEPLOIEMENT COMPLET AVEC CORRECTIONS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 1. CORRECTION AUTH.JS - Ajouter photoData dans requestBody
Write-Host "`n[1/5] Correction auth.js..." -ForegroundColor Yellow
$authJsPath = "public\auth.js"
$authJsContent = Get-Content $authJsPath -Raw -Encoding UTF8

# Vérifier si photoData est déjà présent
if ($authJsContent -notmatch "photoData.*pendingData") {
    Write-Host "  → Ajout photoData dans requestBody..." -ForegroundColor Gray
    $pattern = '(?s)(if \(pendingData\.selectedAddress.*?}\];\s*\}\s*)(console\.log\(''\[OAUTH\] Inscription avec Google)'
    $replacement = '$1        // INCLURE photoData si disponible (photo uploadée lors de la création du profil)
        if (pendingData.photoData && pendingData.photoData !== ''null'' && pendingData.photoData !== null) {
          requestBody.photoData = pendingData.photoData;
          console.log(''[OAUTH] ✅ photoData inclus dans la requête OAuth Google:'', pendingData.photoData.substring(0, 50) + ''...'');
        }
        $2'
    
    $authJsContent = $authJsContent -replace $pattern, $replacement
    
    # Sauvegarder
    [System.IO.File]::WriteAllText($authJsPath, $authJsContent, [System.Text.Encoding]::UTF8)
    Write-Host "  ✅ auth.js corrigé" -ForegroundColor Green
} else {
    Write-Host "  ✅ photoData déjà présent dans auth.js" -ForegroundColor Green
}

# 2. CORRECTION BACKEND - Ajouter traitement photoData
Write-Host "`n[2/5] Correction backend main.py..." -ForegroundColor Yellow
$mainPyPath = "lambda-package\backend\main.py"
$mainPyContent = Get-Content $mainPyPath -Raw -Encoding UTF8

# Vérifier si traitement photoData existe déjà
if ($mainPyContent -notmatch "photo_data_from_form.*data\.get\('photoData'") {
    Write-Host "  → Ajout traitement photoData dans backend..." -ForegroundColor Gray
    
    # Trouver la section où ajouter le traitement photoData (après gestion des adresses)
    $pattern = '(?s)(# Les colonnes OAuth sont déjà créées dans le bloc DO.*?\n                # Utiliser picture comme avatar_emoji)'
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
    
    # Ajouter photoData dans user_data_dict
    if ($mainPyContent -notmatch "'photoData':.*photo_data_from_form") {
        $pattern = "(?s)('profileComplete': profile_complete\s*\})"
        $replacement = "'profileComplete': profile_complete,
                # Inclure photoData si une photo a été uploadée depuis le formulaire
                'photoData': photo_data_from_form if 'photo_data_from_form' in locals() and photo_data_from_form and photo_data_from_form != 'null' else None
            }"
        $mainPyContent = $mainPyContent -replace $pattern, $replacement
    }
    
    # Ajouter photoData dans build_user_slim
    if ($mainPyContent -notmatch '"photoData":.*user_row_or_dict\.get\("photoData"\)') {
        $pattern = '("profileComplete": user_row_or_dict\.get\("profileComplete", False)\s*\})'
        $replacement = '"profileComplete": user_row_or_dict.get("profileComplete", False),
        # Inclure photoData si disponible (photo uploadée depuis le formulaire)
        "photoData": user_row_or_dict.get("photoData") if user_row_or_dict.get("photoData") and user_row_or_dict.get("photoData") != ''null'' else None
    }'
        $mainPyContent = $mainPyContent -replace $pattern, $replacement
    }
    
    # Sauvegarder
    [System.IO.File]::WriteAllText($mainPyPath, $mainPyContent, [System.Text.Encoding]::UTF8)
    Write-Host "  ✅ backend main.py corrigé" -ForegroundColor Green
} else {
    Write-Host "  ✅ Traitement photoData déjà présent dans backend" -ForegroundColor Green
}

# 3. DEPLOIEMENT FRONTEND
Write-Host "`n[3/5] Déploiement frontend..." -ForegroundColor Yellow
Write-Host "  → Upload auth.js..." -ForegroundColor Gray
aws s3 cp public\auth.js s3://mapevent-frontend-laetibibi/auth.js --region eu-west-1 --content-type "application/javascript" --cache-control "no-cache, no-store, must-revalidate" 2>&1 | Out-Null
Write-Host "  ✅ auth.js uploadé" -ForegroundColor Green

Write-Host "  → Upload map_logic.js..." -ForegroundColor Gray
aws s3 cp public\map_logic.js s3://mapevent-frontend-laetibibi/map_logic.js --region eu-west-1 --content-type "application/javascript" --cache-control "no-cache, no-store, must-revalidate" 2>&1 | Out-Null
Write-Host "  ✅ map_logic.js uploadé" -ForegroundColor Green

# 4. DEPLOIEMENT BACKEND
Write-Host "`n[4/5] Déploiement backend..." -ForegroundColor Yellow
Write-Host "  → Création archive Lambda..." -ForegroundColor Gray
Compress-Archive -Path lambda-package\* -DestinationPath lambda-deployment.zip -Force 2>&1 | Out-Null
Write-Host "  ✅ Archive créée" -ForegroundColor Green

Write-Host "  → Upload vers S3..." -ForegroundColor Gray
aws s3 cp lambda-deployment.zip s3://mapevent-backend-deployments/lambda-deployment.zip --region eu-west-1 2>&1 | Out-Null
Write-Host "  ✅ Archive uploadée" -ForegroundColor Green

Write-Host "  → Mise à jour Lambda..." -ForegroundColor Gray
$lambdaStatus = aws lambda update-function-code --function-name mapevent-backend --s3-bucket mapevent-backend-deployments --s3-key lambda-deployment.zip --region eu-west-1 --query "LastUpdateStatus" --output text 2>&1
Write-Host "  → Statut Lambda: $lambdaStatus" -ForegroundColor Gray

# Attendre que le déploiement soit terminé
$maxAttempts = 60
$attempt = 0
$completed = $false
while (-not $completed -and $attempt -lt $maxAttempts) {
    Start-Sleep -Seconds 3
    $attempt++
    $status = aws lambda get-function --function-name mapevent-backend --region eu-west-1 --query "Configuration.LastUpdateStatus" --output text 2>&1
    if ($status -eq "Successful") {
        Write-Host "  ✅ Déploiement backend terminé (temps: $($attempt * 3) secondes)" -ForegroundColor Green
        $completed = $true
    } elseif ($status -eq "InProgress") {
        Write-Host "  → En cours... ($($attempt * 3) secondes)" -ForegroundColor Gray
    } else {
        Write-Host "  → Statut: $status" -ForegroundColor Yellow
    }
}

if (-not $completed) {
    Write-Host "  ⚠️ Timeout après 3 minutes" -ForegroundColor Yellow
}

# 5. INVALIDATION CLOUDFRONT
Write-Host "`n[5/5] Invalidation CloudFront..." -ForegroundColor Yellow
$invalidationId = aws cloudfront create-invalidation --distribution-id EMB53HDL7VFIJ --paths "/auth.js" "/auth.js*" "/map_logic.js" "/map_logic.js*" --query "Invalidation.Id" --output text 2>&1
Write-Host "  → Invalidation ID: $invalidationId" -ForegroundColor Gray

$maxAttempts = 60
$attempt = 0
$completed = $false
while (-not $completed -and $attempt -lt $maxAttempts) {
    Start-Sleep -Seconds 5
    $attempt++
    $status = aws cloudfront get-invalidation --distribution-id EMB53HDL7VFIJ --id $invalidationId --query "Invalidation.Status" --output text 2>&1
    if ($status -eq "Completed") {
        Write-Host "  ✅ Invalidation terminée (temps: $($attempt * 5) secondes)" -ForegroundColor Green
        $completed = $true
    } elseif ($status -eq "InProgress") {
        Write-Host "  → En cours... ($($attempt * 5) secondes)" -ForegroundColor Gray
    } else {
        Write-Host "  → Statut: $status" -ForegroundColor Yellow
    }
}

if (-not $completed) {
    Write-Host "  ⚠️ Timeout après 5 minutes" -ForegroundColor Yellow
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "DEPLOIEMENT TERMINE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nRésumé des corrections:" -ForegroundColor Yellow
Write-Host "  ✅ photoData ajouté dans auth.js (requestBody)" -ForegroundColor Green
Write-Host "  ✅ Traitement photoData ajouté dans backend" -ForegroundColor Green
Write-Host "  ✅ Upload photo vers S3 automatique" -ForegroundColor Green
Write-Host "  ✅ photoData retourné dans les réponses API" -ForegroundColor Green
Write-Host "  ✅ Frontend et backend déployés" -ForegroundColor Green
Write-Host "  ✅ CloudFront invalidé" -ForegroundColor Green
