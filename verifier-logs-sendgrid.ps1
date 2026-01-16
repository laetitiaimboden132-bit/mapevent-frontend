# Script pour verifier les logs Lambda concernant SendGrid

$FUNCTION_NAME = "mapevent-backend"
$REGION = "eu-west-1"

Write-Host "Recuperation des logs Lambda (derniers 5 minutes)..." -ForegroundColor Yellow
Write-Host ""

try {
    $logs = aws logs tail "/aws/lambda/$FUNCTION_NAME" `
        --since 5m `
        --region $REGION `
        --format short 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERREUR: Impossible de recuperer les logs" -ForegroundColor Red
        Write-Host "   Message: $logs" -ForegroundColor Red
        exit 1
    }
    
    if ([string]::IsNullOrWhiteSpace($logs)) {
        Write-Host "Aucun log recent (derniers 5 minutes)" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Essayez de relancer le test d'envoi d'email pour generer des logs" -ForegroundColor Cyan
    } else {
        Write-Host "Logs trouves:" -ForegroundColor Cyan
        Write-Host ""
        
        # Filtrer les lignes pertinentes pour SendGrid
        $lines = $logs -split "`n"
        $sendgridLines = @()
        $errorLines = @()
        
        foreach ($line in $lines) {
            if ($line -match "sendgrid|SENDGRID|email|Email|verification|code") {
                $sendgridLines += $line
            }
            if ($line -match "error|Error|ERROR|exception|Exception|EXCEPTION") {
                $errorLines += $line
            }
        }
        
        if ($sendgridLines.Count -gt 0) {
            Write-Host "=== LIGNES CONCERNANT SENDGRID/EMAIL ===" -ForegroundColor Yellow
            foreach ($line in $sendgridLines) {
                Write-Host $line -ForegroundColor White
            }
            Write-Host ""
        }
        
        if ($errorLines.Count -gt 0) {
            Write-Host "=== ERREURS TROUVEES ===" -ForegroundColor Red
            foreach ($line in $errorLines) {
                Write-Host $line -ForegroundColor Red
            }
            Write-Host ""
        }
        
        if ($sendgridLines.Count -eq 0 -and $errorLines.Count -eq 0) {
            Write-Host "Aucune ligne pertinente trouvee. Affichage des derniers logs:" -ForegroundColor Yellow
            Write-Host ""
            # Afficher les 20 dernieres lignes
            $lastLines = $lines | Select-Object -Last 20
            foreach ($line in $lastLines) {
                Write-Host $line -ForegroundColor Gray
            }
        }
    }
    
} catch {
    Write-Host "ERREUR: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "Pour voir tous les logs en temps reel:" -ForegroundColor Cyan
Write-Host "   aws logs tail /aws/lambda/$FUNCTION_NAME --follow --region $REGION" -ForegroundColor Gray
