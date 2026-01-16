#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script pour supprimer un compte utilisateur de la base de données
Usage: python delete_user_account.py <email>
"""

import os
import sys
import psycopg2
from dotenv import load_dotenv

# Forcer l'encodage UTF-8 pour Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Charger les variables d'environnement depuis lambda.env
load_dotenv('lambda.env')

def get_db_connection():
    """Établit une connexion à la base de données RDS"""
    try:
        conn = psycopg2.connect(
            host=os.environ.get('RDS_HOST'),
            port=os.environ.get('RDS_PORT', '5432'),
            database=os.environ.get('RDS_DB', 'mapevent'),
            user=os.environ.get('RDS_USER'),
            password=os.environ.get('RDS_PASSWORD'),
            connect_timeout=10
        )
        return conn
    except Exception as e:
        print(f"❌ Erreur de connexion à la base de données: {e}")
        return None

def delete_user_avatar_from_s3(user_id):
    """Supprime l'avatar de l'utilisateur depuis S3"""
    try:
        from backend.services.s3_service import delete_avatar_from_s3
        success = delete_avatar_from_s3(user_id)
        if success:
            print(f"✅ Avatar S3 supprimé pour user_id: {user_id}")
        else:
            print(f"⚠️ Avatar S3 non trouvé ou déjà supprimé pour user_id: {user_id}")
    except Exception as e:
        print(f"⚠️ Erreur lors de la suppression de l'avatar S3: {e}")
        # On continue même si la suppression S3 échoue

def delete_user_account(email):
    """Supprime un compte utilisateur et toutes ses données associées"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # 1. Trouver l'utilisateur par email
        print(f"\n🔍 Recherche de l'utilisateur avec l'email: {email}")
        cursor.execute("SELECT id, username, email, profile_photo_url FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if not user:
            print(f"❌ Aucun utilisateur trouvé avec l'email: {email}")
            cursor.close()
            conn.close()
            return False
        
        user_id, username, user_email, profile_photo_url = user
        print(f"✅ Utilisateur trouvé:")
        print(f"   - ID: {user_id}")
        print(f"   - Username: {username}")
        print(f"   - Email: {user_email}")
        print(f"   - Photo URL: {profile_photo_url or 'Aucune'}")
        
        # 2. Compter les données associées avant suppression
        print(f"\n📊 Comptage des données associées...")
        cursor.execute("SELECT COUNT(*) FROM user_likes WHERE user_id = %s", (user_id,))
        likes_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM user_favorites WHERE user_id = %s", (user_id,))
        favorites_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM user_participations WHERE user_id = %s", (user_id,))
        participations_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM user_reviews WHERE user_id = %s", (user_id,))
        reviews_count = cursor.fetchone()[0]
        
        print(f"   - Likes: {likes_count}")
        print(f"   - Favoris: {favorites_count}")
        print(f"   - Participations: {participations_count}")
        print(f"   - Avis: {reviews_count}")
        
        # 3. Supprimer l'avatar S3 si présent
        if profile_photo_url:
            print(f"\n🗑️ Suppression de l'avatar S3...")
            delete_user_avatar_from_s3(user_id)
        
        # 4. Supprimer l'utilisateur (CASCADE supprimera automatiquement toutes les données liées)
        print(f"\n🗑️ Suppression de l'utilisateur et de toutes ses données...")
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        
        # Vérifier que la suppression a réussi
        cursor.execute("SELECT COUNT(*) FROM users WHERE id = %s", (user_id,))
        remaining = cursor.fetchone()[0]
        
        if remaining > 0:
            print(f"❌ Erreur: L'utilisateur n'a pas été supprimé")
            conn.rollback()
            cursor.close()
            conn.close()
            return False
        
        # Commit la transaction
        conn.commit()
        cursor.close()
        conn.close()
        
        print(f"\n✅ Compte utilisateur supprimé avec succès!")
        print(f"   - Email: {email}")
        print(f"   - User ID: {user_id}")
        print(f"   - Toutes les données associées ont été supprimées automatiquement (CASCADE)")
        
        return True
        
    except Exception as e:
        print(f"❌ Erreur lors de la suppression: {e}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.rollback()
            cursor.close()
            conn.close()
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python delete_user_account.py <email> [--force]")
        print("Exemple: python delete_user_account.py laetitia.imboden132@gmail.com --force")
        sys.exit(1)
    
    email = sys.argv[1].strip()
    force = '--force' in sys.argv or '-f' in sys.argv
    
    print("=" * 60)
    print("🗑️  SUPPRESSION DE COMPTE UTILISATEUR")
    print("=" * 60)
    print(f"Email: {email}")
    print("=" * 60)
    
    # Demander confirmation sauf si --force
    if not force:
        try:
            confirmation = input(f"\n⚠️  Êtes-vous sûr de vouloir supprimer le compte {email}? (oui/non): ")
            if confirmation.lower() not in ['oui', 'o', 'yes', 'y']:
                print("❌ Suppression annulée")
                sys.exit(0)
        except (EOFError, KeyboardInterrupt):
            print("\n❌ Suppression annulée (pas de confirmation interactive)")
            sys.exit(0)
    else:
        print("\n⚠️  Mode --force activé: suppression sans confirmation")
    
    success = delete_user_account(email)
    
    if success:
        print("\n" + "=" * 60)
        print("✅ SUPPRESSION TERMINÉE")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ ÉCHEC DE LA SUPPRESSION")
        print("=" * 60)
        sys.exit(1)

