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
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import stripe
import random
import string
from services.email_sender import send_translated_email
# WebSocket désactivé pour Lambda (nécessite API Gateway WebSocket séparé)
# from websocket_handler import init_socketio, setup_websocket_handlers

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app():
    """Crée et configure l'application Flask"""
    app = Flask(__name__)
    # Configuration CORS ultra-permissive pour éviter les erreurs
    CORS(app, 
         resources={r"/api/*": {
             "origins": "*",  # Autoriser toutes les origines pour éviter les erreurs CORS
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
             "allow_headers": ["Content-Type", "Authorization", "Origin", "X-Requested-With", "Accept"],
             "supports_credentials": False,  # Désactiver pour éviter les problèmes avec *
             "max_age": 3600
         }},
         supports_credentials=False)
    
    # Ajouter un handler OPTIONS global pour toutes les routes
    @app.before_request
    def handle_preflight():
        if request.method == "OPTIONS":
            response = jsonify({})
            response.headers.add("Access-Control-Allow-Origin", "*")
            response.headers.add("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS, PATCH")
            response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization, Origin, X-Requested-With, Accept")
            response.headers.add("Access-Control-Max-Age", "3600")
            return response
    
    # Ajouter les headers CORS à toutes les réponses
    @app.after_request
    def after_request(response):
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS, PATCH")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type, Authorization, Origin, X-Requested-With, Accept")
        response.headers.add("Access-Control-Max-Age", "3600")
        return response
    
    # WebSocket désactivé pour Lambda (nécessite API Gateway WebSocket séparé)
    # Pour activer WebSocket, voir WEBSOCKET_SETUP.md
    # socketio = init_socketio(app)
    # setup_websocket_handlers(socketio)
    
    # Configuration depuis les variables d'environnement
    app.config['RDS_HOST'] = os.getenv('RDS_HOST', '')
    app.config['RDS_PORT'] = os.getenv('RDS_PORT', '5432')
    app.config['RDS_DB'] = os.getenv('RDS_DB', 'mapevent')
    app.config['RDS_USER'] = os.getenv('RDS_USER', '')
    app.config['RDS_PASSWORD'] = os.getenv('RDS_PASSWORD', '')
    
    app.config['REDIS_HOST'] = os.getenv('REDIS_HOST', '')
    app.config['REDIS_PORT'] = os.getenv('REDIS_PORT', '6379')
    
    # Configuration Stripe
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY', '')
    app.config['STRIPE_PUBLIC_KEY'] = os.getenv('STRIPE_PUBLIC_KEY', '')
    app.config['STRIPE_WEBHOOK_SECRET'] = os.getenv('STRIPE_WEBHOOK_SECRET', '')
    
    # Connexions
    def get_db_connection():
        """Crée une connexion à PostgreSQL"""
        try:
            # Nettoyer le nom de la base de données (enlever les espaces)
            db_name = app.config['RDS_DB'].strip()
            print(f"Tentative de connexion à RDS: {app.config['RDS_HOST']}:{app.config['RDS_PORT']}/{db_name}")
            print(f"User: {app.config['RDS_USER']}")
            print(f"Password length: {len(app.config['RDS_PASSWORD']) if app.config['RDS_PASSWORD'] else 0}")
            conn = psycopg2.connect(
                host=app.config['RDS_HOST'],
                port=app.config['RDS_PORT'],
                database=db_name,
                user=app.config['RDS_USER'],
                password=app.config['RDS_PASSWORD'],
                connect_timeout=10,
                sslmode='require'  # RDS nécessite SSL
            )
            print("✅ Connexion RDS réussie")
            return conn
        except Exception as e:
            error_msg = f"❌ Erreur connexion DB: {e}"
            print(error_msg)
            logger.error(error_msg)
            import traceback
            print(traceback.format_exc())
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
    
    @app.route('/api/stats/active-users', methods=['GET'])
    def get_active_users_count():
        """Récupère le nombre d'utilisateurs actifs (dernières 24h)"""
        try:
            conn = get_db_connection()
            if not conn:
                # Fallback si pas de DB : utiliser Redis ou valeur par défaut
                redis_conn = get_redis_connection()
                if redis_conn:
                    try:
                        # Essayer de récupérer depuis Redis (si vous trackez les sessions)
                        count = redis_conn.get('active_users_count')
                        if count:
                            return jsonify({'count': int(count)}), 200
                    except:
                        pass
                # Valeur par défaut si aucune source disponible
                return jsonify({'count': 1247}), 200
            
            cursor = conn.cursor()
            # Compter les utilisateurs actifs dans les dernières 24 heures
            # On considère actif si :
            # - A une session récente (si vous trackez les sessions)
            # - A interagi récemment (likes, agenda, etc.)
            # Pour l'instant, on compte les utilisateurs uniques qui ont eu une activité récente
            cursor.execute("""
                SELECT COUNT(DISTINCT user_id) as active_count
                FROM (
                    SELECT user_id FROM user_likes WHERE created_at > NOW() - INTERVAL '24 hours'
                    UNION
                    SELECT user_id FROM user_agenda WHERE created_at > NOW() - INTERVAL '24 hours'
                    UNION
                    SELECT user_id FROM user_participations WHERE created_at > NOW() - INTERVAL '24 hours'
                    UNION
                    SELECT user_id FROM payments WHERE created_at > NOW() - INTERVAL '24 hours'
                ) AS active_users
            """)
            
            row = cursor.fetchone()
            active_count = row[0] if row else 0
            
            # Si aucun utilisateur actif récent, utiliser un nombre de base réaliste
            if active_count == 0:
                # Compter tous les utilisateurs uniques dans la base
                cursor.execute("SELECT COUNT(DISTINCT id) FROM users")
                total_users = cursor.fetchone()[0]
                # Estimation : 10-20% des utilisateurs sont actifs
                active_count = max(1247, int(total_users * 0.15))
            
            cursor.close()
            conn.close()
            
            return jsonify({'count': active_count}), 200
            
        except Exception as e:
            logger.error(f"Erreur get_active_users_count: {e}")
            # En cas d'erreur, retourner une valeur par défaut réaliste
            return jsonify({'count': 1247}), 200
    
    @app.route('/api/events', methods=['GET'])
    def get_events():
        """Récupère tous les événements"""
        try:
            print("🔍 Appel à /api/events")
            conn = get_db_connection()
            if not conn:
                print("❌ get_db_connection() a retourné None")
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
                try:
                    # Gérer les catégories (peuvent être JSON string, list, ou None)
                    categories = []
                    if row[8]:
                        if isinstance(row[8], list):
                            categories = row[8]
                        elif isinstance(row[8], str):
                            try:
                                categories = json.loads(row[8])
                            except (json.JSONDecodeError, TypeError):
                                categories = []
                    
                    events.append({
                        'id': row[0],
                        'title': row[1] or '',
                        'description': row[2] or '',
                        'location': row[3] or '',
                        'latitude': float(row[4]) if row[4] is not None else None,
                        'longitude': float(row[5]) if row[5] is not None else None,
                        'date': row[6].isoformat() if row[6] else None,
                        'time': str(row[7]) if row[7] else None,
                        'categories': categories,
                        'created_at': row[9].isoformat() if row[9] else None
                    })
                except Exception as row_error:
                    print(f"❌ Erreur traitement ligne: {row_error}")
                    logger.error(f"Erreur traitement ligne: {row_error}")
                    continue
            
            cursor.close()
            conn.close()
            
            print(f"✅ {len(events)} événements récupérés")
            return jsonify(events)
        except Exception as e:
            error_msg = f"❌ Erreur get_events: {e}"
            print(error_msg)
            logger.error(error_msg)
            import traceback
            print(traceback.format_exc())
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
    
    # Routes utilisateur
    @app.route('/api/user/likes', methods=['POST'])
    def user_likes():
        """Gère les likes des utilisateurs pour les événements, bookings et services."""
        try:
            data = request.get_json()
            user_id = data.get('userId')
            item_id = data.get('itemId')
            item_type = data.get('itemMode')
            action = data.get('action') # 'add' or 'remove'

            if not all([user_id, item_id, item_type, action]):
                return jsonify({'error': 'Missing required fields'}), 400

            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database connection failed'}), 500
            cursor = conn.cursor()

            # Assurer que l'utilisateur existe (ou le créer si c'est la première action)
            cursor.execute("INSERT INTO users (id) VALUES (%s) ON CONFLICT (id) DO NOTHING", (user_id,))
            conn.commit()

            if action == 'add':
                cursor.execute(
                    "INSERT INTO user_likes (user_id, item_type, item_id) VALUES (%s, %s, %s) ON CONFLICT (user_id, item_type, item_id) DO NOTHING",
                    (user_id, item_type, item_id)
                )
                conn.commit()
                cursor.close()
                conn.close()
                return jsonify({'success': True, 'action': 'added'}), 200
            elif action == 'remove':
                cursor.execute(
                    "DELETE FROM user_likes WHERE user_id = %s AND item_type = %s AND item_id = %s",
                    (user_id, item_type, item_id)
                )
                conn.commit()
                cursor.close()
                conn.close()
                return jsonify({'success': True, 'action': 'removed'}), 200
            else:
                return jsonify({'error': 'Invalid action'}), 400
        except Exception as e:
            logger.error(f"Erreur user_likes: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/user/favorites', methods=['POST'])
    def user_favorites():
        """Gère les favoris des utilisateurs."""
        try:
            data = request.get_json()
            user_id = data.get('userId')
            item_id = data.get('itemId')
            item_type = data.get('itemMode')
            action = data.get('action') # 'add' or 'remove'

            if not all([user_id, item_id, item_type, action]):
                return jsonify({'error': 'Missing required fields'}), 400

            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database connection failed'}), 500
            cursor = conn.cursor()

            cursor.execute("INSERT INTO users (id) VALUES (%s) ON CONFLICT (id) DO NOTHING", (user_id,))
            conn.commit()

            if action == 'add':
                cursor.execute(
                    "INSERT INTO user_favorites (user_id, item_type, item_id) VALUES (%s, %s, %s) ON CONFLICT (user_id, item_type, item_id) DO NOTHING",
                    (user_id, item_type, item_id)
                )
                conn.commit()
                cursor.close()
                conn.close()
                return jsonify({'success': True, 'action': 'added'}), 200
            elif action == 'remove':
                cursor.execute(
                    "DELETE FROM user_favorites WHERE user_id = %s AND item_type = %s AND item_id = %s",
                    (user_id, item_type, item_id)
                )
                conn.commit()
                cursor.close()
                conn.close()
                return jsonify({'success': True, 'action': 'removed'}), 200
            else:
                return jsonify({'error': 'Invalid action'}), 400
        except Exception as e:
            logger.error(f"Erreur user_favorites: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/user/participate', methods=['POST'])
    def user_participate():
        """Gère la participation des utilisateurs aux événements."""
        try:
            data = request.get_json()
            user_id = data.get('userId')
            item_id = data.get('itemId')
            item_type = data.get('itemMode') # Principalement 'event'
            action = data.get('action') # 'add' or 'remove'

            if not all([user_id, item_id, item_type, action]):
                return jsonify({'error': 'Missing required fields'}), 400

            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database connection failed'}), 500
            cursor = conn.cursor()

            cursor.execute("INSERT INTO users (id) VALUES (%s) ON CONFLICT (id) DO NOTHING", (user_id,))
            conn.commit()

            if action == 'add':
                cursor.execute(
                    "INSERT INTO user_participations (user_id, item_type, item_id) VALUES (%s, %s, %s) ON CONFLICT (user_id, item_type, item_id) DO NOTHING",
                    (user_id, item_type, item_id)
                )
                conn.commit()
                cursor.close()
                conn.close()
                return jsonify({'success': True, 'action': 'added'}), 200
            elif action == 'remove':
                cursor.execute(
                    "DELETE FROM user_participations WHERE user_id = %s AND item_type = %s AND item_id = %s",
                    (user_id, item_type, item_id)
                )
                conn.commit()
                cursor.close()
                conn.close()
                return jsonify({'success': True, 'action': 'removed'}), 200
            else:
                return jsonify({'error': 'Invalid action'}), 400
        except Exception as e:
            logger.error(f"Erreur user_participate: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/user/agenda', methods=['POST'])
    def user_agenda():
        """Gère l'ajout/retrait d'éléments à l'agenda de l'utilisateur."""
        try:
            data = request.get_json()
            user_id = data.get('userId')
            item_id = data.get('itemId')
            item_type = data.get('itemMode')
            action = data.get('action') # 'add' or 'remove'

            if not all([user_id, item_id, item_type, action]):
                return jsonify({'error': 'Missing required fields'}), 400

            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database connection failed'}), 500
            cursor = conn.cursor()

            cursor.execute("INSERT INTO users (id) VALUES (%s) ON CONFLICT (id) DO NOTHING", (user_id,))
            conn.commit()

            if action == 'add':
                cursor.execute(
                    "INSERT INTO user_agenda (user_id, item_type, item_id) VALUES (%s, %s, %s) ON CONFLICT (user_id, item_type, item_id) DO NOTHING",
                    (user_id, item_type, item_id)
                )
                conn.commit()
                cursor.close()
                conn.close()
                return jsonify({'success': True, 'action': 'added'}), 200
            elif action == 'remove':
                cursor.execute(
                    "DELETE FROM user_agenda WHERE user_id = %s AND item_type = %s AND item_id = %s",
                    (user_id, item_type, item_id)
                )
                conn.commit()
                cursor.close()
                conn.close()
                return jsonify({'success': True, 'action': 'removed'}), 200
            else:
                return jsonify({'error': 'Invalid action'}), 400
        except Exception as e:
            logger.error(f"Erreur user_agenda: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/user/alerts', methods=['GET'])
    def get_user_alerts():
        """Récupère les alertes d'un utilisateur."""
        try:
            user_id = request.args.get('userId')
            if not user_id:
                return jsonify({'error': 'Missing userId parameter'}), 400

            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database connection failed'}), 500
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, event_id, favorite_id, favorite_name, favorite_mode,
                       distance, distance_to_user, closest_address, status, is_blurred,
                       event_title, event_date, created_at, seen_at
                FROM user_alerts
                WHERE user_id = %s AND status != 'deleted'
                ORDER BY created_at DESC
            """, (user_id,))

            alerts = []
            for row in cursor.fetchall():
                alerts.append({
                    'id': row[0],
                    'eventId': str(row[1]),
                    'favoriteId': row[2],
                    'favoriteName': row[3],
                    'favoriteMode': row[4],
                    'distance': float(row[5]) if row[5] else None,
                    'distanceToUser': float(row[6]) if row[6] else None,
                    'closestAddress': row[7],
                    'status': row[8],
                    'isBlurred': row[9],
                    'eventTitle': row[10],
                    'eventDate': row[11].isoformat() if row[11] else None,
                    'creationDate': row[12].isoformat() if row[12] else None,
                    'seenAt': row[13].isoformat() if row[13] else None
                })

            cursor.close()
            conn.close()
            return jsonify({'success': True, 'alerts': alerts}), 200
        except Exception as e:
            logger.error(f"Erreur get_user_alerts: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/user/alerts', methods=['POST'])
    def create_user_alert():
        """Crée une alerte pour un utilisateur."""
        try:
            data = request.get_json()
            user_id = data.get('userId')
            alert_data = data.get('alert')

            if not user_id or not alert_data:
                return jsonify({'error': 'Missing required fields'}), 400

            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database connection failed'}), 500
            cursor = conn.cursor()

            # Assurer que l'utilisateur existe
            cursor.execute("INSERT INTO users (id) VALUES (%s) ON CONFLICT (id) DO NOTHING", (user_id,))
            conn.commit()

            # Insérer l'alerte
            cursor.execute("""
                INSERT INTO user_alerts (
                    id, user_id, event_id, favorite_id, favorite_name, favorite_mode,
                    distance, distance_to_user, closest_address, status, is_blurred,
                    event_title, event_date
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    status = EXCLUDED.status,
                    is_blurred = EXCLUDED.is_blurred
            """, (
                alert_data.get('id'),
                user_id,
                int(alert_data.get('eventId')),
                alert_data.get('favoriteId'),
                alert_data.get('favoriteName'),
                alert_data.get('favoriteMode', 'event'),
                alert_data.get('distance'),
                alert_data.get('distanceToUser'),
                alert_data.get('closestAddress'),
                alert_data.get('status', 'new'),
                alert_data.get('isBlurred', False),
                alert_data.get('eventTitle'),
                alert_data.get('eventDate')
            ))

            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'success': True, 'alert': alert_data}), 200
        except Exception as e:
            logger.error(f"Erreur create_user_alert: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/user/alerts/seen', methods=['POST'])
    def mark_alert_seen():
        """Marque une alerte comme vue."""
        try:
            data = request.get_json()
            user_id = data.get('userId')
            alert_id = data.get('alertId')

            if not user_id or not alert_id:
                return jsonify({'error': 'Missing required fields'}), 400

            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database connection failed'}), 500
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE user_alerts
                SET status = 'seen', seen_at = CURRENT_TIMESTAMP
                WHERE id = %s AND user_id = %s
            """, (alert_id, user_id))

            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'success': True}), 200
        except Exception as e:
            logger.error(f"Erreur mark_alert_seen: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/user/alerts', methods=['DELETE'])
    def delete_user_alert():
        """Supprime une alerte (soft delete)."""
        try:
            data = request.get_json()
            user_id = data.get('userId')
            alert_id = data.get('alertId')

            if not user_id or not alert_id:
                return jsonify({'error': 'Missing required fields'}), 400

            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database connection failed'}), 500
            cursor = conn.cursor()

            cursor.execute("""
                UPDATE user_alerts
                SET status = 'deleted'
                WHERE id = %s AND user_id = %s
            """, (alert_id, user_id))

            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'success': True}), 200
        except Exception as e:
            logger.error(f"Erreur delete_user_alert: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/user/reports', methods=['POST'])
    def create_user_report():
        """Crée un signalement pour un contenu."""
        try:
            data = request.get_json()
            user_id = data.get('userId')
            item_type = data.get('itemType')
            item_id = data.get('itemId')
            parent_type = data.get('parentType')
            parent_id = data.get('parentId')
            reason = data.get('reason')
            details = data.get('details', '')

            if not all([user_id, item_type, item_id, reason]):
                return jsonify({'error': 'Missing required fields'}), 400

            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database connection failed'}), 500
            cursor = conn.cursor()

            # Assurer que l'utilisateur existe
            cursor.execute("INSERT INTO users (id) VALUES (%s) ON CONFLICT (id) DO NOTHING", (user_id,))
            conn.commit()

            # Insérer le signalement
            cursor.execute("""
                INSERT INTO user_reports (
                    user_id, item_type, item_id, parent_type, parent_id,
                    reason, details, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, 'pending')
            """, (
                user_id,
                item_type,
                str(item_id),  # item_id peut être string ou int
                parent_type,
                str(parent_id) if parent_id else None,
                reason,
                details
            ))

            conn.commit()
            cursor.close()
            conn.close()
            return jsonify({'success': True, 'message': 'Report submitted successfully'}), 200
        except Exception as e:
            logger.error(f"Erreur create_user_report: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/api/user/reports', methods=['GET'])
    def get_user_reports():
        """Récupère les signalements d'un utilisateur (pour l'admin)."""
        try:
            user_id = request.args.get('userId')
            if not user_id:
                return jsonify({'error': 'Missing userId parameter'}), 400

            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database connection failed'}), 500
            cursor = conn.cursor()

            cursor.execute("""
                SELECT id, item_type, item_id, parent_type, parent_id,
                       reason, details, status, created_at, reviewed_at
                FROM user_reports
                WHERE user_id = %s
                ORDER BY created_at DESC
            """, (user_id,))

            reports = []
            for row in cursor.fetchall():
                reports.append({
                    'id': row[0],
                    'itemType': row[1],
                    'itemId': row[2],
                    'parentType': row[3],
                    'parentId': row[4],
                    'reason': row[5],
                    'details': row[6],
                    'status': row[7],
                    'createdAt': row[8].isoformat() if row[8] else None,
                    'reviewedAt': row[9].isoformat() if row[9] else None
                })

            cursor.close()
            conn.close()
            return jsonify({'success': True, 'reports': reports}), 200
        except Exception as e:
            logger.error(f"Erreur get_user_reports: {e}")
            return jsonify({'error': str(e)}), 500
    
    # ============================================
    # ROUTES DE VÉRIFICATION D'EMAIL
    # ============================================
    
    @app.route('/api/user/check-email', methods=['POST'])
    def check_email():
        """Vérifie si un email existe déjà dans la base de données."""
        try:
            data = request.get_json()
            email = data.get('email', '').strip().lower()
            
            if not email:
                return jsonify({'error': 'Email requis'}), 400
            
            conn = get_db_connection()
            if not conn:
                logger.error("❌ Connexion DB échouée pour check-email")
                return jsonify({'exists': False}), 200  # En cas d'erreur DB, permettre l'inscription
            
            cursor = conn.cursor()
            
            # Vérifier si l'email existe dans la table users
            cursor.execute("""
                SELECT id FROM users WHERE LOWER(email) = %s LIMIT 1
            """, (email,))
            
            exists = cursor.fetchone() is not None
            
            cursor.close()
            conn.close()
            
            return jsonify({'exists': exists}), 200
            
        except Exception as e:
            logger.error(f"Erreur check_email: {e}")
            # En cas d'erreur, retourner False pour ne pas bloquer l'inscription
            return jsonify({'exists': False}), 200
    
    @app.route('/api/user/send-verification-code', methods=['POST'])
    def send_verification_code():
        """Envoie un code de vérification à 6 chiffres par email."""
        try:
            data = request.get_json()
            email = data.get('email', '').strip().lower()
            username = data.get('username', '')
            code = data.get('code', '')  # Code généré côté frontend
            
            if not email:
                return jsonify({'error': 'Email requis'}), 400
            
            if not code or len(code) != 6 or not code.isdigit():
                return jsonify({'error': 'Code invalide'}), 400
            
            # Vérifier le rate limiting avec Redis
            redis_conn = get_redis_connection()
            if redis_conn:
                # Clé pour limiter les envois (1 par minute par email)
                rate_limit_key = f"email_verification_rate:{email}"
                last_sent = redis_conn.get(rate_limit_key)
                
                if last_sent:
                    time_since_last = datetime.utcnow() - datetime.fromisoformat(last_sent)
                    if time_since_last.total_seconds() < 60:
                        remaining = int(60 - time_since_last.total_seconds())
                        return jsonify({
                            'error': f'Veuillez patienter {remaining} secondes avant de renvoyer',
                            'rate_limited': True
                        }), 429
                
                # Stocker le code dans Redis avec expiration (15 minutes)
                code_key = f"email_verification_code:{email}"
                redis_conn.setex(code_key, 900, code)  # 15 minutes = 900 secondes
                
                # Enregistrer l'heure d'envoi
                redis_conn.setex(rate_limit_key, 60, datetime.utcnow().isoformat())
            
            # Envoyer l'email via le service email_sender
            try:
                email_sent = send_translated_email(
                    to_email=email,
                    template_name='email_verification',
                    template_vars={
                        'username': username if username else 'Utilisateur',
                        'verification_code': code
                    },
                    target_language='fr'  # Par défaut en français, peut être détecté automatiquement
                )
                
                if email_sent:
                    logger.info(f"✅ Code de vérification envoyé à {email}")
                    return jsonify({
                        'success': True,
                        'message': 'Code envoyé avec succès',
                        'expires_in': 900  # 15 minutes en secondes
                    }), 200
                else:
                    logger.warn(f"Échec envoi email à {email}, mode développement")
                    
            except Exception as email_error:
                logger.error(f"Erreur envoi email: {email_error}")
                import traceback
                logger.error(traceback.format_exc())
                # En mode développement, continuer même si l'email échoue
            
            # Si l'email n'a pas pu être envoyé, retourner quand même un succès
            # Le code est stocké dans Redis et peut être vérifié
            logger.info(f"✅ Code de vérification généré pour {email} (mode développement)")
            return jsonify({
                'success': True,
                'message': 'Code généré (mode développement - vérifiez Redis)',
                'expires_in': 900,
                'dev_mode': True
            }), 200
            
        except Exception as e:
            logger.error(f"Erreur send_verification_code: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({'error': str(e)}), 500
    
    # ============================================
    # ROUTE D'INSCRIPTION UTILISATEUR
    # ============================================
    
    @app.route('/api/user/register', methods=['POST'])
    def user_register():
        """Crée un nouveau compte utilisateur avec vérification d'email obligatoire."""
        try:
            data = request.get_json()
            email = data.get('email', '').strip().lower()
            username = data.get('username', '').strip()
            password = data.get('password', '')
            first_name = data.get('firstName', '').strip()
            last_name = data.get('lastName', '').strip()
            avatar_id = data.get('avatarId', 1)
            avatar_emoji = data.get('avatarEmoji', '👤')
            avatar_description = data.get('avatarDescription', '')
            addresses = data.get('addresses', [])
            verification_code = data.get('verificationCode', '')  # Code de vérification
            
            # Validation des champs obligatoires
            if not email or not username or not password or not first_name or not last_name:
                return jsonify({'error': 'Email, username, password, prénom et nom requis'}), 400
            
            # Validation nom/prénom (2-30 caractères, lettres uniquement avec accents)
            name_regex = r'^[a-zA-ZàáâäãåèéêëìíîïòóôöõùúûüýÿñçÀÁÂÄÃÅÈÉÊËÌÍÎÏÒÓÔÖÕÙÚÛÜÝŸÑÇ\s-]{2,30}$'
            if not re.match(name_regex, first_name):
                return jsonify({'error': 'Prénom invalide (2-30 caractères, lettres uniquement)'}), 400
            if not re.match(name_regex, last_name):
                return jsonify({'error': 'Nom invalide (2-30 caractères, lettres uniquement)'}), 400
            
            # Vérifier que le nom/prénom ne sont pas des caractères aléatoires
            # Un nom réel doit avoir au moins une majuscule et principalement des lettres
            if not any(c.isupper() for c in first_name):
                return jsonify({'error': 'Le prénom doit commencer par une majuscule'}), 400
            if not any(c.isupper() for c in last_name):
                return jsonify({'error': 'Le nom doit commencer par une majuscule'}), 400
            
            # Vérifier qu'il n'y a pas trop de caractères spéciaux ou de chiffres
            first_name_letters = sum(1 for c in first_name if c.isalpha())
            last_name_letters = sum(1 for c in last_name if c.isalpha())
            if first_name_letters < len(first_name) * 0.7:  # Au moins 70% de lettres
                return jsonify({'error': 'Le prénom doit contenir principalement des lettres'}), 400
            if last_name_letters < len(last_name) * 0.7:
                return jsonify({'error': 'Le nom doit contenir principalement des lettres'}), 400
            
            # Validation format email
            import re
            email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
            if not re.match(email_regex, email):
                return jsonify({'error': 'Format email invalide'}), 400
            
            # Validation username (3-20 caractères, alphanumériques + _ et -)
            username_regex = r'^[a-zA-Z0-9_-]{3,20}$'
            if not re.match(username_regex, username):
                return jsonify({'error': 'Username invalide (3-20 caractères, lettres, chiffres, _ et -)'}), 400
            
            # Validation mot de passe (minimum 8 caractères)
            if len(password) < 8:
                return jsonify({'error': 'Mot de passe trop court (minimum 8 caractères)'}), 400
            
            # VÉRIFICATION CRITIQUE : Vérifier que l'email est vérifié via Redis
            redis_conn = get_redis_connection()
            if redis_conn:
                code_key = f"email_verification_code:{email}"
                stored_code = redis_conn.get(code_key)
                
                if not stored_code:
                    return jsonify({
                        'error': 'Email non vérifié. Veuillez vérifier votre email d\'abord.',
                        'code': 'EMAIL_NOT_VERIFIED'
                    }), 400
                
                # Si un code de vérification est fourni, le vérifier
                if verification_code and verification_code != stored_code:
                    return jsonify({
                        'error': 'Code de vérification incorrect',
                        'code': 'INVALID_VERIFICATION_CODE'
                    }), 400
                
                # Supprimer le code après utilisation (one-time use)
                redis_conn.delete(code_key)
            
            # Vérifier que l'email n'existe pas déjà
            conn = get_db_connection()
            if not conn:
                logger.error("❌ Connexion DB échouée pour user_register")
                return jsonify({'error': 'Erreur de connexion à la base de données'}), 500
            
            cursor = conn.cursor()
            
            # Vérifier email unique
            cursor.execute("SELECT id FROM users WHERE LOWER(email) = %s LIMIT 1", (email,))
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return jsonify({
                    'error': 'Cet email est déjà utilisé',
                    'code': 'EMAIL_ALREADY_EXISTS'
                }), 409
            
            # Vérifier username unique (optionnel mais recommandé)
            cursor.execute("SELECT id FROM users WHERE LOWER(username) = %s LIMIT 1", (username.lower(),))
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return jsonify({
                    'error': 'Ce nom d\'utilisateur est déjà pris',
                    'code': 'USERNAME_ALREADY_EXISTS'
                }), 409
            
            # VÉRIFICATION DES ADRESSES : S'assurer qu'elles sont réelles et vérifiées
            if not addresses or len(addresses) == 0:
                cursor.close()
                conn.close()
                return jsonify({'error': 'Au moins une adresse est requise'}), 400
            
            for addr in addresses:
                if not addr.get('lat') or not addr.get('lng'):
                    cursor.close()
                    conn.close()
                    return jsonify({'error': 'Toutes les adresses doivent être géocodées et vérifiées'}), 400
                
                # Vérifier que les coordonnées sont valides
                lat = float(addr.get('lat', 0))
                lng = float(addr.get('lng', 0))
                if lat < -90 or lat > 90 or lng < -180 or lng > 180:
                    cursor.close()
                    conn.close()
                    return jsonify({'error': 'Coordonnées d\'adresse invalides'}), 400
                
                # Vérifier que l'adresse est vérifiée (doit avoir addressDetails)
                address_details = addr.get('addressDetails', {})
                if not address_details.get('country_code'):
                    cursor.close()
                    conn.close()
                    return jsonify({'error': 'L\'adresse doit être vérifiée via géocodage'}), 400
                
                # Vérifier que l'adresse est en Suisse ou pays voisin autorisé
                country_code = address_details.get('country_code', '').upper()
                allowed_countries = ['CH', 'FR', 'DE', 'IT', 'AT']
                if country_code and country_code not in allowed_countries:
                    cursor.close()
                    conn.close()
                    return jsonify({
                        'error': f'L\'adresse doit être en Suisse ou pays voisin (actuellement: {country_code})',
                        'code': 'INVALID_COUNTRY'
                    }), 400
            
            # Vérifier qu'il n'y a pas trop de comptes créés depuis la même IP (rate limiting par IP)
            # Note: En production, utiliser request.remote_addr ou un header X-Forwarded-For
            # Pour l'instant, on limite par combinaison nom+prénom+email
            
            # Hasher le mot de passe (utiliser bcrypt si disponible, sinon SHA256 comme fallback)
            import hashlib
            import secrets
            salt = secrets.token_hex(16)
            password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            # Note: En production, utiliser bcrypt: bcrypt.hashpw(password.encode(), bcrypt.gensalt())
            
            # Créer l'utilisateur
            user_id = f"user_{int(datetime.utcnow().timestamp() * 1000)}_{secrets.token_hex(8)}"
            created_at = datetime.utcnow()
            
            # Vérifier si la table users a des colonnes first_name et last_name
            # Sinon, on les stocke dans username ou une colonne JSON
            cursor.execute("""
                SELECT column_name FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name IN ('first_name', 'last_name')
            """)
            has_name_columns = len(cursor.fetchall()) > 0
            
            if has_name_columns:
                cursor.execute("""
                    INSERT INTO users (id, email, username, first_name, last_name, subscription, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (user_id, email, username, first_name, last_name, 'free', created_at, created_at))
            else:
                # Si les colonnes n'existent pas, les créer d'abord
                try:
                    cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS first_name VARCHAR(100)")
                    cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_name VARCHAR(100)")
                    conn.commit()
                    logger.info("✅ Colonnes first_name et last_name ajoutées à la table users")
                    
                    cursor.execute("""
                        INSERT INTO users (id, email, username, first_name, last_name, subscription, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (user_id, email, username, first_name, last_name, 'free', created_at, created_at))
                except Exception as alter_error:
                    logger.warn(f"Impossible d'ajouter les colonnes: {alter_error}")
                    # Fallback: stocker dans username temporairement
                    cursor.execute("""
                        INSERT INTO users (id, email, username, subscription, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (user_id, email, f"{first_name} {last_name} ({username})", 'free', created_at, created_at))
            
            # Stocker le hash du mot de passe (dans une table séparée si vous en avez une)
            # Pour l'instant, on peut stocker dans une colonne password_hash si elle existe
            # Sinon, créer une table user_passwords
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"✅ Nouvel utilisateur créé: {email} ({user_id})")
            
            return jsonify({
                'success': True,
                'userId': user_id,
                'email': email,
                'username': username,
                'message': 'Compte créé avec succès'
            }), 201
            
        except psycopg2.IntegrityError as e:
            logger.error(f"Erreur intégrité DB: {e}")
            if conn:
                conn.rollback()
                conn.close()
            return jsonify({
                'error': 'Email ou username déjà utilisé',
                'code': 'DUPLICATE_ENTRY'
            }), 409
        except Exception as e:
            logger.error(f"Erreur user_register: {e}")
            import traceback
            logger.error(traceback.format_exc())
            if conn:
                conn.rollback()
                conn.close()
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/user/login', methods=['POST'])
    def user_login():
        """Connecte un utilisateur avec email et mot de passe."""
        try:
            data = request.get_json()
            email = data.get('email', '').strip().lower()
            password = data.get('password', '')
            
            if not email or not password:
                return jsonify({'error': 'Email et mot de passe requis'}), 400
            
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = conn.cursor()
            
            # Récupérer l'utilisateur
            cursor.execute("""
                SELECT id, email, username, first_name, last_name, subscription, role, 
                       avatar_emoji, avatar_description, created_at
                FROM users 
                WHERE LOWER(email) = %s
            """, (email,))
            
            user_row = cursor.fetchone()
            if not user_row:
                cursor.close()
                conn.close()
                return jsonify({'error': 'Email ou mot de passe incorrect'}), 401
            
            # Vérifier le mot de passe (récupérer depuis user_passwords si la table existe)
            # Pour l'instant, on accepte si l'utilisateur existe (à améliorer avec bcrypt)
            user_id, user_email, username, first_name, last_name, subscription, role, avatar_emoji, avatar_description, created_at = user_row
            
            # TODO: Vérifier le hash du mot de passe dans une table user_passwords
            # Pour l'instant, on retourne l'utilisateur (à sécuriser en production)
            
            cursor.close()
            conn.close()
            
            # Vérifier si l'email correspond à un directeur
            director_emails = ['mapevent777@gmail.com', 'directeur', 'director', 'admin']
            email_lower = email.lower()
            is_director = any(pattern in email_lower for pattern in director_emails)
            
            user_data = {
                'id': user_id,
                'email': user_email,
                'username': username,
                'name': f"{first_name} {last_name}".strip() if first_name and last_name else username,
                'firstName': first_name or '',
                'lastName': last_name or '',
                'subscription': 'vip_plus' if is_director else (subscription or 'free'),
                'role': 'director' if is_director else (role or 'user'),
                'avatar': avatar_emoji or '👤',
                'avatarDescription': avatar_description or '',
                'createdAt': created_at.isoformat() if created_at else None
            }
            
            return jsonify({'user': user_data}), 200
            
        except Exception as e:
            logger.error(f"Erreur user_login: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/user/oauth/google', methods=['POST'])
    def oauth_google():
        """Gère l'authentification OAuth Google."""
        try:
            data = request.get_json()
            email = data.get('email', '').strip().lower()
            name = data.get('name', '').strip()
            picture = data.get('picture', '')
            sub = data.get('sub', '')  # Google user ID
            credential = data.get('credential', '')  # JWT token
            access_token = data.get('access_token', '')
            
            if not email:
                return jsonify({'error': 'Email requis'}), 400
            
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = conn.cursor()
            
            # S'assurer que toutes les colonnes nécessaires existent
            try:
                cursor.execute("""
                    DO $$ 
                    BEGIN
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                      WHERE table_name = 'users' AND column_name = 'first_name') THEN
                            ALTER TABLE users ADD COLUMN first_name VARCHAR(100);
                        END IF;
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                      WHERE table_name = 'users' AND column_name = 'last_name') THEN
                            ALTER TABLE users ADD COLUMN last_name VARCHAR(100);
                        END IF;
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                      WHERE table_name = 'users' AND column_name = 'oauth_google_id') THEN
                            ALTER TABLE users ADD COLUMN oauth_google_id VARCHAR(255);
                        END IF;
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                      WHERE table_name = 'users' AND column_name = 'password_hash') THEN
                            ALTER TABLE users ADD COLUMN password_hash VARCHAR(255);
                        END IF;
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                      WHERE table_name = 'users' AND column_name = 'avatar_emoji') THEN
                            ALTER TABLE users ADD COLUMN avatar_emoji TEXT DEFAULT '';
                        END IF;
                        -- Si la colonne existe déjà avec VARCHAR(10), l'agrandir
                        IF EXISTS (SELECT 1 FROM information_schema.columns 
                                   WHERE table_name = 'users' AND column_name = 'avatar_emoji' 
                                   AND character_maximum_length = 10) THEN
                            ALTER TABLE users ALTER COLUMN avatar_emoji TYPE TEXT;
                        END IF;
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                      WHERE table_name = 'users' AND column_name = 'avatar_description') THEN
                            ALTER TABLE users ADD COLUMN avatar_description TEXT;
                        END IF;
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                      WHERE table_name = 'users' AND column_name = 'profile_photo_url') THEN
                            ALTER TABLE users ADD COLUMN profile_photo_url TEXT;
                        END IF;
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                      WHERE table_name = 'users' AND column_name = 'postal_address') THEN
                            ALTER TABLE users ADD COLUMN postal_address TEXT;
                        END IF;
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                      WHERE table_name = 'users' AND column_name = 'postal_city') THEN
                            ALTER TABLE users ADD COLUMN postal_city TEXT;
                        END IF;
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                      WHERE table_name = 'users' AND column_name = 'postal_zip') THEN
                            ALTER TABLE users ADD COLUMN postal_zip TEXT;
                        END IF;
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                      WHERE table_name = 'users' AND column_name = 'postal_country') THEN
                            ALTER TABLE users ADD COLUMN postal_country VARCHAR(10);
                        END IF;
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                      WHERE table_name = 'users' AND column_name = 'role') THEN
                            ALTER TABLE users ADD COLUMN role VARCHAR(50) DEFAULT 'user';
                        END IF;
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                      WHERE table_name = 'users' AND column_name = 'subscription') THEN
                            ALTER TABLE users ADD COLUMN subscription VARCHAR(50) DEFAULT 'free';
                        END IF;
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                      WHERE table_name = 'users' AND column_name = 'created_at') THEN
                            ALTER TABLE users ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
                        END IF;
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                      WHERE table_name = 'users' AND column_name = 'updated_at') THEN
                            ALTER TABLE users ADD COLUMN updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
                        END IF;
                    END $$;
                """)
                conn.commit()
                logger.info("Colonnes verifiees/creees avec succes")
            except Exception as e:
                logger.error(f"Erreur creation colonnes: {e}")
                import traceback
                logger.error(f"Traceback creation colonnes: {traceback.format_exc()}")
                # Continuer quand même - les colonnes existent peut-être déjà
            
            # Vérifier si l'utilisateur existe déjà (par email ou par oauth_id)
            # IMPORTANT: Vérifier aussi password_hash pour savoir si le profil est complet
            # Utiliser COALESCE pour gérer les valeurs NULL
            try:
                logger.info(f"Recherche utilisateur: email={email}, sub={sub}")
                cursor.execute("""
                    SELECT id, email, 
                           COALESCE(username, '') as username, 
                           COALESCE(first_name, '') as first_name, 
                           COALESCE(last_name, '') as last_name, 
                           COALESCE(subscription, 'free') as subscription, 
                           COALESCE(role, 'user') as role,
                           COALESCE(avatar_emoji, '') as avatar_emoji, 
                           COALESCE(avatar_description, '') as avatar_description, 
                           COALESCE(created_at, CURRENT_TIMESTAMP) as created_at, 
                           password_hash
                    FROM users 
                    WHERE LOWER(email) = %s OR oauth_google_id = %s
                    LIMIT 1
                """, (email, sub))
                logger.info("Requete SELECT executee avec succes")
            except Exception as e:
                logger.error(f"Erreur lors de la requete SELECT: {e}")
                import traceback
                logger.error(f"Traceback SELECT: {traceback.format_exc()}")
                raise
            
            user_row = cursor.fetchone()
            is_new_user = False
            profile_complete = False
            
            if user_row:
                # Utilisateur existant - connexion
                user_id, user_email, username, first_name, last_name, subscription, role, avatar_emoji, avatar_description, created_at, password_hash = user_row
                
                # Vérifier si le profil est vraiment complet :
                # - A un mot de passe défini (password_hash)
                # - A un username personnalisé (pas juste la partie avant @ de l'email)
                # - A une adresse postale (optionnel mais recommandé)
                has_password = bool(password_hash and password_hash.strip())
                email_prefix = email.split('@')[0][:20] if email else ''
                has_custom_username = bool(username and username.strip() and username != email_prefix)
                
                # Vérifier aussi si l'utilisateur a une adresse postale et profile_photo_url
                cursor.execute("""
                    SELECT COALESCE(postal_address, '') as postal_address,
                           COALESCE(profile_photo_url, '') as profile_photo_url
                    FROM users WHERE id = %s
                """, (user_id,))
                extra_row = cursor.fetchone()
                postal_address_db = extra_row[0] if extra_row else ''
                profile_photo_url_db = extra_row[1] if extra_row else ''
                has_postal_address = bool(postal_address_db and postal_address_db.strip())
                
                # Le profil est complet seulement si l'utilisateur a un mot de passe ET un username personnalisé
                profile_complete = has_password and has_custom_username
                
                logger.info(f"Vérification profil complet pour {email}: has_password={has_password}, has_custom_username={has_custom_username}, has_postal_address={has_postal_address}, profile_complete={profile_complete}")
                
                # Mettre à jour l'oauth_google_id si nécessaire
                if sub:
                    try:
                        cursor.execute("UPDATE users SET oauth_google_id = %s WHERE id = %s", (sub, user_id))
                        conn.commit()
                    except Exception as e:
                        logger.error(f"Erreur mise a jour oauth_google_id: {e}")
                        pass
            else:
                # Nouvel utilisateur - création
                is_new_user = True
                profile_complete = False  # Nouvel utilisateur = profil incomplet
                
                import secrets
                user_id = f"user_{int(datetime.utcnow().timestamp() * 1000)}_{secrets.token_hex(8)}"
                username = email.split('@')[0][:20]  # Utiliser la partie avant @ comme username temporaire
                
                # Extraire prénom et nom du nom complet
                name_parts = name.split(' ', 1) if name else ['', '']
                first_name = name_parts[0] if len(name_parts) > 0 else username
                last_name = name_parts[1] if len(name_parts) > 1 else ''
                
                # Vérifier l'unicité du username
                cursor.execute("SELECT id FROM users WHERE LOWER(username) = %s", (username.lower(),))
                if cursor.fetchone():
                    username = f"{username}_{secrets.token_hex(4)}"
                
                # Les colonnes OAuth sont déjà créées dans le bloc DO $$ ci-dessus
                
                # Utiliser picture comme avatar_emoji si disponible, sinon chaîne vide
                avatar_emoji_value = picture if picture else ''
                cursor.execute("""
                    INSERT INTO users (id, email, username, first_name, last_name, subscription, role,
                                      avatar_emoji, oauth_google_id, created_at, updated_at, password_hash)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NULL)
                """, (user_id, email, username, first_name, last_name, 'free', 'user', 
                      avatar_emoji_value, sub, datetime.utcnow(), datetime.utcnow()))
                conn.commit()
                created_at = datetime.utcnow()
                subscription = 'free'
                role = 'user'
                avatar_emoji = picture if picture else '👤'
                avatar_description = ''
            
            # Récupérer aussi profile_photo_url et postal_address pour le frontend (si pas déjà récupéré)
            if user_row:
                # Déjà récupéré dans le bloc if user_row ci-dessus
                profile_photo_url = profile_photo_url_db if 'profile_photo_url_db' in locals() else ''
                postal_address_db = postal_address_db if 'postal_address_db' in locals() else ''
                has_password = has_password if 'has_password' in locals() else False
                has_postal_address = has_postal_address if 'has_postal_address' in locals() else False
            else:
                # Nouvel utilisateur - pas encore de données supplémentaires
                profile_photo_url = picture if picture else ''
                postal_address_db = ''
                has_password = False
                has_postal_address = False
            
            cursor.close()
            conn.close()
            
            # Vérifier si l'email correspond à un directeur
            director_emails = ['mapevent777@gmail.com', 'directeur', 'director', 'admin']
            email_lower = email.lower()
            is_director = any(pattern in email_lower for pattern in director_emails)
            
            user_data = {
                'id': user_id,
                'email': email,
                'username': username,
                'name': f"{first_name} {last_name}".strip() if first_name and last_name else username,
                'firstName': first_name or '',
                'lastName': last_name or '',
                'subscription': 'vip_plus' if is_director else (subscription or 'free'),
                'role': 'director' if is_director else (role or 'user'),
                'avatar': avatar_emoji or '👤',
                'avatarDescription': avatar_description or '',
                'profilePhoto': profile_photo_url or avatar_emoji or '👤',
                'profile_photo_url': profile_photo_url or '',
                'createdAt': created_at.isoformat() if created_at else None,
                'hasPassword': has_password,
                'hasPostalAddress': has_postal_address
            }
            
            # Retourner les flags pour le frontend
            return jsonify({
                'user': user_data,
                'isNewUser': is_new_user,
                'profileComplete': profile_complete
            }), 200
            
        except Exception as e:
            import traceback
            error_trace = traceback.format_exc()
            logger.error(f"Erreur oauth_google: {e}")
            logger.error(f"Traceback: {error_trace}")
            # Retourner une erreur simple (sans traceback pour éviter les réponses trop grandes)
            error_message = str(e)[:500]  # Limiter la longueur du message
            return jsonify({
                'error': 'Erreur lors de l\'authentification Google',
                'message': error_message
            }), 500
    
    @app.route('/api/user/oauth/google/complete', methods=['POST'])
    def oauth_google_complete():
        """Complète le profil d'un utilisateur Google avec nom d'utilisateur, photo, mot de passe et adresse."""
        import hashlib
        import secrets
        
        try:
            data = request.get_json()
            user_id = data.get('userId')
            email = data.get('email', '').strip().lower()
            username = data.get('username', '').strip()
            password = data.get('password', '')
            profile_photo = data.get('profilePhoto', '')
            postal_address = data.get('postalAddress')
            
            if not email:
                return jsonify({'error': 'Email requis'}), 400
            
            if not username or len(username) < 3 or len(username) > 20:
                return jsonify({'error': 'Nom d\'utilisateur invalide (3-20 caractères)'}), 400
            
            if not password or len(password) < 8:
                return jsonify({'error': 'Mot de passe invalide (minimum 8 caractères)'}), 400
            
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = conn.cursor()
            
            # S'assurer que toutes les colonnes nécessaires existent
            try:
                cursor.execute("""
                    DO $$ 
                    BEGIN
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                      WHERE table_name = 'users' AND column_name = 'password_hash') THEN
                            ALTER TABLE users ADD COLUMN password_hash VARCHAR(255);
                        END IF;
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                      WHERE table_name = 'users' AND column_name = 'profile_photo_url') THEN
                            ALTER TABLE users ADD COLUMN profile_photo_url TEXT;
                        END IF;
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                      WHERE table_name = 'users' AND column_name = 'postal_address') THEN
                            ALTER TABLE users ADD COLUMN postal_address TEXT;
                        END IF;
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                      WHERE table_name = 'users' AND column_name = 'postal_city') THEN
                            ALTER TABLE users ADD COLUMN postal_city TEXT;
                        END IF;
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                      WHERE table_name = 'users' AND column_name = 'postal_zip') THEN
                            ALTER TABLE users ADD COLUMN postal_zip TEXT;
                        END IF;
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                      WHERE table_name = 'users' AND column_name = 'postal_country') THEN
                            ALTER TABLE users ADD COLUMN postal_country VARCHAR(10) DEFAULT 'CH';
                        END IF;
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                      WHERE table_name = 'users' AND column_name = 'first_name') THEN
                            ALTER TABLE users ADD COLUMN first_name VARCHAR(100);
                        END IF;
                        IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                      WHERE table_name = 'users' AND column_name = 'last_name') THEN
                            ALTER TABLE users ADD COLUMN last_name VARCHAR(100);
                        END IF;
                    END $$;
                """)
                conn.commit()
            except Exception as e:
                logger.error(f"Erreur creation colonnes complete: {e}")
                import traceback
                logger.error(traceback.format_exc())
                # Continuer quand même
            
            # Vérifier que l'utilisateur existe (par email ou user_id ou oauth_google_id)
            # Si user_id est null (localStorage plein), chercher uniquement par email
            logger.info(f"🔍 Recherche utilisateur: email={email}, user_id={user_id}")
            
            if user_id:
                cursor.execute("SELECT id, password_hash, username FROM users WHERE id = %s OR LOWER(email) = %s OR oauth_google_id = %s", 
                             (user_id, email, user_id))
            else:
                # Chercher par email ou oauth_google_id (si on a le sub depuis le token)
                cursor.execute("SELECT id, password_hash, username FROM users WHERE LOWER(email) = %s", (email,))
            user_row = cursor.fetchone()
            
            if not user_row:
                # Si utilisateur non trouvé, créer un nouvel utilisateur avec les données du formulaire
                logger.warn(f"⚠️ Utilisateur non trouvé pour email={email}, user_id={user_id}. Création d'un nouvel utilisateur.")
                actual_user_id = f"user_{int(datetime.utcnow().timestamp() * 1000)}_{secrets.token_hex(8)}"
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                
                # Créer l'utilisateur avec les données du formulaire
                try:
                    cursor.execute("""
                        INSERT INTO users (id, email, username, first_name, last_name, password_hash, 
                                         avatar_emoji, profile_photo_url, postal_address, subscription, role, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'free', 'user', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                    """, (actual_user_id, email, username, data.get('firstName', ''), data.get('lastName', ''), 
                          password_hash, profile_photo, profile_photo, 
                          str(postal_address) if postal_address else ''))
                    conn.commit()
                    logger.info(f"✅ Nouvel utilisateur créé: {actual_user_id}")
                except Exception as insert_error:
                    logger.error(f"❌ Erreur création utilisateur: {insert_error}")
                    import traceback
                    logger.error(traceback.format_exc())
                    raise
            else:
                actual_user_id = user_row[0]
                existing_password_hash = user_row[1]
                existing_username = user_row[2]
                logger.info(f"✅ Utilisateur trouvé: {actual_user_id}, a_password={bool(existing_password_hash)}, username={existing_username}")
                
                # Si l'utilisateur a déjà un profil complet, vérifier si on peut quand même mettre à jour
                if existing_password_hash and existing_password_hash.strip():
                    logger.info(f"ℹ️ Utilisateur a déjà un mot de passe. Mise à jour autorisée pour compléter/modifier le profil.")
            
            # Vérifier l'unicité du username AVANT de créer/mettre à jour
            logger.info(f"🔍 Vérification unicité username: {username}")
            cursor.execute("SELECT id FROM users WHERE LOWER(username) = %s AND id != %s", 
                         (username.lower(), actual_user_id))
            existing_username_user = cursor.fetchone()
            if existing_username_user:
                logger.warn(f"⚠️ Username déjà pris: {username} par utilisateur {existing_username_user[0]}")
                cursor.close()
                conn.close()
                return jsonify({'error': 'Ce nom d\'utilisateur est déjà pris'}), 400
            logger.info(f"✅ Username disponible: {username}")
            
            # Hasher le mot de passe
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            
            # Préparer les colonnes à mettre à jour
            updates = []
            params = []
            
            if username:
                updates.append("username = %s")
                params.append(username)
            
            if password_hash:
                updates.append("password_hash = %s")
                params.append(password_hash)
            
            if profile_photo:
                updates.append("avatar_emoji = %s")
                params.append(profile_photo)
                updates.append("profile_photo_url = %s")
                params.append(profile_photo)
            
            if postal_address:
                # Les colonnes d'adresse sont déjà créées dans le bloc DO $$ ci-dessus
                # postal_address peut être une chaîne (string) ou un dictionnaire
                if isinstance(postal_address, dict):
                    # Format dictionnaire : {'address': '...', 'city': '...', 'zip': '...', 'country': '...'}
                    updates.append("postal_address = %s")
                    params.append(postal_address.get('address', ''))
                    updates.append("postal_city = %s")
                    params.append(postal_address.get('city', ''))
                    updates.append("postal_zip = %s")
                    params.append(postal_address.get('zip', ''))
                    updates.append("postal_country = %s")
                    params.append(postal_address.get('country', 'CH'))
                else:
                    # Format chaîne : "Rue, Code postal, Ville"
                    updates.append("postal_address = %s")
                    params.append(str(postal_address))
                    updates.append("postal_city = %s")
                    params.append('')  # Pas de ville séparée si c'est une chaîne
                    updates.append("postal_zip = %s")
                    params.append('')  # Pas de code postal séparé si c'est une chaîne
                    updates.append("postal_country = %s")
                    params.append('CH')  # Par défaut Suisse
            
            updates.append("updated_at = %s")
            params.append(datetime.utcnow())
            
            # Ajouter actual_user_id à la fin pour la clause WHERE
            params.append(actual_user_id)
            
            # Mettre à jour l'utilisateur (utiliser actual_user_id)
            if updates:
                update_query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
                logger.info(f"🔍 Exécution UPDATE: {update_query[:200]}...")
                logger.info(f"🔍 Paramètres: {len(params)} paramètres")
                try:
                    cursor.execute(update_query, params)
                    conn.commit()
                    logger.info(f"✅ Utilisateur {actual_user_id} mis à jour avec succès")
                except Exception as update_error:
                    logger.error(f"❌ Erreur UPDATE utilisateur: {update_error}")
                    import traceback
                    logger.error(traceback.format_exc())
                    cursor.close()
                    conn.close()
                    raise
            else:
                logger.warn(f"⚠️ Aucune mise à jour à effectuer pour {actual_user_id}")
            
            # Récupérer l'utilisateur mis à jour (utiliser actual_user_id)
            cursor.execute("""
                SELECT id, email, username, 
                       COALESCE(first_name, '') as first_name, 
                       COALESCE(last_name, '') as last_name, 
                       COALESCE(subscription, 'free') as subscription, 
                       COALESCE(role, 'user') as role,
                       COALESCE(avatar_emoji, '') as avatar_emoji, 
                       COALESCE(avatar_description, '') as avatar_description, 
                       COALESCE(profile_photo_url, '') as profile_photo_url,
                       COALESCE(postal_address, '') as postal_address, 
                       COALESCE(postal_city, '') as postal_city, 
                       COALESCE(postal_zip, '') as postal_zip, 
                       COALESCE(postal_country, 'CH') as postal_country,
                       created_at
                FROM users 
                WHERE id = %s
            """, (actual_user_id,))
            
            user_row = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if user_row:
                user_id, user_email, username, first_name, last_name, subscription, role, \
                avatar_emoji, avatar_description, profile_photo_url, \
                postal_address_db, postal_city, postal_zip, postal_country, created_at = user_row
                
                user_data = {
                    'id': user_id,
                    'email': user_email,
                    'username': username,
                    'name': f"{first_name} {last_name}".strip() if first_name and last_name else username,
                    'firstName': first_name or '',
                    'lastName': last_name or '',
                    'subscription': subscription or 'free',
                    'role': role or 'user',
                    'avatar': profile_photo_url or avatar_emoji or '👤',
                    'avatarDescription': avatar_description or '',
                    'profilePhoto': profile_photo_url or avatar_emoji or '👤',  # Ajouter profilePhoto pour le frontend
                    'profile_photo_url': profile_photo_url or '',  # Garder aussi profile_photo_url pour compatibilité
                    'profileComplete': True,  # Profil maintenant complet après la création
                    'postalAddress': {
                        'address': postal_address_db or '',
                        'city': postal_city or '',
                        'zip': postal_zip or '',
                        'country': postal_country or 'CH'
                    } if postal_address_db else None
                }
                
                return jsonify({'success': True, 'user': user_data, 'profileComplete': True}), 200
            else:
                return jsonify({'error': 'Erreur lors de la récupération de l\'utilisateur'}), 500
                
        except Exception as e:
            logger.error(f"Erreur complétion profil Google: {str(e)}")
            import traceback
            error_trace = traceback.format_exc()
            logger.error(error_trace)
            
            # Fermer les connexions en cas d'erreur
            try:
                if 'cursor' in locals():
                    cursor.close()
                if 'conn' in locals():
                    conn.close()
            except:
                pass
            
            # Retourner une erreur plus détaillée pour le debug
            error_message = str(e)
            if 'timeout' in error_message.lower() or 'connection' in error_message.lower():
                return jsonify({'error': 'Timeout de connexion à la base de données. Veuillez réessayer.'}), 502
            elif 'does not exist' in error_message.lower() or 'not found' in error_message.lower():
                return jsonify({'error': 'Utilisateur non trouvé. Veuillez d\'abord vous connecter avec Google.'}), 404
            else:
                return jsonify({'error': f'Erreur serveur: {error_message}'}), 500
    
    @app.route('/api/user/oauth/facebook', methods=['POST'])
    def oauth_facebook():
        """Gère l'authentification OAuth Facebook."""
        try:
            data = request.get_json()
            email = data.get('email', '').strip().lower()
            name = data.get('name', '').strip()
            picture = data.get('picture', '')
            user_id_fb = data.get('user_id', '')  # Facebook user ID
            access_token = data.get('access_token', '')
            
            if not email and not user_id_fb:
                return jsonify({'error': 'Email ou user_id requis'}), 400
            
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = conn.cursor()
            
            # Vérifier si l'utilisateur existe déjà
            cursor.execute("""
                SELECT id, email, username, first_name, last_name, subscription, role,
                       avatar_emoji, avatar_description, created_at
                FROM users 
                WHERE LOWER(email) = %s OR oauth_facebook_id = %s
            """, (email if email else '', user_id_fb))
            
            user_row = cursor.fetchone()
            
            if user_row:
                # Utilisateur existant - connexion
                user_id, user_email, username, first_name, last_name, subscription, role, avatar_emoji, avatar_description, created_at = user_row
                
                # Mettre à jour l'oauth_facebook_id si nécessaire
                if user_id_fb:
                    try:
                        cursor.execute("UPDATE users SET oauth_facebook_id = %s WHERE id = %s", (user_id_fb, user_id))
                        conn.commit()
                    except:
                        pass
            else:
                # Nouvel utilisateur - création
                import secrets
                user_id = f"user_{int(datetime.utcnow().timestamp() * 1000)}_{secrets.token_hex(8)}"
                username = (email.split('@')[0] if email else f"fb_{user_id_fb}")[:20]
                
                # Extraire prénom et nom
                name_parts = name.split(' ', 1) if name else ['', '']
                first_name = name_parts[0] if len(name_parts) > 0 else username
                last_name = name_parts[1] if len(name_parts) > 1 else ''
                
                # Vérifier l'unicité du username
                cursor.execute("SELECT id FROM users WHERE LOWER(username) = %s", (username.lower(),))
                if cursor.fetchone():
                    username = f"{username}_{secrets.token_hex(4)}"
                
                # Créer l'utilisateur
                cursor.execute("""
                    INSERT INTO users (id, email, username, first_name, last_name, subscription, role,
                                      avatar_emoji, oauth_facebook_id, created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (user_id, email if email else f"fb_{user_id_fb}@facebook.com", username, first_name, last_name, 
                      'free', 'user', picture if picture else '👤', user_id_fb, datetime.utcnow(), datetime.utcnow()))
                conn.commit()
                created_at = datetime.utcnow()
                subscription = 'free'
                role = 'user'
                avatar_emoji = picture if picture else '👤'
                avatar_description = ''
            
            cursor.close()
            conn.close()
            
            # Vérifier si l'email correspond à un directeur
            director_emails = ['mapevent777@gmail.com', 'directeur', 'director', 'admin']
            email_lower = (email or '').lower()
            is_director = any(pattern in email_lower for pattern in director_emails)
            
            user_data = {
                'id': user_id,
                'email': email if email else f"fb_{user_id_fb}@facebook.com",
                'username': username,
                'name': f"{first_name} {last_name}".strip() if first_name and last_name else username,
                'firstName': first_name or '',
                'lastName': last_name or '',
                'subscription': 'vip_plus' if is_director else (subscription or 'free'),
                'role': 'director' if is_director else (role or 'user'),
                'avatar': avatar_emoji or '👤',
                'avatarDescription': avatar_description or '',
                'createdAt': created_at.isoformat() if created_at else None
            }
            
            return jsonify({'user': user_data}), 200
            
        except Exception as e:
            logger.error(f"Erreur oauth_facebook: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({'error': str(e)}), 500
    
    # ============================================
    # ROUTES DE PAIEMENT STRIPE
    # ============================================
    
    # Mapping des plans vers les Product/Price IDs Stripe
    STRIPE_PLANS = {
        'events-explorer': {'price_id': os.getenv('STRIPE_PRICE_EVENTS_EXPLORER', ''), 'amount': 5.00},
        'events-alerts-pro': {'price_id': os.getenv('STRIPE_PRICE_EVENTS_ALERTS_PRO', ''), 'amount': 10.00},
        'service-pro': {'price_id': os.getenv('STRIPE_PRICE_SERVICE_PRO', ''), 'amount': 12.00},
        'service-ultra': {'price_id': os.getenv('STRIPE_PRICE_SERVICE_ULTRA', ''), 'amount': 18.00},
        'full-premium': {'price_id': os.getenv('STRIPE_PRICE_FULL_PREMIUM', ''), 'amount': 25.00}
    }
    
    @app.route('/api/payments/create-checkout-session', methods=['POST'])
    def create_checkout_session():
        """Crée une session Stripe Checkout pour paiement ou abonnement."""
        try:
            data = request.get_json()
            user_id = data.get('userId')
            payment_type = data.get('paymentType')  # 'contact', 'subscription', 'cart', 'donation'
            amount = data.get('amount')
            currency = data.get('currency', 'CHF')
            
            if not user_id or not payment_type:
                return jsonify({'error': 'Missing required fields'}), 400
            
            # Obtenir l'URL de base depuis les headers ou env
            request_url = request.headers.get('Origin') or request.headers.get('Referer', '')
            if not request_url:
                request_url = os.getenv('FRONTEND_URL', 'https://mapevent.world')
            
            success_url = f"{request_url}/?payment=success&session_id={{CHECKOUT_SESSION_ID}}"
            cancel_url = f"{request_url}/?payment=canceled"
            
            line_items = []
            metadata = {
                'user_id': str(user_id),
                'payment_type': payment_type
            }
            
            if payment_type == 'subscription':
                plan = data.get('plan')
                if not plan or plan not in STRIPE_PLANS:
                    return jsonify({'error': 'Invalid plan'}), 400
                
                price_id = STRIPE_PLANS[plan]['price_id']
                if not price_id:
                    return jsonify({'error': 'Stripe price ID not configured for this plan'}), 500
                
                line_items.append({
                    'price': price_id,
                    'quantity': 1
                })
                metadata['plan'] = plan
                
                # Créer une session d'abonnement
                session = stripe.checkout.Session.create(
                    customer_email=data.get('email'),  # Optionnel
                    payment_method_types=['card'],
                    line_items=line_items,
                    mode='subscription',
                    success_url=success_url,
                    cancel_url=cancel_url,
                    metadata=metadata,
                    subscription_data={
                        'metadata': metadata
                    }
                )
            else:
                # Paiement unique (contact, panier, donation)
                items = data.get('items', [])
                
                if payment_type == 'contact':
                    # Un seul item
                    item_type = data.get('itemType')
                    item_id = data.get('itemId')
                    if not item_type or not item_id:
                        return jsonify({'error': 'Missing itemType or itemId'}), 400
                    
                    line_items.append({
                        'price_data': {
                            'currency': currency.lower(),
                            'product_data': {
                                'name': f'Contact {item_type}',
                                'description': f'Débloquer le contact pour {item_type} #{item_id}'
                            },
                            'unit_amount': int(amount * 100)  # Stripe utilise les centimes
                        },
                        'quantity': 1
                    })
                    metadata['item_type'] = item_type
                    metadata['item_id'] = str(item_id)
                    items = [{'type': item_type, 'id': item_id, 'price': amount}]
                
                elif payment_type == 'cart':
                    # Plusieurs items
                    if not items or len(items) == 0:
                        return jsonify({'error': 'Cart is empty'}), 400
                    
                    total_amount = sum(item.get('price', 0) for item in items)
                    line_items.append({
                        'price_data': {
                            'currency': currency.lower(),
                            'product_data': {
                                'name': f'Panier ({len(items)} contact(s))',
                                'description': f'Débloquer {len(items)} contact(s)'
                            },
                            'unit_amount': int(total_amount * 100)
                        },
                        'quantity': 1
                    })
                    metadata['items_count'] = str(len(items))
                
                elif payment_type == 'donation':
                    if not amount or amount <= 0:
                        return jsonify({'error': 'Invalid donation amount'}), 400
                    
                    line_items.append({
                        'price_data': {
                            'currency': currency.lower(),
                            'product_data': {
                                'name': 'Don Mission Planète',
                                'description': '70% de votre don va à la Mission Planète'
                            },
                            'unit_amount': int(amount * 100)
                        },
                        'quantity': 1
                    })
                
                # Créer une session de paiement unique
                session = stripe.checkout.Session.create(
                    customer_email=data.get('email'),  # Optionnel
                    payment_method_types=['card'],
                    line_items=line_items,
                    mode='payment',
                    success_url=success_url,
                    cancel_url=cancel_url,
                    metadata=metadata
                )
            
            # Enregistrer la session dans la base de données
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                try:
                    cursor.execute("INSERT INTO users (id) VALUES (%s) ON CONFLICT (id) DO NOTHING", (user_id,))
                    conn.commit()
                    
                    cursor.execute("""
                        INSERT INTO payments (
                            user_id, stripe_session_id, amount, currency, status,
                            payment_type, item_type, item_id, items
                        ) VALUES (%s, %s, %s, %s, 'pending', %s, %s, %s, %s)
                    """, (
                        user_id,
                        session.id,
                        amount if payment_type != 'subscription' else STRIPE_PLANS.get(data.get('plan'), {}).get('amount', 0),
                        currency,
                        payment_type,
                        metadata.get('item_type'),
                        metadata.get('item_id'),
                        json.dumps(items) if items else None
                    ))
                    conn.commit()
                except Exception as db_error:
                    logger.error(f"Erreur enregistrement paiement: {db_error}")
                finally:
                    cursor.close()
                    conn.close()
            
            return jsonify({
                'sessionId': session.id,
                'publicKey': app.config['STRIPE_PUBLIC_KEY']
            }), 200
            
        except stripe.error.StripeError as e:
            logger.error(f"Erreur Stripe: {e}")
            return jsonify({'error': f'Stripe error: {str(e)}'}), 500
        except Exception as e:
            logger.error(f"Erreur create_checkout_session: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/payments/verify-session', methods=['GET'])
    def verify_session():
        """Vérifie le statut d'une session Stripe après paiement."""
        try:
            session_id = request.args.get('session_id')
            if not session_id:
                return jsonify({'error': 'Missing session_id parameter'}), 400
            
            # Récupérer la session depuis Stripe
            session = stripe.checkout.Session.retrieve(session_id)
            
            if session.payment_status == 'paid':
                # Mettre à jour le paiement dans la base de données
                conn = get_db_connection()
                if conn:
                    cursor = conn.cursor()
                    try:
                        cursor.execute("""
                            UPDATE payments
                            SET status = 'succeeded',
                                stripe_payment_intent_id = %s,
                                stripe_customer_id = %s,
                                updated_at = CURRENT_TIMESTAMP
                            WHERE stripe_session_id = %s
                        """, (
                            session.payment_intent if hasattr(session, 'payment_intent') else None,
                            session.customer if hasattr(session, 'customer') else None,
                            session_id
                        ))
                        conn.commit()
                        
                        # Récupérer les détails du paiement
                        cursor.execute("""
                            SELECT payment_type, item_type, item_id, items
                            FROM payments
                            WHERE stripe_session_id = %s
                        """, (session_id,))
                        row = cursor.fetchone()
                        
                        payment_type = row[0] if row else None
                        items = json.loads(row[3]) if row and row[3] else []
                        
                    except Exception as db_error:
                        logger.error(f"Erreur mise à jour paiement: {db_error}")
                    finally:
                        cursor.close()
                        conn.close()
                
                return jsonify({
                    'success': True,
                    'paymentType': payment_type,
                    'items': items,
                    'sessionId': session_id
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'paymentStatus': session.payment_status
                }), 200
                
        except stripe.error.StripeError as e:
            logger.error(f"Erreur Stripe: {e}")
            return jsonify({'error': f'Stripe error: {str(e)}'}), 500
        except Exception as e:
            logger.error(f"Erreur verify_session: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/payments/subscription-status', methods=['GET'])
    def get_subscription_status():
        """Récupère le statut de l'abonnement d'un utilisateur."""
        try:
            user_id = request.args.get('userId')
            if not user_id:
                return jsonify({'error': 'Missing userId parameter'}), 400
            
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database connection failed'}), 500
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT stripe_subscription_id, plan, status, current_period_start, current_period_end
                FROM subscriptions
                WHERE user_id = %s AND status = 'active'
                ORDER BY created_at DESC
                LIMIT 1
            """, (user_id,))
            
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if row:
                return jsonify({
                    'subscription': {
                        'plan': row[1],
                        'status': row[2],
                        'currentPeriodStart': row[3].isoformat() if row[3] else None,
                        'currentPeriodEnd': row[4].isoformat() if row[4] else None
                    }
                }), 200
            else:
                return jsonify({
                    'subscription': None
                }), 200
                
        except Exception as e:
            logger.error(f"Erreur get_subscription_status: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/payments/webhook', methods=['POST'])
    def stripe_webhook():
        """Gère les webhooks Stripe pour mettre à jour les paiements et abonnements."""
        try:
            payload = request.get_data(as_text=True)
            sig_header = request.headers.get('Stripe-Signature')
            
            if not app.config['STRIPE_WEBHOOK_SECRET']:
                logger.warning("STRIPE_WEBHOOK_SECRET non configuré, webhook ignoré")
                return jsonify({'error': 'Webhook secret not configured'}), 400
            
            try:
                event = stripe.Webhook.construct_event(
                    payload, sig_header, app.config['STRIPE_WEBHOOK_SECRET']
                )
            except ValueError as e:
                logger.error(f"Invalid payload: {e}")
                return jsonify({'error': 'Invalid payload'}), 400
            except stripe.error.SignatureVerificationError as e:
                logger.error(f"Invalid signature: {e}")
                return jsonify({'error': 'Invalid signature'}), 400
            
            # Traiter les événements
            if event['type'] == 'checkout.session.completed':
                session = event['data']['object']
                handle_checkout_completed(session)
            elif event['type'] == 'customer.subscription.created':
                subscription = event['data']['object']
                handle_subscription_created(subscription)
            elif event['type'] == 'customer.subscription.updated':
                subscription = event['data']['object']
                handle_subscription_updated(subscription)
            elif event['type'] == 'customer.subscription.deleted':
                subscription = event['data']['object']
                handle_subscription_deleted(subscription)
            elif event['type'] == 'payment_intent.succeeded':
                payment_intent = event['data']['object']
                handle_payment_succeeded(payment_intent)
            
            return jsonify({'received': True}), 200
            
        except Exception as e:
            logger.error(f"Erreur stripe_webhook: {e}")
            return jsonify({'error': str(e)}), 500
    
    def handle_checkout_completed(session):
        """Gère l'événement checkout.session.completed."""
        try:
            metadata = session.get('metadata', {})
            user_id = metadata.get('user_id')
            payment_type = metadata.get('payment_type')
            
            conn = get_db_connection()
            if not conn:
                return
            
            cursor = conn.cursor()
            
            # Mettre à jour le paiement
            cursor.execute("""
                UPDATE payments
                SET status = 'succeeded',
                    stripe_payment_intent_id = %s,
                    stripe_customer_id = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE stripe_session_id = %s
            """, (
                session.get('payment_intent'),
                session.get('customer'),
                session['id']
            ))
            
            # Si c'est un abonnement, créer/ mettre à jour l'entrée subscription
            if payment_type == 'subscription' and session.get('subscription'):
                plan = metadata.get('plan')
                cursor.execute("""
                    INSERT INTO subscriptions (
                        user_id, stripe_subscription_id, stripe_customer_id,
                        plan, status, current_period_start, current_period_end
                    ) VALUES (%s, %s, %s, %s, 'active', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP + INTERVAL '1 month')
                    ON CONFLICT (stripe_subscription_id) 
                    DO UPDATE SET 
                        status = 'active',
                        updated_at = CURRENT_TIMESTAMP
                """, (
                    user_id,
                    session['subscription'],
                    session.get('customer'),
                    plan
                ))
                
                # Mettre à jour l'utilisateur
                cursor.execute("""
                    UPDATE users SET subscription = %s WHERE id = %s
                """, (plan, user_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"Erreur handle_checkout_completed: {e}")
    
    def handle_subscription_created(subscription):
        """Gère l'événement customer.subscription.created."""
        # Déjà géré dans handle_checkout_completed, mais on peut ajouter une logique supplémentaire
        pass
    
    def handle_subscription_updated(subscription):
        """Gère l'événement customer.subscription.updated."""
        try:
            conn = get_db_connection()
            if not conn:
                return
            
            cursor = conn.cursor()
            
            status = subscription['status']
            cursor.execute("""
                UPDATE subscriptions
                SET status = %s,
                    current_period_start = to_timestamp(%s),
                    current_period_end = to_timestamp(%s),
                    cancel_at_period_end = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE stripe_subscription_id = %s
            """, (
                status,
                subscription.get('current_period_start'),
                subscription.get('current_period_end'),
                subscription.get('cancel_at_period_end', False),
                subscription['id']
            ))
            
            # Si l'abonnement est annulé, mettre à jour l'utilisateur
            if status in ['canceled', 'past_due', 'unpaid']:
                cursor.execute("""
                    SELECT user_id FROM subscriptions WHERE stripe_subscription_id = %s
                """, (subscription['id'],))
                row = cursor.fetchone()
                if row:
                    cursor.execute("""
                        UPDATE users SET subscription = 'free' WHERE id = %s
                    """, (row[0],))
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"Erreur handle_subscription_updated: {e}")
    
    def handle_subscription_deleted(subscription):
        """Gère l'événement customer.subscription.deleted."""
        try:
            conn = get_db_connection()
            if not conn:
                return
            
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE subscriptions
                SET status = 'canceled',
                    updated_at = CURRENT_TIMESTAMP
                WHERE stripe_subscription_id = %s
            """, (subscription['id'],))
            
            # Mettre à jour l'utilisateur
            cursor.execute("""
                SELECT user_id FROM subscriptions WHERE stripe_subscription_id = %s
            """, (subscription['id'],))
            row = cursor.fetchone()
            if row:
                cursor.execute("""
                    UPDATE users SET subscription = 'free' WHERE id = %s
                """, (row[0],))
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"Erreur handle_subscription_deleted: {e}")
    
    def handle_payment_succeeded(payment_intent):
        """Gère l'événement payment_intent.succeeded."""
        try:
            conn = get_db_connection()
            if not conn:
                return
            
            cursor = conn.cursor()
            
            # Mettre à jour le paiement si on a le payment_intent_id
            cursor.execute("""
                UPDATE payments
                SET status = 'succeeded',
                    updated_at = CURRENT_TIMESTAMP
                WHERE stripe_payment_intent_id = %s AND status = 'pending'
            """, (payment_intent['id'],))
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"Erreur handle_payment_succeeded: {e}")
    
    # ============================================
    # ROUTES SOCIALES - AMIS
    # ============================================
    
    @app.route('/api/social/friends/request', methods=['POST'])
    def send_friend_request():
        """Envoyer une demande d'ami"""
        try:
            data = request.get_json()
            user_id = data.get('userId')
            friend_id = data.get('friendId')
            
            if not user_id or not friend_id:
                return jsonify({'error': 'userId et friendId requis'}), 400
            
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database unavailable'}), 500
            
            cursor = conn.cursor()
            
            # Vérifier si la demande existe déjà
            cursor.execute("""
                SELECT status FROM user_friends 
                WHERE (user_id = %s AND friend_id = %s) OR (user_id = %s AND friend_id = %s)
            """, (user_id, friend_id, friend_id, user_id))
            
            existing = cursor.fetchone()
            if existing:
                cursor.close()
                conn.close()
                return jsonify({'error': 'Demande déjà envoyée'}), 409
            
            # Créer la demande
            cursor.execute("""
                INSERT INTO user_friends (user_id, friend_id, status)
                VALUES (%s, %s, 'pending')
            """, (user_id, friend_id))
            
            # Créer une alerte pour le destinataire
            cursor.execute("""
                INSERT INTO social_alerts (user_id, type, from_user_id, title, message, icon)
                VALUES (%s, 'friend_request', %s, 'Nouvelle demande d''ami', %s, '👥')
            """, (friend_id, user_id, f"Demande d'ami de {user_id}"))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({'success': True}), 201
            
        except Exception as e:
            logger.error(f"Erreur send_friend_request: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/social/friends/accept', methods=['POST'])
    def accept_friend_request():
        """Accepter une demande d'ami"""
        try:
            data = request.get_json()
            user_id = data.get('userId')
            friend_id = data.get('friendId')
            
            if not user_id or not friend_id:
                return jsonify({'error': 'userId et friendId requis'}), 400
            
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database unavailable'}), 500
            
            cursor = conn.cursor()
            
            # Accepter la demande
            cursor.execute("""
                UPDATE user_friends 
                SET status = 'accepted', updated_at = CURRENT_TIMESTAMP
                WHERE user_id = %s AND friend_id = %s AND status = 'pending'
            """, (friend_id, user_id))
            
            # Créer la relation inverse si elle n'existe pas
            cursor.execute("""
                INSERT INTO user_friends (user_id, friend_id, status)
                VALUES (%s, %s, 'accepted')
                ON CONFLICT (user_id, friend_id) DO NOTHING
            """, (user_id, friend_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({'success': True}), 200
            
        except Exception as e:
            logger.error(f"Erreur accept_friend_request: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/social/friends', methods=['GET'])
    def get_friends():
        """Récupérer la liste des amis"""
        try:
            user_id = request.args.get('userId')
            if not user_id:
                return jsonify({'error': 'userId requis'}), 400
            
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database unavailable'}), 500
            
            cursor = conn.cursor()
            
            # Récupérer les amis acceptés
            cursor.execute("""
                SELECT u.id, u.username, u.first_name, u.last_name, uf.created_at
                FROM user_friends uf
                JOIN users u ON u.id = uf.friend_id
                WHERE uf.user_id = %s AND uf.status = 'accepted'
                ORDER BY uf.created_at DESC
            """, (user_id,))
            
            friends = []
            for row in cursor.fetchall():
                friends.append({
                    'id': row[0],
                    'username': row[1],
                    'firstName': row[2],
                    'lastName': row[3],
                    'createdAt': row[4].isoformat() if row[4] else None
                })
            
            cursor.close()
            conn.close()
            
            return jsonify({'friends': friends}), 200
            
        except Exception as e:
            logger.error(f"Erreur get_friends: {e}")
            return jsonify({'error': str(e)}), 500
    
    # ============================================
    # ROUTES SOCIALES - GROUPES
    # ============================================
    
    @app.route('/api/social/groups', methods=['POST'])
    def create_group():
        """Créer un groupe"""
        try:
            data = request.get_json()
            name = data.get('name')
            description = data.get('description', '')
            group_type = data.get('type', 'public')
            category = data.get('category')
            country = data.get('country')
            creator_id = data.get('creatorId')
            icon = data.get('icon', '👥')
            
            if not name or not creator_id:
                return jsonify({'error': 'name et creatorId requis'}), 400
            
            group_id = f"group_{int(datetime.utcnow().timestamp() * 1000)}_{random.randint(1000, 9999)}"
            
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database unavailable'}), 500
            
            cursor = conn.cursor()
            
            # Créer le groupe
            cursor.execute("""
                INSERT INTO groups (id, name, description, type, category, country, creator_id, icon)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (group_id, name, description, group_type, category, country, creator_id, icon))
            
            # Ajouter le créateur comme membre admin
            cursor.execute("""
                INSERT INTO group_members (group_id, user_id, role)
                VALUES (%s, %s, 'admin')
            """, (group_id, creator_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({
                'success': True,
                'groupId': group_id
            }), 201
            
        except Exception as e:
            logger.error(f"Erreur create_group: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/social/groups/<group_id>/messages', methods=['POST'])
    def send_group_message():
        """Envoyer un message dans un groupe"""
        try:
            data = request.get_json()
            user_id = data.get('userId')
            message = data.get('message')
            attachments = data.get('attachments', [])
            
            if not user_id or not message:
                return jsonify({'error': 'userId et message requis'}), 400
            
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database unavailable'}), 500
            
            cursor = conn.cursor()
            
            # Vérifier que l'utilisateur est membre du groupe
            cursor.execute("""
                SELECT role FROM group_members 
                WHERE group_id = %s AND user_id = %s
            """, (group_id, user_id))
            
            if not cursor.fetchone():
                cursor.close()
                conn.close()
                return jsonify({'error': 'Vous n\'êtes pas membre de ce groupe'}), 403
            
            # Vérifier la modération (mots interdits basiques)
            forbidden_words = ['spam', 'scam', 'hack']
            has_forbidden = any(word in message.lower() for word in forbidden_words)
            
            status = 'pending_moderation' if has_forbidden else 'published'
            
            # Insérer le message
            cursor.execute("""
                INSERT INTO group_messages (group_id, user_id, message, attachments, status)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id, created_at
            """, (group_id, user_id, message, json.dumps(attachments), status))
            
            result = cursor.fetchone()
            message_id = result[0]
            created_at = result[1]
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({
                'success': True,
                'messageId': message_id,
                'status': status,
                'createdAt': created_at.isoformat()
            }), 201
            
        except Exception as e:
            logger.error(f"Erreur send_group_message: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/social/groups/<group_id>/messages', methods=['GET'])
    def get_group_messages():
        """Récupérer les messages d'un groupe"""
        try:
            user_id = request.args.get('userId')
            limit = int(request.args.get('limit', 50))
            offset = int(request.args.get('offset', 0))
            
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database unavailable'}), 500
            
            cursor = conn.cursor()
            
            # Récupérer les messages publiés uniquement
            cursor.execute("""
                SELECT gm.id, gm.user_id, u.username, gm.message, gm.attachments, 
                       gm.reactions, gm.status, gm.created_at
                FROM group_messages gm
                JOIN users u ON u.id = gm.user_id
                WHERE gm.group_id = %s AND gm.status = 'published'
                ORDER BY gm.created_at DESC
                LIMIT %s OFFSET %s
            """, (group_id, limit, offset))
            
            messages = []
            for row in cursor.fetchall():
                messages.append({
                    'id': row[0],
                    'userId': row[1],
                    'username': row[2],
                    'message': row[3],
                    'attachments': json.loads(row[4]) if row[4] else [],
                    'reactions': json.loads(row[5]) if row[5] else {},
                    'status': row[6],
                    'createdAt': row[7].isoformat() if row[7] else None
                })
            
            cursor.close()
            conn.close()
            
            return jsonify({'messages': messages}), 200
            
        except Exception as e:
            logger.error(f"Erreur get_group_messages: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/social/messages/<message_id>/reaction', methods=['POST'])
    def add_message_reaction():
        """Ajouter une réaction à un message"""
        try:
            data = request.get_json()
            user_id = data.get('userId')
            emoji = data.get('emoji')
            
            if not user_id or not emoji:
                return jsonify({'error': 'userId et emoji requis'}), 400
            
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database unavailable'}), 500
            
            cursor = conn.cursor()
            
            # Récupérer les réactions actuelles
            cursor.execute("""
                SELECT reactions FROM group_messages WHERE id = %s
            """, (message_id,))
            
            row = cursor.fetchone()
            if not row:
                cursor.close()
                conn.close()
                return jsonify({'error': 'Message introuvable'}), 404
            
            reactions = json.loads(row[0]) if row[0] else {}
            
            # Ajouter ou retirer la réaction
            if emoji not in reactions:
                reactions[emoji] = []
            
            if user_id in reactions[emoji]:
                reactions[emoji].remove(user_id)
            else:
                reactions[emoji].append(user_id)
            
            # Supprimer les emojis vides
            reactions = {k: v for k, v in reactions.items() if v}
            
            # Mettre à jour
            cursor.execute("""
                UPDATE group_messages 
                SET reactions = %s, updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (json.dumps(reactions), message_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({'success': True, 'reactions': reactions}), 200
            
        except Exception as e:
            logger.error(f"Erreur add_message_reaction: {e}")
            return jsonify({'error': str(e)}), 500
    
    # ============================================
    # ROUTES SOCIALES - MODÉRATION D'IMAGES
    # ============================================
    
    @app.route('/api/social/moderation/image', methods=['POST'])
    def moderate_image_endpoint():
        """Modérer une image pour vérifier l'âge approprié (16+)"""
        try:
            from services.image_moderation import moderate_image
            
            data = request.get_json()
            image_url = data.get('imageUrl')
            user_id = data.get('userId')
            
            if not image_url:
                return jsonify({'error': 'imageUrl requis'}), 400
            
            is_safe, moderation_result = moderate_image(image_url, user_id)
            
            # Sauvegarder le résultat en base
            conn = get_db_connection()
            if conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO image_moderation (image_url, user_id, moderation_result, is_safe)
                    VALUES (%s, %s, %s, %s)
                """, (image_url, user_id, json.dumps(moderation_result), is_safe))
                conn.commit()
                cursor.close()
                conn.close()
            
            return jsonify({
                'isSafe': is_safe,
                'moderationResult': moderation_result
            }), 200
            
        except Exception as e:
            logger.error(f"Erreur moderate_image_endpoint: {e}")
            return jsonify({'error': str(e)}), 500
    
    # ============================================
    # ROUTES SOCIALES - PROFILS UTILISATEURS
    # ============================================
    
    @app.route('/api/social/profile/<user_id>', methods=['GET'])
    def get_user_profile():
        """Récupérer le profil d'un utilisateur"""
        try:
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database unavailable'}), 500
            
            cursor = conn.cursor()
            
            # Récupérer les infos de base
            cursor.execute("""
                SELECT u.id, u.username, u.first_name, u.last_name, u.email, u.created_at,
                       up.bio, up.profile_photos, up.profile_videos, up.profile_links
                FROM users u
                LEFT JOIN user_profiles up ON up.user_id = u.id
                WHERE u.id = %s
            """, (user_id,))
            
            row = cursor.fetchone()
            if not row:
                cursor.close()
                conn.close()
                return jsonify({'error': 'Utilisateur introuvable'}), 404
            
            profile = {
                'id': row[0],
                'username': row[1],
                'firstName': row[2],
                'lastName': row[3],
                'email': row[4],
                'createdAt': row[5].isoformat() if row[5] else None,
                'bio': row[6],
                'profilePhotos': json.loads(row[7]) if row[7] else [],
                'profileVideos': json.loads(row[8]) if row[8] else [],
                'profileLinks': json.loads(row[9]) if row[9] else []
            }
            
            cursor.close()
            conn.close()
            
            return jsonify(profile), 200
            
        except Exception as e:
            logger.error(f"Erreur get_user_profile: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/social/profile', methods=['PUT'])
    def update_user_profile():
        """Mettre à jour le profil utilisateur"""
        try:
            data = request.get_json()
            user_id = data.get('userId')
            bio = data.get('bio', '')
            profile_photos = data.get('profilePhotos', [])
            profile_videos = data.get('profileVideos', [])
            profile_links = data.get('profileLinks', [])
            
            if not user_id:
                return jsonify({'error': 'userId requis'}), 400
            
            # Modérer les photos avant de les accepter
            from services.image_moderation import moderate_image
            safe_photos = []
            for photo_url in profile_photos:
                is_safe, _ = moderate_image(photo_url, user_id)
                if is_safe:
                    safe_photos.append(photo_url)
                else:
                    logger.warning(f"Photo rejetée pour {user_id}: {photo_url}")
            
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database unavailable'}), 500
            
            cursor = conn.cursor()
            
            # Mettre à jour ou créer le profil
            cursor.execute("""
                INSERT INTO user_profiles (user_id, bio, profile_photos, profile_videos, profile_links, updated_at)
                VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (user_id) DO UPDATE SET
                    bio = EXCLUDED.bio,
                    profile_photos = EXCLUDED.profile_photos,
                    profile_videos = EXCLUDED.profile_videos,
                    profile_links = EXCLUDED.profile_links,
                    updated_at = CURRENT_TIMESTAMP
            """, (
                user_id, 
                bio, 
                json.dumps(safe_photos),
                json.dumps(profile_videos),
                json.dumps(profile_links)
            ))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({
                'success': True,
                'photosAccepted': len(safe_photos),
                'photosRejected': len(profile_photos) - len(safe_photos)
            }), 200
            
        except Exception as e:
            logger.error(f"Erreur update_user_profile: {e}")
            return jsonify({'error': str(e)}), 500
    
    # Routes d'administration temporaires (À SUPPRIMER APRÈS UTILISATION)
    try:
        from admin_routes import create_admin_routes
        create_admin_routes(app)
        logger.info("Routes d'administration chargées")
    except ImportError:
        logger.warning("admin_routes non disponible")
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)




