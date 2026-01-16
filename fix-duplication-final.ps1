# Correction finale de la duplication photoData

$file = "public\map_logic.js"
$content = [System.IO.File]::ReadAllText($file, [System.Text.Encoding]::UTF8)

# Trouver la ligne avec la duplication
$lines = $content -split "`n"
$newLines = @()
$skipNext = $false

for ($i = 0; $i -lt $lines.Count; $i++) {
    $line = $lines[$i]
    
    # Si on trouve la première occurrence de photoData dans pendingRegisterData
    if ($line -match "photoData:\s*photoData," -and $i -gt 0 -and $lines[$i-1] -match "pendingRegisterData\s*=") {
        $newLines += $line
        # Vérifier les lignes suivantes pour trouver la duplication
        $j = $i + 1
        while ($j -lt $lines.Count -and $j -lt $i + 10) {
            if ($lines[$j] -match "photoData:\s*window\.registerData") {
                # Skip cette ligne (duplication)
                Write-Host "Ligne $($j+1) supprimee (duplication photoData)" -ForegroundColor Yellow
                $j++
                continue
            }
            if ($lines[$j] -match "addresses:\s*addresses") {
                # On a trouve la fin, on peut continuer normalement
                break
            }
            $j++
        }
        $i = $j - 1
        continue
    }
    
    $newLines += $line
}

$newContent = $newLines -join "`n"
[System.IO.File]::WriteAllText($file, $newContent, [System.Text.Encoding]::UTF8)

Write-Host "`nVerification..." -ForegroundColor Yellow
$verifyContent = [System.IO.File]::ReadAllText($file, [System.Text.Encoding]::UTF8)
$photoDataCount = ([regex]::Matches($verifyContent, "photoData:\s*")).Count
Write-Host "Occurrences de 'photoData:' trouvees: $photoDataCount" -ForegroundColor Cyan

# Compter dans pendingRegisterData uniquement
if ($verifyContent -match '(?s)pendingRegisterData\s*=\s*\{[^}]*\}') {
    $pendingBlock = $matches[0]
    $photoDataInPending = ([regex]::Matches($pendingBlock, "photoData:")).Count
    Write-Host "Occurrences de 'photoData:' dans pendingRegisterData: $photoDataInPending" -ForegroundColor Cyan
    
    if ($photoDataInPending -eq 1) {
        Write-Host "`n✅ Duplication corrigee!" -ForegroundColor Green
    } else {
        Write-Host "`n⚠️ Duplication toujours presente ($photoDataInPending occurrences)" -ForegroundColor Yellow
    }
}
