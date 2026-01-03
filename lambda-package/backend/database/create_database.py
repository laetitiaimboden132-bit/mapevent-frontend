"""
Script Python pour créer la base de données mapevent dans RDS
Usage: python create_database.py
"""

import psycopg2
import sys
import os

# Configuration depuis les variables d'environnement
RDS_HOST = os.getenv('RDS_HOST', 'mapevent-db.cr0mmuc0elm6.eu-west-1.rds.amazonaws.com')
RDS_USER = os.getenv('RDS_USER', 'postgres')
RDS_PASSWORD = os.getenv('RDS_PASSWORD', '666666Laeti69!')
RDS_PORT = os.getenv('RDS_PORT', '5432')
RDS_DB_NEW = os.getenv('RDS_DB_NEW', 'mapevent')

try:
    # Se connecter à la base par défaut 'postgres' pour créer une nouvelle base
    print(f"🔌 Connexion à RDS: {RDS_HOST}:{RDS_PORT}/postgres")
    conn = psycopg2.connect(
        host=RDS_HOST,
        port=RDS_PORT,
        database='postgres',  # On se connecte à la base par défaut
        user=RDS_USER,
        password=RDS_PASSWORD,
        connect_timeout=10,
        sslmode='require'
    )
    print("✅ Connexion réussie")
    
    # Mettre la connexion en mode autocommit pour créer la base
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Vérifier si la base existe déjà
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (RDS_DB_NEW,))
    exists = cursor.fetchone()
    
    if exists:
        print(f"⚠️  La base de données '{RDS_DB_NEW}' existe déjà")
    else:
        # Créer la base de données
        print(f"📦 Création de la base de données '{RDS_DB_NEW}'...")
        cursor.execute(f'CREATE DATABASE "{RDS_DB_NEW}";')
        print(f"✅ Base de données '{RDS_DB_NEW}' créée avec succès!")
    
    cursor.close()
    conn.close()
    print("🎉 Terminé!")
    sys.exit(0)
    
except psycopg2.Error as e:
    print(f"❌ Erreur PostgreSQL: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

