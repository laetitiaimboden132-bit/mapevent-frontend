"""
Endpoint Lambda temporaire pour exécuter du SQL directement
⚠️ À SUPPRIMER après utilisation pour des raisons de sécurité
"""
import os
import psycopg2
import json
import logging
from typing import Dict, Any

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Endpoint temporaire pour exécuter du SQL directement depuis Lambda.
    
    Usage:
    POST /api/admin/execute-sql
    Body: {
        "sql": "SELECT * FROM users;"
    }
    
    ⚠️ ATTENTION: Cet endpoint est temporaire et doit être supprimé après utilisation !
    """
    
    try:
        # Récupérer le SQL depuis le body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})
        
        sql_query = body.get('sql', '').strip()
        
        if not sql_query:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'SQL query is required',
                    'message': 'Veuillez fournir une requête SQL dans le champ "sql"'
                })
            }
        
        # Se connecter à la base de données
        db_config = {
            'host': os.environ.get('DB_HOST'),
            'port': int(os.environ.get('DB_PORT', 5432)),
            'database': os.environ.get('DB_NAME', 'postgres'),
            'user': os.environ.get('DB_USER', 'postgres'),
            'password': os.environ.get('DB_PASSWORD')
        }
        
        conn = psycopg2.connect(**db_config)
        cursor = conn.cursor()
        
        # Exécuter la requête
        try:
            cursor.execute(sql_query)
            
            # Si c'est une requête SELECT, récupérer les résultats
            if sql_query.upper().strip().startswith('SELECT'):
                columns = [desc[0] for desc in cursor.description] if cursor.description else []
                rows = cursor.fetchall()
                
                results = []
                for row in rows:
                    results.append(dict(zip(columns, row)))
                
                conn.commit()
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
                        'rows': results,
                        'count': len(results)
                    }, default=str)
                }
            else:
                # Pour INSERT, UPDATE, DELETE, etc.
                affected_rows = cursor.rowcount
                conn.commit()
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
                        'message': f'Query executed successfully',
                        'affected_rows': affected_rows
                    })
                }
        
        except Exception as query_error:
            conn.rollback()
            cursor.close()
            conn.close()
            
            logger.error(f"SQL Error: {str(query_error)}")
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'SQL execution failed',
                    'message': str(query_error)
                })
            }
    
    except psycopg2.Error as db_error:
        logger.error(f"Database connection error: {str(db_error)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Database connection failed',
                'message': str(db_error)
            })
        }
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }

