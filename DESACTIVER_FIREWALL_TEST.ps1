# Script pour désactiver temporairement le firewall et tester la connexion

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "TEST SANS FIREWALL WINDOWS" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "ATTENTION: Ce script va desactiver temporairement le firewall Windows" -ForegroundColor Yellow
Write-Host "pour tester la connexion a la base de donnees." -ForegroundColor Yellow
Write-Host ""
Write-Host "Le firewall sera reactive automatiquement apres le test." -ForegroundColor Yellow
Write-Host ""

# Vérifier les privilèges administrateur
$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERREUR: Ce script doit etre execute en tant qu'administrateur!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Solution:" -ForegroundColor Yellow
    Write-Host "  1. Fermez PowerShell" -ForegroundColor White
    Write-Host "  2. Clic droit sur PowerShell > 'Executer en tant qu'administrateur'" -ForegroundColor White
    Write-Host "  3. Relancez ce script" -ForegroundColor White
    Write-Host ""
    exit 1
}

# Sauvegarder l'état actuel du firewall
Write-Host "Sauvegarde de l'etat actuel du firewall..." -ForegroundColor Yellow
$firewallState = @{
    Domain = (Get-NetFirewallProfile -Profile Domain).Enabled
    Private = (Get-NetFirewallProfile -Profile Private).Enabled
    Public = (Get-NetFirewallProfile -Profile Public).Enabled
}

Write-Host "  Domain: $($firewallState.Domain)" -ForegroundColor Gray
Write-Host "  Private: $($firewallState.Private)" -ForegroundColor Gray
Write-Host "  Public: $($firewallState.Public)" -ForegroundColor Gray
Write-Host ""

# Désactiver le firewall
Write-Host "Desactivation du firewall..." -ForegroundColor Yellow
Set-NetFirewallProfile -Profile Domain,Private,Public -Enabled False
Write-Host "  OK: Firewall desactive" -ForegroundColor Green
Write-Host ""

# Attendre un peu
Start-Sleep -Seconds 2

# Tester la connexion
Write-Host "Test de connexion a la base de donnees..." -ForegroundColor Yellow
Write-Host ""

Set-Location "C:\MapEventAI_NEW\frontend"
python supprimer-comptes.py

$testResult = $LASTEXITCODE

Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan

# Réactiver le firewall
Write-Host "Reactivation du firewall..." -ForegroundColor Yellow
if ($firewallState.Domain) {
    Set-NetFirewallProfile -Profile Domain -Enabled True
}
if ($firewallState.Private) {
    Set-NetFirewallProfile -Profile Private -Enabled True
}
if ($firewallState.Public) {
    Set-NetFirewallProfile -Profile Public -Enabled True
}
Write-Host "  OK: Firewall reactive" -ForegroundColor Green
Write-Host ""

if ($testResult -eq 0) {
    Write-Host "SUCCES: La connexion a fonctionne!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Le firewall Windows bloquait la connexion." -ForegroundColor Yellow
    Write-Host "Pour permettre PostgreSQL en permanence:" -ForegroundColor Yellow
    Write-Host "  New-NetFirewallRule -DisplayName 'PostgreSQL' -Direction Inbound -Protocol TCP -LocalPort 5432 -Action Allow" -ForegroundColor White
} else {
    Write-Host "ERREUR: La connexion a toujours echoue." -ForegroundColor Red
    Write-Host ""
    Write-Host "Causes possibles:" -ForegroundColor Yellow
    Write-Host "  1. Propagation reseau pas encore complete (attendez 30 minutes)" -ForegroundColor White
    Write-Host "  2. Regle Security Group incorrecte (verifiez Type: PostgreSQL, Port: 5432)" -ForegroundColor White
    Write-Host "  3. Autre probleme de reseau" -ForegroundColor White
}


