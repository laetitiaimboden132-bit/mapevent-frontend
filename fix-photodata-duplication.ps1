# Correction de la duplication photoData dans pendingRegisterData

Write-Host "Correction duplication photoData..." -ForegroundColor Yellow

$mapLogicPath = "public\map_logic.js"
$content = Get-Content $mapLogicPath -Raw -Encoding UTF8

# Trouver et corriger la duplication
$pattern = '(?s)(// Récupérer photoData depuis registerData.*?\n    const photoData =.*?\n    \n    window\.pendingRegisterData = \{[^}]*?photoData:[^,}]*?,\s*photoLater:[^,}]*?,\s*addressLater:[^,}]*?,\s*selectedAddress:[^,}]*?,\s*)photoData:[^,}]*?,\s*(addresses:)'

$replacement = '$1photoData: photoData, // INCLURE photoData (photo uploadée lors de la création - base64 ou URL)
      console.log(''[REGISTER] pendingRegisterData créé avec photoData:'', photoData ? (photoData.substring(0, 50) + ''...'') : ''null'');
      $2'

if ($content -match $pattern) {
    $content = $content -replace $pattern, $replacement
    [System.IO.File]::WriteAllText($mapLogicPath, $content, [System.Text.Encoding]::UTF8)
    Write-Host "✅ Duplication corrigée" -ForegroundColor Green
} else {
    Write-Host "⚠️ Pattern non trouvé, correction manuelle nécessaire" -ForegroundColor Yellow
    # Correction manuelle directe
    $content = $content -replace '(?s)(photoData: photoData, // INCLURE photoData.*?\n      photoLater:.*?\n      addressLater:.*?\n      selectedAddress:.*?\n      )photoData:.*?\n      ', '$1'
    [System.IO.File]::WriteAllText($mapLogicPath, $content, [System.Text.Encoding]::UTF8)
    Write-Host "✅ Correction manuelle appliquée" -ForegroundColor Green
}

# Déployer
Write-Host "`nDéploiement..." -ForegroundColor Yellow
aws s3 cp public\map_logic.js s3://mapevent-frontend-laetibibi/map_logic.js --region eu-west-1 --content-type "application/javascript" --cache-control "no-cache, no-store, must-revalidate" 2>&1 | Out-Null
$invalidationId = aws cloudfront create-invalidation --distribution-id EMB53HDL7VFIJ --paths "/map_logic.js" "/map_logic.js*" --query "Invalidation.Id" --output text 2>&1
Start-Sleep -Seconds 15
Write-Host "✅ Déploiement terminé" -ForegroundColor Green
