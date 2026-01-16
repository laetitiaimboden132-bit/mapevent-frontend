# Script PowerShell pour configurer la Bucket Policy via AWS CLI
# Utilisez ce script si la section "Politique du compartiment" n'apparaît pas dans la console

Write-Host "`n=== Configuration Bucket Policy via AWS CLI ===" -ForegroundColor Cyan

$BUCKET_NAME = "mapevent-avatars"
$REGION = "eu-west-1"
$POLICY_FILE = "bucket-policy.json"

# Créer le fichier JSON de politique
$POLICY_JSON = @{
    Version = "2012-10-17"
    Statement = @(
        @{
            Sid = "PublicReadGetObject"
            Effect = "Allow"
            Principal = "*"
            Action = "s3:GetObject"
            Resource = "arn:aws:s3:::$BUCKET_NAME/avatars/*"
        }
    )
} | ConvertTo-Json -Depth 10

Write-Host "`n📋 Politique à appliquer:" -ForegroundColor Yellow
Write-Host $POLICY_JSON -ForegroundColor Gray

# Sauvegarder dans un fichier
$POLICY_JSON | Out-File -FilePath $POLICY_FILE -Encoding UTF8 -NoNewline

Write-Host "`n✅ Fichier créé: $POLICY_FILE" -ForegroundColor Green

# Vérifier que AWS CLI est installé
Write-Host "`n🔍 Vérification AWS CLI..." -ForegroundColor Yellow
try {
    $awsVersion = aws --version 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ AWS CLI installé: $awsVersion" -ForegroundColor Green
    } else {
        Write-Host "❌ AWS CLI non trouvé" -ForegroundColor Red
        Write-Host "   Installez AWS CLI depuis: https://aws.amazon.com/cli/" -ForegroundColor Yellow
        exit 1
    }
} catch {
    Write-Host "❌ AWS CLI non installé" -ForegroundColor Red
    Write-Host "   Installez AWS CLI depuis: https://aws.amazon.com/cli/" -ForegroundColor Yellow
    exit 1
}

# Appliquer la politique
Write-Host "`n🔧 Application de la Bucket Policy..." -ForegroundColor Yellow

try {
    aws s3api put-bucket-policy `
        --bucket $BUCKET_NAME `
        --region $REGION `
        --policy file://$POLICY_FILE
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ Bucket Policy appliquée avec succès !" -ForegroundColor Green
        
        # Vérifier la politique
        Write-Host "`n🔍 Vérification de la politique..." -ForegroundColor Yellow
        aws s3api get-bucket-policy --bucket $BUCKET_NAME --region $REGION | ConvertFrom-Json | ConvertTo-Json -Depth 10
        
        Write-Host "`n✅ Configuration terminée !" -ForegroundColor Green
        Write-Host "`n🧪 Testez cette URL dans votre navigateur:" -ForegroundColor Cyan
        Write-Host "   https://$BUCKET_NAME.s3.$REGION.amazonaws.com/avatars/user_1767389921855_75fbd18e9395ca09.jpg" -ForegroundColor White
    } else {
        Write-Host "`n❌ Erreur lors de l'application de la Bucket Policy" -ForegroundColor Red
        Write-Host "   Code de sortie: $LASTEXITCODE" -ForegroundColor Red
        Write-Host "`n💡 Vérifiez:" -ForegroundColor Yellow
        Write-Host "   - Vos identifiants AWS sont configurés (aws configure)" -ForegroundColor White
        Write-Host "   - Vous avez les permissions s3:PutBucketPolicy" -ForegroundColor White
        Write-Host "   - Le bucket existe et est dans la bonne région" -ForegroundColor White
    }
} catch {
    Write-Host "`n❌ Erreur: $_" -ForegroundColor Red
    Write-Host "`n💡 Vérifiez vos permissions AWS et que le bucket existe" -ForegroundColor Yellow
}

# Nettoyer le fichier temporaire (optionnel - commentez si vous voulez le garder)
# if (Test-Path $POLICY_FILE) {
#     Remove-Item $POLICY_FILE -Force
#     Write-Host "`n🧹 Fichier temporaire supprimé" -ForegroundColor Gray
# }

Write-Host "`n=== Terminé ===" -ForegroundColor Cyan




