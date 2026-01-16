# Script PowerShell pour vérifier et configurer le bucket S3 mapevent-avatars
# Vérifie la configuration CORS, la politique du bucket, et l'accès public

Write-Host "`n=== Vérification du bucket S3 mapevent-avatars ===" -ForegroundColor Cyan

$BUCKET_NAME = "mapevent-avatars"
$REGION = "eu-west-1"

# 1. Vérifier si le bucket existe
Write-Host "`n1️⃣ Vérification de l'existence du bucket..." -ForegroundColor Yellow
try {
    $bucketExists = aws s3api head-bucket --bucket $BUCKET_NAME --region $REGION 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Bucket existe" -ForegroundColor Green
    } else {
        Write-Host "❌ Bucket n'existe pas ou erreur d'accès" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Erreur: $_" -ForegroundColor Red
    exit 1
}

# 2. Vérifier la configuration CORS
Write-Host "`n2️⃣ Vérification de la configuration CORS..." -ForegroundColor Yellow
try {
    $corsConfig = aws s3api get-bucket-cors --bucket $BUCKET_NAME --region $REGION 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Configuration CORS présente:" -ForegroundColor Green
        $corsConfig | ConvertFrom-Json | ConvertTo-Json -Depth 10 | Write-Host -ForegroundColor Gray
    } else {
        Write-Host "⚠️ Pas de configuration CORS trouvée" -ForegroundColor Yellow
        Write-Host "   Exécutez: .\configurer-cors-s3.ps1" -ForegroundColor Cyan
    }
} catch {
    Write-Host "⚠️ Erreur lors de la vérification CORS: $_" -ForegroundColor Yellow
}

# 3. Vérifier la politique du bucket
Write-Host "`n3️⃣ Vérification de la politique du bucket..." -ForegroundColor Yellow
try {
    $bucketPolicy = aws s3api get-bucket-policy --bucket $BUCKET_NAME --region $REGION 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Politique du bucket présente:" -ForegroundColor Green
        $policyJson = ($bucketPolicy | ConvertFrom-Json).Policy | ConvertFrom-Json
        $policyJson | ConvertTo-Json -Depth 10 | Write-Host -ForegroundColor Gray
        
        # Vérifier si l'accès public est autorisé
        $policyStr = $policyJson | ConvertTo-Json -Depth 10
        if ($policyStr -match "Principal.*\*" -or $policyStr -match "Effect.*Allow") {
            Write-Host "✅ Accès public détecté dans la politique" -ForegroundColor Green
        } else {
            Write-Host "⚠️ Accès public peut-être limité" -ForegroundColor Yellow
        }
    } else {
        Write-Host "⚠️ Pas de politique du bucket trouvée" -ForegroundColor Yellow
        Write-Host "   Le bucket peut nécessiter une politique pour l'accès public" -ForegroundColor Cyan
    }
} catch {
    Write-Host "⚠️ Erreur lors de la vérification de la politique: $_" -ForegroundColor Yellow
}

# 4. Vérifier le Block Public Access
Write-Host "`n4️⃣ Vérification du Block Public Access..." -ForegroundColor Yellow
try {
    $blockPublicAccess = aws s3api get-public-access-block --bucket $BUCKET_NAME --region $REGION 2>&1
    if ($LASTEXITCODE -eq 0) {
        $blockConfig = $blockPublicAccess | ConvertFrom-Json
        Write-Host "Configuration Block Public Access:" -ForegroundColor Gray
        $blockConfig | ConvertTo-Json | Write-Host -ForegroundColor Gray
        
        if ($blockConfig.PublicAccessBlockConfiguration.BlockPublicAcls -or 
            $blockConfig.PublicAccessBlockConfiguration.BlockPublicPolicy) {
            Write-Host "⚠️ Block Public Access est activé - cela peut bloquer l'accès public" -ForegroundColor Yellow
        } else {
            Write-Host "✅ Block Public Access n'est pas activé" -ForegroundColor Green
        }
    } else {
        Write-Host "✅ Block Public Access n'est pas configuré (par défaut désactivé)" -ForegroundColor Green
    }
} catch {
    Write-Host "ℹ️ Block Public Access non configuré (par défaut désactivé)" -ForegroundColor Gray
}

# 5. Tester l'accès à un fichier (si un avatar existe)
Write-Host "`n5️⃣ Test d'accès à un fichier..." -ForegroundColor Yellow
$testKey = "avatars/user_1767389921855_75fbd18e9395ca09.jpg"
try {
    $headObject = aws s3api head-object --bucket $BUCKET_NAME --key $testKey --region $REGION 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Fichier de test trouvé: $testKey" -ForegroundColor Green
        $objectInfo = $headObject | ConvertFrom-Json
        Write-Host "   Taille: $($objectInfo.ContentLength) bytes" -ForegroundColor Gray
        Write-Host "   Content-Type: $($objectInfo.ContentType)" -ForegroundColor Gray
        
        # Tester l'URL publique
        $publicUrl = "https://$BUCKET_NAME.s3.$REGION.amazonaws.com/$testKey"
        Write-Host "`n   URL publique: $publicUrl" -ForegroundColor Cyan
        Write-Host "   Testez cette URL dans votre navigateur pour vérifier CORS" -ForegroundColor Gray
    } else {
        Write-Host "⚠️ Fichier de test non trouvé: $testKey" -ForegroundColor Yellow
        Write-Host "   Cela est normal si aucun avatar n'a été uploadé" -ForegroundColor Gray
    }
} catch {
    Write-Host "⚠️ Erreur lors du test d'accès: $_" -ForegroundColor Yellow
}

Write-Host "`n=== Résumé ===" -ForegroundColor Cyan
Write-Host "Pour corriger les problèmes CORS:" -ForegroundColor Yellow
Write-Host "1. Exécutez: .\configurer-cors-s3.ps1" -ForegroundColor White
Write-Host "2. Vérifiez que la politique du bucket permet l'accès public en lecture" -ForegroundColor White
Write-Host "3. Videz le cache du navigateur et réessayez" -ForegroundColor White




