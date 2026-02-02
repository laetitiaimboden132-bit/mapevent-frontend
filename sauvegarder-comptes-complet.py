#!/usr/bin/env python3
"""
Script de sauvegarde complète de tous les comptes utilisateurs
Sauvegarde toutes les données utilisateurs et tables associées
"""

import psycopg2
import json
import os
from datetime import datetime
from pathlib import Path
import sys

# Configuration depuis les variables d'environnement ou lambda.env
RDS_HOST = os.getenv('RDS_HOST', 'mapevent-db.cr0mmuc0elm6.eu-west-1.rds.amazonaws.com')
RDS_PORT = int(os.getenv('RDS_PORT', '5432'))
RDS_DB = os.getenv('RDS_DB', 'mapevent')
RDS_USER = os.getenv('RDS_USER', 'postgres')
RDS_PASSWORD = os.getenv('RDS_PASSWORD', '')

# Essayer de charger depuis lambda.env si disponible
if not RDS_PASSWORD:
    try:
        lambda_env_path = Path('lambda-package/lambda.env')
        if lambda_env_path.exists():
            with open(lambda_env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('RDS_PASSWORD='):
                        RDS_PASSWORD = line.split('=', 1)[1].strip().strip('"').strip("'")
                        break
    except:
        pass

if not RDS_PASSWORD:
    print("ERREUR: RDS_PASSWORD non defini")
    print("   Definissez la variable d'environnement RDS_PASSWORD")
    print("   OU ajoutez RDS_PASSWORD dans lambda-package/lambda.env")
    sys.exit(1)

def get_db_connection():
    """Crée une connexion à PostgreSQL"""
    try:
        print(f"Tentative de connexion à {RDS_HOST}:{RDS_PORT}/{RDS_DB}...")
        print(f"User: {RDS_USER}")
        conn = psycopg2.connect(
            host=RDS_HOST,
            port=RDS_PORT,
            database=RDS_DB,
            user=RDS_USER,
            password=RDS_PASSWORD,
            connect_timeout=30,  # Augmenter le timeout à 30 secondes
            sslmode='require'
        )
        print("OK: Connexion reussie!")
        return conn
    except psycopg2.OperationalError as e:
        print(f"ERREUR connexion DB (OperationalError): {e}")
        print("\nCauses possibles:")
        print("  1. La base de donnees n'est pas accessible publiquement")
        print("  2. Votre IP n'est pas autorisee dans les Security Groups")
        print("  3. Le firewall bloque le port 5432")
        print("  4. Le mot de passe est incorrect")
        return None
    except Exception as e:
        print(f"ERREUR connexion DB: {e}")
        return None

def backup_table(conn, table_name, where_clause=None):
    """Sauvegarde une table complète"""
    try:
        cursor = conn.cursor()
        
        query = f"SELECT * FROM {table_name}"
        if where_clause:
            query += f" WHERE {where_clause}"
        query += " ORDER BY id"
        
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        
        data = []
        for row in rows:
            row_dict = {}
            for i, col in enumerate(columns):
                value = row[i]
                # Convertir les types non sérialisables en JSON
                if isinstance(value, (datetime,)):
                    value = value.isoformat()
                elif hasattr(value, '__dict__'):
                    value = str(value)
                row_dict[col] = value
            data.append(row_dict)
        
        cursor.close()
        return data
    except Exception as e:
        print(f"⚠️ Erreur sauvegarde table {table_name}: {e}")
        return []

def main():
    print("=" * 70)
    print("SAUVEGARDE COMPLETE DES COMPTES UTILISATEURS")
    print("=" * 70)
    print()
    
    # Connexion a la base de donnees
    print("Connexion a la base de donnees...")
    conn = get_db_connection()
    if not conn:
        print("ERREUR: Impossible de se connecter a la base de donnees")
        sys.exit(1)
    print("OK: Connexion reussie")
    print()
    
    # Creer le dossier de sauvegarde
    backup_dir = Path("sauvegardes")
    backup_dir.mkdir(exist_ok=True)
    
    # Nom du fichier avec timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"comptes_utilisateurs_{timestamp}.json"
    
    print(f"Creation de la sauvegarde: {backup_file}")
    print()
    
    # Dictionnaire pour stocker toutes les données
    backup_data = {
        'metadata': {
            'timestamp': datetime.now().isoformat(),
            'database': RDS_DB,
            'host': RDS_HOST,
            'version': '1.0'
        },
        'tables': {}
    }
    
    # Liste des tables à sauvegarder (dans l'ordre des dépendances)
    tables_to_backup = [
        # Tables principales
        ('users', None),
        ('user_passwords', None),
        ('user_profiles', None),
        ('email_verification_tokens', None),
        
        # Tables de relations
        ('user_likes', None),
        ('user_favorites', None),
        ('user_participations', None),
        ('user_agenda', None),
        ('user_reviews', None),
        ('user_friends', None),
        
        # Tables d'abonnements
        ('subscriptions', None),
        
        # Tables d'alertes
        ('user_alerts', None),
        ('user_alert_settings', None),
        
        # Tables de signalements
        ('user_reports', None),
        
        # Tables de groupes
        ('groups', None),
        ('group_members', None),
    ]
    
    # Sauvegarder chaque table
    total_records = 0
    for table_name, where_clause in tables_to_backup:
        print(f"Sauvegarde de {table_name}...", end=" ")
        try:
            data = backup_table(conn, table_name, where_clause)
            backup_data['tables'][table_name] = data
            count = len(data)
            total_records += count
            print(f"OK: {count} enregistrements")
        except Exception as e:
            print(f"ERREUR: {e}")
            backup_data['tables'][table_name] = []
    
    print()
    print(f"Total: {total_records} enregistrements sauvegardes")
    print()
    
    # Compter les utilisateurs
    users_count = len(backup_data['tables'].get('users', []))
    print(f"Utilisateurs sauvegardes: {users_count}")
    print()
    
    # Sauvegarder dans le fichier JSON
    print(f"Ecriture dans {backup_file}...")
    try:
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False, default=str)
        file_size = backup_file.stat().st_size / 1024  # Taille en KB
        print(f"OK: Sauvegarde creee: {file_size:.2f} KB")
    except Exception as e:
        print(f"ERREUR ecriture fichier: {e}")
        conn.close()
        sys.exit(1)
    
    # Creer aussi un resume
    summary_file = backup_dir / f"resume_comptes_{timestamp}.txt"
    print()
    print(f"Creation du resume: {summary_file}")
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("=" * 70 + "\n")
        f.write("RÉSUMÉ DE LA SAUVEGARDE DES COMPTES UTILISATEURS\n")
        f.write("=" * 70 + "\n\n")
        f.write(f"Date: {backup_data['metadata']['timestamp']}\n")
        f.write(f"Base de données: {backup_data['metadata']['database']}\n")
        f.write(f"Fichier: {backup_file.name}\n\n")
        f.write("Statistiques par table:\n")
        f.write("-" * 70 + "\n")
        for table_name, data in backup_data['tables'].items():
            f.write(f"  {table_name:30} : {len(data):5} enregistrements\n")
        f.write("-" * 70 + "\n")
        f.write(f"  {'TOTAL':30} : {total_records:5} enregistrements\n")
        f.write("\n")
        f.write("Détails des utilisateurs:\n")
        f.write("-" * 70 + "\n")
        for user in backup_data['tables'].get('users', []):
            f.write(f"  - {user.get('email', 'N/A'):40} ({user.get('username', 'N/A')})\n")
            f.write(f"    ID: {user.get('id', 'N/A')}\n")
            f.write(f"    Rôle: {user.get('role', 'user')}\n")
            f.write(f"    Créé: {user.get('created_at', 'N/A')}\n")
            f.write("\n")
    
    print("OK: Resume cree")
    print()
    
    # Fermer la connexion
    conn.close()
    
    print("=" * 70)
    print("SAUVEGARDE TERMINEE AVEC SUCCES")
    print("=" * 70)
    print()
    print(f"Fichier de sauvegarde: {backup_file}")
    print(f"Fichier resume: {summary_file}")
    print()
    print("Pour restaurer, utilisez: restaurer-comptes-complet.py")
    print()

if __name__ == '__main__':
    main()
