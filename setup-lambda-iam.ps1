# Script pour configurer les permissions IAM Lambda pour S3
# Exécuter: .\setup-lambda-iam.ps1

$FUNCTION_NAME = "MapEventAI-Backend"  # À adapter selon votre nom de fonction Lambda
$REGION = "eu-west-1"
$POLICY_NAME = "S3AvatarsAccessPolicy"

Write-Host "🔐 Configuration des permissions IAM Lambda pour S3" -ForegroundColor Cyan
Write-Host ""

# Vérifier que AWS CLI est installé
if (-not (Get-Command aws -ErrorAction SilentlyContinue)) {
    Write-Host "❌ AWS CLI n'est pas installé" -ForegroundColor Red
    exit 1
}

# 1. Récupérer le rôle IAM de la fonction Lambda
Write-Host "📥 Récupération du rôle IAM de la fonction Lambda..." -ForegroundColor Yellow
try {
    $functionConfig = aws lambda get-function-configuration --function-name $FUNCTION_NAME --region $REGION | ConvertFrom-Json
    $roleArn = $functionConfig.Role
    $roleName = ($roleArn -split '/')[-1]
    
    Write-Host "✅ Rôle IAM trouvé: $roleName" -ForegroundColor Green
    Write-Host ""
    
    # 2. Créer la politique IAM
    Write-Host "📝 Création de la politique IAM..." -ForegroundColor Yellow
    
    $policyDocument = Get-Content "setup-lambda-iam-policy.json" -Raw
    
    # Vérifier si la politique existe déjà
    $existingPolicies = aws iam list-policies --scope Local --query "Policies[?PolicyName=='$POLICY_NAME']" | ConvertFrom-Json
    
    if ($existingPolicies.Count -eq 0) {
        # Créer la politique
        $policyResult = aws iam create-policy `
            --policy-name $POLICY_NAME `
            --policy-document $policyDocument `
            --description "Permissions pour accéder au bucket S3 mapevent-avatars"
        
        if ($LASTEXITCODE -eq 0) {
            $policyArn = ($policyResult | ConvertFrom-Json).Policy.Arn
            Write-Host "✅ Politique IAM créée: $policyArn" -ForegroundColor Green
        } else {
            Write-Host "❌ Erreur lors de la création de la politique" -ForegroundColor Red
            exit 1
        }
    } else {
        $policyArn = $existingPolicies[0].Arn
        Write-Host "✅ Politique IAM existe déjà: $policyArn" -ForegroundColor Green
    }
    
    Write-Host ""
    
    # 3. Attacher la politique au rôle
    Write-Host "🔗 Attachement de la politique au rôle..." -ForegroundColor Yellow
    
    try {
        aws iam attach-role-policy `
            --role-name $roleName `
            --policy-arn $policyArn
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Politique attachée au rôle avec succès !" -ForegroundColor Green
        } else {
            Write-Host "⚠️ La politique est peut-être déjà attachée" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "⚠️ Erreur: $_" -ForegroundColor Yellow
        Write-Host "   La politique est peut-être déjà attachée" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "✅ Configuration IAM terminée !" -ForegroundColor Green
    
} catch {
    Write-Host "❌ Erreur: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "💡 Configuration manuelle requise:" -ForegroundColor Yellow
    Write-Host "   1. Allez dans AWS Console > IAM > Rôles" -ForegroundColor White
    Write-Host "   2. Trouvez le rôle de votre fonction Lambda" -ForegroundColor White
    Write-Host "   3. Ajoutez la politique avec les permissions suivantes:" -ForegroundColor White
    Write-Host "      - s3:PutObject sur arn:aws:s3:::mapevent-avatars/*" -ForegroundColor Cyan
    Write-Host "      - s3:PutObjectAcl sur arn:aws:s3:::mapevent-avatars/*" -ForegroundColor Cyan
    Write-Host "      - s3:GetObject sur arn:aws:s3:::mapevent-avatars/*" -ForegroundColor Cyan
    Write-Host "      - s3:DeleteObject sur arn:aws:s3:::mapevent-avatars/*" -ForegroundColor Cyan
    Write-Host "      - s3:ListBucket sur arn:aws:s3:::mapevent-avatars" -ForegroundColor Cyan
}

Write-Host ""

