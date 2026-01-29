# Deploy frontend ultra-court (sans les longs checks). Usage: .\deploy-rapide.ps1
$PUBLIC = "public"
$BUCKET = "mapevent-frontend-laetibibi"
$REGION = "eu-west-1"
$CF_ID = "EMB53HDL7VFIJ"
Set-Location $PSScriptRoot
if (-not (Test-Path $PUBLIC)) { Write-Host "Erreur: dossier $PUBLIC absent"; exit 1 }
Write-Host "Upload S3..." -ForegroundColor Cyan
aws s3 sync $PUBLIC "s3://$BUCKET" --region $REGION --delete --exclude "*.git*" --exclude "*.md" --exclude "*.ps1" --exclude "*.sh"
if ($LASTEXITCODE -ne 0) { Write-Host "Erreur S3"; exit 1 }
Write-Host "Invalidation CloudFront..." -ForegroundColor Cyan
aws cloudfront create-invalidation --distribution-id $CF_ID --paths "/*" --query "Invalidation.Id" --output text
Write-Host "Termine. Site: https://mapevent.world" -ForegroundColor Green
