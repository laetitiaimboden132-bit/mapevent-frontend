"""
Backend Flask pour MapEventAI
API REST pour gérer les événements, bookings et services
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import psycopg2
import redis
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Crée et configure l'application Flask"""
    app = Flask(__name__)
    CORS(app)  # Permettre les requêtes cross-origin
    
    # Configuration depuis les variables d'environnement
    app.config['RDS_HOST'] = os.getenv('RDS_HOST', '')
    app.config['RDS_PORT'] = os.getenv('RDS_PORT', '5432')
    app.config['RDS_DB'] = os.getenv('RDS_DB', 'mapevent')
    app.config['RDS_USER'] = os.getenv('RDS_USER', '')
    app.config['RDS_PASSWORD'] = os.getenv('RDS_PASSWORD', '')
    
    app.config['REDIS_HOST'] = os.getenv('REDIS_HOST', '')
    app.config['REDIS_PORT'] = os.getenv('REDIS_PORT', '6379')
    
    # Connexions
    def get_db_connection():
        """Crée une connexion à PostgreSQL"""
        try:
            conn = psycopg2.connect(
                host=app.config['RDS_HOST'],
                port=app.config['RDS_PORT'],
                database=app.config['RDS_DB'],
                user=app.config['RDS_USER'],
                password=app.config['RDS_PASSWORD']
            )
            return conn
        except Exception as e:
            logger.error(f"Erreur connexion DB: {e}")
            return None
    
    def get_redis_connection():
        """Crée une connexion à Redis"""
        try:
            r = redis.Redis(
                host=app.config['REDIS_HOST'],
                port=int(app.config['REDIS_PORT']),
                decode_responses=True
            )
            r.ping()  # Tester la connexion
            return r
        except Exception as e:
            logger.error(f"Erreur connexion Redis: {e}")
            return None
    
    # Routes API
    
    @app.route('/api/health', methods=['GET'])
    def health():
        """Vérification de santé de l'API"""
        return jsonify({
            'status': 'ok',
            'timestamp': datetime.utcnow().isoformat()
        })
    
    @app.route('/api/events', methods=['GET'])
    def get_events():
        """Récupère tous les événements"""
        try:
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, title, description, location, latitude, longitude, 
                       date, time, categories, created_at
                FROM events
                ORDER BY created_at DESC
            """)
            
            events = []
            for row in cursor.fetchall():
                events.append({
                    'id': row[0],
                    'title': row[1],
                    'description': row[2],
                    'location': row[3],
                    'latitude': float(row[4]) if row[4] else None,
                    'longitude': float(row[5]) if row[5] else None,
                    'date': row[6].isoformat() if row[6] else None,
                    'time': str(row[7]) if row[7] else None,
                    'categories': row[8] if isinstance(row[8], list) else json.loads(row[8]) if row[8] else [],
                    'created_at': row[9].isoformat() if row[9] else None
                })
            
            cursor.close()
            conn.close()
            
            return jsonify(events)
        except Exception as e:
            logger.error(f"Erreur get_events: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/events/publish', methods=['POST'])
    def publish_event():
        """Publie un nouvel événement"""
        try:
            data = request.get_json()
            
            # Validation
            required_fields = ['title', 'location', 'latitude', 'longitude']
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'Missing field: {field}'}), 400
            
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO events (title, description, location, latitude, longitude, 
                                  date, time, categories, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                data.get('title'),
                data.get('description', ''),
                data.get('location'),
                float(data.get('latitude')),
                float(data.get('longitude')),
                data.get('date'),
                data.get('time'),
                json.dumps(data.get('categories', [])),
                datetime.utcnow()
            ))
            
            event_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()
            
            # Invalider le cache Redis
            redis_conn = get_redis_connection()
            if redis_conn:
                redis_conn.delete('events:all')
            
            return jsonify({'id': event_id, 'status': 'published'}), 201
        except Exception as e:
            logger.error(f"Erreur publish_event: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/bookings', methods=['GET'])
    def get_bookings():
        """Récupère tous les bookings"""
        try:
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, description, location, latitude, longitude, 
                       categories, created_at
                FROM bookings
                ORDER BY created_at DESC
            """)
            
            bookings = []
            for row in cursor.fetchall():
                bookings.append({
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'location': row[3],
                    'latitude': float(row[4]) if row[4] else None,
                    'longitude': float(row[5]) if row[5] else None,
                    'categories': row[6] if isinstance(row[6], list) else json.loads(row[6]) if row[6] else [],
                    'created_at': row[7].isoformat() if row[7] else None
                })
            
            cursor.close()
            conn.close()
            
            return jsonify(bookings)
        except Exception as e:
            logger.error(f"Erreur get_bookings: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/bookings/publish', methods=['POST'])
    def publish_booking():
        """Publie un nouveau booking"""
        try:
            data = request.get_json()
            
            # Validation
            required_fields = ['name', 'location', 'latitude', 'longitude']
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'Missing field: {field}'}), 400
            
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO bookings (name, description, location, latitude, longitude, 
                                     categories, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                data.get('name'),
                data.get('description', ''),
                data.get('location'),
                float(data.get('latitude')),
                float(data.get('longitude')),
                json.dumps(data.get('categories', [])),
                datetime.utcnow()
            ))
            
            booking_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()
            
            # Invalider le cache Redis
            redis_conn = get_redis_connection()
            if redis_conn:
                redis_conn.delete('bookings:all')
            
            return jsonify({'id': booking_id, 'status': 'published'}), 201
        except Exception as e:
            logger.error(f"Erreur publish_booking: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/services', methods=['GET'])
    def get_services():
        """Récupère tous les services"""
        try:
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, description, location, latitude, longitude, 
                       categories, created_at
                FROM services
                ORDER BY created_at DESC
            """)
            
            services = []
            for row in cursor.fetchall():
                services.append({
                    'id': row[0],
                    'name': row[1],
                    'description': row[2],
                    'location': row[3],
                    'latitude': float(row[4]) if row[4] else None,
                    'longitude': float(row[5]) if row[5] else None,
                    'categories': row[6] if isinstance(row[6], list) else json.loads(row[6]) if row[6] else [],
                    'created_at': row[7].isoformat() if row[7] else None
                })
            
            cursor.close()
            conn.close()
            
            return jsonify(services)
        except Exception as e:
            logger.error(f"Erreur get_services: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/services/publish', methods=['POST'])
    def publish_service():
        """Publie un nouveau service"""
        try:
            data = request.get_json()
            
            # Validation
            required_fields = ['name', 'location', 'latitude', 'longitude']
            for field in required_fields:
                if field not in data:
                    return jsonify({'error': f'Missing field: {field}'}), 400
            
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO services (name, description, location, latitude, longitude, 
                                     categories, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (
                data.get('name'),
                data.get('description', ''),
                data.get('location'),
                float(data.get('latitude')),
                float(data.get('longitude')),
                json.dumps(data.get('categories', [])),
                datetime.utcnow()
            ))
            
            service_id = cursor.fetchone()[0]
            conn.commit()
            cursor.close()
            conn.close()
            
            # Invalider le cache Redis
            redis_conn = get_redis_connection()
            if redis_conn:
                redis_conn.delete('services:all')
            
            return jsonify({'id': service_id, 'status': 'published'}), 201
        except Exception as e:
            logger.error(f"Erreur publish_service: {e}")
            return jsonify({'error': str(e)}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)


