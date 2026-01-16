# Script pour démarrer Docker Desktop et créer la Lambda Layer

$ErrorActionPreference = "Stop"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "DEMARRAGE DOCKER ET CREATION LAMBDA LAYER" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Démarrer Docker Desktop
Write-Host "1. Demarrage de Docker Desktop..." -ForegroundColor Yellow
Write-Host "   (Cela peut prendre 1-2 minutes)" -ForegroundColor Gray

# Vérifier si Docker est déjà démarré
try {
    docker ps 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "   OK: Docker est deja demarre" -ForegroundColor Green
    } else {
        throw "Docker n'est pas demarre"
    }
} catch {
    Write-Host "   Docker n'est pas demarre. Demarrage..." -ForegroundColor Yellow
    
    # Essayer de démarrer Docker Desktop
    $dockerPath = "${env:ProgramFiles}\Docker\Docker\Docker Desktop.exe"
    if (Test-Path $dockerPath) {
        Start-Process -FilePath $dockerPath -WindowStyle Minimized
        Write-Host "   Docker Desktop en cours de demarrage..." -ForegroundColor Gray
        
        # Attendre que Docker soit prêt (max 2 minutes)
        $timeout = 120
        $elapsed = 0
        $dockerReady = $false
        
        while ($elapsed -lt $timeout) {
            Start-Sleep -Seconds 5
            $elapsed += 5
            try {
                docker ps 2>&1 | Out-Null
                if ($LASTEXITCODE -eq 0) {
                    $dockerReady = $true
                    break
                }
            } catch {
                # Docker n'est pas encore prêt
            }
            Write-Host "   Attente... ($elapsed s)" -ForegroundColor Gray
        }
        
        if ($dockerReady) {
            Write-Host "   OK: Docker est maintenant pret" -ForegroundColor Green
        } else {
            Write-Host "ERREUR: Docker n'a pas pu demarrer dans les delais" -ForegroundColor Red
            Write-Host "   Demarrez Docker Desktop manuellement et reessayez" -ForegroundColor Yellow
            exit 1
        }
    } else {
        Write-Host "ERREUR: Docker Desktop n'est pas trouve!" -ForegroundColor Red
        Write-Host "   Installez Docker Desktop: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host ""
Write-Host "2. Creation de la Lambda Layer avec Docker..." -ForegroundColor Yellow
Write-Host ""

# Exécuter le script de création de Layer avec Docker
Set-Location "lambda-package"

try {
    & "..\creer-layer-docker.ps1"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "============================================================" -ForegroundColor Green
        Write-Host "SUCCES: Lambda Layer creee avec Docker !" -ForegroundColor Green
        Write-Host "============================================================" -ForegroundColor Green
        Write-Host ""
    } else {
        Write-Host "ERREUR: Echec de la creation de la Layer" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "ERREUR: $_" -ForegroundColor Red
    Set-Location ..
    exit 1
} finally {
    Set-Location ..
}

Write-Host "Termine !" -ForegroundColor Green
Write-Host ""
