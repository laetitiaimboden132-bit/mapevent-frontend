# Script pour voir les logs Lambda sans problème d'encodage

param(
    [int]$Minutes = 5,
    [string]$Filter = ""
)

$FUNCTION_NAME = "mapevent-backend"
$REGION = "eu-west-1"
$LOG_GROUP = "/aws/lambda/$FUNCTION_NAME"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "LOGS LAMBDA - $FUNCTION_NAME" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Récupération des logs (derniers $Minutes minutes)..." -ForegroundColor Yellow
Write-Host ""

try {
    # Récupérer les logs avec format JSON pour éviter les problèmes d'encodage
    $logs = aws logs tail $LOG_GROUP `
        --since ${Minutes}m `
        --region $REGION `
        --format json `
        2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERREUR: Impossible de récupérer les logs" -ForegroundColor Red
        Write-Host "Message: $logs" -ForegroundColor Red
        exit 1
    }
    
    # Parser le JSON
    $logEntries = $logs | ConvertFrom-Json
    
    if ($logEntries.Count -eq 0) {
        Write-Host "Aucun log récent (derniers $Minutes minutes)" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Essayez d'augmenter le nombre de minutes:" -ForegroundColor Cyan
        Write-Host "   .\voir-logs-lambda.ps1 -Minutes 10" -ForegroundColor Gray
        exit 0
    }
    
    Write-Host "Logs trouvés: $($logEntries.Count) entrées" -ForegroundColor Green
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Filtrer si nécessaire
    $filteredLogs = if ($Filter) {
        $logEntries | Where-Object { $_.message -match $Filter }
    } else {
        $logEntries
    }
    
    # Afficher les logs
    foreach ($log in $filteredLogs) {
        $timestamp = $log.timestamp
        $message = $log.message
        
        # Colorer selon le type de log
        if ($message -match "ERROR|Exception|Traceback|❌|ERREUR") {
            Write-Host "[$timestamp] " -NoNewline -ForegroundColor Red
            Write-Host $message -ForegroundColor Red
        } elseif ($message -match "WARNING|⚠️|ATTENTION") {
            Write-Host "[$timestamp] " -NoNewline -ForegroundColor Yellow
            Write-Host $message -ForegroundColor Yellow
        } elseif ($message -match "INFO|✅|SUCCESS") {
            Write-Host "[$timestamp] " -NoNewline -ForegroundColor Green
            Write-Host $message -ForegroundColor Green
        } else {
            Write-Host "[$timestamp] " -NoNewline -ForegroundColor Gray
            Write-Host $message -ForegroundColor White
        }
    }
    
    Write-Host ""
    Write-Host "============================================================" -ForegroundColor Cyan
    Write-Host ""
    
    # Résumé des erreurs
    $errors = $logEntries | Where-Object { $_.message -match "ERROR|Exception|Traceback" }
    if ($errors.Count -gt 0) {
        Write-Host "⚠️  ERREURS TROUVÉES: $($errors.Count)" -ForegroundColor Red
        Write-Host ""
        Write-Host "Dernières erreurs:" -ForegroundColor Yellow
        $errors | Select-Object -Last 5 | ForEach-Object {
            Write-Host "  - $($_.message)" -ForegroundColor Red
        }
    } else {
        Write-Host "✅ Aucune erreur dans les logs récents" -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "Pour filtrer les logs:" -ForegroundColor Cyan
    Write-Host "   .\voir-logs-lambda.ps1 -Filter 'sendgrid'" -ForegroundColor Gray
    Write-Host "   .\voir-logs-lambda.ps1 -Filter 'bcrypt'" -ForegroundColor Gray
    Write-Host "   .\voir-logs-lambda.ps1 -Filter 'ERROR'" -ForegroundColor Gray
    
} catch {
    Write-Host "ERREUR lors de la récupération des logs:" -ForegroundColor Red
    Write-Host "   $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Essayez avec format short:" -ForegroundColor Yellow
    Write-Host "   aws logs tail $LOG_GROUP --since ${Minutes}m --region $REGION --format short" -ForegroundColor Gray
}
