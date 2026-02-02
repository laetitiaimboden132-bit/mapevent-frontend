#!/usr/bin/env python3
"""
Créer les secrets dans AWS Secrets Manager
Migre les clés depuis lambda.env vers Secrets Manager (chiffré)
"""

import boto3
import json
from pathlib import Path

print("=" * 70)
print("CREATION DES SECRETS DANS AWS SECRETS MANAGER")
print("=" * 70)
print()

# Lire lambda.env
lambda_env_path = Path('lambda-package/lambda.env')
if not lambda_env_path.exists():
    print("ERREUR: lambda.env introuvable")
    exit(1)

# Parser lambda.env
secrets_data = {}
with open(lambda_env_path, 'r', encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        if line and not line.startswith('#') and '=' in line:
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            secrets_data[key] = value

print("Secrets trouves dans lambda.env:")
for key in ['RDS_PASSWORD', 'SENDGRID_API_KEY', 'STRIPE_SECRET_KEY', 'JWT_SECRET']:
    if key in secrets_data:
        print(f"  - {key}: {'*' * 20} (present)")
    else:
        print(f"  - {key}: (absent)")
print()

# Créer les secrets dans Secrets Manager
secrets_client = boto3.client('secretsmanager', region_name='eu-west-1')

secrets_to_create = [
    {
        'name': '/mapevent/rds/password',
        'key': 'RDS_PASSWORD',
        'description': 'Mot de passe RDS PostgreSQL'
    },
    {
        'name': '/mapevent/sendgrid/api-key',
        'key': 'SENDGRID_API_KEY',
        'description': 'Clé API SendGrid pour envoi d\'emails'
    },
    {
        'name': '/mapevent/stripe/secret-key',
        'key': 'STRIPE_SECRET_KEY',
        'description': 'Clé secrète Stripe pour paiements'
    },
    {
        'name': '/mapevent/jwt/secret',
        'key': 'JWT_SECRET',
        'description': 'Secret JWT pour authentification'
    }
]

created = []
skipped = []

for secret_info in secrets_to_create:
    secret_name = secret_info['name']
    env_key = secret_info['key']
    description = secret_info['description']
    
    if env_key not in secrets_data or not secrets_data[env_key]:
        print(f"SKIP: {secret_name} (valeur absente dans lambda.env)")
        skipped.append(secret_name)
        continue
    
    secret_value = secrets_data[env_key]
    
    try:
        # Vérifier si le secret existe déjà
        try:
            existing = secrets_client.describe_secret(SecretId=secret_name)
            print(f"SKIP: {secret_name} (existe deja)")
            skipped.append(secret_name)
            continue
        except secrets_client.exceptions.ResourceNotFoundException:
            pass  # Le secret n'existe pas, on peut le créer
        
        # Créer le secret
        print(f"Creation: {secret_name}...", end=" ")
        response = secrets_client.create_secret(
            Name=secret_name,
            Description=description,
            SecretString=secret_value,
            Tags=[
                {'Key': 'Project', 'Value': 'MapEvent'},
                {'Key': 'Type', 'Value': 'API-Key'}
            ]
        )
        print("OK")
        created.append(secret_name)
        
    except Exception as e:
        print(f"ERREUR: {e}")
        skipped.append(secret_name)

print()
print("=" * 70)
print("RESUME")
print("=" * 70)
print()
print(f"Secrets crees: {len(created)}")
for name in created:
    print(f"  - {name}")
print()
print(f"Secrets ignores: {len(skipped)}")
for name in skipped:
    print(f"  - {name}")
print()
print("PROCHAINES ETAPES:")
print("1. Modifier Lambda pour utiliser Secrets Manager")
print("2. Tester que tout fonctionne")
print("3. Supprimer les cles de lambda.env (optionnel)")
print()
