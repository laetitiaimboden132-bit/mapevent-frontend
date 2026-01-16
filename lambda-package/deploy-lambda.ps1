# Script automatique pour deployer Lambda avec toutes les dependances

param(
    [switch]$SkipZip = $false,
    [switch]$SkipUpload = $false
)

$ZIP_FILE = "lambda-deploy-with-deps.zip"
$DEPS_DIR = "lambda-deps"
$FUNCTION_NAME = "mapevent-backend"
$REGION = "eu-west-1"

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  DEPLOY AUTOMATIQUE LAMBDA" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# ETAPE 1: Nettoyage
Write-Host "[1/5] Nettoyage..." -ForegroundColor Yellow
Remove-Item -Path $ZIP_FILE -ErrorAction SilentlyContinue
Remove-Item -Path $DEPS_DIR -Recurse -ErrorAction SilentlyContinue
Write-Host "   OK" -ForegroundColor Green

# ETAPE 2: Installation des dependances
if (-not $SkipZip) {
    Write-Host "`n[2/5] Installation des dependances Python..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $DEPS_DIR -Force | Out-Null
    
    # Essayer Docker d'abord (garantit les bonnes dépendances Linux)
    $useDocker = $false
    try {
        docker --version | Out-Null
        Write-Host "   Utilisation de Docker pour installer les dépendances Linux..." -ForegroundColor Gray
        
        # Créer un conteneur temporaire avec Python 3.12 Linux
        # Convertir le chemin Windows en format Docker (C:\path -> /c/path)
        $workspacePath = (Get-Location).Path
        $dockerPath = $workspacePath -replace '^([A-Z]):', '/$1' -replace '\\', '/' -replace '([A-Z])', {$_.Value.ToLower()}
        
        Write-Host "   Chemin Windows: $workspacePath" -ForegroundColor Gray
        Write-Host "   Chemin Docker: $dockerPath" -ForegroundColor Gray
        
        # Utiliser le format de volume Docker pour Linux
        # Convertir le chemin Windows en format Linux (/c/path)
        $linuxPath = "/" + ($workspacePath -replace '^([A-Z]):', '$1' -replace '\\', '/' -replace '^([A-Z])', {$_.Value.ToLower()})
        $dockerCmd = "docker run --rm -v `"${workspacePath}:${linuxPath}`" -w ${linuxPath} python:3.12-slim pip install --no-cache-dir -r backend/requirements.txt -t lambda-deps"
        
        Write-Host "   Exécution Docker..." -ForegroundColor Gray
        $dockerOutput = Invoke-Expression $dockerCmd 2>&1 | Tee-Object -Variable dockerResult
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "   ✅ Dépendances installées avec Docker (Linux)" -ForegroundColor Green
            $useDocker = $true
        } else {
            Write-Host "   ⚠️  Docker a échoué (code: $LASTEXITCODE)" -ForegroundColor Yellow
            Write-Host "   Sortie: $dockerOutput" -ForegroundColor Gray
            $useDocker = $false
        }
    } catch {
        Write-Host "   ⚠️  Docker non disponible: $_" -ForegroundColor Yellow
        $useDocker = $false
    }
    
    # Fallback vers pip Windows si Docker n'est pas disponible
    if (-not $useDocker) {
        Write-Host "   Installation depuis requirements.txt (Windows)..." -ForegroundColor Gray
        Write-Host "   ⚠️  ATTENTION: psycopg2-binary peut ne pas fonctionner correctement" -ForegroundColor Yellow
        $pipOutput = pip install -r backend/requirements.txt -t $DEPS_DIR 2>&1
        
        # Verifier si psycopg2 est installe
        $psycopgInstalled = $pipOutput | Select-String -Pattern "Successfully installed.*psycopg2" -Quiet
        if ($psycopgInstalled) {
            Write-Host "   ✅ psycopg2-binary installe (mais binaires Windows)" -ForegroundColor Yellow
        } else {
            Write-Host "   ⚠️  psycopg2 peut ne pas etre installe correctement" -ForegroundColor Yellow
        }
        
        # Installer bcrypt avec Docker (nécessite binaires Linux)
        Write-Host "   Installation de bcrypt avec Docker (Linux)..." -ForegroundColor Gray
        try {
            # Format Docker Desktop pour Windows
            $bcryptCmd = "docker run --rm -v `"${workspacePath}:/workspace`" -w /workspace python:3.12-slim sh -c `"pip install --no-cache-dir bcrypt==4.1.2 -t /workspace/lambda-deps`""
            Invoke-Expression $bcryptCmd 2>&1 | Out-Null
            if ($LASTEXITCODE -eq 0) {
                Write-Host "   ✅ bcrypt installé avec Docker (Linux)" -ForegroundColor Green
            } else {
                Write-Host "   ⚠️  Échec installation bcrypt avec Docker (code: $LASTEXITCODE)" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "   ⚠️  Impossible d'installer bcrypt avec Docker: $_" -ForegroundColor Yellow
            Write-Host "   ⚠️  bcrypt sera installé avec pip Windows (peut ne pas fonctionner dans Lambda)" -ForegroundColor Yellow
        }
    }
    
    Write-Host "   OK" -ForegroundColor Green
} else {
    Write-Host "`n[2/5] Installation des dependances... SKIPPE" -ForegroundColor Gray
}

# ETAPE 3: Copie des fichiers source
if (-not $SkipZip) {
    Write-Host "`n[3/5] Copie des fichiers source..." -ForegroundColor Yellow
    Copy-Item -Path "lambda_function.py" -Destination $DEPS_DIR -Force
    Copy-Item -Path "handler.py" -Destination $DEPS_DIR -Force
    Copy-Item -Path "backend" -Destination $DEPS_DIR -Recurse -Force
    
    # CRITIQUE: Supprimer bcrypt du ZIP de déploiement pour forcer l'utilisation du Layer
    # Le Layer dans /opt/python a les binaires Linux compilés (_bcrypt.so)
    $bcryptDirs = @(
        "$DEPS_DIR\bcrypt",
        "$DEPS_DIR\bcrypt-*.dist-info"
    )
    foreach ($bcryptDir in $bcryptDirs) {
        if (Test-Path $bcryptDir) {
            Write-Host "   ⚠️  Suppression de $bcryptDir (utiliser le Layer à la place)" -ForegroundColor Yellow
            Remove-Item -Path $bcryptDir -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
    # Supprimer aussi les fichiers .pyc et __pycache__ de bcrypt s'ils existent
    Get-ChildItem -Path $DEPS_DIR -Recurse -Filter "*bcrypt*" -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
    
    Write-Host "   OK" -ForegroundColor Green
} else {
    Write-Host "`n[3/5] Copie des fichiers source... SKIPPE" -ForegroundColor Gray
}

# ETAPE 4: Creation du ZIP
if (-not $SkipZip) {
    Write-Host "`n[4/5] Creation du ZIP..." -ForegroundColor Yellow
    Set-Location $DEPS_DIR
    Compress-Archive -Path * -DestinationPath "..\$ZIP_FILE" -Force
    Set-Location ..
    
    $SIZE_MB = (Get-Item $ZIP_FILE).Length / 1MB
    Write-Host "   ZIP cree: $ZIP_FILE ($([math]::Round($SIZE_MB, 2)) MB)" -ForegroundColor Green
    
    if ($SIZE_MB -gt 50) {
        Write-Host "   ⚠️  ZIP > 50MB - Upload direct peut echouer" -ForegroundColor Yellow
        Write-Host "   💡 Utilisez S3 pour uploader des ZIP > 50MB" -ForegroundColor Yellow
    }
    
    # Nettoyage
    Remove-Item -Path $DEPS_DIR -Recurse -Force
    Write-Host "   OK" -ForegroundColor Green
} else {
    Write-Host "`n[4/5] Creation du ZIP... SKIPPE" -ForegroundColor Gray
    if (-not (Test-Path $ZIP_FILE)) {
        Write-Host "   ❌ ERREUR: ZIP non trouve ($ZIP_FILE)" -ForegroundColor Red
        exit 1
    }
}

# ETAPE 5: Upload vers Lambda
if (-not $SkipUpload) {
    Write-Host "`n[5/5] Upload vers Lambda..." -ForegroundColor Yellow
    Write-Host "   Fonction: $FUNCTION_NAME" -ForegroundColor Gray
    Write-Host "   Region: $REGION" -ForegroundColor Gray
    
    try {
        $response = aws lambda update-function-code `
            --function-name $FUNCTION_NAME `
            --zip-file "fileb://$ZIP_FILE" `
            --region $REGION `
            --publish 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            $result = $response | ConvertFrom-Json
            Write-Host "   ✅ Upload reussi!" -ForegroundColor Green
            Write-Host "   Version: $($result.Version)" -ForegroundColor Gray
            Write-Host "   CodeSize: $([math]::Round($result.CodeSize / 1MB, 2)) MB" -ForegroundColor Gray
            Write-Host "   LastModified: $($result.LastModified)" -ForegroundColor Gray
            
            Write-Host "`n   ⏳ Attente 15 secondes pour que Lambda deploie..." -ForegroundColor Yellow
            Start-Sleep -Seconds 15
            
            Write-Host "`n   Verification des logs..." -ForegroundColor Yellow
            $logs = aws logs tail /aws/lambda/$FUNCTION_NAME --since 1m --region $REGION --format short 2>&1 | Select-String -Pattern "INIT_START|Variables RDS|Application Flask" | Select-Object -Last 5
            if ($logs) {
                Write-Host "   ✅ Logs Lambda actifs" -ForegroundColor Green
            } else {
                Write-Host "   ⚠️  Aucun log recent trouve (normal si pas de requete)" -ForegroundColor Yellow
            }
        } else {
            Write-Host "   ❌ ERREUR lors de l'upload:" -ForegroundColor Red
            Write-Host $response -ForegroundColor Red
            exit 1
        }
    } catch {
        Write-Host "   ❌ ERREUR: $_" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "`n[5/5] Upload vers Lambda... SKIPPE" -ForegroundColor Gray
}

Write-Host "`n========================================" -ForegroundColor Green
Write-Host "  DEPLOY TERMINE AVEC SUCCES!" -ForegroundColor Green
Write-Host "========================================`n" -ForegroundColor Green

Write-Host "Pour tester:" -ForegroundColor Cyan
Write-Host "  1. Allez sur https://mapevent.world" -ForegroundColor White
Write-Host "  2. Connectez-vous avec Google" -ForegroundColor White
Write-Host "  3. Verifiez les logs CloudWatch" -ForegroundColor White


