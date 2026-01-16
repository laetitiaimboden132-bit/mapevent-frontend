#!/usr/bin/env python3
"""
Script Python ULTRA-SIMPLE pour supprimer les comptes
Pas besoin d'installer quoi que ce soit de plus!
"""

import sys
import os

# Informations de connexion
RDS_HOST = "mapevent-db.cr0mmuc0elm6.eu-west-1.rds.amazonaws.com"
RDS_PORT = 5432
RDS_DB = "mapevent"
RDS_USER = "postgres"
RDS_PASSWORD = "666666Laeti69!"

print("=" * 60)
print("SUPPRESSION DES COMPTES - METHODE ULTRA-SIMPLE")
print("=" * 60)
print()

# Vérifier si psycopg2 est installé
try:
    import psycopg2
except ImportError:
    print("ERREUR: psycopg2 n'est pas installe!")
    print()
    print("INSTALLATION RAPIDE:")
    print("  pip install psycopg2-binary")
    print()
    print("OU executez:")
    print("  python -m pip install psycopg2-binary")
    print()
    sys.exit(1)

# Se connecter à la base de données
print("Connexion a la base de donnees...")
try:
    conn = psycopg2.connect(
        host=RDS_HOST,
        port=RDS_PORT,
        database=RDS_DB,
        user=RDS_USER,
        password=RDS_PASSWORD
    )
    print("  OK: Connecte!")
    print()
except Exception as e:
    print(f"  ERREUR: {e}")
    print()
    print("VERIFIEZ:")
    print("  1. Que votre IP est autorisee dans le Security Group RDS")
    print("  2. Que la base est 'Accessible publiquement'")
    print()
    sys.exit(1)

# Étape 1: Voir tous les comptes
print("ETAPE 1: Liste de tous les comptes...")
print()

cursor = conn.cursor()
cursor.execute("SELECT email, username, role, first_name, last_name FROM users ORDER BY created_at DESC")
users = cursor.fetchall()

if len(users) == 0:
    print("Aucun compte trouve. Rien a supprimer.")
    conn.close()
    sys.exit(0)

print(f"Nombre de comptes trouves: {len(users)}")
print()
print("LISTE DES COMPTES:")
print()

for user in users:
    email, username, role, first_name, last_name = user
    role = role or "user"
    role_display = f"({role})" if role in ['director', 'admin'] else ""
    print(f"  - {email} {role_display}")
    if first_name or last_name:
        print(f"    Nom: {first_name} {last_name}")

print()

# Étape 2: Demander quel compte garder
email_a_garder = None

if len(sys.argv) > 1:
    email_a_garder = sys.argv[1]
    print(f"Email a garder (fourni en parametre): {email_a_garder}")
else:
    print("Quel compte voulez-vous GARDER?")
    print("  (Tapez l'email du compte a garder)")
    print("  (Ou laissez vide pour supprimer TOUS les comptes)")
    print()
    email_a_garder = input("Email du compte a garder (ou Entree pour tout supprimer): ").strip()

print()
print("ATTENTION: Cette operation est IRREVERSIBLE!")
print()

if not email_a_garder:
    print("Vous allez supprimer TOUS les comptes!")
    confirmation = input("Tapez 'OUI' en majuscules pour confirmer: ")
    
    if confirmation != "OUI":
        print("Annule.")
        conn.close()
        sys.exit(0)
    
    # Supprimer tous les comptes
    print()
    print("Suppression de TOUS les comptes...")
    cursor.execute("DELETE FROM users")
    deleted_count = cursor.rowcount
    conn.commit()
    
    print(f"SUCCES: {deleted_count} compte(s) supprime(s)!")
    
else:
    print(f"Vous allez garder: {email_a_garder}")
    print("Tous les autres comptes seront supprimes!")
    print()
    confirmation = input("Tapez 'OUI' en majuscules pour confirmer: ")
    
    if confirmation != "OUI":
        print("Annule.")
        conn.close()
        sys.exit(0)
    
    # Vérifier que le compte existe
    cursor.execute("SELECT email FROM users WHERE email = %s", (email_a_garder,))
    if not cursor.fetchone():
        print(f"ERREUR: Le compte {email_a_garder} n'existe pas!")
        conn.close()
        sys.exit(1)
    
    # Supprimer tous sauf celui à garder
    print()
    print(f"Suppression de tous les comptes SAUF: {email_a_garder}")
    cursor.execute("DELETE FROM users WHERE email != %s", (email_a_garder,))
    deleted_count = cursor.rowcount
    conn.commit()
    
    print(f"SUCCES: {deleted_count} compte(s) supprime(s)!")
    
    # Vérifier
    cursor.execute("SELECT email, username, role FROM users")
    remaining = cursor.fetchall()
    print()
    print("Comptes restants:")
    for user in remaining:
        email, username, role = user
        print(f"  - {email} (role: {role or 'user'})")

cursor.close()
conn.close()

print()
print("TERMINE!")


