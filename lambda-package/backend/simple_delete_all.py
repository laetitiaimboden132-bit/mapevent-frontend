"""
Endpoint simple pour supprimer tous les comptes sans Flask
À utiliser directement depuis Lambda
"""
import os
import psycopg2
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler_simple_delete_all(event, context):
    """
    Handler Lambda simple pour supprimer tous les comptes
    """
    try:
        # Connexion à la base de données
        conn = psycopg2.connect(
            host=os.environ.get('RDS_HOST'),
            port=int(os.environ.get('RDS_PORT', 5432)),
            database=os.environ.get('RDS_DB', 'postgres'),
            user=os.environ.get('RDS_USER', 'postgres'),
            password=os.environ.get('RDS_PASSWORD')
        )
        
        cursor = conn.cursor()
        
        # Compter les comptes avant suppression
        cursor.execute("SELECT COUNT(*) FROM users")
        total_before = cursor.fetchone()[0]
        
        if total_before == 0:
            cursor.close()
            conn.close()
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'success': True,
                    'message': 'Aucun compte à supprimer',
                    'deleted_count': 0
                })
            }
        
        # Supprimer tous les comptes
        cursor.execute("DELETE FROM users")
        deleted_count = cursor.rowcount
        
        # Vérifier
        cursor.execute("SELECT COUNT(*) FROM users")
        total_after = cursor.fetchone()[0]
        
        if total_after != 0:
            conn.rollback()
            cursor.close()
            conn.close()
            return {
                'statusCode': 500,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': f'Erreur: {total_after} comptes restants'
                })
            }
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.warning(f"TOUS LES COMPTES ONT ÉTÉ SUPPRIMÉS: {deleted_count} supprimés")
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'success': True,
                'message': 'Tous les comptes ont été supprimés avec succès',
                'deleted_count': deleted_count
            })
        }
        
    except Exception as e:
        logger.error(f"Erreur simple_delete_all: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': str(e)
            })
        }

