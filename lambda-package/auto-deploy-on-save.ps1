# Script pour surveiller les modifications et deployer automatiquement

param(
    [string]$WatchPath = "backend",
    [int]$DebounceSeconds = 5
)

$FUNCTION_NAME = "mapevent-backend"
$REGION = "eu-west-1"
$LAST_DEPLOY = 0

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "  AUTO-DEPLOY LAMBDA" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan
Write-Host "Surveillance du dossier: $WatchPath" -ForegroundColor Yellow
Write-Host "Debounce: $DebounceSeconds secondes" -ForegroundColor Yellow
Write-Host "`nAppuyez sur Ctrl+C pour arreter`n" -ForegroundColor Gray

function Deploy-Lambda {
    param([string]$ChangedFile)
    
    Write-Host "`n[$(Get-Date -Format 'HH:mm:ss')] 📝 Modification detectee: $ChangedFile" -ForegroundColor Cyan
    Write-Host "   Attente $DebounceSeconds secondes avant deploy..." -ForegroundColor Yellow
    
    Start-Sleep -Seconds $DebounceSeconds
    
    Write-Host "`n[$(Get-Date -Format 'HH:mm:ss')] 🚀 Deploy en cours..." -ForegroundColor Green
    
    # Executer le script de deploy
    & .\deploy-lambda.ps1 -SkipZip:$false -SkipUpload:$false
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n[$(Get-Date -Format 'HH:mm:ss')] ✅ Deploy termine avec succes!" -ForegroundColor Green
    } else {
        Write-Host "`n[$(Get-Date -Format 'HH:mm:ss')] ❌ Erreur lors du deploy" -ForegroundColor Red
    }
    
    Write-Host "`nSurveillance reprise...`n" -ForegroundColor Gray
}

# Creer un FileSystemWatcher
$watcher = New-Object System.IO.FileSystemWatcher
$watcher.Path = (Resolve-Path $WatchPath).Path
$watcher.Filter = "*.py"
$watcher.IncludeSubdirectories = $true
$watcher.EnableRaisingEvents = $true

# Timer pour debounce
$timer = $null

# Action a executer lors d'un changement
$action = {
    param($source, $e)
    
    # Annuler le timer precedent
    if ($timer) {
        $timer.Stop()
        $timer.Dispose()
    }
    
    # Creer un nouveau timer
    $script:timer = New-Object System.Timers.Timer
    $script:timer.Interval = $DebounceSeconds * 1000
    $script:timer.AutoReset = $false
    $script:timer.Add_Elapsed({
        Deploy-Lambda -ChangedFile $e.FullPath
    })
    $script:timer.Start()
}

# Enregistrer les evenements
Register-ObjectEvent -InputObject $watcher -EventName "Changed" -Action $action | Out-Null
Register-ObjectEvent -InputObject $watcher -EventName "Created" -Action $action | Out-Null

Write-Host "✅ Surveillance active - Modifiez un fichier .py pour declencher le deploy automatique" -ForegroundColor Green

# Attendre indefiniment
try {
    while ($true) {
        Start-Sleep -Seconds 1
    }
} finally {
    $watcher.EnableRaisingEvents = $false
    $watcher.Dispose()
    Write-Host "`nSurveillance arretee" -ForegroundColor Yellow
}






