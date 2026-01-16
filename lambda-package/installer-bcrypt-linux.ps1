# Script pour installer bcrypt avec les binaires Linux pour Lambda

Write-Host "Installation de bcrypt pour Lambda (Linux)..." -ForegroundColor Cyan

$DEPS_DIR = "lambda-deps"
New-Item -ItemType Directory -Path $DEPS_DIR -Force | Out-Null

# Méthode 1: Essayer avec Docker (recommandé)
try {
    docker --version | Out-Null
    Write-Host "Utilisation de Docker pour installer bcrypt Linux..." -ForegroundColor Yellow
    
    $workspacePath = (Get-Location).Path
    $dockerCmd = "docker run --rm -v `"${workspacePath}:/workspace`" -w /workspace python:3.12-slim bash -c `"pip install --no-cache-dir bcrypt==4.1.2 -t lambda-deps`""
    
    Invoke-Expression $dockerCmd
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ bcrypt installé avec Docker (Linux)" -ForegroundColor Green
        
        # Vérifier que bcrypt est bien installé
        if (Test-Path "$DEPS_DIR/bcrypt") {
            Write-Host "✅ bcrypt trouvé dans $DEPS_DIR" -ForegroundColor Green
        } else {
            Write-Host "⚠️  bcrypt non trouvé après installation" -ForegroundColor Yellow
        }
    } else {
        Write-Host "❌ Échec installation Docker" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "❌ Docker non disponible: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "SOLUTION ALTERNATIVE:" -ForegroundColor Yellow
    Write-Host "1. Téléchargez bcrypt wheel pour Linux depuis:" -ForegroundColor White
    Write-Host "   https://pypi.org/project/bcrypt/#files" -ForegroundColor Gray
    Write-Host "2. Ou utilisez AWS Lambda Layers avec bcrypt pré-installé" -ForegroundColor White
    exit 1
}

Write-Host ""
Write-Host "✅ Installation terminée!" -ForegroundColor Green
