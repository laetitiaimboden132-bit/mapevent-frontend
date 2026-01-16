# Script PowerShell pour créer la table user_passwords dans PostgreSQL RDS
# Usage: .\creer_table_user_passwords.ps1

$RDS_HOST = "mapevent-db.cr0mmuc0elm6.eu-west-1.rds.amazonaws.com"
$RDS_PORT = "5432"
$RDS_DB = "mapevent"
$RDS_USER = "postgres"

Write-Host "=== Création de la table user_passwords ===" -ForegroundColor Cyan
Write-Host ""

# Demander le mot de passe
$securePassword = Read-Host "Entrez le mot de passe PostgreSQL" -AsSecureString
$RDS_PASSWORD = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword))

Write-Host "Connexion à PostgreSQL..." -ForegroundColor Yellow

# Lire le script SQL
$sqlScript = Get-Content -Path "create_user_passwords_table.sql" -Raw

# Exécuter via psql si disponible, sinon utiliser Python
if (Get-Command psql -ErrorAction SilentlyContinue) {
    Write-Host "Utilisation de psql..." -ForegroundColor Yellow
    
    $env:PGPASSWORD = $RDS_PASSWORD
    $result = psql -h $RDS_HOST -p $RDS_PORT -U $RDS_USER -d $RDS_DB -c $sqlScript 2>&1
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Table user_passwords créée avec succès!" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Résultat: $result" -ForegroundColor Yellow
        # Vérifier si la table existe déjà
        $checkResult = psql -h $RDS_HOST -p $RDS_PORT -U $RDS_USER -d $RDS_DB -c "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'user_passwords');" -t 2>&1
        if ($checkResult -match "t") {
            Write-Host "✅ La table existe déjà!" -ForegroundColor Green
        } else {
            Write-Host "❌ Erreur lors de la création" -ForegroundColor Red
        }
    }
    
    $env:PGPASSWORD = $null
} else {
    Write-Host "psql non trouvé, utilisation de Python..." -ForegroundColor Yellow
    
    # Créer un script Python temporaire
    $pythonScript = @"
import psycopg2
import sys

try:
    conn = psycopg2.connect(
        host="$RDS_HOST",
        port=$RDS_PORT,
        database="$RDS_DB",
        user="$RDS_USER",
        password="$RDS_PASSWORD",
        sslmode='require'
    )
    
    cursor = conn.cursor()
    
    # Créer la table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_passwords (
            user_id VARCHAR(255) PRIMARY KEY,
            password_hash TEXT NOT NULL,
            salt VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Ajouter la contrainte de clé étrangère
    cursor.execute("""
        DO `$\$
        BEGIN
            IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users') THEN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.table_constraints 
                    WHERE constraint_name = 'user_passwords_user_id_fkey'
                ) THEN
                    ALTER TABLE user_passwords 
                    ADD CONSTRAINT user_passwords_user_id_fkey 
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
                END IF;
            END IF;
        END `$\$;
    """)
    
    # Créer l'index
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_passwords_user ON user_passwords(user_id);
    """)
    
    conn.commit()
    cursor.close()
    conn.close()
    
    print("✅ Table user_passwords créée avec succès!")
    sys.exit(0)
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    sys.exit(1)
"@
    
    $tempPythonFile = [System.IO.Path]::GetTempFileName() + ".py"
    $pythonScript | Out-File -FilePath $tempPythonFile -Encoding UTF8
    
    try {
        $result = python $tempPythonFile 2>&1
        Write-Host $result
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✅ Table user_passwords créée avec succès!" -ForegroundColor Green
        }
    } catch {
        Write-Host "❌ Erreur: $_" -ForegroundColor Red
        Write-Host ""
        Write-Host "Alternative: Exécutez manuellement le script SQL dans RDS Query Editor" -ForegroundColor Yellow
    } finally {
        Remove-Item $tempPythonFile -ErrorAction SilentlyContinue
    }
}

Write-Host ""
Write-Host "=== Vérification ===" -ForegroundColor Cyan
Write-Host "La table sera créée automatiquement lors du premier register si elle n'existe pas." -ForegroundColor Gray
Write-Host "Mais il est recommandé de la créer manuellement avant." -ForegroundColor Gray




