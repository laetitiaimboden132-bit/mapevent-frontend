"""
Script pour supprimer TOUS les comptes utilisateurs de la base de données
ATTENTION: Cette opération est IRRÉVERSIBLE
"""

import os
import sys
import psycopg2
import boto3
from typing import List, Tuple

# Configuration depuis les variables d'environnement
RDS_HOST = os.environ.get('RDS_HOST', 'localhost')
RDS_PORT = os.environ.get('RDS_PORT', '5432')
RDS_DB = os.environ.get('RDS_DB', 'mapevent')
RDS_USER = os.environ.get('RDS_USER', 'postgres')
RDS_PASSWORD = os.environ.get('RDS_PASSWORD', '')

# Configuration S3
S3_BUCKET_NAME = os.environ.get('S3_AVATARS_BUCKET', 'mapevent-avatars')
S3_REGION = os.environ.get('AWS_REGION', 'eu-west-1')
S3_AVATARS_PREFIX = 'avatars/'

def get_db_connection():
    """Établit une connexion à la base de données PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host=RDS_HOST,
            port=RDS_PORT,
            database=RDS_DB,
            user=RDS_USER,
            password=RDS_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"ERREUR de connexion a la base de donnees: {e}")
        return None

def get_s3_client():
    """Retourne un client S3 configuré"""
    try:
        return boto3.client('s3', region_name=S3_REGION)
    except Exception as e:
        print(f"⚠️ Erreur création client S3: {e}")
        return None

def delete_all_avatars_from_s3(user_ids: List[str]) -> int:
    """Supprime tous les avatars des utilisateurs de S3"""
    s3_client = get_s3_client()
    if not s3_client:
        print("Client S3 non disponible, skip suppression S3")
        return 0
    
    deleted_count = 0
    extensions = ['jpg', 'jpeg', 'png', 'gif', 'webp']
    
    print(f"\nSuppression des avatars S3...")
    for user_id in user_ids:
        for ext in extensions:
            s3_key = f"{S3_AVATARS_PREFIX}{user_id}.{ext}"
            try:
                s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
                deleted_count += 1
                print(f"   Supprime: {s3_key}")
            except Exception as e:
                # Ignorer si le fichier n'existe pas
                pass
    
    print(f"{deleted_count} avatars supprimes de S3")
    return deleted_count

def delete_all_users():
    """Supprime TOUS les comptes utilisateurs et leurs données associées"""
    conn = get_db_connection()
    if not conn:
        print("❌ Impossible de se connecter à la base de données")
        return False
    
    try:
        cursor = conn.cursor()
        
        # 1. Récupérer tous les user_ids avant suppression
        print("\nRecuperation de tous les utilisateurs...")
        cursor.execute("SELECT id, email, username FROM users")
        all_users = cursor.fetchall()
        user_count = len(all_users)
        
        if user_count == 0:
            print("Aucun utilisateur a supprimer")
            cursor.close()
            conn.close()
            return True
        
        print(f"ATTENTION: {user_count} utilisateur(s) trouve(s)")
        for user_id, email, username in all_users:
            print(f"   - {email} ({username or 'N/A'}) - ID: {user_id}")
        
        # 2. Compter les données associées
        print(f"\n📊 Comptage des données associées...")
        cursor.execute("SELECT COUNT(*) FROM user_likes")
        likes_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM user_favorites")
        favorites_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM user_agenda")
        agenda_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM user_participations")
        participations_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM user_reviews")
        reviews_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM user_passwords")
        passwords_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM subscriptions")
        subscriptions_count = cursor.fetchone()[0]
        
        print(f"   - Likes: {likes_count}")
        print(f"   - Favoris: {favorites_count}")
        print(f"   - Agenda: {agenda_count}")
        print(f"   - Participations: {participations_count}")
        print(f"   - Avis: {reviews_count}")
        print(f"   - Mots de passe: {passwords_count}")
        print(f"   - Abonnements: {subscriptions_count}")
        
        # 3. Récupérer les user_ids pour suppression S3
        user_ids = [user_id for user_id, _, _ in all_users]
        
        # 4. Supprimer tous les avatars S3
        delete_all_avatars_from_s3(user_ids)
        
        # 5. Demander confirmation
        print(f"\nATTENTION: Cette operation va supprimer:")
        print(f"   - {user_count} utilisateur(s)")
        print(f"   - {likes_count} like(s)")
        print(f"   - {favorites_count} favori(s)")
        print(f"   - {agenda_count} entrée(s) d'agenda")
        print(f"   - {participations_count} participation(s)")
        print(f"   - {reviews_count} avis")
        print(f"   - {passwords_count} mot(s) de passe")
        print(f"   - {subscriptions_count} abonnement(s)")
        print(f"\nCette operation est IRREVERSIBLE!")
        
        # En mode non-interactif, utiliser une variable d'environnement
        confirm = os.environ.get('CONFIRM_DELETE_ALL', '').lower()
        if confirm != 'yes':
            print("\nSuppression annulee. Pour confirmer, definissez CONFIRM_DELETE_ALL=yes")
            cursor.close()
            conn.close()
            return False
        
        # 6. Supprimer tous les utilisateurs (CASCADE supprimera automatiquement toutes les données liées)
        print(f"\nSuppression de tous les utilisateurs...")
        cursor.execute("DELETE FROM users")
        deleted_rows = cursor.rowcount
        
        # 7. Vérifier que tous les utilisateurs ont été supprimés
        cursor.execute("SELECT COUNT(*) FROM users")
        remaining = cursor.fetchone()[0]
        
        if remaining > 0:
            print(f"ERREUR: {remaining} utilisateur(s) n'ont pas ete supprimes")
            conn.rollback()
            cursor.close()
            conn.close()
            return False
        
        # 8. Commit la transaction
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"\nSUCCES: Tous les comptes utilisateurs ont ete supprimes!")
        print(f"   - {deleted_rows} utilisateur(s) supprime(s)")
        print(f"   - Toutes les donnees associees ont ete supprimees automatiquement (CASCADE)")
        
        return True
        
    except Exception as e:
        print(f"ERREUR lors de la suppression: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()
            cursor.close()
            conn.close()
        return False

if __name__ == '__main__':
    import sys
    import io
    # Forcer l'encodage UTF-8 pour la sortie
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    print("=" * 60)
    print("SUPPRESSION DE TOUS LES COMPTES UTILISATEURS")
    print("=" * 60)
    print("\nATTENTION: Cette operation est IRREVERSIBLE!")
    print("   Tous les comptes utilisateurs et leurs donnees seront supprimes.")
    print("\n   Pour confirmer, definissez la variable d'environnement:")
    print("   CONFIRM_DELETE_ALL=yes")
    print("=" * 60)
    
    success = delete_all_users()
    
    if success:
        print("\nOperation terminee avec succes")
        sys.exit(0)
    else:
        print("\nOperation echouee")
        sys.exit(1)

