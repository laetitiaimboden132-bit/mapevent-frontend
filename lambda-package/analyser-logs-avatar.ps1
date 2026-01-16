# Script PowerShell pour analyser les logs CloudWatch concernant l'avatar
# Recherche spécifiquement les informations sur profile_photo_url

Write-Host "`n=== Analyse des logs CloudWatch - Avatar ===" -ForegroundColor Cyan

$FUNCTION_NAME = "mapevent-backend"
$LOG_GROUP = "/aws/lambda/$FUNCTION_NAME"
$REGION = "eu-west-1"
$HOURS_BACK = 2

# Calculer le temps de début
$startTime = (Get-Date).AddHours(-$HOURS_BACK)
$startTimeUnix = [Math]::Floor([decimal](Get-Date -Date $startTime -UFormat %s))

Write-Host "`n🔍 Recherche des logs des dernières $HOURS_BACK heures..." -ForegroundColor Yellow
Write-Host "   Fonction: $FUNCTION_NAME" -ForegroundColor Gray
Write-Host "   Région: $REGION" -ForegroundColor Gray
Write-Host "   Depuis: $startTime" -ForegroundColor Gray

# Récupérer les logs
$logFile = "logs-avatar-$(Get-Date -Format 'yyyyMMdd-HHmmss').txt"

try {
    # Récupérer les logs et les sauvegarder dans un fichier
    aws logs tail $LOG_GROUP --region $REGION --since "${HOURS_BACK}h" --format short > $logFile 2>&1
    
    if ($LASTEXITCODE -eq 0 -or (Test-Path $logFile)) {
        Write-Host "`n✅ Logs récupérés dans: $logFile" -ForegroundColor Green
        
        # Lire le contenu du fichier
        $logs = Get-Content $logFile -Raw -ErrorAction SilentlyContinue
        
        if ($logs) {
            Write-Host "`n📊 Analyse des logs..." -ForegroundColor Yellow
            
            # Rechercher les mentions de profile_photo_url
            $profilePhotoMatches = [regex]::Matches($logs, "profile_photo_url[^\s]*", [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
            if ($profilePhotoMatches.Count -gt 0) {
                Write-Host "`n✅ Mentions de 'profile_photo_url' trouvées: $($profilePhotoMatches.Count)" -ForegroundColor Green
                $profilePhotoMatches | ForEach-Object {
                    $context = $logs.Substring([Math]::Max(0, $_.Index - 100), [Math]::Min(200, $logs.Length - $_.Index + 100))
                    Write-Host "   ...$context..." -ForegroundColor Gray
                }
            } else {
                Write-Host "`n⚠️ Aucune mention de 'profile_photo_url' trouvée" -ForegroundColor Yellow
            }
            
            # Rechercher les mentions de S3 upload
            $s3UploadMatches = [regex]::Matches($logs, "upload.*S3|Avatar upload|s3.*avatar", [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
            if ($s3UploadMatches.Count -gt 0) {
                Write-Host "`n✅ Mentions d'upload S3 trouvées: $($s3UploadMatches.Count)" -ForegroundColor Green
                $s3UploadMatches | ForEach-Object {
                    $context = $logs.Substring([Math]::Max(0, $_.Index - 100), [Math]::Min(200, $logs.Length - $_.Index + 100))
                    Write-Host "   ...$context..." -ForegroundColor Gray
                }
            } else {
                Write-Host "`n⚠️ Aucune mention d'upload S3 trouvée" -ForegroundColor Yellow
            }
            
            # Rechercher les réponses oauth_google
            $oauthMatches = [regex]::Matches($logs, "oauth.*google|/api/user/oauth/google", [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
            if ($oauthMatches.Count -gt 0) {
                Write-Host "`n✅ Requêtes OAuth Google trouvées: $($oauthMatches.Count)" -ForegroundColor Green
                
                # Extraire les lignes autour des requêtes OAuth
                $lines = $logs -split "`n"
                for ($i = 0; $i -lt $lines.Length; $i++) {
                    if ($lines[$i] -match "oauth.*google|/api/user/oauth/google") {
                        Write-Host "`n   Ligne $($i+1):" -ForegroundColor Cyan
                        # Afficher la ligne et les 5 lignes suivantes
                        for ($j = 0; $j -lt 6 -and ($i+$j) -lt $lines.Length; $j++) {
                            if ($lines[$i+$j] -match "profile_photo|profilePhoto|avatar|S3|response|user") {
                                Write-Host "      $($lines[$i+$j])" -ForegroundColor White
                            }
                        }
                    }
                }
            }
            
            # Rechercher les erreurs
            $errorMatches = [regex]::Matches($logs, "ERROR|Exception|Traceback|Failed|Error", [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
            if ($errorMatches.Count -gt 0) {
                Write-Host "`n⚠️ Erreurs trouvées: $($errorMatches.Count)" -ForegroundColor Yellow
                $errorMatches | Select-Object -First 10 | ForEach-Object {
                    $context = $logs.Substring([Math]::Max(0, $_.Index - 50), [Math]::Min(150, $logs.Length - $_.Index + 50))
                    Write-Host "   ...$context..." -ForegroundColor Red
                }
            }
            
            # Rechercher les réponses JSON avec profile_photo_url
            $jsonMatches = [regex]::Matches($logs, '\{[^}]*"profile_photo_url"[^}]*\}', [System.Text.RegularExpressions.RegexOptions]::IgnoreCase)
            if ($jsonMatches.Count -gt 0) {
                Write-Host "`n✅ JSON avec profile_photo_url trouvé: $($jsonMatches.Count)" -ForegroundColor Green
                $jsonMatches | Select-Object -First 3 | ForEach-Object {
                    Write-Host "   $($_.Value)" -ForegroundColor White
                }
            }
            
        } else {
            Write-Host "`n⚠️ Le fichier de logs est vide ou n'a pas pu être lu" -ForegroundColor Yellow
        }
        
    } else {
        Write-Host "`n❌ Erreur lors de la récupération des logs" -ForegroundColor Red
        Write-Host "   Code de sortie: $LASTEXITCODE" -ForegroundColor Red
    }
    
} catch {
    Write-Host "`n❌ Erreur: $_" -ForegroundColor Red
}

Write-Host "`n📋 Résumé:" -ForegroundColor Cyan
Write-Host "   - Vérifiez si 'profile_photo_url' est présent dans les réponses" -ForegroundColor White
Write-Host "   - Vérifiez si l'upload S3 a réussi" -ForegroundColor White
Write-Host "   - Vérifiez s'il y a des erreurs" -ForegroundColor White
Write-Host "`n💡 Fichier de logs complet: $logFile" -ForegroundColor Gray




