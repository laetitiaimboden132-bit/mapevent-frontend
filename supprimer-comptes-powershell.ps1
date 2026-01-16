# Script PowerShell pour supprimer tous les comptes SAUF un compte admin
# SOLUTION SIMPLE - Pas besoin de pgAdmin ou SQL manuel!

param(
    [string]$EmailAGarder = "",
    [string]$SupprimerTous = "non"
)

# Informations de connexion
$RDS_HOST = "mapevent-db.cr0mmuc0elm6.eu-west-1.rds.amazonaws.com"
$RDS_PORT = "5432"
$RDS_DB = "mapevent"
$RDS_USER = "postgres"
$RDS_PASSWORD = "666666Laeti69!"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "SUPPRESSION DES COMPTES - METHODE SIMPLE" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier si psql est installé
$psqlPath = Get-Command psql -ErrorAction SilentlyContinue

if (-not $psqlPath) {
    Write-Host "ERREUR: psql n'est pas installe!" -ForegroundColor Red
    Write-Host ""
    Write-Host "SOLUTION: Installez PostgreSQL client:" -ForegroundColor Yellow
    Write-Host "  1. Allez sur: https://www.postgresql.org/download/windows/" -ForegroundColor White
    Write-Host "  2. Telechargez 'PostgreSQL' (pas pgAdmin, juste le client)" -ForegroundColor White
    Write-Host "  3. Installez-le" -ForegroundColor White
    Write-Host "  4. Relancez ce script" -ForegroundColor White
    Write-Host ""
    Write-Host "OU utilisez la methode alternative ci-dessous..." -ForegroundColor Yellow
    Write-Host ""
    
    # Méthode alternative : utiliser .NET
    Write-Host "Tentative avec methode alternative (.NET)..." -ForegroundColor Yellow
    
    try {
        # Charger l'assembly Npgsql si disponible
        Add-Type -Path "C:\Program Files\PostgreSQL\*\bin\npgsql.dll" -ErrorAction SilentlyContinue
        
        if (-not ([System.Management.Automation.PSTypeName]'Npgsql.NpgsqlConnection').Type) {
            Write-Host "ERREUR: Npgsql non disponible" -ForegroundColor Red
            Write-Host ""
            Write-Host "INSTALLEZ PostgreSQL client (voir ci-dessus)" -ForegroundColor Yellow
            exit 1
        }
    } catch {
        Write-Host "ERREUR: Impossible de charger Npgsql" -ForegroundColor Red
        Write-Host ""
        Write-Host "INSTALLEZ PostgreSQL client:" -ForegroundColor Yellow
        Write-Host "  https://www.postgresql.org/download/windows/" -ForegroundColor White
        exit 1
    }
}

# Étape 1: Voir tous les comptes
Write-Host "ETAPE 1: Liste de tous les comptes..." -ForegroundColor Yellow
Write-Host ""

if ($psqlPath) {
    # Méthode avec psql
    $env:PGPASSWORD = $RDS_PASSWORD
    $query = "SELECT email, username, role FROM users ORDER BY created_at DESC;"
    
    $result = & psql -h $RDS_HOST -p $RDS_PORT -U $RDS_USER -d $RDS_DB -c $query 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host $result -ForegroundColor White
    } else {
        Write-Host "ERREUR de connexion:" -ForegroundColor Red
        Write-Host $result -ForegroundColor Red
        Write-Host ""
        Write-Host "VERIFIEZ:" -ForegroundColor Yellow
        Write-Host "  1. Que votre IP est autorisee dans le Security Group RDS" -ForegroundColor White
        Write-Host "  2. Que la base est 'Accessible publiquement'" -ForegroundColor White
        exit 1
    }
} else {
    Write-Host "Utilisation de la methode .NET..." -ForegroundColor Yellow
    # Méthode .NET (si psql n'est pas disponible)
    # Code à implémenter si nécessaire
}

Write-Host ""

# Étape 2: Demander quel compte garder
if ([string]::IsNullOrWhiteSpace($EmailAGarder)) {
    if ($SupprimerTous -eq "oui") {
        Write-Host "ATTENTION: Vous allez supprimer TOUS les comptes!" -ForegroundColor Red
        Write-Host ""
        $confirmation = Read-Host "Tapez 'OUI' pour confirmer"
        
        if ($confirmation -ne "OUI") {
            Write-Host "Annule." -ForegroundColor Yellow
            exit 0
        }
        
        # Supprimer tous les comptes
        Write-Host ""
        Write-Host "Suppression de TOUS les comptes..." -ForegroundColor Yellow
        
        if ($psqlPath) {
            $deleteQuery = "DELETE FROM users;"
            $env:PGPASSWORD = $RDS_PASSWORD
            $result = & psql -h $RDS_HOST -p $RDS_PORT -U $RDS_USER -d $RDS_DB -c $deleteQuery 2>&1
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "SUCCES: Tous les comptes ont ete supprimes!" -ForegroundColor Green
            } else {
                Write-Host "ERREUR:" -ForegroundColor Red
                Write-Host $result -ForegroundColor Red
            }
        }
    } else {
        Write-Host "Quel compte voulez-vous GARDER?" -ForegroundColor Cyan
        Write-Host "  (Tapez l'email du compte a garder, ou 'TOUS' pour tout supprimer)" -ForegroundColor Yellow
        Write-Host ""
        $EmailAGarder = Read-Host "Email du compte a garder"
        
        if ($EmailAGarder -eq "TOUS" -or [string]::IsNullOrWhiteSpace($EmailAGarder)) {
            Write-Host "Suppression de TOUS les comptes..." -ForegroundColor Yellow
            $deleteQuery = "DELETE FROM users;"
        } else {
            Write-Host "Suppression de tous les comptes SAUF: $EmailAGarder" -ForegroundColor Yellow
            $deleteQuery = "DELETE FROM users WHERE email != '$EmailAGarder';"
        }
        
        Write-Host ""
        Write-Host "ATTENTION: Cette operation est IRREVERSIBLE!" -ForegroundColor Red
        $confirmation = Read-Host "Tapez 'OUI' pour confirmer"
        
        if ($confirmation -ne "OUI") {
            Write-Host "Annule." -ForegroundColor Yellow
            exit 0
        }
        
        # Exécuter la suppression
        if ($psqlPath) {
            $env:PGPASSWORD = $RDS_PASSWORD
            $result = & psql -h $RDS_HOST -p $RDS_PORT -U $RDS_USER -d $RDS_DB -c $deleteQuery 2>&1
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host ""
                Write-Host "SUCCES: Comptes supprimes!" -ForegroundColor Green
                
                # Vérifier
                Write-Host ""
                Write-Host "Verification..." -ForegroundColor Yellow
                $checkQuery = "SELECT email, username, role FROM users;"
                $checkResult = & psql -h $RDS_HOST -p $RDS_PORT -U $RDS_USER -d $RDS_DB -c $checkQuery 2>&1
                Write-Host $checkResult -ForegroundColor White
            } else {
                Write-Host "ERREUR:" -ForegroundColor Red
                Write-Host $result -ForegroundColor Red
            }
        }
    }
} else {
    # Email fourni en paramètre
    Write-Host "Suppression de tous les comptes SAUF: $EmailAGarder" -ForegroundColor Yellow
    Write-Host ""
    
    if ($psqlPath) {
        $deleteQuery = "DELETE FROM users WHERE email != '$EmailAGarder';"
        $env:PGPASSWORD = $RDS_PASSWORD
        $result = & psql -h $RDS_HOST -p $RDS_PORT -U $RDS_USER -d $RDS_DB -c $deleteQuery 2>&1
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "SUCCES: Comptes supprimes!" -ForegroundColor Green
        } else {
            Write-Host "ERREUR:" -ForegroundColor Red
            Write-Host $result -ForegroundColor Red
        }
    }
}

Write-Host ""


