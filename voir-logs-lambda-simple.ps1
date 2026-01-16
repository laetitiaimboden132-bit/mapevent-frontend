# Script simple pour voir les logs Lambda (gère l'encodage)

param(
    [int]$Minutes = 5
)

$FUNCTION_NAME = "mapevent-backend"
$REGION = "eu-west-1"
$LOG_GROUP = "/aws/lambda/$FUNCTION_NAME"

Write-Host "Récupération des logs Lambda (derniers $Minutes minutes)..." -ForegroundColor Cyan
Write-Host ""

# Utiliser --output text et rediriger vers un fichier temporaire pour éviter les problèmes d'encodage
$tempFile = [System.IO.Path]::GetTempFileName()

try {
    # Récupérer les logs et sauvegarder dans un fichier
    aws logs tail $LOG_GROUP `
        --since ${Minutes}m `
        --region $REGION `
        --format short `
        --output text > $tempFile 2>&1
    
    if (Test-Path $tempFile) {
        # Lire le fichier avec l'encodage UTF-8
        $logs = Get-Content $tempFile -Encoding UTF8 -ErrorAction SilentlyContinue
        
        if ($logs) {
            Write-Host "============================================================" -ForegroundColor Cyan
            Write-Host "LOGS LAMBDA - $FUNCTION_NAME" -ForegroundColor Cyan
            Write-Host "============================================================" -ForegroundColor Cyan
            Write-Host ""
            
            # Filtrer et afficher les logs importants
            $errorLogs = @()
            $warningLogs = @()
            $infoLogs = @()
            
            foreach ($line in $logs) {
                if ($line -match "ERROR|Exception|Traceback|bcrypt|psycopg2|sendgrid|email") {
                    if ($line -match "ERROR|Exception|Traceback") {
                        $errorLogs += $line
                        Write-Host $line -ForegroundColor Red
                    } elseif ($line -match "WARNING") {
                        $warningLogs += $line
                        Write-Host $line -ForegroundColor Yellow
                    } else {
                        $infoLogs += $line
                        Write-Host $line -ForegroundColor White
                    }
                }
            }
            
            Write-Host ""
            Write-Host "============================================================" -ForegroundColor Cyan
            Write-Host ""
            
            if ($errorLogs.Count -gt 0) {
                Write-Host "⚠️  ERREURS TROUVÉES: $($errorLogs.Count)" -ForegroundColor Red
                Write-Host ""
                Write-Host "Dernières erreurs:" -ForegroundColor Yellow
                $errorLogs | Select-Object -Last 5 | ForEach-Object {
                    Write-Host "  $_" -ForegroundColor Red
                }
            } else {
                Write-Host "✅ Aucune erreur critique trouvée" -ForegroundColor Green
            }
            
            Write-Host ""
            Write-Host "Pour voir tous les logs (sans filtre):" -ForegroundColor Cyan
            Write-Host "   Get-Content $tempFile" -ForegroundColor Gray
            
        } else {
            Write-Host "Aucun log récent trouvé" -ForegroundColor Yellow
        }
    } else {
        Write-Host "Erreur: Impossible de récupérer les logs" -ForegroundColor Red
    }
    
} catch {
    Write-Host "ERREUR: $($_.Exception.Message)" -ForegroundColor Red
} finally {
    # Garder le fichier pour inspection manuelle
    if (Test-Path $tempFile) {
        Write-Host ""
        Write-Host "Logs sauvegardés dans: $tempFile" -ForegroundColor Gray
        Write-Host "(Le fichier sera supprimé automatiquement)" -ForegroundColor Gray
    }
}
