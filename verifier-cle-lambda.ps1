# Script pour voir la valeur exacte de SENDGRID_API_KEY dans Lambda

$FUNCTION_NAME = "mapevent-backend"
$REGION = "eu-west-1"

Write-Host "Recuperation de la configuration Lambda..." -ForegroundColor Yellow
Write-Host ""

try {
    $config = aws lambda get-function-configuration `
        --function-name $FUNCTION_NAME `
        --region $REGION `
        --query 'Environment.Variables' `
        --output json 2>&1
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERREUR: $config" -ForegroundColor Red
        exit 1
    }
    
    $envVars = $config | ConvertFrom-Json
    
    Write-Host "Variables d'environnement trouvees:" -ForegroundColor Cyan
    Write-Host ""
    
    foreach ($key in $envVars.PSObject.Properties.Name) {
        $value = $envVars.$key
        
        if ($key -eq "SENDGRID_API_KEY") {
            Write-Host "$key = " -NoNewline -ForegroundColor Yellow
            if ([string]::IsNullOrWhiteSpace($value)) {
                Write-Host "(VIDE)" -ForegroundColor Red
            } elseif ($value.Length -lt 10) {
                Write-Host "$value (TROP COURT - devrait faire ~69 caracteres)" -ForegroundColor Red
            } elseif (-not ($value -match "^SG\.")) {
                Write-Host "$value (NE COMMENCE PAS PAR 'SG.')" -ForegroundColor Red
            } else {
                $masked = $value.Substring(0, 5) + "..." + $value.Substring($value.Length - 5)
                Write-Host "$masked (OK - $($value.Length) caracteres)" -ForegroundColor Green
            }
        } else {
            # Masquer les autres clés sensibles
            if ($key -match "PASSWORD|SECRET|KEY|TOKEN") {
                $masked = if ($value.Length -gt 10) { 
                    $value.Substring(0, 5) + "..." + $value.Substring($value.Length - 5) 
                } else { 
                    "***" 
                }
                Write-Host "$key = $masked" -ForegroundColor Gray
            } else {
                Write-Host "$key = $value" -ForegroundColor Gray
            }
        }
    }
    
    Write-Host ""
    
    if (-not ($envVars.PSObject.Properties.Name -contains "SENDGRID_API_KEY")) {
        Write-Host "❌ SENDGRID_API_KEY n'existe pas dans Lambda" -ForegroundColor Red
    } elseif ([string]::IsNullOrWhiteSpace($envVars.SENDGRID_API_KEY)) {
        Write-Host "❌ SENDGRID_API_KEY est VIDE" -ForegroundColor Red
    } elseif (-not ($envVars.SENDGRID_API_KEY -match "^SG\.")) {
        Write-Host "❌ SENDGRID_API_KEY a un format invalide" -ForegroundColor Red
        Write-Host "   Valeur actuelle: $($envVars.SENDGRID_API_KEY)" -ForegroundColor Yellow
        Write-Host "   (Une cle SendGrid doit commencer par 'SG.')" -ForegroundColor Yellow
    } else {
        Write-Host "✅ SENDGRID_API_KEY semble correcte" -ForegroundColor Green
    }
    
} catch {
    Write-Host "ERREUR: $($_.Exception.Message)" -ForegroundColor Red
}
