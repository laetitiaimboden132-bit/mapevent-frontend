#!/usr/bin/env python3
"""
Script de restauration complète des comptes utilisateurs
Restaure toutes les données depuis un fichier de sauvegarde JSON
"""

import psycopg2
import json
import os
from datetime import datetime
from pathlib import Path
import sys

# Configuration depuis les variables d'environnement
RDS_HOST = os.getenv('RDS_HOST', 'mapevent-db.cr0mmuc0elm6.eu-west-1.rds.amazonaws.com')
RDS_PORT = int(os.getenv('RDS_PORT', '5432'))
RDS_DB = os.getenv('RDS_DB', 'mapevent')
RDS_USER = os.getenv('RDS_USER', 'postgres')
RDS_PASSWORD = os.getenv('RDS_PASSWORD', '')

if not RDS_PASSWORD:
    print("❌ ERREUR: RDS_PASSWORD non défini")
    sys.exit(1)

def get_db_connection():
    """Crée une connexion à PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host=RDS_HOST,
            port=RDS_PORT,
            database=RDS_DB,
            user=RDS_USER,
            password=RDS_PASSWORD,
            connect_timeout=10,
            sslmode='require'
        )
        return conn
    except Exception as e:
        print(f"❌ Erreur connexion DB: {e}")
        return None

def restore_table(conn, table_name, data, primary_key='id'):
    """Restaure une table"""
    if not data:
        return 0
    
    try:
        cursor = conn.cursor()
        
        # Obtenir les colonnes de la table
        cursor.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = %s
            ORDER BY ordinal_position
        """, (table_name,))
        columns_info = cursor.fetchall()
        columns = [col[0] for col in columns_info]
        
        restored = 0
        for row_data in data:
            try:
                # Filtrer les colonnes qui existent dans la table
                filtered_data = {k: v for k, v in row_data.items() if k in columns}
                
                if not filtered_data:
                    continue
                
                # Construire la requête INSERT ... ON CONFLICT
                cols = list(filtered_data.keys())
                placeholders = ', '.join(['%s'] * len(cols))
                col_names = ', '.join(cols)
                
                # Construire la clause ON CONFLICT
                update_clause = ', '.join([f"{col} = EXCLUDED.{col}" for col in cols if col != primary_key])
                
                query = f"""
                    INSERT INTO {table_name} ({col_names})
                    VALUES ({placeholders})
                    ON CONFLICT ({primary_key}) DO UPDATE SET {update_clause}
                """
                
                values = [filtered_data[col] for col in cols]
                cursor.execute(query, values)
                restored += 1
            except Exception as e:
                print(f"  ⚠️ Erreur restauration ligne {row_data.get(primary_key, 'unknown')}: {e}")
                continue
        
        conn.commit()
        cursor.close()
        return restored
    except Exception as e:
        print(f"  ❌ Erreur restauration table {table_name}: {e}")
        conn.rollback()
        return 0

def main():
    print("=" * 70)
    print("🔄 RESTAURATION COMPLÈTE DES COMPTES UTILISATEURS")
    print("=" * 70)
    print()
    
    # Demander le fichier de sauvegarde
    if len(sys.argv) > 1:
        backup_file = Path(sys.argv[1])
    else:
        # Chercher le dernier fichier de sauvegarde
        backup_dir = Path("sauvegardes")
        if not backup_dir.exists():
            print("❌ Dossier 'sauvegardes' introuvable")
            sys.exit(1)
        
        backup_files = sorted(backup_dir.glob("comptes_utilisateurs_*.json"), reverse=True)
        if not backup_files:
            print("❌ Aucun fichier de sauvegarde trouvé")
            sys.exit(1)
        
        backup_file = backup_files[0]
        print(f"📁 Utilisation du dernier fichier: {backup_file.name}")
    
    if not backup_file.exists():
        print(f"❌ Fichier introuvable: {backup_file}")
        sys.exit(1)
    
    print(f"📦 Chargement de la sauvegarde: {backup_file}")
    print()
    
    # Charger le fichier JSON
    try:
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
    except Exception as e:
        print(f"❌ Erreur lecture fichier: {e}")
        sys.exit(1)
    
    # Afficher les métadonnées
    metadata = backup_data.get('metadata', {})
    print(f"📅 Date de sauvegarde: {metadata.get('timestamp', 'N/A')}")
    print(f"🗄️ Base de données: {metadata.get('database', 'N/A')}")
    print()
    
    # Demander confirmation
    print("⚠️ ATTENTION: Cette opération va restaurer tous les comptes utilisateurs.")
    print("   Les données existantes seront remplacées par celles de la sauvegarde.")
    print()
    response = input("Continuer ? (oui/non): ").strip().lower()
    if response not in ['oui', 'o', 'yes', 'y']:
        print("❌ Restauration annulée")
        sys.exit(0)
    
    print()
    print("🔌 Connexion à la base de données...")
    conn = get_db_connection()
    if not conn:
        print("❌ Impossible de se connecter à la base de données")
        sys.exit(1)
    print("✅ Connexion réussie")
    print()
    
    # Ordre de restauration (respecter les dépendances)
    restore_order = [
        'users',
        'user_passwords',
        'user_profiles',
        'email_verification_tokens',
        'user_likes',
        'user_favorites',
        'user_participations',
        'user_agenda',
        'user_reviews',
        'user_friends',
        'subscriptions',
        'user_alerts',
        'user_alert_settings',
        'user_reports',
        'groups',
        'group_members',
    ]
    
    # Restaurer chaque table
    total_restored = 0
    for table_name in restore_order:
        if table_name not in backup_data.get('tables', {}):
            continue
        
        data = backup_data['tables'][table_name]
        if not data:
            continue
        
        print(f"🔄 Restauration de {table_name}...", end=" ")
        count = restore_table(conn, table_name, data)
        total_restored += count
        print(f"✅ {count} enregistrements restaurés")
    
    print()
    print(f"📊 Total: {total_restored} enregistrements restaurés")
    print()
    
    # Fermer la connexion
    conn.close()
    
    print("=" * 70)
    print("✅ RESTAURATION TERMINÉE AVEC SUCCÈS")
    print("=" * 70)
    print()

if __name__ == '__main__':
    main()
