# Script PowerShell pour configurer S3 pour les avatars
# Exécuter: .\setup-s3-avatars.ps1

$BUCKET_NAME = "mapevent-avatars"
$REGION = "eu-west-1"

Write-Host "🚀 Configuration S3 pour les avatars MapEvent" -ForegroundColor Cyan
Write-Host ""

# Vérifier que AWS CLI est installé
if (-not (Get-Command aws -ErrorAction SilentlyContinue)) {
    Write-Host "❌ AWS CLI n'est pas installé. Installez-le depuis: https://aws.amazon.com/cli/" -ForegroundColor Red
    exit 1
}

Write-Host "✅ AWS CLI détecté" -ForegroundColor Green
Write-Host ""

# 1. Créer le bucket S3
Write-Host "📦 Étape 1: Création du bucket S3..." -ForegroundColor Yellow
try {
    # Vérifier si le bucket existe déjà
    $bucketExists = aws s3api head-bucket --bucket $BUCKET_NAME --region $REGION 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Bucket '$BUCKET_NAME' existe déjà" -ForegroundColor Green
    } else {
        # Créer le bucket
        if ($REGION -eq "us-east-1") {
            aws s3api create-bucket --bucket $BUCKET_NAME --region $REGION
        } else {
            aws s3api create-bucket --bucket $BUCKET_NAME --region $REGION --create-bucket-configuration LocationConstraint=$REGION
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Bucket '$BUCKET_NAME' créé avec succès" -ForegroundColor Green
        } else {
            Write-Host "❌ Erreur lors de la création du bucket" -ForegroundColor Red
            exit 1
        }
    }
} catch {
    Write-Host "⚠️ Erreur: $_" -ForegroundColor Yellow
    Write-Host "   Le bucket existe peut-être déjà ou vous n'avez pas les permissions" -ForegroundColor Yellow
}

Write-Host ""

# 2. Configurer les permissions du bucket (public read)
Write-Host "🔐 Étape 2: Configuration des permissions du bucket..." -ForegroundColor Yellow

$bucketPolicy = @{
    Version = "2012-10-17"
    Statement = @(
        @{
            Effect = "Allow"
            Principal = "*"
            Action = "s3:GetObject"
            Resource = "arn:aws:s3:::$BUCKET_NAME/*"
        }
    )
} | ConvertTo-Json -Depth 10

$bucketPolicyFile = "bucket-policy.json"
$bucketPolicy | Out-File -FilePath $bucketPolicyFile -Encoding UTF8

try {
    aws s3api put-bucket-policy --bucket $BUCKET_NAME --policy file://$bucketPolicyFile --region $REGION
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Politique de bucket configurée (lecture publique)" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Erreur lors de la configuration de la politique" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️ Erreur: $_" -ForegroundColor Yellow
}

Write-Host ""

# 3. Configurer CORS
Write-Host "🌐 Étape 3: Configuration CORS..." -ForegroundColor Yellow

$corsConfig = @{
    CORSRules = @(
        @{
            AllowedHeaders = @("*")
            AllowedMethods = @("GET", "PUT", "POST", "DELETE", "HEAD")
            AllowedOrigins = @("https://mapevent.world", "http://localhost:8000", "http://localhost:3000")
            ExposeHeaders = @("ETag", "Content-Length")
            MaxAgeSeconds = 3000
        }
    )
} | ConvertTo-Json -Depth 10

$corsConfigFile = "cors-config.json"
$corsConfig | Out-File -FilePath $corsConfigFile -Encoding UTF8

try {
    aws s3api put-bucket-cors --bucket $BUCKET_NAME --cors-configuration file://$corsConfigFile --region $REGION
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Configuration CORS appliquée" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Erreur lors de la configuration CORS" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️ Erreur: $_" -ForegroundColor Yellow
}

Write-Host ""

# 4. Désactiver le blocage d'accès public (si nécessaire)
Write-Host "🔓 Étape 4: Configuration du blocage d'accès public..." -ForegroundColor Yellow

$publicAccessBlock = @{
    BlockPublicAcls = $false
    IgnorePublicAcls = $false
    BlockPublicPolicy = $false
    RestrictPublicBuckets = $false
} | ConvertTo-Json

$publicAccessBlockFile = "public-access-block.json"
$publicAccessBlock | Out-File -FilePath $publicAccessBlockFile -Encoding UTF8

try {
    aws s3api put-public-access-block --bucket $BUCKET_NAME --public-access-block-configuration file://$publicAccessBlockFile --region $REGION
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Blocage d'accès public configuré (lecture publique autorisée)" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Erreur lors de la configuration du blocage d'accès public" -ForegroundColor Yellow
    }
} catch {
    Write-Host "⚠️ Erreur: $_" -ForegroundColor Yellow
}

Write-Host ""

# 5. Créer le dossier avatars/
Write-Host "📁 Étape 5: Création du dossier avatars/..." -ForegroundColor Yellow
try {
    # Créer un fichier vide pour créer le dossier
    $tempFile = "temp-avatar-placeholder.txt"
    "placeholder" | Out-File -FilePath $tempFile -Encoding UTF8
    aws s3 cp $tempFile "s3://$BUCKET_NAME/avatars/.gitkeep" --region $REGION
    Remove-Item $tempFile -ErrorAction SilentlyContinue
    Write-Host "✅ Dossier avatars/ créé" -ForegroundColor Green
} catch {
    Write-Host "⚠️ Le dossier sera créé automatiquement lors du premier upload" -ForegroundColor Yellow
}

Write-Host ""

# 6. Afficher les informations de configuration
Write-Host "📋 Configuration terminée !" -ForegroundColor Green
Write-Host ""
Write-Host "Bucket S3: $BUCKET_NAME" -ForegroundColor Cyan
Write-Host "Région: $REGION" -ForegroundColor Cyan
Write-Host "URL de base: https://$BUCKET_NAME.s3.$REGION.amazonaws.com" -ForegroundColor Cyan
Write-Host ""
Write-Host "📝 Variables d'environnement Lambda à configurer:" -ForegroundColor Yellow
Write-Host "   S3_AVATARS_BUCKET=$BUCKET_NAME" -ForegroundColor White
Write-Host "   AWS_REGION=$REGION" -ForegroundColor White
Write-Host ""

# Nettoyer les fichiers temporaires
Remove-Item $bucketPolicyFile -ErrorAction SilentlyContinue
Remove-Item $corsConfigFile -ErrorAction SilentlyContinue
Remove-Item $publicAccessBlockFile -ErrorAction SilentlyContinue

Write-Host "✅ Configuration S3 terminée !" -ForegroundColor Green

