#!/usr/bin/env python3
"""
Script pour vérifier l'accessibilité de RDS
"""

import boto3
import sys

try:
    rds = boto3.client('rds', region_name='eu-west-1')
    
    print("Verification de l'accessibilite de RDS...")
    print()
    
    response = rds.describe_db_instances(DBInstanceIdentifier='mapevent-db')
    
    if not response['DBInstances']:
        print("ERREUR: Base de donnees introuvable")
        sys.exit(1)
    
    db = response['DBInstances'][0]
    
    print(f"Base de donnees: {db['DBInstanceIdentifier']}")
    print(f"Status: {db['DBInstanceStatus']}")
    print(f"Endpoint: {db['Endpoint']['Address']}")
    print(f"Port: {db['Endpoint']['Port']}")
    print(f"Accessible publiquement: {'OUI' if db.get('PubliclyAccessible', False) else 'NON'}")
    print()
    
    # Vérifier les Security Groups
    print("Security Groups:")
    for sg in db['VpcSecurityGroups']:
        print(f"  - {sg['VpcSecurityGroupId']} ({sg['Status']})")
    print()
    
    if not db.get('PubliclyAccessible', False):
        print("=" * 70)
        print("PROBLEME TROUVE: La base n'est PAS accessible publiquement!")
        print("=" * 70)
        print()
        print("SOLUTION:")
        print("1. AWS Console > RDS > mapevent-db")
        print("2. Cliquez sur 'Modifier' (Modify)")
        print("3. Dans 'Connectivite', cochez 'Accessible publiquement'")
        print("4. Cliquez sur 'Continuer' puis 'Modifier la base de donnees'")
        print("5. Attendez 5-10 minutes que la modification soit terminee")
        print()
    else:
        print("OK: La base est accessible publiquement")
        print()
        print("Si vous avez toujours un timeout, verifiez:")
        print("1. Votre IP est autorisee dans les Security Groups")
        print("2. Le firewall Windows n'bloque pas le port 5432")
        print("3. Votre IP n'a pas change (redemarrage routeur)")
    
except Exception as e:
    print(f"ERREUR: {e}")
    print()
    print("Assurez-vous que:")
    print("1. AWS CLI est configure (aws configure)")
    print("2. Vous avez les permissions RDS")
