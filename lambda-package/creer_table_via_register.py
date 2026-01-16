#!/usr/bin/env python3
"""
Script pour créer la table user_passwords en déclenchant un register de test
La table sera créée automatiquement lors du premier register
"""

import requests
import json

LAMBDA_URL = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"

# Créer un utilisateur de test pour déclencher la création de la table
test_user = {
    "email": "test_table_creation@example.com",
    "username": "test_table_user",
    "password": "TestPassword123!",
    "firstName": "Test",
    "lastName": "User"
}

print("Création d'un utilisateur de test pour déclencher la création de la table...")
print(f"Endpoint: {LAMBDA_URL}/api/user/register")

try:
    response = requests.post(
        f"{LAMBDA_URL}/api/user/register",
        json=test_user,
        headers={"Content-Type": "application/json"},
        timeout=30
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code in [200, 201]:
        print("\n✅ Table user_passwords créée automatiquement lors du register!")
        print("   (L'utilisateur de test a été créé, vous pouvez le supprimer si nécessaire)")
    elif response.status_code == 400 and "already exists" in response.text.lower():
        print("\n✅ L'utilisateur existe déjà, mais la table devrait être créée.")
    else:
        print(f"\n⚠️  Réponse inattendue: {response.status_code}")
        print("   La table sera créée lors du prochain register valide.")
        
except Exception as e:
    print(f"❌ Erreur: {e}")
    print("\n⚠️  La table sera créée automatiquement lors du premier register valide.")




