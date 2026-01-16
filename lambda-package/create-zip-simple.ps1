# Script simple pour creer le ZIP Lambda

$ZIP_FILE = "lambda-deploy-fixed.zip"

Write-Host "Creation du ZIP Lambda..." -ForegroundColor Cyan

# Nettoyer
Remove-Item -Path $ZIP_FILE -ErrorAction SilentlyContinue

# Fichiers a inclure (code source uniquement)
$filesToInclude = @(
    "lambda_function.py",
    "handler.py",
    "backend"
)

# Creer le ZIP avec 7-Zip ou Compress-Archive
Write-Host "Compression des fichiers..." -ForegroundColor Yellow

# Methode 1: Compress-Archive (si disponible)
try {
    Compress-Archive -Path $filesToInclude -DestinationPath $ZIP_FILE -Force
    Write-Host "ZIP cree avec Compress-Archive" -ForegroundColor Green
} catch {
    Write-Host "Erreur Compress-Archive, essai autre methode..." -ForegroundColor Yellow
    # Methode alternative si Compress-Archive echoue
    $tempDir = "temp-zip"
    New-Item -ItemType Directory -Path $tempDir -Force | Out-Null
    Copy-Item -Path $filesToInclude -Destination $tempDir -Recurse -Force
    Compress-Archive -Path "$tempDir\*" -DestinationPath $ZIP_FILE -Force
    Remove-Item -Path $tempDir -Recurse -Force
}

$SIZE = (Get-Item $ZIP_FILE).Length / 1KB
Write-Host "ZIP cree: $ZIP_FILE ($([math]::Round($SIZE, 2)) KB)" -ForegroundColor Green






