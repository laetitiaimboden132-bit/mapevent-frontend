# Script pour voir les logs Lambda (filtre les caractères problématiques)

param(
    [int]$Minutes = 5
)

$FUNCTION_NAME = "mapevent-backend"
$REGION = "eu-west-1"
$LOG_GROUP = "/aws/lambda/$FUNCTION_NAME"

Write-Host "Récupération des logs Lambda..." -ForegroundColor Cyan
Write-Host ""

# Utiliser CloudWatch Logs Insights pour éviter les problèmes d'encodage
$query = @"
fields @timestamp, @message
| filter @message like /ERROR/ or @message like /Exception/ or @message like /Traceback/ or @message like /send-verification/ or @message like /email/
| sort @timestamp desc
| limit 50
"@

$tempQueryFile = [System.IO.Path]::GetTempFileName() + ".txt"
$query | Out-File -FilePath $tempQueryFile -Encoding UTF8

try {
    Write-Host "Exécution de la requête CloudWatch Logs Insights..." -ForegroundColor Yellow
    
    # Créer la requête
    $startTime = (Get-Date).AddMinutes(-$Minutes).ToUniversalTime()
    $endTime = (Get-Date).ToUniversalTime()
    
    $startTimeStr = $startTime.ToString("yyyy-MM-ddTHH:mm:ss")
    $endTimeStr = $endTime.ToString("yyyy-MM-ddTHH:mm:ss")
    
    $queryId = aws logs start-query `
        --log-group-name $LOG_GROUP `
        --start-time ([int](New-TimeSpan -Start (Get-Date "1970-01-01") -End $startTime).TotalSeconds) `
        --end-time ([int](New-TimeSpan -Start (Get-Date "1970-01-01") -End $endTime).TotalSeconds) `
        --query-string $query `
        --region $REGION `
        --query 'queryId' `
        --output text 2>&1
    
    if ($LASTEXITCODE -eq 0 -and $queryId -notmatch "error") {
        Write-Host "Attente des résultats (5 secondes)..." -ForegroundColor Yellow
        Start-Sleep -Seconds 5
        
        # Récupérer les résultats
        $results = aws logs get-query-results `
            --query-id $queryId `
            --region $REGION `
            --output json 2>&1 | ConvertFrom-Json
        
        if ($results.results.Count -gt 0) {
            Write-Host ""
            Write-Host "============================================================" -ForegroundColor Cyan
            Write-Host "LOGS TROUVÉS: $($results.results.Count)" -ForegroundColor Green
            Write-Host "============================================================" -ForegroundColor Cyan
            Write-Host ""
            
            foreach ($result in $results.results) {
                $timestamp = ($result | Where-Object { $_.field -eq '@timestamp' }).value
                $message = ($result | Where-Object { $_.field -eq '@message' }).value
                
                # Nettoyer les emojis et caractères problématiques
                $cleanMessage = $message -replace '[^\x00-\x7F]', '?'
                
                if ($cleanMessage -match "ERROR|Exception|Traceback") {
                    Write-Host "[$timestamp] " -NoNewline -ForegroundColor Red
                    Write-Host $cleanMessage -ForegroundColor Red
                } elseif ($cleanMessage -match "WARNING") {
                    Write-Host "[$timestamp] " -NoNewline -ForegroundColor Yellow
                    Write-Host $cleanMessage -ForegroundColor Yellow
                } else {
                    Write-Host "[$timestamp] " -NoNewline -ForegroundColor Gray
                    Write-Host $cleanMessage -ForegroundColor White
                }
            }
        } else {
            Write-Host "Aucun log trouvé avec les filtres" -ForegroundColor Yellow
            Write-Host ""
            Write-Host "Récupération des logs bruts..." -ForegroundColor Yellow
            
            # Fallback: récupérer les logs bruts
            $rawLogs = aws logs tail $LOG_GROUP `
                --since ${Minutes}m `
                --region $REGION `
                --format short 2>&1 | Out-String
            
            # Nettoyer et afficher
            $cleanLogs = $rawLogs -replace '[^\x00-\x7F]', '?'
            $cleanLogs -split "`n" | Select-Object -Last 30 | ForEach-Object {
                if ($_ -match "ERROR|Exception|Traceback|send-verification|email") {
                    Write-Host $_ -ForegroundColor White
                }
            }
        }
    } else {
        Write-Host "Erreur lors de la création de la requête: $queryId" -ForegroundColor Red
        Write-Host ""
        Write-Host "Récupération des logs bruts (sans filtre)..." -ForegroundColor Yellow
        
        # Fallback simple
        aws logs tail $LOG_GROUP `
            --since ${Minutes}m `
            --region $REGION `
            --format short 2>&1 | 
        ForEach-Object { $_ -replace '[^\x00-\x7F]', '?' } |
        Select-String -Pattern "ERROR|Exception|Traceback|send-verification|email|bcrypt|psycopg2" |
        Select-Object -Last 20
    }
    
} catch {
    Write-Host "ERREUR: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Méthode alternative: Vérifiez les logs dans la console AWS" -ForegroundColor Yellow
    Write-Host "CloudWatch > Log groups > $LOG_GROUP" -ForegroundColor Gray
} finally {
    Remove-Item -Path $tempQueryFile -Force -ErrorAction SilentlyContinue
}

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
