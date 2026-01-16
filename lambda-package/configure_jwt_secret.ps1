# Script PowerShell pour configurer JWT_SECRET dans AWS Lambda
# Usage: .\configure_jwt_secret.ps1 [secret]

param(
    [string]$Secret = ""
)

$FUNCTION_NAME = "mapevent-backend"
$REGION = "eu-west-1"

# Générer un secret si non fourni
if ([string]::IsNullOrEmpty($Secret)) {
    Write-Host "Génération d'un secret aléatoire..." -ForegroundColor Yellow
    # Méthode compatible avec toutes les versions de PowerShell
    $bytes = New-Object byte[] 32
    $rng = New-Object System.Security.Cryptography.RNGCryptoServiceProvider
    $rng.GetBytes($bytes)
    $Secret = [System.BitConverter]::ToString($bytes).Replace("-", "").ToLower()
    $rng.Dispose()
    Write-Host "Secret généré: $Secret" -ForegroundColor Green
} else {
    Write-Host "Utilisation du secret fourni" -ForegroundColor Yellow
}

# Récupérer les variables d'environnement actuelles
Write-Host "Récupération des variables d'environnement actuelles..." -ForegroundColor Yellow
try {
    $currentConfig = aws lambda get-function-configuration `
        --function-name $FUNCTION_NAME `
        --region $REGION `
        --query 'Environment' `
        --output json | ConvertFrom-Json
    
    $currentVars = @{}
    if ($currentConfig.Variables) {
        $currentConfig.Variables.PSObject.Properties | ForEach-Object {
            $currentVars[$_.Name] = $_.Value
        }
    }
    
    # Ajouter ou mettre à jour JWT_SECRET
    $currentVars["JWT_SECRET"] = $Secret
    
    # Mettre à jour la fonction Lambda avec le format correct
    Write-Host "Mise à jour de la fonction Lambda..." -ForegroundColor Yellow
    
    # Construire le JSON pour --environment Variables
    # Format attendu: {"Variables": {"KEY1": "VALUE1", "KEY2": "VALUE2"}}
    $varsJson = @{}
    foreach ($key in $currentVars.Keys) {
        $varsJson[$key] = $currentVars[$key]
    }
    
    $envObject = @{
        Variables = $varsJson
    }
    
    $envJson = $envObject | ConvertTo-Json -Depth 10 -Compress
    
    # Sauvegarder dans un fichier temporaire pour éviter les problèmes d'échappement
    $tempFile = [System.IO.Path]::GetTempFileName() + ".json"
    $envJson | Out-File -FilePath $tempFile -Encoding UTF8 -NoNewline
    
    try {
        # Utiliser le fichier JSON avec --cli-input-json
        $inputJson = @{
            FunctionName = $FUNCTION_NAME
            Environment = $envObject
        } | ConvertTo-Json -Depth 10
        
        $inputFile = [System.IO.Path]::GetTempFileName() + ".json"
        $inputJson | Out-File -FilePath $inputFile -Encoding UTF8 -NoNewline
        
        $result = aws lambda update-function-configuration `
            --cli-input-json "file://$inputFile" `
            --region $REGION `
            --output json 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ JWT_SECRET configuré avec succès!" -ForegroundColor Green
        } else {
            throw $result
        }
        
        Remove-Item $inputFile -ErrorAction SilentlyContinue
    } catch {
        Write-Host "⚠️  Erreur avec --cli-input-json, tentative avec --environment..." -ForegroundColor Yellow
        
        # Alternative : utiliser --environment directement
        $envJsonEscaped = $envJson -replace '"', '\"'
        
        $result = aws lambda update-function-configuration `
            --function-name $FUNCTION_NAME `
            --region $REGION `
            --environment "$envJsonEscaped" `
            --output json 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ JWT_SECRET configuré avec succès!" -ForegroundColor Green
        } else {
            Write-Host "❌ Erreur: $result" -ForegroundColor Red
            throw
        }
    } finally {
        Remove-Item $tempFile -ErrorAction SilentlyContinue
    }
    
    Write-Host "✅ JWT_SECRET configuré avec succès!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Valeur configurée: $Secret" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "⚠️  IMPORTANT: Notez ce secret dans un endroit sûr!" -ForegroundColor Yellow
    Write-Host "   Il sera nécessaire pour valider les tokens JWT." -ForegroundColor Yellow
    
} catch {
    Write-Host "❌ Erreur lors de la configuration: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "Vérifiez que:" -ForegroundColor Yellow
    Write-Host "  1. AWS CLI est installé et configuré" -ForegroundColor White
    Write-Host "  2. Vous avez les permissions Lambda:UpdateFunctionConfiguration" -ForegroundColor White
    Write-Host "  3. Le nom de la fonction est correct: $FUNCTION_NAME" -ForegroundColor White
    exit 1
}

