# Script pour tester si CloudShell fonctionne
# Note: CloudShell doit être ouvert dans le navigateur AWS Console
# Ce script affiche juste les instructions

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "AWS CloudShell - Instructions" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Allez sur AWS Console : https://console.aws.amazon.com" -ForegroundColor Yellow
Write-Host ""
Write-Host "2. Cliquez sur l'icone CloudShell (en haut de la page)" -ForegroundColor Yellow
Write-Host "   OU allez sur : https://console.aws.amazon.com/cloudshell/home" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Attendez que CloudShell demarre (30-60 secondes)" -ForegroundColor Yellow
Write-Host ""
Write-Host "4. Dans CloudShell, installez psql :" -ForegroundColor Yellow
Write-Host "   sudo yum install -y postgresql15" -ForegroundColor White
Write-Host ""
Write-Host "5. Connectez-vous a la base (remplacez le mot de passe) :" -ForegroundColor Yellow
Write-Host "   PGPASSWORD='VOTRE_MOT_DE_PASSE' psql -h mapevent-db.cr0mmuc0elm6.eu-west-1.rds.amazonaws.com -U postgres -d postgres" -ForegroundColor White
Write-Host ""
Write-Host "6. Voir tous les comptes :" -ForegroundColor Yellow
Write-Host "   SELECT email, username, role FROM users;" -ForegroundColor White
Write-Host ""
Write-Host "7. Supprimer tous sauf l'admin (remplacez l'email) :" -ForegroundColor Yellow
Write-Host "   DELETE FROM users WHERE email != 'VOTRE-EMAIL-ADMIN@example.com';" -ForegroundColor White
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Pour plus de details, ouvrez : SUPPRIMER_COMPTES_CLOUDSHELL.txt" -ForegroundColor Green
Write-Host ""

