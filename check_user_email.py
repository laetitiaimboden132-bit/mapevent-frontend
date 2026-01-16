#!/usr/bin/env python3
"""
Script pour vérifier le username associé à un email
"""
import os
import psycopg2
from urllib.parse import urlparse

# Configuration DB depuis les variables d'environnement
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/dbname')

def get_db_connection():
    """Crée une connexion à la base de données"""
    try:
        result = urlparse(DATABASE_URL)
        conn = psycopg2.connect(
            database=result.path[1:],
            user=result.username,
            password=result.password,
            host=result.hostname,
            port=result.port
        )
        return conn
    except Exception as e:
        print(f"❌ Erreur connexion DB: {e}")
        return None

def check_user_email(email):
    """Vérifie le username associé à un email"""
    conn = get_db_connection()
    if not conn:
        print("❌ Impossible de se connecter à la base de données")
        return
    
    try:
        cursor = conn.cursor()
        
        # Chercher par email (normalisé et non normalisé)
        email_lower = email.lower().strip()
        email_canonical = email_lower.replace('.', '').replace('+', '')
        
        cursor.execute("""
            SELECT id, email, email_canonical, username, first_name, last_name, 
                   created_at, profile_photo_url, google_sub
            FROM users 
            WHERE LOWER(email) = %s 
               OR email_canonical = %s 
               OR email_canonical = %s
            ORDER BY created_at DESC
        """, (email_lower, email_lower, email_canonical))
        
        rows = cursor.fetchall()
        
        if not rows:
            print(f"❌ Aucun utilisateur trouvé pour {email}")
            return
        
        print(f"\n✅ {len(rows)} utilisateur(s) trouvé(s) pour {email}:\n")
        
        for i, row in enumerate(rows, 1):
            user_id, user_email, user_email_canonical, username, first_name, last_name, created_at, profile_photo_url, google_sub = row
            print(f"--- Utilisateur #{i} ---")
            print(f"ID: {user_id}")
            print(f"Email: {user_email}")
            print(f"Email canonique: {user_email_canonical}")
            print(f"Username: {username or '(vide)'}")
            print(f"Nom: {first_name or ''} {last_name or ''}".strip() or "(vide)")
            print(f"Google Sub: {google_sub or '(vide)'}")
            print(f"Créé le: {created_at}")
            print(f"Photo: {'Oui' if profile_photo_url else 'Non'}")
            print()
        
        cursor.close()
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    email = "laetitia.imboden132@gmail.com"
    print(f"🔍 Recherche du username pour: {email}\n")
    check_user_email(email)


