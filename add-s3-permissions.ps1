# Script pour ajouter les permissions S3 au rôle Lambda

$LAMBDA_FUNCTION_NAME = "mapevent-backend"
$REGION = "eu-west-1"
$BUCKET_NAME = "mapevent-avatars"

Write-Host "🔧 Ajout des permissions S3 au rôle Lambda..." -ForegroundColor Yellow

try {
    # Récupérer le nom du rôle
    $roleArn = aws lambda get-function-configuration --function-name $LAMBDA_FUNCTION_NAME --region $REGION --query "Role" --output text
    $roleName = $roleArn.Split('/')[-1]
    
    Write-Host "   Rôle Lambda: $roleName" -ForegroundColor Gray
    
    # Créer une politique inline pour S3
    $policyDocument = @{
        Version = "2012-10-17"
        Statement = @(
            @{
                Effect = "Allow"
                Action = @(
                    "s3:PutObject",
                    "s3:PutObjectAcl",
                    "s3:GetObject",
                    "s3:DeleteObject"
                )
                Resource = "arn:aws:s3:::$BUCKET_NAME/*"
            }
        )
    } | ConvertTo-Json -Compress
    
    # Sauvegarder temporairement
    $policyFile = "s3-policy-temp.json"
    $policyDocument | Out-File -FilePath $policyFile -Encoding utf8
    
    # Ajouter la politique inline
    Write-Host "📤 Ajout de la politique S3..." -ForegroundColor Cyan
    aws iam put-role-policy `
        --role-name $roleName `
        --policy-name "S3AvatarsAccess" `
        --policy-document "file://$policyFile"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Permissions S3 ajoutées avec succès !" -ForegroundColor Green
    } else {
        Write-Host "❌ Erreur lors de l'ajout des permissions" -ForegroundColor Red
    }
    
    # Nettoyer
    Remove-Item -Path $policyFile -ErrorAction SilentlyContinue
    
} catch {
    Write-Host "❌ Erreur: $_" -ForegroundColor Red
    Write-Host "`n💡 Vous pouvez ajouter manuellement les permissions dans AWS Console:" -ForegroundColor Yellow
    Write-Host "   1. IAM > Rôles > [Nom du rôle Lambda]" -ForegroundColor Gray
    Write-Host "   2. Ajouter une politique inline avec les permissions S3" -ForegroundColor Gray
    exit 1
}






