"""
Script pour créer les tables en base de données PostgreSQL
Usage: python create_tables.py
"""

import os
import sys
import psycopg2
from pathlib import Path

# Ajouter le répertoire parent au path pour importer les variables d'environnement
sys.path.insert(0, str(Path(__file__).parent.parent))

def create_tables():
    """Crée toutes les tables en lisant le fichier schema.sql"""
    
    # Lire les variables d'environnement
    RDS_HOST = os.getenv('RDS_HOST', '')
    RDS_PORT = os.getenv('RDS_PORT', '5432')
    RDS_DB = os.getenv('RDS_DB', 'mapevent')
    RDS_USER = os.getenv('RDS_USER', '')
    RDS_PASSWORD = os.getenv('RDS_PASSWORD', '')
    
    if not RDS_HOST or not RDS_USER or not RDS_PASSWORD:
        print("❌ ERREUR: Variables d'environnement manquantes!")
        print("   Assurez-vous que RDS_HOST, RDS_USER et RDS_PASSWORD sont définis")
        return False
    
    # Lire le fichier SQL
    schema_file = Path(__file__).parent / 'schema.sql'
    if not schema_file.exists():
        print(f"❌ ERREUR: Fichier schema.sql non trouvé: {schema_file}")
        return False
    
    print(f"📖 Lecture du fichier schema.sql...")
    with open(schema_file, 'r', encoding='utf-8') as f:
        sql_content = f.read()
    
    # Se connecter à la base de données
    print(f"🔌 Connexion à la base de données...")
    print(f"   Host: {RDS_HOST}")
    print(f"   Port: {RDS_PORT}")
    print(f"   Database: {RDS_DB}")
    print(f"   User: {RDS_USER}")
    print(f"   Tentative de connexion...")
    
    try:
        conn = psycopg2.connect(
            host=RDS_HOST,
            port=RDS_PORT,
            database=RDS_DB,
            user=RDS_USER,
            password=RDS_PASSWORD,
            connect_timeout=10
        )
        print("✅ Connexion réussie!")
        
        # Exécuter le script SQL
        print("\n📝 Exécution du script SQL...")
        cursor = conn.cursor()
        cursor.execute(sql_content)
        conn.commit()
        cursor.close()
        conn.close()
        
        print("✅ Tables créées avec succès!")
        print("\n📋 Tables créées:")
        print("   - events")
        print("   - bookings")
        print("   - services")
        print("   - users")
        print("   - user_likes")
        print("   - user_favorites")
        print("   - user_participations")
        print("   - user_agenda")
        print("   - user_reviews")
        print("   - user_reports")
        print("   - discussions")
        print("\n✅ Triggers et fonctions créés automatiquement!")
        
        return True
        
    except psycopg2.Error as e:
        print(f"❌ ERREUR lors de la création des tables: {e}")
        return False
    except Exception as e:
        print(f"❌ ERREUR inattendue: {e}")
        return False

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Création des tables MapEventAI")
    print("=" * 60)
    print()
    
    success = create_tables()
    
    if success:
        print("\n" + "=" * 60)
        print("✅ TERMINÉ AVEC SUCCÈS!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ ÉCHEC!")
        print("=" * 60)
        sys.exit(1)

