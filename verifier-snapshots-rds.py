#!/usr/bin/env python3
"""
Vérifier l'état des snapshots RDS
"""

import boto3
from datetime import datetime

rds = boto3.client('rds', region_name='eu-west-1')

print("=" * 70)
print("SNAPSHOTS RDS EXISTANTS")
print("=" * 70)
print()

# Lister tous les snapshots
response = rds.describe_db_snapshots(DBInstanceIdentifier='mapevent-db')

if not response['DBSnapshots']:
    print("Aucun snapshot trouve")
else:
    print(f"Total: {len(response['DBSnapshots'])} snapshot(s)")
    print()
    
    # Afficher les snapshots dans l'ordre retourné (AWS les retourne déjà triés)
    snapshots = response['DBSnapshots']
    
    for i, snapshot in enumerate(snapshots[:10], 1):  # Afficher les 10 plus récents
        status = snapshot['Status']
        status_text = "OK" if status == 'available' else "EN COURS" if status == 'creating' else "ERREUR"
        
        print(f"{i}. {snapshot['DBSnapshotIdentifier']}")
        print(f"   Status: {status_text} ({status})")
        if 'SnapshotCreateTime' in snapshot:
            print(f"   Date: {snapshot['SnapshotCreateTime']}")
        print(f"   Taille: {snapshot.get('AllocatedStorage', 'N/A')} GB")
        print()

print("=" * 70)
print()
print("Le premier snapshot cree est en cours de creation...")
print("Attendez qu'il soit termine (status: available) avant d'en creer un autre")
print()
print("Pour suivre la progression:")
print("  AWS Console > RDS > Snapshots")
print()
