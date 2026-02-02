# Script PowerShell pour déployer auth.js avec cache-busting
# Usage: .\deploy-auth-version.ps1
# Note: Pas besoin d'être administrateur sauf si AWS CLI nécessite des permissions spéciales

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DEPLOIEMENT AUTH.JS - VERSION CORRIGÉE" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Générer un timestamp unique pour le cache-busting
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
Write-Host "Timestamp généré: $timestamp" -ForegroundColor Yellow

# Variables
$S3_BUCKET = "mapevent-frontend-laetibibi"
$CLOUDFRONT_DISTRIBUTION_ID = "EMB53HDL7VFIJ"
$REGION = "eu-west-1"
$PUBLIC_FOLDER = "public"

# Vérifier que auth.js existe
Write-Host "`nVérification de auth.js..." -ForegroundColor Green
$authJsPath = "$PUBLIC_FOLDER\auth.js"
if (-not (Test-Path $authJsPath)) {
    Write-Host "[ERREUR] Fichier auth.js non trouvé!" -ForegroundColor Red
    exit 1
}
Write-Host "[OK] auth.js trouvé" -ForegroundColor Green

# Vérifier que mapevent.html existe
Write-Host "`nMise à jour du cache-busting dans mapevent.html..." -ForegroundColor Green
$htmlPath = "$PUBLIC_FOLDER\mapevent.html"
if (-not (Test-Path $htmlPath)) {
    Write-Host "[ERREUR] Fichier mapevent.html non trouvé!" -ForegroundColor Red
    exit 1
}

# Mettre à jour le cache-busting dans mapevent.html
$htmlContent = Get-Content $htmlPath -Raw -Encoding UTF8
$htmlContent = $htmlContent -replace 'auth\.js\?v=\d{8}-\d{6}', "auth.js?v=$timestamp"
Set-Content -Path $htmlPath -Value $htmlContent -NoNewline -Encoding UTF8
Write-Host "[OK] Cache-busting mis à jour: auth.js?v=$timestamp" -ForegroundColor Green

# Vérifier AWS CLI
Write-Host "`nVérification AWS CLI..." -ForegroundColor Green
try {
    $awsVersion = aws --version 2>&1
    Write-Host "[OK] AWS CLI: $awsVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERREUR] AWS CLI n'est pas installé!" -ForegroundColor Red
    Write-Host "   Installez-le depuis: https://aws.amazon.com/cli/" -ForegroundColor Yellow
    exit 1
}

# Vérifier les credentials AWS
try {
    $awsIdentity = aws sts get-caller-identity 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERREUR] AWS credentials non configurés!" -ForegroundColor Red
        Write-Host "   Configurez avec: aws configure" -ForegroundColor Yellow
        exit 1
    }
    Write-Host "[OK] AWS credentials valides" -ForegroundColor Green
} catch {
    Write-Host "[ERREUR] Erreur lors de la vérification des credentials AWS" -ForegroundColor Red
    exit 1
}

# ETAPE 1: Uploader les fichiers vers S3
Write-Host ""
Write-Host "[ETAPE 1] Upload des fichiers vers S3..." -ForegroundColor Yellow
Write-Host "   Bucket: s3://$S3_BUCKET" -ForegroundColor Gray
Write-Host "   Dossier: $PUBLIC_FOLDER" -ForegroundColor Gray

try {
    # Uploader auth.js et mapevent.html en priorité
    Write-Host "   Upload auth.js..." -ForegroundColor Gray
    aws s3 cp "$PUBLIC_FOLDER\auth.js" "s3://$S3_BUCKET/auth.js" --region $REGION --content-type "application/javascript" --cache-control "no-cache, no-store, must-revalidate"
    
    Write-Host "   Upload mapevent.html..." -ForegroundColor Gray
    aws s3 cp "$PUBLIC_FOLDER\mapevent.html" "s3://$S3_BUCKET/mapevent.html" --region $REGION --content-type "text/html" --cache-control "no-cache, no-store, must-revalidate"
    
    # Synchroniser le reste des fichiers
    Write-Host "   Synchronisation du reste des fichiers..." -ForegroundColor Gray
    aws s3 sync $PUBLIC_FOLDER "s3://$S3_BUCKET" --region $REGION --exclude "*.git*" --exclude "*.md" --exclude "*.bat" --exclude "*.ps1" --exclude "*.sh" --exclude "*.zip" --exclude "node_modules/*" --exclude ".DS_Store" --exclude "Thumbs.db"
    
    if ($LASTEXITCODE -ne 0) {
        throw "Erreur lors de l'upload"
    }
    
    Write-Host "[OK] Upload terminé avec succès!" -ForegroundColor Green
} catch {
    Write-Host "[ERREUR] Erreur lors de l'upload vers S3: $_" -ForegroundColor Red
    exit 1
}

# ETAPE 2: Invalider CloudFront
Write-Host ""
Write-Host "[ETAPE 2] Invalidation du cache CloudFront..." -ForegroundColor Yellow
Write-Host "   Distribution ID: $CLOUDFRONT_DISTRIBUTION_ID" -ForegroundColor Gray

try {
    # Invalider spécifiquement les fichiers critiques
    Write-Host "   Chemins à invalider:" -ForegroundColor Gray
    Write-Host "     - /auth.js" -ForegroundColor Gray
    Write-Host "     - /auth.js*" -ForegroundColor Gray
    Write-Host "     - /mapevent.html" -ForegroundColor Gray
    Write-Host "     - /mapevent.html*" -ForegroundColor Gray
    
    # Créer l'invalidation
    $invalidationId = aws cloudfront create-invalidation `
        --distribution-id $CLOUDFRONT_DISTRIBUTION_ID `
        --paths "/auth.js" "/auth.js*" "/mapevent.html" "/mapevent.html*" `
        --query "Invalidation.Id" `
        --output text
    
    if ($LASTEXITCODE -ne 0) {
        throw "Erreur lors de l'invalidation"
    }
    
    Write-Host "[OK] Invalidation créée: $invalidationId" -ForegroundColor Green
    Write-Host "   Attente de la completion de l'invalidation..." -ForegroundColor Yellow
    
    # Attendre que l'invalidation soit complète
    $maxAttempts = 60  # 60 tentatives = 5 minutes max
    $attempt = 0
    $completed = $false
    
    while (-not $completed -and $attempt -lt $maxAttempts) {
        Start-Sleep -Seconds 5
        $attempt++
        
        $status = aws cloudfront get-invalidation --distribution-id $CLOUDFRONT_DISTRIBUTION_ID --id $invalidationId --query "Invalidation.Status" --output text 2>&1
        
        if ($status -eq "Completed") {
            Write-Host "" -ForegroundColor Green
            Write-Host "========================================" -ForegroundColor Green
            Write-Host "[OK] INVALIDATION CLOUDFRONT TERMINÉE!" -ForegroundColor Green
            Write-Host "========================================" -ForegroundColor Green
            Write-Host ""
            Write-Host "   Temps: $($attempt * 5) secondes" -ForegroundColor Cyan
            Write-Host "   ID: $invalidationId" -ForegroundColor Cyan
            Write-Host ""
            $completed = $true
        } elseif ($status -eq "InProgress") {
            Write-Host "   En cours... ($($attempt * 5) secondes)" -ForegroundColor Gray
        } else {
            Write-Host "   Statut: $status" -ForegroundColor Yellow
        }
    }
    
    if (-not $completed) {
        Write-Host "" -ForegroundColor Yellow
        Write-Host "[ATTENTION] Timeout après 5 minutes. L'invalidation continue en arrière-plan." -ForegroundColor Yellow
        Write-Host "   ID d'invalidation: $invalidationId" -ForegroundColor Yellow
        Write-Host "   Vous pouvez vérifier le statut dans la console AWS CloudFront." -ForegroundColor Yellow
        Write-Host ""
    }
} catch {
    Write-Host "[ERREUR] Erreur lors de l'invalidation CloudFront: $_" -ForegroundColor Red
    Write-Host "   Vous pouvez invalider manuellement depuis la console AWS" -ForegroundColor Gray
    exit 1
}

# ETAPE 3: Résumé
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DÉPLOIEMENT TERMINÉ!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Site: https://mapevent.world" -ForegroundColor Cyan
Write-Host "Version auth.js: $timestamp" -ForegroundColor Yellow
Write-Host ""
Write-Host "Pour vérifier:" -ForegroundColor Yellow
Write-Host "  1. Ouvrir https://mapevent.world" -ForegroundColor White
Write-Host "  2. Ouvrir la console (F12)" -ForegroundColor White
Write-Host "  3. Copier-coller le script TEST_AUTH_VERSION.js" -ForegroundColor White
Write-Host "  4. Vérifier que vous voyez '[OK][OK][OK] SUCCES' au point 5" -ForegroundColor White
Write-Host ""
Write-Host "Si ce n'est pas le cas:" -ForegroundColor Yellow
Write-Host "  - Vider le cache du navigateur (Ctrl+Shift+Delete)" -ForegroundColor White
Write-Host "  - Recharger la page en forçant (Ctrl+F5)" -ForegroundColor White
Write-Host "  - Attendre 1-2 minutes si l'invalidation n'est pas terminée" -ForegroundColor White
Write-Host ""
