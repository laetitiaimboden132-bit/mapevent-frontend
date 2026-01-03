# Script pour réinitialiser le mot de passe RDS

$DB_INSTANCE = "mapevent-db"
$REGION = "eu-west-1"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  REINITIALISATION MOT DE PASSE RDS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Générer un mot de passe sécurisé
function Generate-SecurePassword {
    $length = 16
    $chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*"
    $password = ""
    for ($i = 0; $i -lt $length; $i++) {
        $password += $chars[(Get-Random -Maximum $chars.Length)]
    }
    return $password
}

Write-Host "1. Generation d'un mot de passe securise..." -ForegroundColor Yellow
$newPassword = Generate-SecurePassword
Write-Host "   Mot de passe genere: $newPassword" -ForegroundColor Green
Write-Host ""

# Demander confirmation
Write-Host "2. Voulez-vous reinitialiser le mot de passe maintenant ?" -ForegroundColor Yellow
Write-Host "   ⚠️  L'instance sera redemarree (2-5 minutes)" -ForegroundColor Red
Write-Host ""
$confirm = Read-Host "   Tapez 'OUI' pour confirmer"

if ($confirm -ne "OUI") {
    Write-Host ""
    Write-Host "Operation annulee." -ForegroundColor Yellow
    exit
}

Write-Host ""
Write-Host "3. Reinitialisation du mot de passe..." -ForegroundColor Yellow

try {
    $result = aws rds modify-db-instance `
        --db-instance-identifier $DB_INSTANCE `
        --master-user-password $newPassword `
        --apply-immediately `
        --region $REGION `
        --output json 2>&1 | ConvertFrom-Json
    
    if ($result) {
        Write-Host ""
        Write-Host "✅ Mot de passe reinitialise avec succes!" -ForegroundColor Green
        Write-Host ""
        Write-Host "   Instance: $($result.DBInstance.DBInstanceIdentifier)" -ForegroundColor Cyan
        Write-Host "   Status: $($result.DBInstance.DBInstanceStatus)" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "⏳ L'instance est en cours de modification..." -ForegroundColor Yellow
        Write-Host "   Cela peut prendre 2-5 minutes." -ForegroundColor Yellow
        Write-Host ""
        
        # Mettre à jour lambda.env
        Write-Host "4. Mise a jour de lambda.env..." -ForegroundColor Yellow
        $envFile = "lambda.env"
        if (Test-Path $envFile) {
            $content = Get-Content $envFile -Raw
            $content = $content -replace 'RDS_PASSWORD=.*', "RDS_PASSWORD=$newPassword"
            Set-Content -Path $envFile -Value $content -NoNewline
            Write-Host "   ✅ lambda.env mis a jour" -ForegroundColor Green
        } else {
            Write-Host "   ⚠️  Fichier lambda.env non trouve" -ForegroundColor Yellow
        }
        
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host "  MOT DE PASSE ENREGISTRE" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Nouveau mot de passe: $newPassword" -ForegroundColor Green
        Write-Host ""
        Write-Host "⚠️  IMPORTANT: Sauvegardez ce mot de passe!" -ForegroundColor Red
        Write-Host ""
        Write-Host "Prochaine etape:" -ForegroundColor Yellow
        Write-Host "  1. Attendez que l'instance soit disponible (status: available)" -ForegroundColor Gray
        Write-Host "  2. Executez: .\configure_lambda_env.ps1" -ForegroundColor Gray
        Write-Host ""
        
        # Afficher le statut en temps réel
        Write-Host "Verification du statut..." -ForegroundColor Cyan
        Start-Sleep -Seconds 5
        
        $status = aws rds describe-db-instances `
            --db-instance-identifier $DB_INSTANCE `
            --region $REGION `
            --query 'DBInstances[0].DBInstanceStatus' `
            --output text 2>$null
        
        Write-Host "   Status actuel: $status" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Pour suivre la progression:" -ForegroundColor Yellow
        Write-Host "   aws rds describe-db-instances --db-instance-identifier $DB_INSTANCE --region $REGION --query 'DBInstances[0].DBInstanceStatus' --output text" -ForegroundColor Gray
        
    } else {
        Write-Host "❌ Erreur lors de la reinitialisation" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host ""
    Write-Host "❌ Erreur: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Verifiez que:" -ForegroundColor Yellow
    Write-Host "  - AWS CLI est configure" -ForegroundColor Gray
    Write-Host "  - Vous avez les permissions RDS" -ForegroundColor Gray
    Write-Host "  - L'instance existe: $DB_INSTANCE" -ForegroundColor Gray
    exit 1
}





