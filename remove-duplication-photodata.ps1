# Script pour supprimer la duplication photoData dans pendingRegisterData

$file = "public\map_logic.js"
$content = [System.IO.File]::ReadAllText($file, [System.Text.Encoding]::UTF8)

# Pattern pour trouver la duplication
$pattern = '(?s)(photoData:\s*photoData[^,]*,\s*photoLater:[^,]*,\s*addressLater:[^,]*,\s*selectedAddress:[^,]*,\s*)photoData:\s*window\.registerData[^,]*,\s*'

if ($content -match $pattern) {
    Write-Host "Duplication trouvee, suppression..." -ForegroundColor Yellow
    $content = $content -replace $pattern, '$1'
    [System.IO.File]::WriteAllText($file, $content, [System.Text.Encoding]::UTF8)
    Write-Host "✅ Duplication supprimee" -ForegroundColor Green
} else {
    Write-Host "Pas de duplication trouvee avec ce pattern" -ForegroundColor Yellow
    # Essayer un autre pattern
    $pattern2 = '(?s)(photoData:\s*photoData[^}]*?)(photoData:\s*window\.registerData[^}]*?)(addresses:)'
    if ($content -match $pattern2) {
        Write-Host "Duplication trouvee avec pattern alternatif, suppression..." -ForegroundColor Yellow
        $content = $content -replace $pattern2, '$1$3'
        [System.IO.File]::WriteAllText($file, $content, [System.Text.Encoding]::UTF8)
        Write-Host "✅ Duplication supprimee" -ForegroundColor Green
    } else {
        Write-Host "Aucune duplication trouvee" -ForegroundColor Green
    }
}

# Verification
$verifyContent = [System.IO.File]::ReadAllText($file, [System.Text.Encoding]::UTF8)
if ($verifyContent -match '(?s)pendingRegisterData\s*=\s*\{[^}]*\}') {
    $pendingBlock = $matches[0]
    $photoDataCount = ([regex]::Matches($pendingBlock, "photoData:")).Count
    Write-Host "`nVerification: $photoDataCount occurrence(s) de 'photoData:' dans pendingRegisterData" -ForegroundColor Cyan
    if ($photoDataCount -eq 1) {
        Write-Host "✅ Pas de duplication" -ForegroundColor Green
    } else {
        Write-Host "⚠️ Duplication toujours presente ($photoDataCount occurrences)" -ForegroundColor Yellow
    }
}
