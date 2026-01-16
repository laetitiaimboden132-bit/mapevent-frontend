# 📊 Créer la table user_passwords dans PostgreSQL

## Option 1 : Via AWS RDS Query Editor (Recommandé)

1. Aller dans **AWS Console** → **RDS**
2. Sélectionner votre base de données **`mapevent-db`**
3. Cliquer sur **Query Editor** (ou utiliser un client PostgreSQL)
4. Exécuter le script `create_user_passwords_table.sql`

## Option 2 : Via psql (ligne de commande)

```powershell
# Se connecter à RDS (remplacer les valeurs)
$env:PGPASSWORD = "VOTRE_MOT_DE_PASSE"
psql -h mapevent-db.cr0mmuc0elm6.eu-west-1.rds.amazonaws.com `
     -U postgres `
     -d mapevent `
     -f create_user_passwords_table.sql
```

## Option 3 : Via script Python

```python
import psycopg2
import os

conn = psycopg2.connect(
    host=os.environ.get('RDS_HOST'),
    port=os.environ.get('RDS_PORT', '5432'),
    database=os.environ.get('RDS_DB', 'mapevent'),
    user=os.environ.get('RDS_USER'),
    password=os.environ.get('RDS_PASSWORD'),
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
    DO $$
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
    END $$;
""")

# Créer l'index
cursor.execute("""
    CREATE INDEX IF NOT EXISTS idx_user_passwords_user ON user_passwords(user_id);
""")

conn.commit()
cursor.close()
conn.close()

print("✅ Table user_passwords créée avec succès")
```

## Vérification

```sql
-- Vérifier que la table existe
SELECT table_name, column_name, data_type 
FROM information_schema.columns 
WHERE table_name = 'user_passwords' 
ORDER BY ordinal_position;

-- Vérifier les contraintes
SELECT constraint_name, constraint_type 
FROM information_schema.table_constraints 
WHERE table_name = 'user_passwords';
```

## ⚠️ Important

- La table sera créée automatiquement lors du premier `register` si elle n'existe pas
- Mais il est recommandé de la créer manuellement avant pour éviter les erreurs




