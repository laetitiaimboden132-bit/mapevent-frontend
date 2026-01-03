# Script pour vérifier le statut de la dernière invalidation CloudFront

$distId = aws cloudfront list-distributions --query "DistributionList.Items[?Aliases.Items[0]=='mapevent.world'].Id" --output text --region eu-west-1

if ($distId) {
    Write-Host "🔍 Vérification du statut de l'invalidation CloudFront..." -ForegroundColor Cyan
    Write-Host ""
    
    $invalidation = aws cloudfront list-invalidations --distribution-id $distId --max-items 1 --region eu-west-1 --query "InvalidationList.Items[0]" --output json | ConvertFrom-Json
    
    if ($invalidation) {
        Write-Host "ID de l'invalidation: $($invalidation.Id)" -ForegroundColor Yellow
        Write-Host "Statut: $($invalidation.Status)" -ForegroundColor $(if ($invalidation.Status -eq "Completed") { "Green" } else { "Yellow" })
        Write-Host "Créée le: $($invalidation.CreateTime)" -ForegroundColor Gray
        
        if ($invalidation.Status -eq "Completed") {
            Write-Host ""
            Write-Host "✅ L'invalidation est terminée ! Vous pouvez rafraîchir la page." -ForegroundColor Green
        } else {
            Write-Host ""
            Write-Host "⏳ L'invalidation est en cours... Attendez quelques secondes et relancez cette commande." -ForegroundColor Yellow
        }
    } else {
        Write-Host "⚠️ Aucune invalidation trouvée." -ForegroundColor Yellow
    }
} else {
    Write-Host "❌ Distribution CloudFront non trouvée pour mapevent.world" -ForegroundColor Red
}








