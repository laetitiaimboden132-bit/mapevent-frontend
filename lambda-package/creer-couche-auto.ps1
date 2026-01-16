# Script automatique pour créer une couche Lambda psycopg2
# Attend que Docker soit démarré, puis crée et ajoute la couche automatiquement

$layerDir = "psycopg2-layer-temp"
$zipFile = "psycopg2-layer.zip"
$layerName = "psycopg2-py312-mapevent"

Write-Host "`n=== Création automatique couche Lambda psycopg2 ===" -ForegroundColor Cyan

# Nettoyer
Remove-Item -Path $layerDir -Recurse -ErrorAction SilentlyContinue
Remove-Item -Path $zipFile -ErrorAction SilentlyContinue

# Créer la structure
New-Item -ItemType Directory -Path "$layerDir\python\lib\python3.12\site-packages" -Force | Out-Null

Write-Host "`n1. Vérification Docker..." -ForegroundColor Yellow
$dockerReady = $false
$maxAttempts = 30
$attempt = 0

while (-not $dockerReady -and $attempt -lt $maxAttempts) {
    try {
        docker ps 2>&1 | Out-Null
        if ($LASTEXITCODE -eq 0) {
            $dockerReady = $true
            Write-Host "   ✅ Docker est démarré!" -ForegroundColor Green
        }
    } catch {
        # Docker n'est pas prêt
    }
    
    if (-not $dockerReady) {
        $attempt++
        if ($attempt -eq 1) {
            Write-Host "   ⏳ Docker n'est pas démarré. Attente..." -ForegroundColor Yellow
            Write-Host "   💡 Veuillez démarrer Docker Desktop si ce n'est pas déjà fait" -ForegroundColor Cyan
        }
        Start-Sleep -Seconds 2
        Write-Host "   ... Tentative $attempt/$maxAttempts" -ForegroundColor Gray
    }
}

if (-not $dockerReady) {
    Write-Host "`n❌ Docker n'est pas disponible après $maxAttempts tentatives" -ForegroundColor Red
    Write-Host "`nSolutions:" -ForegroundColor Yellow
    Write-Host "1. Démarrer Docker Desktop manuellement" -ForegroundColor White
    Write-Host "2. Utiliser AWS Console pour ajouter une couche publique" -ForegroundColor White
    Write-Host "3. Réessayer ce script après avoir démarré Docker" -ForegroundColor White
    exit 1
}

Write-Host "`n2. Installation de psycopg2-binary dans Docker..." -ForegroundColor Yellow
$pwd = (Get-Location).Path
$dockerCmd = "docker run --rm -v `"${pwd}:/workspace`" -w /workspace/$layerDir python:3.12-slim pip install --no-cache-dir psycopg2-binary==2.9.9 -t python/lib/python3.12/site-packages"

Write-Host "   Exécution: docker run..." -ForegroundColor Gray
$dockerOutput = Invoke-Expression $dockerCmd 2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "   ❌ Docker a échoué" -ForegroundColor Red
    Write-Host "   Sortie: $dockerOutput" -ForegroundColor Gray
    exit 1
}

Write-Host "   ✅ psycopg2-binary installé!" -ForegroundColor Green

Write-Host "`n3. Création du ZIP..." -ForegroundColor Yellow
Set-Location $layerDir
Compress-Archive -Path python -DestinationPath "..\$zipFile" -Force
Set-Location ..

$size = (Get-Item $zipFile).Length / 1MB
Write-Host "   ✅ ZIP créé: $zipFile ($([math]::Round($size, 2)) MB)" -ForegroundColor Green

Write-Host "`n4. Publication de la couche Lambda..." -ForegroundColor Yellow
$layerOutput = aws lambda publish-layer-version `
    --layer-name $layerName `
    --zip-file "fileb://$zipFile" `
    --compatible-runtimes python3.12 `
    --region eu-west-1 `
    2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "   ❌ Erreur lors de la publication: $layerOutput" -ForegroundColor Red
    exit 1
}

$layerJson = $layerOutput | ConvertFrom-Json
$layerArn = $layerJson.LayerVersionArn
Write-Host "   ✅ Couche publiée: $layerArn" -ForegroundColor Green

Write-Host "`n5. Ajout de la couche à la fonction Lambda..." -ForegroundColor Yellow
$updateOutput = aws lambda update-function-configuration `
    --function-name mapevent-backend `
    --layers $layerArn `
    --region eu-west-1 `
    2>&1

if ($LASTEXITCODE -ne 0) {
    Write-Host "   ❌ Erreur lors de l'ajout: $updateOutput" -ForegroundColor Red
    Write-Host "`n⚠️  La couche a été créée mais n'a pas pu être ajoutée automatiquement" -ForegroundColor Yellow
    Write-Host "   ARN de la couche: $layerArn" -ForegroundColor Gray
    Write-Host "   Ajoutez-la manuellement dans AWS Console" -ForegroundColor Yellow
    exit 1
}

Write-Host "   ✅ Couche ajoutée à mapevent-backend!" -ForegroundColor Green

# Nettoyer
Remove-Item -Path $layerDir -Recurse -Force -ErrorAction SilentlyContinue

Write-Host "`n🎉🎉🎉 SUCCÈS COMPLET!" -ForegroundColor Green
Write-Host "`n✅ La couche psycopg2 est maintenant configurée sur votre fonction Lambda" -ForegroundColor Green
Write-Host "`nProchaine étape: Redéployer le code" -ForegroundColor Cyan
Write-Host "  .\deploy-lambda.ps1" -ForegroundColor White
Write-Host "`nEnsuite, testez la connexion!" -ForegroundColor Cyan





