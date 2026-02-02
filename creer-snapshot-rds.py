#!/usr/bin/env python3
"""
Script pour créer un snapshot RDS de la base de données
C'est la méthode la plus simple et fiable pour sauvegarder tous les comptes
"""

import boto3
from datetime import datetime
import sys

def create_rds_snapshot():
    """Crée un snapshot RDS de la base de données"""
    try:
        rds = boto3.client('rds', region_name='eu-west-1')
        
        db_identifier = 'mapevent-db'
        
        # Nom du snapshot avec timestamp
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        snapshot_id = f'mapevent-comptes-{timestamp}'
        
        print("=" * 70)
        print("CREATION D'UN SNAPSHOT RDS")
        print("=" * 70)
        print()
        print(f"Base de donnees: {db_identifier}")
        print(f"Nom du snapshot: {snapshot_id}")
        print()
        
        # Vérifier que la base existe
        print("Verification de la base de donnees...")
        try:
            response = rds.describe_db_instances(DBInstanceIdentifier=db_identifier)
            db = response['DBInstances'][0]
            print(f"OK: Base trouvee - Status: {db['DBInstanceStatus']}")
        except Exception as e:
            print(f"ERREUR: Base de donnees introuvable: {e}")
            return False
        
        print()
        print("Creation du snapshot...")
        print("(Cela peut prendre quelques minutes)")
        print()
        
        # Créer le snapshot
        response = rds.create_db_snapshot(
            DBSnapshotIdentifier=snapshot_id,
            DBInstanceIdentifier=db_identifier,
            Tags=[
                {
                    'Key': 'Type',
                    'Value': 'SauvegardeComptes'
                },
                {
                    'Key': 'Date',
                    'Value': timestamp
                }
            ]
        )
        
        snapshot = response['DBSnapshot']
        
        print("=" * 70)
        print("SNAPSHOT CREE AVEC SUCCES!")
        print("=" * 70)
        print()
        print(f"ID du snapshot: {snapshot_id}")
        print(f"Status: {snapshot['Status']}")
        if 'SnapshotCreateTime' in snapshot:
            print(f"Date de creation: {snapshot['SnapshotCreateTime']}")
        print()
        print("Le snapshot est en cours de creation...")
        print("Vous pouvez suivre la progression dans AWS Console > RDS > Snapshots")
        print()
        print("Pour restaurer plus tard:")
        print("  1. AWS Console > RDS > Snapshots")
        print(f"  2. Selectionnez: {snapshot_id}")
        print("  3. Actions > Restaurer le snapshot")
        print()
        
        return True
        
    except Exception as e:
        print(f"ERREUR: {e}")
        print()
        print("Causes possibles:")
        print("  1. AWS CLI non configure (aws configure)")
        print("  2. Permissions insuffisantes")
        print("  3. Base de donnees en cours de modification")
        return False

if __name__ == '__main__':
    success = create_rds_snapshot()
    sys.exit(0 if success else 1)
