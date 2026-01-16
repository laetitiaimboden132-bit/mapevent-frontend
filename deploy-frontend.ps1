# Script de deploiement Frontend vers S3 et invalidation CloudFront
# Usage: .\deploy-frontend.ps1

$ErrorActionPreference = "Stop"

Write-Host "Deploiement Frontend MapEvent vers S3..." -ForegroundColor Cyan

# Variables - CONFIGUREES AUTOMATIQUEMENT
$S3_BUCKET = "mapevent-frontend-laetibibi"
$CLOUDFRONT_DISTRIBUTION_ID = "EMB53HDL7VFIJ"
$REGION = "eu-west-1"
$PUBLIC_FOLDER = "public"

# Verifier que le dossier public existe
if (-not (Test-Path $PUBLIC_FOLDER)) {
    Write-Host "Erreur: Le dossier $PUBLIC_FOLDER n'existe pas!" -ForegroundColor Red
    exit 1
}

# Verifier que AWS CLI est installe
try {
    $awsVersion = aws --version 2>&1
    Write-Host "AWS CLI detecte: $awsVersion" -ForegroundColor Green
} catch {
    Write-Host "Erreur: AWS CLI n'est pas installe!" -ForegroundColor Red
    Write-Host "   Installez-le depuis: https://aws.amazon.com/cli/" -ForegroundColor Yellow
    exit 1
}

# Verifier les credentials AWS
try {
    $awsIdentity = aws sts get-caller-identity 2>&1
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Erreur: AWS credentials non configures!" -ForegroundColor Red
        Write-Host "   Configurez avec: aws configure" -ForegroundColor Yellow
        exit 1
    }
    Write-Host "AWS credentials OK" -ForegroundColor Green
    Write-Host "   $awsIdentity" -ForegroundColor Gray
} catch {
    Write-Host "Erreur lors de la verification des credentials AWS" -ForegroundColor Red
    exit 1
}

# Uploader les fichiers vers S3
Write-Host ""
Write-Host "Upload des fichiers vers S3..." -ForegroundColor Yellow
Write-Host "   Bucket: s3://$S3_BUCKET" -ForegroundColor Gray
Write-Host "   Dossier: $PUBLIC_FOLDER" -ForegroundColor Gray

try {
    aws s3 sync $PUBLIC_FOLDER "s3://$S3_BUCKET" --region $REGION --delete --exclude "*.git*" --exclude "*.md" --exclude "*.bat" --exclude "*.ps1" --exclude "*.sh" --exclude "*.zip" --exclude "node_modules/*" --exclude ".DS_Store" --exclude "Thumbs.db"
    
    if ($LASTEXITCODE -ne 0) {
        throw "Erreur lors de l'upload"
    }
    
    Write-Host "Upload termine avec succes!" -ForegroundColor Green
} catch {
    Write-Host "Erreur lors de l'upload vers S3: $_" -ForegroundColor Red
    exit 1
}

# Invalider le cache CloudFront si l'ID est fourni
if ($CLOUDFRONT_DISTRIBUTION_ID) {
    Write-Host ""
    Write-Host "Invalidation du cache CloudFront..." -ForegroundColor Yellow
    Write-Host "   Distribution ID: $CLOUDFRONT_DISTRIBUTION_ID" -ForegroundColor Gray
    
    try {
        # Invalider spécifiquement les fichiers modifiés
        $paths = @(
            "/map_logic.js*",
            "/auth.js*",
            "/mapevent.html*",
            "/index.html*"
        )
        
        Write-Host "   Chemins a invalider:" -ForegroundColor Gray
        foreach ($path in $paths) {
            Write-Host "     - $path" -ForegroundColor Gray
        }
        
        # Créer l'invalidation avec les chemins spécifiques
        $invalidationId = aws cloudfront create-invalidation --distribution-id $CLOUDFRONT_DISTRIBUTION_ID --paths "/map_logic.js*" "/auth.js*" "/mapevent.html*" "/index.html*" --query "Invalidation.Id" --output text
        
        if ($LASTEXITCODE -ne 0) {
            throw "Erreur lors de l'invalidation"
        }
        
        Write-Host "Invalidation creee: $invalidationId" -ForegroundColor Green
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
        Write-Host "Erreur lors de l'invalidation CloudFront: $_" -ForegroundColor Yellow
        Write-Host "   Vous pouvez invalider manuellement depuis la console AWS" -ForegroundColor Gray
    }
} else {
    Write-Host ""
    Write-Host "CloudFront Distribution ID non configure" -ForegroundColor Yellow
    Write-Host "   Pour invalider le cache, configurez CLOUDFRONT_DISTRIBUTION_ID dans le script" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Deploiement termine!" -ForegroundColor Green
Write-Host "   Site: https://mapevent.world" -ForegroundColor Cyan
Write-Host ""
Write-Host "Astuce: Videz le cache de votre navigateur pour voir les changements" -ForegroundColor Yellow
