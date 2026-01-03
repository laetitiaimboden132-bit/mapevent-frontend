"""
Routes d'administration temporaires pour créer les tables
⚠️ À SUPPRIMER APRÈS UTILISATION pour des raisons de sécurité
"""

from flask import jsonify
import psycopg2
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def create_admin_routes(app):
    """Ajoute les routes d'administration temporaires"""
    
    @app.route('/api/admin/create-database', methods=['POST'])
    def create_database():
        """
        Route temporaire pour créer la base de données mapevent
        ⚠️ À SUPPRIMER APRÈS UTILISATION
        """
        try:
            # Se connecter à la base par défaut 'postgres' pour créer une nouvelle base
            conn = psycopg2.connect(
                host=app.config['RDS_HOST'],
                port=app.config['RDS_PORT'],
                database='postgres',  # On se connecte à la base par défaut
                user=app.config['RDS_USER'],
                password=app.config['RDS_PASSWORD'],
                connect_timeout=10,
                sslmode='require'
            )
            
            # Mettre la connexion en mode autocommit pour créer la base
            conn.autocommit = True
            cursor = conn.cursor()
            
            db_name = app.config['RDS_DB'].strip()
            
            # Vérifier si la base existe déjà
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db_name,))
            exists = cursor.fetchone()
            
            if exists:
                logger.info(f"La base de données '{db_name}' existe déjà")
                cursor.close()
                conn.close()
                return jsonify({
                    'status': 'exists',
                    'message': f"La base de données '{db_name}' existe déjà"
                }), 200
            else:
                # Créer la base de données
                logger.info(f"Création de la base de données '{db_name}'...")
                cursor.execute(f'CREATE DATABASE "{db_name}";')
                cursor.close()
                conn.close()
                
                logger.info(f"Base de données '{db_name}' créée avec succès")
                return jsonify({
                    'status': 'success',
                    'message': f"Base de données '{db_name}' créée avec succès"
                }), 200
            
        except psycopg2.Error as e:
            logger.error(f"Erreur PostgreSQL: {e}")
            return jsonify({
                'error': 'Database error',
                'message': str(e)
            }), 500
        except Exception as e:
            logger.error(f"Erreur: {e}")
            return jsonify({
                'error': 'Unknown error',
                'message': str(e)
            }), 500
    
    @app.route('/api/admin/create-tables', methods=['POST'])
    def create_tables():
        """
        Route temporaire pour créer les tables en base de données
        ⚠️ À SUPPRIMER APRÈS UTILISATION
        """
        try:
            # Lire le fichier schema.sql
            schema_file = Path(__file__).parent / 'database' / 'schema.sql'
            if not schema_file.exists():
                return jsonify({'error': 'schema.sql not found'}), 500
            
            with open(schema_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # Se connecter à la base de données
            db_name = app.config['RDS_DB'].strip()  # Nettoyer les espaces
            conn = psycopg2.connect(
                host=app.config['RDS_HOST'],
                port=app.config['RDS_PORT'],
                database=db_name,
                user=app.config['RDS_USER'],
                password=app.config['RDS_PASSWORD'],
                connect_timeout=10,
                sslmode='require'  # RDS nécessite SSL
            )
            
            # Exécuter le script SQL
            cursor = conn.cursor()
            cursor.execute(sql_content)
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info("Tables créées avec succès via route admin")
            
            return jsonify({
                'status': 'success',
                'message': 'Tables créées avec succès',
                'tables': [
                    'events', 'bookings', 'services', 'users',
                    'user_likes', 'user_favorites', 'user_participations',
                    'user_agenda', 'user_reviews', 'user_reports', 'discussions'
                ]
            }), 200
            
        except psycopg2.Error as e:
            logger.error(f"Erreur PostgreSQL: {e}")
            return jsonify({
                'error': 'Database error',
                'message': str(e)
            }), 500
        except Exception as e:
            logger.error(f"Erreur: {e}")
            return jsonify({
                'error': 'Unknown error',
                'message': str(e)
            }), 500


