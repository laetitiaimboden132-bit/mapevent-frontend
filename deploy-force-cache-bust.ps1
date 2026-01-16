# Script de deploiement FORCE avec invalidation CloudFront specifique
# Usage: .\deploy-force-cache-bust.ps1

$ErrorActionPreference = "Stop"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DEPLOIEMENT FORCE - Cache-Bust" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Variables
$S3_BUCKET = "mapevent-frontend-laetibibi"
$CLOUDFRONT_DISTRIBUTION_ID = "EMB53HDL7VFIJ"
$REGION = "eu-west-1"
$PUBLIC_FOLDER = "public"

# Verifier que le dossier public existe
if (-not (Test-Path $PUBLIC_FOLDER)) {
    Write-Host "ERREUR: Le dossier $PUBLIC_FOLDER n'existe pas!" -ForegroundColor Red
    exit 1
}

# Verifier AWS CLI
try {
    $awsVersion = aws --version 2>&1
    Write-Host "[OK] AWS CLI: $awsVersion" -ForegroundColor Green
} catch {
    Write-Host "[ERREUR] AWS CLI n'est pas installe!" -ForegroundColor Red
    exit 1
}

# Verifier les credentials AWS
try {
    $awsIdentity = aws sts get-caller-identity 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[ERREUR] AWS credentials non configures!" -ForegroundColor Red
        exit 1
    }
    Write-Host "[OK] AWS credentials valides" -ForegroundColor Green
} catch {
    Write-Host "[ERREUR] Erreur lors de la verification des credentials AWS" -ForegroundColor Red
    exit 1
}

# ETAPE 1: Uploader les fichiers vers S3
Write-Host ""
Write-Host "[ETAPE 1] Upload des fichiers vers S3..." -ForegroundColor Yellow
Write-Host "   Bucket: s3://$S3_BUCKET" -ForegroundColor Gray
Write-Host "   Dossier: $PUBLIC_FOLDER" -ForegroundColor Gray

try {
    # Uploader map_logic.js et mapevent.html en priorite
    Write-Host "   Upload map_logic.js..." -ForegroundColor Gray
    aws s3 cp "$PUBLIC_FOLDER\map_logic.js" "s3://$S3_BUCKET/map_logic.js" --region $REGION --content-type "application/javascript" --cache-control "no-cache, no-store, must-revalidate"
    
    Write-Host "   Upload mapevent.html..." -ForegroundColor Gray
    aws s3 cp "$PUBLIC_FOLDER\mapevent.html" "s3://$S3_BUCKET/mapevent.html" --region $REGION --content-type "text/html" --cache-control "no-cache, no-store, must-revalidate"
    
    # Synchroniser le reste des fichiers
    Write-Host "   Synchronisation du reste des fichiers..." -ForegroundColor Gray
    aws s3 sync $PUBLIC_FOLDER "s3://$S3_BUCKET" --region $REGION --exclude "*.git*" --exclude "*.md" --exclude "*.bat" --exclude "*.ps1" --exclude "*.sh" --exclude "*.zip" --exclude "node_modules/*" --exclude ".DS_Store" --exclude "Thumbs.db"
    
    if ($LASTEXITCODE -ne 0) {
        throw "Erreur lors de l'upload"
    }
    
    Write-Host "[OK] Upload termine avec succes!" -ForegroundColor Green
} catch {
    Write-Host "[ERREUR] Erreur lors de l'upload vers S3: $_" -ForegroundColor Red
    exit 1
}

# ETAPE 2: Invalider CloudFront
Write-Host ""
Write-Host "[ETAPE 2] Invalidation du cache CloudFront..." -ForegroundColor Yellow
Write-Host "   Distribution ID: $CLOUDFRONT_DISTRIBUTION_ID" -ForegroundColor Gray

try {
    # Invalider specifiquement les fichiers critiques
    $paths = @(
        "/map_logic.js",
        "/map_logic.js*",
        "/mapevent.html",
        "/mapevent.html*",
        "/index.html",
        "/index.html*"
    )
    
    Write-Host "   Chemins a invalider:" -ForegroundColor Gray
    foreach ($path in $paths) {
        Write-Host "     - $path" -ForegroundColor Gray
    }
    
    # Creer l'invalidation
    $invalidationId = aws cloudfront create-invalidation `
        --distribution-id $CLOUDFRONT_DISTRIBUTION_ID `
        --paths "/map_logic.js" "/map_logic.js*" "/mapevent.html" "/mapevent.html*" "/index.html" "/index.html*" `
        --query "Invalidation.Id" `
        --output text
    
    if ($LASTEXITCODE -ne 0) {
        throw "Erreur lors de l'invalidation"
    }
    
    Write-Host "[OK] Invalidation creee: $invalidationId" -ForegroundColor Green
    Write-Host "   Attente de la completion de l'invalidation..." -ForegroundColor Yellow
    
    # Attendre que l'invalidation soit complete
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
            Write-Host "========================================" -ForegroundColor Green
            Write-Host "[OK] INVALIDATION CLOUDFRONT TERMINEE!" -ForegroundColor Green
            Write-Host "========================================" -ForegroundColor Green
            Write-Host "========================================" -ForegroundColor Green
            Write-Host "" -ForegroundColor Green
            Write-Host "   Temps: $($attempt * 5) secondes" -ForegroundColor Cyan
            Write-Host "   ID: $invalidationId" -ForegroundColor Cyan
            Write-Host "" -ForegroundColor Green
            Write-Host "   Le cache est maintenant invalide." -ForegroundColor Yellow
            Write-Host "   Vous pouvez tester le site maintenant." -ForegroundColor Yellow
            Write-Host "" -ForegroundColor Green
            Write-Host "========================================" -ForegroundColor Green
            Write-Host "========================================" -ForegroundColor Green
            Write-Host "" -ForegroundColor Green
            $completed = $true
        } elseif ($status -eq "InProgress") {
            Write-Host "   En cours... ($($attempt * 5) secondes)" -ForegroundColor Gray
        } else {
            Write-Host "   Statut: $status" -ForegroundColor Yellow
        }
    }
    
    if (-not $completed) {
        Write-Host "" -ForegroundColor Yellow
        Write-Host "[ATTENTION] Timeout apres 5 minutes. L'invalidation continue en arriere-plan." -ForegroundColor Yellow
        Write-Host "   ID d'invalidation: $invalidationId" -ForegroundColor Yellow
        Write-Host "   Vous pouvez verifier le statut dans la console AWS CloudFront." -ForegroundColor Yellow
        Write-Host ""
    }
} catch {
    Write-Host "[ERREUR] Erreur lors de l'invalidation CloudFront: $_" -ForegroundColor Red
    Write-Host "   Vous pouvez invalider manuellement depuis la console AWS" -ForegroundColor Gray
    exit 1
}

# ETAPE 3: Verification
Write-Host ""
Write-Host "[ETAPE 3] Verification..." -ForegroundColor Yellow
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "DEPLOIEMENT TERMINE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Site: https://mapevent.world" -ForegroundColor Cyan
Write-Host ""
Write-Host "Pour verifier:" -ForegroundColor Yellow
Write-Host "  1. Ouvrir https://mapevent.world" -ForegroundColor White
Write-Host "  2. Ouvrir la console (F12)" -ForegroundColor White
Write-Host "  3. Taper: typeof openAuthModal" -ForegroundColor White
Write-Host "  4. Resultat attendu: 'function'" -ForegroundColor Green
Write-Host ""
Write-Host "Si ce n'est pas le cas:" -ForegroundColor Yellow
Write-Host "  - Vider le cache du navigateur (Ctrl+Shift+Delete)" -ForegroundColor White
Write-Host "  - Recharger la page en forcant (Ctrl+F5)" -ForegroundColor White
Write-Host "  - Attendre 1-2 minutes si l'invalidation n'est pas terminee" -ForegroundColor White
Write-Host ""

