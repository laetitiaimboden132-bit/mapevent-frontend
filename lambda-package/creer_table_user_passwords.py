#!/usr/bin/env python3
"""
Script Python pour créer la table user_passwords dans PostgreSQL RDS
Usage: python creer_table_user_passwords.py
"""

import os
import sys
import psycopg2

# Configuration depuis les variables d'environnement ou valeurs par défaut
RDS_HOST = os.environ.get('RDS_HOST', 'mapevent-db.cr0mmuc0elm6.eu-west-1.rds.amazonaws.com')
RDS_PORT = os.environ.get('RDS_PORT', '5432')
RDS_DB = os.environ.get('RDS_DB', 'mapevent')
RDS_USER = os.environ.get('RDS_USER', 'postgres')
RDS_PASSWORD = os.environ.get('RDS_PASSWORD', '')

if not RDS_PASSWORD:
    print("❌ RDS_PASSWORD non défini dans les variables d'environnement")
    print("   Définissez RDS_PASSWORD ou modifiez le script pour entrer le mot de passe")
    sys.exit(1)

try:
    print(f"Connexion à PostgreSQL: {RDS_HOST}:{RDS_PORT}/{RDS_DB}")
    conn = psycopg2.connect(
        host=RDS_HOST,
        port=RDS_PORT,
        database=RDS_DB,
        user=RDS_USER,
        password=RDS_PASSWORD,
        sslmode='require',
        connect_timeout=10
    )
    
    cursor = conn.cursor()
    
    print("Création de la table user_passwords...")
    
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
    
    # Vérifier que la table existe
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_name = 'user_passwords'
        )
    """)
    
    table_exists = cursor.fetchone()[0]
    
    if table_exists:
        print("✅ Table user_passwords créée avec succès!")
        
        # Afficher la structure
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns 
            WHERE table_name = 'user_passwords' 
            ORDER BY ordinal_position
        """)
        
        print("\nStructure de la table:")
        for row in cursor.fetchall():
            print(f"  - {row[0]}: {row[1]} (nullable: {row[2]})")
    else:
        print("❌ La table n'a pas été créée")
        sys.exit(1)
    
    cursor.close()
    conn.close()
    
except psycopg2.Error as e:
    print(f"❌ Erreur PostgreSQL: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)




