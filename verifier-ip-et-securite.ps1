# Script pour vérifier l'IP et donner des instructions
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "VERIFICATION IP ET SECURITE RDS" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Récupérer l'IP publique
Write-Host "Recuperation de votre IP publique..." -ForegroundColor Yellow
try {
    $ip = (Invoke-WebRequest -Uri "https://api.ipify.org" -UseBasicParsing -TimeoutSec 10).Content.Trim()
    Write-Host ""
    Write-Host "VOTRE IP PUBLIQUE ACTUELLE: $ip" -ForegroundColor Green
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host "VERIFICATIONS A FAIRE SUR AWS:" -ForegroundColor Cyan
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "1. VERIFIER QUE CETTE IP EST DANS LE SECURITY GROUP:" -ForegroundColor Yellow
    Write-Host "   - Allez sur AWS Console > RDS > mapevent-db" -ForegroundColor White
    Write-Host "   - Connectivite et securite > Groupes de securite" -ForegroundColor White
    Write-Host "   - Cliquez sur 'default (sg-09293e0d6313eb92c)'" -ForegroundColor White
    Write-Host "   - Regles entrantes > Vérifiez que '$ip/32' est presente" -ForegroundColor White
    Write-Host "   - Type: PostgreSQL | Port: 5432 | Source: $ip/32" -ForegroundColor White
    Write-Host ""
    Write-Host "2. VERIFIER QUE LA BASE EST PUBLIQUE:" -ForegroundColor Yellow
    Write-Host "   - RDS > mapevent-db > Connectivite et securite" -ForegroundColor White
    Write-Host "   - 'Accessible publiquement' doit etre OUI" -ForegroundColor White
    Write-Host ""
    Write-Host "3. TEMPS DE PROPAGATION AWS:" -ForegroundColor Yellow
    Write-Host "   - Attendez 10-30 minutes apres avoir modifie le Security Group" -ForegroundColor White
    Write-Host "   - Ou attendez 10-30 minutes apres avoir mis 'Accessible publiquement'" -ForegroundColor White
    Write-Host ""
    Write-Host "4. PARE-FEU TIERS:" -ForegroundColor Yellow
    Write-Host "   - Verifiez votre antivirus/pare-feu tiers" -ForegroundColor White
    Write-Host "   - Ajoutez une exception pour Python ou port 5432" -ForegroundColor White
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Voulez-vous que je vous aide a tester la connexion depuis Lambda?" -ForegroundColor Green
    Write-Host "(Cela permettra de savoir si c'est un probleme local ou AWS)" -ForegroundColor Gray
    Write-Host ""
    
} catch {
    Write-Host "ERREUR: Impossible de recuperer l'IP automatiquement" -ForegroundColor Red
    Write-Host ""
    Write-Host "Allez sur https://whatismyip.com manuellement" -ForegroundColor Yellow
    Write-Host ""
}

