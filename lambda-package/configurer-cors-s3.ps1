# Script PowerShell pour configurer CORS sur le bucket S3 mapevent-avatars
# Ce script configure CORS pour permettre l'accès aux images depuis le frontend

Write-Host "`n=== Configuration CORS pour mapevent-avatars ===" -ForegroundColor Cyan

$BUCKET_NAME = "mapevent-avatars"
$REGION = "eu-west-1"

# Configuration CORS complète
$CORS_CONFIG = @{
    CORSRules = @(
        @{
            AllowedHeaders = @("*")
            AllowedMethods = @("GET", "HEAD")
            AllowedOrigins = @("*")
            ExposeHeaders = @("ETag", "Content-Length", "Content-Type")
            MaxAgeSeconds = 3600
        }
    )
} | ConvertTo-Json -Depth 10

Write-Host "`n📋 Configuration CORS:" -ForegroundColor Yellow
Write-Host $CORS_CONFIG -ForegroundColor Gray

# Sauvegarder la config dans un fichier temporaire
$TEMP_FILE = "cors-config-temp.json"
$CORS_CONFIG | Out-File -FilePath $TEMP_FILE -Encoding UTF8

Write-Host "`n🔧 Application de la configuration CORS..." -ForegroundColor Yellow

try {
    # Appliquer la configuration CORS
    aws s3api put-bucket-cors `
        --bucket $BUCKET_NAME `
        --region $REGION `
        --cors-configuration file://$TEMP_FILE
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n✅ Configuration CORS appliquée avec succès !" -ForegroundColor Green
        
        # Vérifier la configuration
        Write-Host "`n🔍 Vérification de la configuration..." -ForegroundColor Yellow
        aws s3api get-bucket-cors --bucket $BUCKET_NAME --region $REGION | ConvertFrom-Json | ConvertTo-Json -Depth 10
        
        Write-Host "`n✅ CORS configuré correctement !" -ForegroundColor Green
        Write-Host "   - AllowedOrigins: *" -ForegroundColor White
        Write-Host "   - AllowedMethods: GET, HEAD" -ForegroundColor White
        Write-Host "   - AllowedHeaders: *" -ForegroundColor White
    } else {
        Write-Host "`n❌ Erreur lors de l'application de la configuration CORS" -ForegroundColor Red
        Write-Host "   Code de sortie: $LASTEXITCODE" -ForegroundColor Red
    }
} catch {
    Write-Host "`n❌ Erreur: $_" -ForegroundColor Red
} finally {
    # Nettoyer le fichier temporaire
    if (Test-Path $TEMP_FILE) {
        Remove-Item $TEMP_FILE -Force
    }
}

Write-Host "`n💡 Note: Si le bucket n'autorise pas les ACLs, assurez-vous que la politique du bucket permet l'accès public en lecture." -ForegroundColor Cyan
Write-Host "   Vous pouvez vérifier avec: aws s3api get-bucket-policy --bucket $BUCKET_NAME" -ForegroundColor Gray




