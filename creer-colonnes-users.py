#!/usr/bin/env python3
"""
Script Python pour créer toutes les colonnes nécessaires dans la table users
Ce script se connecte à votre base de données RDS et exécute le script SQL
"""

import os
import sys
import psycopg2
from psycopg2 import sql

def get_rds_config():
    """Récupère la configuration RDS depuis lambda.env"""
    # Obtenir le répertoire du script Python
    script_dir = os.path.dirname(os.path.abspath(__file__))
    lambda_env_path = os.path.join(script_dir, "lambda-package", "lambda.env")
    
    config = {
        'host': None,
        'port': '5432',
        'database': 'mapevent',
        'user': 'postgres',
        'password': None
    }
    
    # Lire lambda.env
    if os.path.exists(lambda_env_path):
        print(f"[OK] Lecture de {lambda_env_path}...")
        with open(lambda_env_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line.startswith('RDS_HOST='):
                    config['host'] = line.split('=', 1)[1].strip()
                elif line.startswith('RDS_PORT='):
                    config['port'] = line.split('=', 1)[1].strip()
                elif line.startswith('RDS_DB='):
                    config['database'] = line.split('=', 1)[1].strip()
                elif line.startswith('RDS_USER='):
                    config['user'] = line.split('=', 1)[1].strip()
                elif line.startswith('RDS_PASSWORD='):
                    config['password'] = line.split('=', 1)[1].strip()
    else:
        print(f"[ATTENTION] Fichier {lambda_env_path} non trouve")
        print("   Utilisation des valeurs par defaut...")
    
    # Vérifier les valeurs requises
    if not config['host']:
        print("[ERREUR] RDS_HOST non trouve dans lambda.env")
        print("   Valeur par defaut: mapevent-db.cr0mmuc0elm6.eu-west-1.rds.amazonaws.com")
        config['host'] = 'mapevent-db.cr0mmuc0elm6.eu-west-1.rds.amazonaws.com'
    
    if not config['password']:
        print("[ERREUR] RDS_PASSWORD non trouve dans lambda.env")
        print("   Valeur par defaut: 666666Laeti69!")
        config['password'] = '666666Laeti69!'
    
    return config

def read_sql_script():
    """Lit le script SQL"""
    # Obtenir le répertoire du script Python
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sql_file = os.path.join(script_dir, "CREER_COLONNES_USERS.sql")
    
    if not os.path.exists(sql_file):
        print(f"[ERREUR] Fichier {sql_file} introuvable!")
        sys.exit(1)
    
    print(f"[OK] Lecture de {sql_file}...")
    with open(sql_file, 'r', encoding='utf-8') as f:
        return f.read()

def execute_sql(conn, sql_script):
    """Exécute le script SQL"""
    cursor = conn.cursor()
    
    try:
        # Exécuter le script complet
        cursor.execute(sql_script)
        conn.commit()
        print("[OK] Script SQL execute avec succes!")
        return True
    except Exception as e:
        conn.rollback()
        print(f"[ERREUR] Erreur lors de l'execution SQL: {e}")
        print(f"   Type d'erreur: {type(e).__name__}")
        return False
    finally:
        cursor.close()

def main():
    print("=" * 50)
    print("Création des colonnes users pour OAuth")
    print("=" * 50)
    print()
    
    # Récupérer la configuration
    print("[1/3] Récupération de la configuration RDS...")
    config = get_rds_config()
    
    print(f"   Host: {config['host']}")
    print(f"   Port: {config['port']}")
    print(f"   Database: {config['database']}")
    print(f"   User: {config['user']}")
    print(f"   Password: {'*' * len(config['password'])}")
    print()
    
    # Lire le script SQL
    print("[2/3] Lecture du script SQL...")
    sql_script = read_sql_script()
    print(f"   Script SQL chargé: {len(sql_script)} caractères")
    print()
    
    # Se connecter à la base de données
    print("[3/3] Connexion à la base de données et exécution...")
    try:
        conn = psycopg2.connect(
            host=config['host'],
            port=config['port'],
            database=config['database'],
            user=config['user'],
            password=config['password'],
            connect_timeout=10,
            sslmode='require'
        )
        print("[OK] Connexion RDS reussie!")
        print()
        
        # Exécuter le script
        success = execute_sql(conn, sql_script)
        
        conn.close()
        
        if success:
            print()
            print("=" * 50)
            print("[SUCCES] Colonnes creees avec succes!")
            print("=" * 50)
            print()
            print("Prochaines etapes:")
            print("  1. Publiez votre application Google OAuth en mode Production")
            print("  2. Testez la connexion Google sur https://mapevent.world")
            print("  3. Le formulaire d'inscription devrait s'afficher automatiquement")
        else:
            print()
            print("=" * 50)
            print("[ERREUR] Echec de l'execution SQL")
            print("=" * 50)
            sys.exit(1)
            
    except psycopg2.OperationalError as e:
        print(f"[ERREUR] Erreur de connexion: {e}")
        print()
        print("Verifiez:")
        print("  1. Que l'endpoint RDS est correct")
        print("  2. Que le mot de passe est correct")
        print("  3. Que votre IP est autorisee dans les Security Groups RDS")
        sys.exit(1)
    except Exception as e:
        print(f"[ERREUR] Erreur inattendue: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

