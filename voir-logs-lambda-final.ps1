# Script final pour voir les logs Lambda (gère l'encodage UTF-8)

param(
    [int]$Minutes = 5
)

$FUNCTION_NAME = "mapevent-backend"
$REGION = "eu-west-1"
$LOG_GROUP = "/aws/lambda/$FUNCTION_NAME"

Write-Host "Récupération des logs Lambda..." -ForegroundColor Cyan
Write-Host ""

# Créer un fichier temporaire avec UTF-8
$tempFile = Join-Path $env:TEMP "lambda-logs-$(Get-Date -Format 'yyyyMMdd-HHmmss').txt"

try {
    # Récupérer les logs et sauvegarder dans un fichier UTF-8
    $env:AWS_PAGER = ""
    aws logs tail $LOG_GROUP `
        --since ${Minutes}m `
        --region $REGION `
        --format short 2>&1 | 
    Out-File -FilePath $tempFile -Encoding UTF8 -Force
    
    if (Test-Path $tempFile) {
        # Lire le fichier avec UTF-8
        $logs = Get-Content $tempFile -Encoding UTF8 -Raw
        
        if ($logs) {
            Write-Host "============================================================" -ForegroundColor Cyan
            Write-Host "LOGS LAMBDA - $FUNCTION_NAME" -ForegroundColor Cyan
            Write-Host "============================================================" -ForegroundColor Cyan
            Write-Host ""
            
            # Séparer les lignes
            $logLines = $logs -split "`n"
            
            # Filtrer les lignes importantes
            $importantLines = $logLines | Where-Object {
                $_ -match "ERROR|Exception|Traceback|send-verification|email|bcrypt|psycopg2|WARNING|INFO.*send|INFO.*email"
            }
            
            if ($importantLines.Count -gt 0) {
                Write-Host "Lignes importantes trouvées: $($importantLines.Count)" -ForegroundColor Green
                Write-Host ""
                
                foreach ($line in $importantLines) {
                    # Nettoyer la ligne (enlever les caractères de contrôle)
                    $cleanLine = $line.Trim()
                    
                    if ($cleanLine -match "ERROR|Exception|Traceback") {
                        Write-Host $cleanLine -ForegroundColor Red
                    } elseif ($cleanLine -match "WARNING") {
                        Write-Host $cleanLine -ForegroundColor Yellow
                    } elseif ($cleanLine -match "INFO") {
                        Write-Host $cleanLine -ForegroundColor Green
                    } else {
                        Write-Host $cleanLine -ForegroundColor White
                    }
                }
            } else {
                Write-Host "Aucune ligne importante trouvée" -ForegroundColor Yellow
                Write-Host ""
                Write-Host "Dernières lignes (sans filtre):" -ForegroundColor Cyan
                $logLines | Select-Object -Last 20 | ForEach-Object {
                    Write-Host $_.Trim() -ForegroundColor Gray
                }
            }
            
            Write-Host ""
            Write-Host "============================================================" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "Fichier complet sauvegardé dans:" -ForegroundColor Cyan
            Write-Host "   $tempFile" -ForegroundColor Gray
            Write-Host ""
            Write-Host "Pour voir tous les logs:" -ForegroundColor Cyan
            Write-Host "   Get-Content '$tempFile' -Encoding UTF8" -ForegroundColor Gray
            
        } else {
            Write-Host "Aucun log trouvé" -ForegroundColor Yellow
        }
    } else {
        Write-Host "Erreur: Impossible de créer le fichier de logs" -ForegroundColor Red
    }
    
} catch {
    Write-Host "ERREUR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Vérifiez les logs dans la console AWS:" -ForegroundColor Yellow
    Write-Host "   CloudWatch > Log groups > $LOG_GROUP" -ForegroundColor Gray
}
