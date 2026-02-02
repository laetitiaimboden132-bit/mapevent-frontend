# Script d'organisation professionnelle de la structure
Write-Host "🚀 Organisation de la structure..." -ForegroundColor Cyan

# Créer le dossier si nécessaire
$testDir = "public\tests\diagnostic"
if (-not (Test-Path $testDir)) {
    New-Item -ItemType Directory -Path $testDir -Force | Out-Null
}

# Déplacer les fichiers de test
$patterns = @("TEST_*", "DIAGNOSTIC_*", "diagnostic-*", "debug-*", "fix-*", "TRACE_*")
$moved = 0

foreach ($pattern in $patterns) {
    $files = Get-ChildItem -Path "public" -Filter $pattern -File -ErrorAction SilentlyContinue
    foreach ($file in $files) {
        $dest = Join-Path $testDir $file.Name
        if (-not (Test-Path $dest)) {
            try {
                Move-Item -Path $file.FullName -Destination $dest -Force
                Write-Host "  ✅ Déplacé: $($file.Name)" -ForegroundColor Green
                $moved++
            } catch {
                Write-Host "  ⚠️ Erreur avec $($file.Name): $_" -ForegroundColor Yellow
            }
        }
    }
}

Write-Host ""
Write-Host "Resume: $moved fichier(s) deplace(s)" -ForegroundColor Yellow
Write-Host "Structure organisee avec succes!" -ForegroundColor Green
