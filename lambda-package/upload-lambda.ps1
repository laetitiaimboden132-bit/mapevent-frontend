# Script pour uploader le ZIP Lambda dans AWS
param(
    [string]$FunctionName = "mapevent-backend",
    [string]$Region = "eu-west-1",
    [string]$ZipFile = "lambda-deploy-fixed.zip"
)

Write-Host "`n=== Upload Lambda ===" -ForegroundColor Cyan
Write-Host "Fonction: $FunctionName" -ForegroundColor White
Write-Host "Region: $Region" -ForegroundColor White
Write-Host "Fichier: $ZipFile" -ForegroundColor White
Write-Host ""

# Vérifier que le fichier existe
if (-not (Test-Path $ZipFile)) {
    Write-Host "ERREUR: Fichier $ZipFile non trouve!" -ForegroundColor Red
    exit 1
}

$fileSize = (Get-Item $ZipFile).Length / 1KB
Write-Host "Taille du fichier: $([math]::Round($fileSize, 2)) KB" -ForegroundColor Yellow
Write-Host ""

# Lire le fichier ZIP
Write-Host "Lecture du fichier ZIP..." -ForegroundColor Yellow
$zipBytes = [System.IO.File]::ReadAllBytes((Resolve-Path $ZipFile).Path)
Write-Host "Fichier lu: $($zipBytes.Length) bytes" -ForegroundColor Green
Write-Host ""

# Uploader dans Lambda
Write-Host "Upload dans Lambda..." -ForegroundColor Yellow
try {
    $response = aws lambda update-function-code `
        --function-name $FunctionName `
        --region $Region `
        --zip-file "fileb://$ZipFile" `
        --output json 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        $result = $response | ConvertFrom-Json
        Write-Host "`nSUCCES!" -ForegroundColor Green
        Write-Host "Fonction: $($result.FunctionName)" -ForegroundColor White
        Write-Host "Version: $($result.Version)" -ForegroundColor White
        Write-Host "CodeSize: $([math]::Round($result.CodeSize / 1KB, 2)) KB" -ForegroundColor White
        Write-Host "LastModified: $($result.LastModified)" -ForegroundColor White
        Write-Host "`nAttendez 10-20 secondes pour que Lambda deploie le nouveau code..." -ForegroundColor Yellow
    } else {
        Write-Host "`nERREUR lors de l'upload:" -ForegroundColor Red
        Write-Host $response -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "`nERREUR: $_" -ForegroundColor Red
    exit 1
}

Write-Host "`n=== Termine ===" -ForegroundColor Cyan






