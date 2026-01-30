"""
Backend Flask pour MapEventAI
API REST pour gérer les événements, bookings et services
"""

import logging
logger = logging.getLogger(__name__)
logger.info("main.py: Starting imports...")

from flask import Flask, request, jsonify
logger.info("main.py: Flask imported")
import os
logger.info("main.py: os imported")
import psycopg2
logger.info("main.py: psycopg2 imported")
import redis
logger.info("main.py: redis imported")
import json
logger.info("main.py: json imported")
import re
logger.info("main.py: re imported")
from datetime import datetime, timedelta
logger.info("main.py: datetime imported")
from typing import Dict, List, Optional
logger.info("main.py: typing imported")
import stripe
logger.info("main.py: stripe imported")
import random
import string
import secrets
from functools import wraps
logger.info("main.py: random/string/secrets imported")
logger.info("main.py: Importing email_sender...")
from services.email_sender import send_translated_email
logger.info("main.py: email_sender imported")
logger.info("main.py: Importing auth...")
from auth import (
    hash_password, verify_password, 
    generate_access_token, generate_refresh_token, verify_token,
    require_auth, get_token_from_request
)
logger.info("main.py: auth imported - ALL IMPORTS DONE")
# WebSocket désactivé pour Lambda (nécessite API Gateway WebSocket séparé)
# from websocket_handler import init_socketio, setup_websocket_handlers

# Configuration du logging (si pas déjà configuré)
if not logging.getLogger().handlers:
    logging.basicConfig(level=logging.INFO)
# logger déjà défini plus haut

def clean_user_text(text):
    """
    Nettoie agressivement un texte utilisateur pour supprimer les caractères spéciaux indésirables.
    Supprime notamment les patterns "om/xxx", les caractères grecs, et autres caractères spéciaux.
    """
    if not text or not isinstance(text, str):
        return text
    
    import re
    
    # Supprimer tous les patterns "om/xxx" ou "xxx/xxx" au début ou dans le texte
    cleaned = re.sub(r'^om/[^\s]*\s*', '', text, flags=re.IGNORECASE)
    cleaned = re.sub(r'om/[^\s]*', '', cleaned, flags=re.IGNORECASE)
    
    # Supprimer tout pattern "xxx/xxx" au début (lettres suivies de /)
    cleaned = re.sub(r'^[a-z]+\/[^\s]*\s*', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'^[A-Z]+\/[^\s]*\s*', '', cleaned)
    
    # Supprimer les patterns avec slash et caractères spéciaux (comme "om/α" ou "om/ε")
    cleaned = re.sub(r'[a-z]+/[αβεγδεζηθικλμνξοπρστυφχψω]', '', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'[a-z]+/[^\w\s]', '', cleaned, flags=re.IGNORECASE)
    
    # Supprimer les caractères spéciaux isolés (symboles Unicode non-ASCII sauf caractères accentués français)
    # Garder seulement les lettres, chiffres, espaces et caractères accentués français
    cleaned = re.sub(r'[^\w\s\u00C0-\u017F\u00E0-\u00FF\u00E9\u00E8\u00EA\u00EB\u00E0\u00E2\u00E7\u00F9\u00FB\u00FC]', '', cleaned)
    
    # Supprimer les slashes restants et caractères bizarres
    cleaned = re.sub(r'/+', '', cleaned)
    cleaned = re.sub(r'[^\w\s\u00C0-\u017F\u00E0-\u00FF\u00E9\u00E8\u00EA\u00EB\u00E0\u00E2\u00E7\u00F9\u00FB\u00FC]', '', cleaned)
    
    # Nettoyer les espaces multiples
    cleaned = re.sub(r'\s+', ' ', cleaned)
    cleaned = cleaned.strip()
    
    return cleaned

def normalize_email(email):
    """
    Canonicalise un email pour éviter les doublons.
    - Lowercase + trim
    - Pour Gmail/Googlemail : retire les points dans la partie locale et retire +tag
    - Retourne l'email canonicalisé
    """
    if not email or not isinstance(email, str):
        return email
    
    email = email.strip().lower()
    
    # Séparer local@domain
    if '@' not in email:
        return email
    
    local_part, domain = email.split('@', 1)
    
    # Pour Gmail et Googlemail, normaliser la partie locale
    if domain in ['gmail.com', 'googlemail.com']:
        # Retirer tous les points
        local_part = local_part.replace('.', '')
        # Retirer +tag (tout ce qui suit +)
        if '+' in local_part:
            local_part = local_part.split('+')[0]
        # Normaliser googlemail.com -> gmail.com
        domain = 'gmail.com'
    
    return f"{local_part}@{domain}"

def build_user_slim(user_row_or_dict):
    """
    Construit un objet user minimal (slim) pour les réponses API.
    Accepte dict DB ou dict déjà formé.
    Exclut explicitement avatar base64, profilePhoto, avatarDescription, et tous les champs lourds.
    """
    if not user_row_or_dict:
        return {}
    
    # Normaliser en dict si c'est une row DB
    if isinstance(user_row_or_dict, (tuple, list)):
        # Si c'est une row DB, on ne peut pas l'utiliser directement ici
        # Cette fonction attend un dict
        return {}
    
    return {
        "id": str(user_row_or_dict.get("id") or user_row_or_dict.get("user_id") or ""),
        "email": user_row_or_dict.get("email") or user_row_or_dict.get("email_canonical") or "",
        "username": user_row_or_dict.get("username") or "",
        "name": user_row_or_dict.get("name") or f"{(user_row_or_dict.get('first_name') or '').strip()} {(user_row_or_dict.get('last_name') or '').strip()}".strip() or user_row_or_dict.get("username") or "",
        "firstName": user_row_or_dict.get("firstName") or user_row_or_dict.get("first_name") or "",
        "lastName": user_row_or_dict.get("lastName") or user_row_or_dict.get("last_name") or "",
        "role": user_row_or_dict.get("role") or "user",
        "subscription": user_row_or_dict.get("subscription") or "free",
        "profile_photo_url": user_row_or_dict.get("profile_photo_url") or "",
        "hasPassword": bool(user_row_or_dict.get("password_hash")) if "password_hash" in user_row_or_dict else bool(user_row_or_dict.get("hasPassword", False)),
        "hasPostalAddress": bool(user_row_or_dict.get("postal_address") or user_row_or_dict.get("postalAddress")),
        "profileComplete": user_row_or_dict.get("profileComplete", False),
        # Inclure photoData si disponible (photo uploadée depuis le formulaire)
        "photoData": user_row_or_dict.get("photoData") if user_row_or_dict.get("photoData") and user_row_or_dict.get("photoData") != 'null' else None
    }

def sanitize_user_for_response(user_data):
    """
    Nettoie l'objet user pour la réponse API en excluant les champs volumineux.
    
    Whitelist de champs autorisés:
    - id, email, username, name, firstName, lastName
    - subscription, role, profile_photo_url
    - hasPassword, hasPostalAddress
    - postal_address/postalAddress (si présent)
    - createdAt
    
    Exclut explicitement:
    - profilePhoto, avatar (images base64)
    - Tous les tableaux volumineux (likes, favorites, agenda, etc.)
    
    Sécurité: Coupe tout champ string > 5000 chars
    """
    if not user_data or not isinstance(user_data, dict):
        return {}
    
    # Whitelist de champs autorisés
    allowed_fields = {
        'id', 'email', 'username', 'name', 'firstName', 'lastName',
        'subscription', 'role', 'profile_photo_url',
        'hasPassword', 'hasPostalAddress',
        'postal_address', 'postalAddress', 'postalCity', 'postalZip', 'postalCountry',
        'createdAt', 'created_at', 'profileComplete'
    }
    
    # Champs explicitement exclus (images base64, tableaux volumineux)
    excluded_fields = {
        'profilePhoto', 'avatar', 'avatar_emoji', 'avatarDescription',
        'address', 'addresses', 'likes', 'favorites', 'agenda', 'participating',
        'alerts', 'statusAlerts', 'proximityAlerts', 'eventAlarms', 'reviews',
        'friends', 'friendRequests', 'sentRequests', 'blockedUsers',
        'conversations', 'groups', 'profilePhotos', 'profileLinks',
        'history', 'photos', 'eventStatusHistory'
    }
    
    sanitized = {}
    
    for key, value in user_data.items():
        # Ignorer les champs exclus
        if key in excluded_fields:
            continue
        
        # Ne garder que les champs whitelistés
        if key not in allowed_fields:
            continue
        
        # Traitement selon le type
        if value is None:
            sanitized[key] = None
        elif isinstance(value, bool):
            sanitized[key] = value
        elif isinstance(value, (int, float)):
            sanitized[key] = value
        elif isinstance(value, str):
            # SÉCURITÉ: Couper les strings > 5000 chars
            if len(value) > 5000:
                logger.warn(f"⚠️ Champ string trop long ({len(value)} chars) pour {key} - tronqué à 5000")
                sanitized[key] = value[:5000]
            else:
                sanitized[key] = value
        elif isinstance(value, dict):
            # Pour postal_address/postalAddress, garder le dict mais limiter les valeurs
            if key in ('postal_address', 'postalAddress'):
                sanitized_dict = {}
                for k, v in value.items():
                    if isinstance(v, str) and len(v) > 5000:
                        sanitized_dict[k] = v[:5000]
                    else:
                        sanitized_dict[k] = v
                sanitized[key] = sanitized_dict
        else:
            # Convertir en string si type inattendu
            str_value = str(value)
            if len(str_value) > 5000:
                sanitized[key] = str_value[:5000]
            else:
                sanitized[key] = str_value
    
    return sanitized

def create_app():
    """Crée et configure l'application Flask"""
    app = Flask(__name__)
    # Configuration CORS - Autoriser mapevent.world et toutes les origines
    # Note: Quand Access-Control-Allow-Headers est "*", Authorization n'est pas traité
    # Il faut donc lister explicitement les headers
    allowed_origins = [
        "https://mapevent.world",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]
    
    # CORS: Géré manuellement dans @app.after_request et @app.before_request
    # Flask-CORS désactivé pour éviter les headers dupliqués
    
    # DÉSACTIVÉ: Handler OPTIONS géré uniquement dans le handler Lambda
    # Le handler Lambda gère toutes les requêtes OPTIONS et ajoute les headers CORS correctement
    # Cela évite les doublons comme "https://mapevent.world, https://mapevent.world"
    # @app.before_request
    # def handle_preflight():
    #     # DÉSACTIVÉ - CORS géré dans handler.py uniquement
    #     pass
    
    # CORS désactivé dans Flask - géré uniquement dans le handler Lambda
    # Le handler Lambda remplace tous les headers CORS pour éviter les doublons comme "https://mapevent.world, https://mapevent.world"
    @app.after_request
    def after_request(response):
        # SUPPRIMER tous les headers CORS ajoutés par Flask pour éviter les doublons
        # Le handler Lambda les ajoutera correctement avec une seule valeur
        cors_headers_to_remove = [
            'Access-Control-Allow-Origin',
            'Access-Control-Allow-Methods',
            'Access-Control-Allow-Headers',
            'Access-Control-Max-Age',
            'Access-Control-Allow-Credentials',
            'Access-Control-Expose-Headers'
        ]
        for header in cors_headers_to_remove:
            if header in response.headers:
                del response.headers[header]
        return response
    
    # WebSocket désactivé pour Lambda (nécessite API Gateway WebSocket séparé)
    # Pour activer WebSocket, voir WEBSOCKET_SETUP.md
    # socketio = init_socketio(app)
    # setup_websocket_handlers(socketio)
    
    # Configuration depuis les variables d'environnement Lambda
    # Dans Lambda, utiliser directement os.environ (dictionnaire) pour accéder aux variables
    app.config['RDS_HOST'] = os.environ.get('RDS_HOST', '')
    app.config['RDS_PORT'] = os.environ.get('RDS_PORT', '5432')
    app.config['RDS_DB'] = os.environ.get('RDS_DB', 'mapevent')
    app.config['RDS_USER'] = os.environ.get('RDS_USER', '')
    app.config['RDS_PASSWORD'] = os.environ.get('RDS_PASSWORD', '')
    
    # Debug: Afficher les valeurs chargées
    print("Variables RDS chargees:")
    print(f"   RDS_HOST: {app.config['RDS_HOST'][:30]}..." if len(app.config['RDS_HOST']) > 30 else f"   RDS_HOST: {app.config['RDS_HOST']}")
    print(f"   RDS_PORT: {app.config['RDS_PORT']}")
    print(f"   RDS_DB: {app.config['RDS_DB']}")
    print(f"   RDS_USER: {app.config['RDS_USER']}")
    print(f"   RDS_PASSWORD length: {len(app.config['RDS_PASSWORD']) if app.config['RDS_PASSWORD'] else 0}")
    
    app.config['REDIS_HOST'] = os.getenv('REDIS_HOST', '')
    app.config['REDIS_PORT'] = os.getenv('REDIS_PORT', '6379')
    
    # Configuration Stripe
    stripe_key = os.getenv('STRIPE_SECRET_KEY', '')
    stripe.api_key = stripe_key
    app.config['STRIPE_PUBLIC_KEY'] = os.getenv('STRIPE_PUBLIC_KEY', '')
    app.config['STRIPE_WEBHOOK_SECRET'] = os.getenv('STRIPE_WEBHOOK_SECRET', '')
    
    # Debug Stripe
    print(f"[STRIPE] API Key configurée: {'OUI (' + stripe_key[:10] + '...)' if stripe_key else 'NON - MANQUANTE!'}")
    print(f"[STRIPE] stripe.api_key set: {bool(stripe.api_key)}")
    print(f"[STRIPE] stripe.checkout disponible: {hasattr(stripe, 'checkout') and stripe.checkout is not None}")
    
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
            logger.info("Connexion RDS reussie")
            return conn
        except Exception as e:
            error_msg = f"Erreur connexion DB: {e}"
            logger.error(error_msg)
            import traceback
            print(traceback.format_exc())
            return None
    
    def get_redis_connection(timeout=0.15):
        """Crée une connexion à Redis avec timeout optionnel (défaut 200ms)"""
        try:
            r = redis.Redis(
                host=app.config['REDIS_HOST'],
                port=int(app.config['REDIS_PORT']),
                decode_responses=True,
                socket_connect_timeout=timeout,
                socket_timeout=timeout
            )
            r.ping()  # Tester la connexion
            return r
        except Exception as e:
            logger.error(f"Erreur connexion Redis: {e}")
            return None
    
    def get_client_ip():
        """Récupère l'IP du client depuis les headers de requête"""
        # Vérifier les headers proxy (X-Forwarded-For, X-Real-IP)
        if request.headers.get('X-Forwarded-For'):
            # Prendre la première IP (client réel)
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()
        if request.headers.get('X-Real-IP'):
            return request.headers.get('X-Real-IP')
        # Fallback sur remote_addr
        return request.remote_addr or 'unknown'
    
    def rate_limit(max_attempts=5, window_seconds=60, key_prefix='rate_limit'):
        """
        Décorateur de rate limiting pour protéger contre les attaques par force brute.
        
        Args:
            max_attempts: Nombre maximum de tentatives autorisées
            window_seconds: Fenêtre de temps en secondes
            key_prefix: Préfixe pour la clé Redis
        
        Returns:
            Décorateur qui applique le rate limiting
        """
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Récupérer l'IP du client
                client_ip = get_client_ip()
                endpoint_name = func.__name__
                
                # Clé Redis pour ce client + endpoint
                rate_limit_key = f"{key_prefix}:{endpoint_name}:{client_ip}"
                
                # Vérifier le rate limiting avec Redis
                redis_conn = get_redis_connection()
                if redis_conn:
                    try:
                        # Récupérer le nombre de tentatives actuelles
                        attempts = redis_conn.get(rate_limit_key)
                        
                        if attempts:
                            attempts = int(attempts)
                            if attempts >= max_attempts:
                                # Trop de tentatives - bloquer
                                ttl = redis_conn.ttl(rate_limit_key)
                                remaining_seconds = ttl if ttl > 0 else window_seconds
                                
                                logger.warning(f"🚫 Rate limit dépassé pour {endpoint_name} - IP: {client_ip} ({attempts}/{max_attempts} tentatives)")
                                
                                return jsonify({
                                    'error': f'Trop de tentatives. Veuillez réessayer dans {remaining_seconds} secondes.',
                                    'rate_limited': True,
                                    'retry_after': remaining_seconds
                                }), 429
                            
                            # Incrémenter le compteur
                            redis_conn.incr(rate_limit_key)
                        else:
                            # Première tentative - créer la clé avec expiration
                            redis_conn.setex(rate_limit_key, window_seconds, 1)
                        
                    except Exception as redis_error:
                        # Si Redis échoue, logger mais continuer (graceful degradation)
                        logger.warning(f"⚠️ Rate limiting Redis indisponible pour {endpoint_name}: {redis_error}")
                        # Continuer sans bloquer si Redis est indisponible
                
                # Exécuter la fonction originale
                return func(*args, **kwargs)
            
            return wrapper
        return decorator
    
    # Routes API
    
    @app.route('/health', methods=['GET'])
    @app.route('/api/health', methods=['GET'])
    def health():
        """Vérification de santé de l'API - Sans DB, sans Stripe, toujours 200"""
        return jsonify({'ok': True}), 200
    
    @app.route('/api/health/db', methods=['GET'])
    def health_db():
        """Test de connexion à la base de données PostgreSQL"""
        try:
            conn = get_db_connection()
            if not conn:
                return jsonify({'ok': False, 'error': 'Database connection failed'}), 500
            
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            result = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if result and result[0] == 1:
                return jsonify({'ok': True, 'db': 'connected'}), 200
            else:
                return jsonify({'ok': False, 'error': 'Database query failed'}), 500
        except Exception as e:
            logger.error(f"Erreur health_db: {e}")
            return jsonify({'ok': False, 'error': str(e)}), 500
    
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
    
    @app.route('/api/user/send-verification-link', methods=['POST'])
    def send_verification_link():
        """Envoie un lien magique de vérification par email (plus professionnel qu'un code)."""
        try:
            data = request.get_json()
            email = data.get('email', '').strip().lower()
            username = data.get('username', '')
            
            if not email:
                return jsonify({'error': 'Email requis'}), 400
            
            # Générer un token sécurisé (32 caractères hexadécimaux)
            token = secrets.token_urlsafe(32)
            
            # URL de vérification
            base_url = os.getenv('FRONTEND_URL', 'https://mapevent.world')
            verification_url = f"{base_url}/verify-email?token={token}&email={email}"
            
            # Vérifier le rate limiting avec Redis (optionnel)
            redis_conn = None
            try:
                redis_conn = get_redis_connection()
            except Exception as redis_error:
                logger.warning(f"Redis non disponible pour lien magique: {redis_error}")
                redis_conn = None
            
            if redis_conn:
                try:
                    # Clé pour limiter les envois (1 par 5 minutes par email)
                    rate_limit_key = f"email_verification_rate:{email}"
                    last_sent = redis_conn.get(rate_limit_key)
                    
                    if last_sent:
                        time_since_last = datetime.utcnow() - datetime.fromisoformat(last_sent)
                        if time_since_last.total_seconds() < 300:  # 5 minutes
                            remaining = int(300 - time_since_last.total_seconds())
                            return jsonify({
                                'error': f'Veuillez patienter {remaining} secondes avant de renvoyer',
                                'rate_limited': True
                            }), 429
                    
                    # Stocker le token dans Redis avec expiration (24 heures)
                    token_key = f"email_verification_token:{email}"
                    redis_conn.setex(token_key, 86400, token)  # 24 heures
                    
                    # Enregistrer l'heure d'envoi
                    redis_conn.setex(rate_limit_key, 300, datetime.utcnow().isoformat())
                except Exception as redis_error:
                    logger.warning(f"Erreur Redis lors du stockage du token: {redis_error}")
                    # Continuer même si Redis échoue - on stockera en DB si nécessaire
            
            # Envoyer l'email avec le lien
            sendgrid_configured = bool(os.getenv('SENDGRID_API_KEY', '').strip())
            email_sent = False
            
            if sendgrid_configured:
                try:
                    email_sent = send_translated_email(
                        to_email=email,
                        template_name='email_verification_link',
                        template_vars={
                            'username': username if username else 'Utilisateur',
                            'verification_url': verification_url,
                            'expires_in': '24'
                        },
                        target_language='fr'
                    )
                    
                    if email_sent:
                        logger.info(f"✅ Lien de vérification envoyé à {email}")
                        return jsonify({
                            'success': True,
                            'message': 'Lien de vérification envoyé avec succès',
                            'expires_in': 86400,  # 24 heures
                            'email_sent': True
                        }), 200
                    else:
                        logger.error(f"❌ Échec envoi email à {email}")
                        # Continuer pour stocker le token même si l'email n'a pas été envoyé
                except Exception as email_error:
                    logger.error(f"❌ Erreur envoi email: {email_error}")
                    import traceback
                    logger.error(traceback.format_exc())
                    # Continuer pour stocker le token même si l'email échoue
            
            # Si Redis n'est pas disponible, stocker le token en base de données comme fallback
            if not redis_conn:
                try:
                    conn = get_db_connection()
                    if conn:
                        cursor = conn.cursor()
                        # Créer une table temporaire pour les tokens si elle n'existe pas
                        cursor.execute("""
                            CREATE TABLE IF NOT EXISTS email_verification_tokens (
                                email VARCHAR(255) PRIMARY KEY,
                                token VARCHAR(255) NOT NULL,
                                expires_at TIMESTAMP NOT NULL,
                                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                            )
                        """)
                        # Stocker le token
                        expires_at = datetime.utcnow() + timedelta(hours=24)
                        cursor.execute("""
                            INSERT INTO email_verification_tokens (email, token, expires_at)
                            VALUES (%s, %s, %s)
                            ON CONFLICT (email) DO UPDATE SET token = %s, expires_at = %s
                        """, (email, token, expires_at, token, expires_at))
                        conn.commit()
                        cursor.close()
                        conn.close()
                        logger.info(f"Token stocké en base de données pour {email}")
                except Exception as db_error:
                    logger.warning(f"Impossible de stocker le token en DB: {db_error}")
            
            # Mode développement : afficher le lien dans les logs
            logger.info(f"🔗 LIEN DE VÉRIFICATION: {verification_url}")
            logger.info(f"   Email: {email}")
            logger.info(f"   Token: {token}")
            
            # Retourner le résultat avec email_sent pour que le frontend sache si l'email a été envoyé
            if not sendgrid_configured:
                logger.warning("⚠️ SENDGRID_API_KEY non configurée - email non envoyé")
                return jsonify({
                    'success': False,
                    'error': 'SENDGRID_API_KEY non configurée. Impossible d\'envoyer l\'email.',
                    'email_sent': False,
                    'dev_mode': True,
                    'verification_url': verification_url  # Retourner le lien en mode dev
                }), 500
            elif not email_sent:
                logger.error(f"❌ Échec envoi email à {email}")
                return jsonify({
                    'success': False,
                    'error': 'Impossible d\'envoyer l\'email. Vérifiez votre configuration SendGrid.',
                    'email_sent': False,
                    'dev_mode': True,
                    'verification_url': verification_url  # Retourner le lien en mode dev
                }), 500
            else:
                # Email envoyé avec succès
                return jsonify({
                    'success': True,
                    'message': 'Lien de vérification envoyé avec succès',
                    'expires_in': 86400,
                    'email_sent': True
                }), 200
            
        except Exception as e:
            logger.error(f"Erreur send_verification_link: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/user/send-verification-code', methods=['POST'])
    def send_verification_code():
        """Envoie un code de vérification à 6 chiffres par email (ancienne méthode, gardée pour compatibilité)."""
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
                        'code': str(code),
                        'expires_in': '15'
                    },
                    target_language='fr'  # Par défaut en français, peut être détecté automatiquement
                )
                
                if email_sent:
                    logger.info(f"✅ Code de vérification envoyé à {email}")
                    return jsonify({
                        'success': True,
                        'message': 'Code envoyé avec succès',
                        'expires_in': 900,  # 15 minutes en secondes
                        'email_sent': True
                    }), 200
                else:
                    logger.error(f"❌ Échec envoi email à {email}")
                    # Retourner une erreur si l'email n'a pas pu être envoyé
                    return jsonify({
                        'success': False,
                        'error': 'Impossible d\'envoyer l\'email. Vérifiez votre configuration SendGrid.',
                        'email_sent': False,
                        'dev_mode': True,
                        'code': code  # En mode dev, retourner le code pour debug
                    }), 500
                    
            except Exception as email_error:
                logger.error(f"❌ Erreur envoi email: {email_error}")
                import traceback
                logger.error(traceback.format_exc())
                # Retourner une erreur avec le code en mode développement
                return jsonify({
                    'success': False,
                    'error': f'Erreur lors de l\'envoi de l\'email: {str(email_error)}',
                    'email_sent': False,
                    'dev_mode': True,
                    'code': code  # En mode dev, retourner le code pour debug
                }), 500
            
        except Exception as e:
            logger.error(f"Erreur send_verification_code: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/user/verify-email-link', methods=['GET'])
    def verify_email_link():
        """Vérifie l'email via un lien magique (token dans l'URL)."""
        try:
            token = request.args.get('token', '')
            email = request.args.get('email', '').strip().lower()
            
            if not token or not email:
                return jsonify({'error': 'Token et email requis'}), 400
            
            # Vérifier le token dans Redis ou en base de données
            redis_conn = None
            stored_token = None
            
            try:
                redis_conn = get_redis_connection()
                if redis_conn:
                    token_key = f"email_verification_token:{email}"
                    stored_token = redis_conn.get(token_key)
                    if stored_token:
                        stored_token = stored_token.decode() if isinstance(stored_token, bytes) else stored_token
            except Exception as redis_error:
                logger.warning(f"Redis non disponible pour vérification: {redis_error}")
            
            # Fallback: vérifier en base de données
            if not stored_token:
                try:
                    conn = get_db_connection()
                    if conn:
                        cursor = conn.cursor()
                        cursor.execute("""
                            SELECT token, expires_at FROM email_verification_tokens
                            WHERE email = %s AND expires_at > CURRENT_TIMESTAMP
                        """, (email,))
                        result = cursor.fetchone()
                        if result:
                            stored_token = result[0]
                        cursor.close()
                        conn.close()
                except Exception as db_error:
                    logger.warning(f"Erreur DB lors de la vérification: {db_error}")
            
            if not stored_token:
                return jsonify({
                    'error': 'Lien expiré ou invalide. Veuillez demander un nouveau lien.',
                    'code': 'TOKEN_EXPIRED'
                }), 400
            
            # Vérifier le token
            if token != stored_token:
                return jsonify({
                    'error': 'Lien invalide',
                    'code': 'INVALID_TOKEN'
                }), 400
            
            # Token valide - marquer l'email comme vérifié dans la DB
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Erreur de connexion à la base de données'}), 500
            
            cursor = conn.cursor()
            
            # Vérifier si l'utilisateur existe
            cursor.execute("SELECT id, email, username, role FROM users WHERE LOWER(email) = %s LIMIT 1", (email,))
            user_row = cursor.fetchone()
            
            if not user_row:
                cursor.close()
                conn.close()
                return jsonify({'error': 'Utilisateur non trouvé'}), 404
            
            user_id, user_email, username, user_role = user_row
            
            # Mettre à jour email_verified
            try:
                cursor.execute("""
                    UPDATE users 
                    SET email_verified = TRUE, updated_at = %s
                    WHERE LOWER(email) = %s
                """, (datetime.utcnow(), email))
                conn.commit()
                logger.info(f"✅ Email vérifié via lien magique: {email}")
            except Exception as db_error:
                logger.warning(f"Colonne email_verified peut-être absente: {db_error}")
                # Continuer même si la colonne n'existe pas
            
            # Générer les tokens pour connexion automatique
            access_token = generate_access_token(user_id, user_email, user_role or 'user')
            refresh_token = generate_refresh_token(user_id)
            
            cursor.close()
            conn.close()
            
            # Supprimer le token (one-time use)
            try:
                if redis_conn:
                    token_key = f"email_verification_token:{email}"
                    redis_conn.delete(token_key)
            except Exception:
                pass
            
            # Supprimer aussi de la base de données
            try:
                conn = get_db_connection()
                if conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM email_verification_tokens WHERE email = %s", (email,))
                    conn.commit()
                    cursor.close()
                    conn.close()
            except Exception:
                pass
            
            # Rediriger vers la page de succès avec les tokens
            base_url = os.getenv('FRONTEND_URL', 'https://mapevent.world')
            return jsonify({
                'success': True,
                'message': 'Email vérifié avec succès',
                'accessToken': access_token,
                'refreshToken': refresh_token,
                'userId': user_id,
                'email': user_email,
                'username': username,
                'redirect_url': f"{base_url}/verify-email?token={access_token}&refresh={refresh_token}&email={user_email}"
            }), 200
            
        except Exception as e:
            logger.error(f"Erreur verify_email_link: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/user/verify-email', methods=['POST'])
    def verify_email():
        """Vérifie le code de vérification d'email et marque l'email comme vérifié (ancienne méthode)."""
        try:
            data = request.get_json()
            email = data.get('email', '').strip().lower()
            code = data.get('code', '')
            
            if not email:
                return jsonify({'error': 'Email requis'}), 400
            
            if not code or len(code) != 6 or not code.isdigit():
                return jsonify({'error': 'Code invalide (6 chiffres requis)'}), 400
            
            # Vérifier le code dans Redis
            redis_conn = get_redis_connection()
            if not redis_conn:
                return jsonify({'error': 'Service de vérification temporairement indisponible'}), 503
            
            code_key = f"email_verification_code:{email}"
            stored_code = redis_conn.get(code_key)
            
            if not stored_code:
                return jsonify({
                    'error': 'Code expiré ou invalide. Veuillez demander un nouveau code.',
                    'code': 'CODE_EXPIRED'
                }), 400
            
            # Vérifier le code
            stored_code_str = stored_code.decode() if isinstance(stored_code, bytes) else stored_code
            if code != stored_code_str:
                return jsonify({
                    'error': 'Code incorrect',
                    'code': 'INVALID_CODE'
                }), 400
            
            # Code valide - supprimer le code (one-time use)
            redis_conn.delete(code_key)
            
            # Marquer l'email comme vérifié dans la base de données
            conn = get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    # Mettre à jour le champ email_verified si la colonne existe
                    try:
                        cursor.execute("""
                            UPDATE users 
                            SET email_verified = TRUE 
                            WHERE LOWER(email) = %s
                        """, (email,))
                        conn.commit()
                    except Exception as db_error:
                        # Si la colonne n'existe pas, ce n'est pas grave
                        logger.warning(f"Colonne email_verified peut-être absente: {db_error}")
                    finally:
                        cursor.close()
                        conn.close()
                except Exception as db_error:
                    logger.error(f"Erreur DB lors de la vérification: {db_error}")
                    # Continuer même si la DB échoue
            
            logger.info(f"✅ Email vérifié: {email}")
            return jsonify({
                'success': True,
                'message': 'Email vérifié avec succès',
                'email': email
            }), 200
            
        except Exception as e:
            logger.error(f"Erreur verify_email: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({'error': str(e)}), 500
    
    # ============================================
    # ROUTE D'INSCRIPTION UTILISATEUR
    # ============================================
    
    @app.route('/api/user/exists', methods=['GET'])
    def user_exists():
        """Vérifier si un email ou username existe déjà (ultra rapide pour pré-check)"""
        try:
            email = request.args.get('email')
            username = request.args.get('username')
            
            if not email and not username:
                return jsonify({'error': 'email ou username requis'}), 400
            
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = conn.cursor()
            
            exists = False
            field = None
            
            if email:
                cursor.execute("SELECT id FROM users WHERE LOWER(email) = %s LIMIT 1", (email.lower(),))
                if cursor.fetchone():
                    exists = True
                    field = 'email'
            
            if not exists and username:
                cursor.execute("SELECT id FROM users WHERE LOWER(username) = %s LIMIT 1", (username.lower(),))
                if cursor.fetchone():
                    exists = True
                    field = 'username'
            
            cursor.close()
            conn.close()
            
            return jsonify({
                'exists': exists,
                'field': field
            }), 200
            
        except Exception as e:
            logger.error(f"Erreur user_exists: {e}")
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/user/register', methods=['POST'])
    @rate_limit(max_attempts=5, window_seconds=300, key_prefix='register')  # 5 tentatives par 5 minutes
    def user_register():
        """Crée un nouveau compte utilisateur avec vérification d'email obligatoire."""
        try:
            data = request.get_json()
            email = data.get('email', '').strip().lower()
            username_raw = data.get('username', '').strip()
            # NETTOYER le username pour supprimer les caractères spéciaux indésirables
            username = clean_user_text(username_raw)
            password = data.get('password', '')
            # NETTOYER immédiatement le mot de passe de la mémoire après traitement
            # (ne pas le logger ni l'exposer dans les erreurs)
            password_for_validation = password  # Copie pour validation
            password = None  # Nettoyer la variable originale
            password = password_for_validation  # Réassigner pour hashage
            
            # ⚠️ firstName et lastName sont OPTIONNELS (comme les leaders mondiaux)
            first_name_raw = data.get('firstName', '').strip()
            last_name_raw = data.get('lastName', '').strip()
            # NETTOYER firstName et lastName seulement s'ils sont fournis
            first_name = clean_user_text(first_name_raw) if first_name_raw else ''
            last_name = clean_user_text(last_name_raw) if last_name_raw else ''
            avatar_id = data.get('avatarId', 1)
            avatar_emoji = data.get('avatarEmoji', '👤')
            avatar_description = data.get('avatarDescription', '')
            addresses = data.get('addresses', [])
            verification_code = data.get('verificationCode', '')  # Code de vérification
            
            # Validation des champs obligatoires
            logger.info(f"Validation champs - email: {bool(email)}, username: {bool(username)}, password: {bool(password)}, first_name: {bool(first_name)}, last_name: {bool(last_name)}")
            # ⚠️ firstName et lastName sont OPTIONNELS (comme les leaders mondiaux : Twitter, Instagram, TikTok)
            # Seul username est requis pour l'identification
            if not email or not username or not password:
                missing = []
                if not email: missing.append('email')
                if not username: missing.append('username')
                if not password: missing.append('password')
                # ⚠️ firstName et lastName sont OPTIONNELS (comme les leaders mondiaux)
                # Ne pas les ajouter à la liste des champs manquants
                logger.warning(f"Champs manquants: {', '.join(missing)}")
                return jsonify({'error': f'Champs requis manquants: {", ".join(missing)}'}), 400
            
            # ⚠️ firstName et lastName sont OPTIONNELS - validation seulement si fournis
            # Si fournis, valider le format (mais ne pas exiger)
            if first_name or last_name:
                logger.info(f"Validation nom/prenom optionnels - first_name: '{first_name}', last_name: '{last_name}'")
                name_regex = r'^[a-zA-ZàáâäãåèéêëìíîïòóôöõùúûüýÿñçÀÁÂÄÃÅÈÉÊËÌÍÎÏÒÓÔÖÕÙÚÛÜÝŸÑÇ\s-]{2,30}$'
                if first_name and not re.match(name_regex, first_name):
                    logger.warning(f"Format prenom invalide: '{first_name}'")
                    return jsonify({'error': 'Prénom invalide (2-30 caractères, lettres uniquement)'}), 400
                if last_name and not re.match(name_regex, last_name):
                    logger.warning(f"Format nom invalide: '{last_name}'")
                    return jsonify({'error': 'Nom invalide (2-30 caractères, lettres uniquement)'}), 400
                logger.info("Validation nom/prenom optionnels OK")
            
            # Validation format email
            logger.info("Validation format email...")
            email_regex = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
            if not re.match(email_regex, email):
                return jsonify({'error': 'Format email invalide'}), 400
            logger.info("Validation email OK")
            
            # Validation username (3-20 caractères, alphanumériques + _ et -)
            logger.info(f"Validation username... username='{username}', length={len(username) if username else 0}")
            username_regex = r'^[a-zA-Z0-9_-]{3,20}$'
            if not re.match(username_regex, username):
                logger.warning(f"Username invalide: '{username}' (length: {len(username) if username else 0})")
                return jsonify({'error': 'Username invalide (3-20 caractères, lettres, chiffres, _ et -)'}), 400
            logger.info("Validation username OK")
            
            # Validation mot de passe RENFORCÉE (12+ caractères, complexité requise)
            logger.info("Validation mot de passe...")
            if len(password) < 12:
                return jsonify({'error': 'Mot de passe trop court (minimum 12 caractères requis)'}), 400
            
            # Vérifier la complexité du mot de passe
            has_upper = any(c.isupper() for c in password)
            has_lower = any(c.islower() for c in password)
            has_digit = any(c.isdigit() for c in password)
            has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)
            
            if not has_upper:
                return jsonify({'error': 'Le mot de passe doit contenir au moins une majuscule'}), 400
            if not has_lower:
                return jsonify({'error': 'Le mot de passe doit contenir au moins une minuscule'}), 400
            if not has_digit:
                return jsonify({'error': 'Le mot de passe doit contenir au moins un chiffre'}), 400
            if not has_special:
                return jsonify({'error': 'Le mot de passe doit contenir au moins un caractère spécial (!@#$%^&*...)'}), 400
            
            # Vérifier contre une liste de mots de passe communs
            common_passwords = ['password', 'password123', '12345678', '123456789', '1234567890', 
                              'qwerty', 'abc123', 'monkey', '1234567', 'letmein', 'trustno1',
                              'dragon', 'baseball', 'iloveyou', 'master', 'sunshine', 'ashley',
                              'bailey', 'passw0rd', 'shadow', '123123', '654321', 'superman',
                              'qazwsx', 'michael', 'football', 'welcome', 'jesus', 'ninja',
                              'mustang', 'password1', '123qwe', 'admin', 'login', 'princess']
            if password.lower() in [p.lower() for p in common_passwords]:
                return jsonify({'error': 'Ce mot de passe est trop commun. Veuillez en choisir un autre.'}), 400
            logger.info("Validation mot de passe OK")
            
            # PRIORITÉ 1: Vérifier email/username en PREMIER (avant Redis, avant tout)
            logger.info("Vérification email/username uniques en DB...")
            # Cela permet de retourner 409 en <200ms si conflit
            conn = get_db_connection()
            if not conn:
                logger.error("❌ Connexion DB échouée pour user_register")
                return jsonify({'error': 'Erreur de connexion à la base de données'}), 500
            
            logger.info("✅ Connexion DB réussie, création du cursor...")
            cursor = conn.cursor()
            logger.info("✅ Cursor créé")
            
            # Vérifier email unique (CHECK IMMÉDIAT)
            logger.info(f"Vérification email unique: {email}")
            try:
                cursor.execute("SELECT id FROM users WHERE LOWER(email) = %s LIMIT 1", (email,))
                existing_email = cursor.fetchone()
                logger.info(f"Résultat vérification email: {existing_email}")
                if existing_email:
                    cursor.close()
                    conn.close()
                    logger.info(f"⚠️ Email déjà utilisé: {email}")
                    return jsonify({
                        'error': 'Cet email est déjà utilisé',
                        'code': 'EMAIL_ALREADY_EXISTS'
                    }), 409
            except Exception as email_check_error:
                logger.error(f"❌ Erreur lors de la vérification email: {email_check_error}")
                import traceback
                logger.error(traceback.format_exc())
                cursor.close()
                conn.close()
                return jsonify({'error': 'Erreur lors de la vérification de l\'email'}), 500
            
            # Vérifier username unique (CHECK IMMÉDIAT)
            logger.info(f"Vérification username unique: {username}")
            try:
                cursor.execute("SELECT id FROM users WHERE LOWER(username) = %s LIMIT 1", (username.lower(),))
                existing_username = cursor.fetchone()
                logger.info(f"Résultat vérification username: {existing_username}")
                if existing_username:
                    cursor.close()
                    conn.close()
                    logger.info(f"⚠️ Username déjà pris: {username}")
                    return jsonify({
                        'error': 'Ce nom d\'utilisateur est déjà pris',
                        'code': 'USERNAME_ALREADY_EXISTS'
                    }), 409
            except Exception as username_check_error:
                logger.error(f"❌ Erreur lors de la vérification username: {username_check_error}")
                import traceback
                logger.error(traceback.format_exc())
                cursor.close()
                conn.close()
                return jsonify({'error': 'Erreur lors de la vérification du username'}), 500
            
            logger.info("✅ Email et username uniques confirmés")
            
            # VÉRIFICATION EMAIL - DÉSACTIVÉE pour inscription email/mot de passe
            # Les leaders mondiaux (Reddit, Twitter, etc.) n'utilisent pas de vérification email
            # pour l'inscription standard. Ils utilisent principalement OAuth (Google, GitHub, etc.)
            # qui évite complètement le besoin de vérification.
            # 
            # SendGrid reste disponible pour d'autres usages (notifications, réinitialisation mot de passe, etc.)
            # mais n'est PAS utilisé pour la vérification lors de l'inscription.
            #
            # On vérifie uniquement que l'email n'est pas déjà utilisé (fait plus haut ligne 1769-1777).
            email_verified = True  # Toujours vérifié pour inscription email/mot de passe
            logger.info(f"ℹ️ Création de compte sans vérification email (comme les leaders mondiaux) pour: {email}")
            
            # VÉRIFICATION DES ADRESSES : Optionnelles mais si fournies, doivent être vérifiées
            address_label = None
            address_lat = None
            address_lng = None
            address_country_code = None
            address_city = None
            address_postcode = None
            address_street = None
            
            if addresses and len(addresses) > 0:
                # Prendre la première adresse comme adresse principale
                addr = addresses[0]
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
                
                # Extraire les données d'adresse
                address_label = addr.get('label', '')
                address_lat = lat
                address_lng = lng
                address_country_code = address_details.get('country_code', '').upper()
                address_city = address_details.get('city', '')
                address_postcode = address_details.get('postcode', '')
                address_street = address_details.get('street', '')
                
                # ⚠️⚠️⚠️ CRITIQUE : ACCEPTATION MONDIALE - Tous les pays du monde sont acceptés
                # MapEvent est une plateforme mondiale : Afrique, Asie, Amériques, Océanie, Europe, etc.
                # Les utilisateurs peuvent créer des événements partout dans le monde
                # La vérification d'adresse via géocodage garantit la validité de l'adresse
                if address_country_code:
                    logger.info(f"✅ Adresse acceptée (monde entier): {address_country_code} - {address_label}")
                # Pas de restriction de pays - accepter toutes les adresses vérifiées par géocodage
            
            # Vérifier qu'il n'y a pas trop de comptes créés depuis la même IP (rate limiting par IP)
            # Note: En production, utiliser request.remote_addr ou un header X-Forwarded-For
            # Pour l'instant, on limite par combinaison nom+prénom+email
            
            # Vérifier la configuration SendGrid et Redis pour les logs
            sendgrid_configured = bool(os.getenv('SENDGRID_API_KEY', '').strip())
            redis_conn = None
            try:
                redis_conn = get_redis_connection()
            except Exception:
                redis_conn = None
            
            logger.info("✅ Toutes les validations passées, prêt pour hashage du mot de passe")
            logger.info(f"Email vérifié: {email_verified}, SendGrid configuré: {sendgrid_configured}, Redis disponible: {redis_conn is not None}")
            
            # Hasher le mot de passe avec bcrypt (OBLIGATOIRE)
            try:
                logger.info("Tentative de hashage du mot de passe avec bcrypt...")
                password_hash, salt = hash_password(password)
                logger.info(f"✅ Mot de passe hashé avec succès (hash length: {len(password_hash)}, salt length: {len(salt)})")
            except Exception as hash_error:
                logger.error(f"❌ ERREUR lors du hashage du mot de passe: {hash_error}")
                import traceback
                logger.error(traceback.format_exc())
                cursor.close()
                conn.close()
                return jsonify({
                    'error': f'Erreur lors du hashage du mot de passe: {str(hash_error)}',
                    'code': 'PASSWORD_HASH_ERROR'
                }), 500
            # NETTOYER le mot de passe de la mémoire immédiatement après hashage
            password = None  # Ne jamais logger ni exposer le mot de passe
            
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
            
            # Ajouter les colonnes d'adresse et privacy si elles n'existent pas
            cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS address_label VARCHAR(500)")
            cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS address_lat DECIMAL(10, 8)")
            cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS address_lng DECIMAL(11, 8)")
            cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS address_country_code VARCHAR(2)")
            cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS address_city VARCHAR(100)")
            cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS address_postcode VARCHAR(20)")
            cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS address_street VARCHAR(200)")
            cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS address_verified BOOLEAN DEFAULT FALSE")
            cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE")
            cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_public BOOLEAN DEFAULT FALSE")
            cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS show_name BOOLEAN DEFAULT FALSE")
            cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS show_photo BOOLEAN DEFAULT FALSE")
            cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS show_city_country_only BOOLEAN DEFAULT FALSE")
            cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_photo_url TEXT")
            
            if has_name_columns:
                # Insérer avec tous les champs (adresse + privacy + email_verified)
                cursor.execute("""
                    INSERT INTO users (id, email, username, first_name, last_name, subscription, 
                                     address_label, address_lat, address_lng, address_country_code, 
                                     address_city, address_postcode, address_street, address_verified,
                                     email_verified, profile_public, show_name, show_photo, show_city_country_only,
                                     created_at, updated_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (user_id, email, username, first_name, last_name, 'free',
                     address_label, address_lat, address_lng, address_country_code,
                     address_city, address_postcode, address_street, 
                     True if address_label else False,  # address_verified
                     email_verified,  # email_verified (True si SendGrid non configuré)
                     False,  # profile_public (privé par défaut)
                     False,  # show_name (privé par défaut)
                     False,  # show_photo (privé par défaut)
                     False,  # show_city_country_only (privé par défaut)
                     created_at, created_at))
            else:
                # Si les colonnes n'existent pas, les créer d'abord
                try:
                    cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS first_name VARCHAR(100)")
                    cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS last_name VARCHAR(100)")
                    conn.commit()
                    logger.info("✅ Colonnes first_name et last_name ajoutées à la table users")
                    
                    cursor.execute("""
                        INSERT INTO users (id, email, username, first_name, last_name, subscription, 
                                         address_label, address_lat, address_lng, address_country_code, 
                                         address_city, address_postcode, address_street, address_verified,
                                         email_verified, profile_public, show_name, show_photo, show_city_country_only,
                                         created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (user_id, email, username, first_name, last_name, 'free',
                         address_label, address_lat, address_lng, address_country_code,
                         address_city, address_postcode, address_street, 
                         True if address_label else False,  # address_verified
                         email_verified,  # email_verified (True si SendGrid non configuré)
                         False,  # profile_public (privé par défaut)
                         False,  # show_name (privé par défaut)
                         False,  # show_photo (privé par défaut)
                         False,  # show_city_country_only (privé par défaut)
                         created_at, created_at))
                except Exception as alter_error:
                    logger.warn(f"Impossible d'ajouter les colonnes: {alter_error}")
                    # Fallback: stocker dans username temporairement
                    cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS email_verified BOOLEAN DEFAULT FALSE")
                    cursor.execute("""
                        INSERT INTO users (id, email, username, subscription, email_verified, created_at, updated_at)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                    """, (user_id, email, f"{first_name} {last_name} ({username})", 'free', email_verified, created_at, created_at))
            
            # Créer la table user_passwords si elle n'existe pas
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_passwords (
                    user_id VARCHAR(255) PRIMARY KEY,
                    password_hash TEXT NOT NULL,
                    salt VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Insérer le hash du mot de passe dans user_passwords
            cursor.execute("""
                INSERT INTO user_passwords (user_id, password_hash, salt, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (user_id) DO UPDATE SET
                    password_hash = EXCLUDED.password_hash,
                    salt = EXCLUDED.salt,
                    updated_at = EXCLUDED.updated_at
            """, (user_id, password_hash, salt, created_at, created_at))
            
            conn.commit()
            
            # MODE TEST: Supprimer automatiquement le compte IMMÉDIATEMENT après création
            # Cela permet de réutiliser le même email pour les tests
            # Désactivez cette section en production
            TEST_MODE_AUTO_DELETE = os.getenv('TEST_MODE_AUTO_DELETE', 'true').lower() == 'true'
            if TEST_MODE_AUTO_DELETE:
                try:
                    logger.info(f"🧪 MODE TEST: Suppression automatique du compte {user_id} après création")
                    # Supprimer le mot de passe
                    cursor.execute("DELETE FROM user_passwords WHERE user_id = %s", (user_id,))
                    # Supprimer l'utilisateur
                    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
                    conn.commit()
                    logger.info(f"✅ Compte {user_id} supprimé automatiquement (mode test)")
                except Exception as delete_error:
                    logger.warning(f"⚠️ Erreur lors de la suppression automatique: {delete_error}")
                    # Ne pas bloquer si la suppression échoue
            
            cursor.close()
            conn.close()
            
            logger.info(f"✅ Nouvel utilisateur créé: {email} ({user_id})")
            
            # ⚠️⚠️⚠️ CRITIQUE : Uploader la photo vers S3 si photoData est fourni
            profile_photo_url = None
            photo_data = data.get('photoData', '')
            if photo_data and photo_data.strip() and photo_data != 'null' and photo_data != 'undefined':
                try:
                    from services.s3_service import upload_avatar_to_s3
                    s3_url = upload_avatar_to_s3(user_id, photo_data)
                    if s3_url:
                        # Mettre à jour profile_photo_url dans la base de données
                        cursor.execute("UPDATE users SET profile_photo_url = %s WHERE id = %s", (s3_url, user_id))
                        conn.commit()
                        profile_photo_url = s3_url
                        logger.info(f"✅ Photo uploadée vers S3 pour {email}: {s3_url[:100]}...")
                    else:
                        logger.warning(f"⚠️ Échec upload photo vers S3 pour {email}")
                except Exception as photo_error:
                    logger.error(f"❌ Erreur upload photo vers S3: {photo_error}")
                    # Ne pas bloquer la création du compte si l'upload de photo échoue
            
            # ⚠️⚠️⚠️ CRITIQUE : Générer les tokens JWT pour connexion automatique (comme les leaders mondiaux)
            # L'utilisateur doit être connecté automatiquement après création du compte
            # Rôle par défaut: 'user' (pas de vérification de directeur ici)
            user_role = 'user'
            access_token = generate_access_token(user_id, email, user_role)
            refresh_token = generate_refresh_token(user_id)
            
            logger.info(f"✅ Tokens générés pour {email} - Connexion automatique activée")
            
            # IMPORTANT: On n'envoie PAS d'email de bienvenue automatique
            # L'utilisateur choisit sa méthode de vérification après le formulaire :
            # - Google OAuth (vérification officielle Google)
            # - Email (envoi d'email de vérification uniquement si demandé)
            # Les leaders mondiaux n'envoient pas d'email de bienvenue automatique
            
            return jsonify({
                'success': True,
                'userId': user_id,
                'id': user_id,  # Pour compatibilité
                'email': email,
                'username': username,
                'firstName': first_name,
                'lastName': last_name,
                'profile_photo_url': profile_photo_url or '',  # URL S3 si photo uploadée
                'photoData': None,  # Ne pas envoyer base64 dans la réponse (trop gros)
                'accessToken': access_token,  # ⚠️⚠️⚠️ CRITIQUE : Token pour connexion automatique
                'refreshToken': refresh_token,  # ⚠️⚠️⚠️ CRITIQUE : Refresh token
                'message': 'Compte créé avec succès' + (' (supprimé automatiquement - mode test)' if TEST_MODE_AUTO_DELETE else '')
            }), 201
            
        except psycopg2.IntegrityError as e:
            logger.error(f"Erreur intégrité DB: {e}")
            if conn:
                conn.rollback()
                conn.close()
            # Vérifier si c'est l'email ou le username qui est dupliqué
            error_msg = str(e).lower()
            if 'email' in error_msg or 'users_email_key' in error_msg:
                return jsonify({
                    'error': 'Un compte existe déjà avec cet email. Connecte-toi.',
                    'code': 'EMAIL_ALREADY_EXISTS',
                    'field': 'email'
                }), 409
            elif 'username' in error_msg or 'users_username_key' in error_msg:
                return jsonify({
                    'error': 'Ce nom d\'utilisateur est déjà pris. Veuillez en choisir un autre.',
                    'code': 'USERNAME_ALREADY_EXISTS',
                    'field': 'username'
                }), 409
            else:
                return jsonify({
                    'error': 'Un compte existe déjà avec cet email. Connecte-toi.',
                    'code': 'USER_ALREADY_EXISTS',
                    'field': 'email'
                }), 409
        except Exception as e:
            logger.error(f"Erreur user_register: {e}")
            import traceback
            logger.error(traceback.format_exc())
            if conn:
                conn.rollback()
                conn.close()
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/auth/login', methods=['POST'])
    @rate_limit(max_attempts=5, window_seconds=300, key_prefix='login')  # 5 tentatives par 5 minutes
    def auth_login():
        """Connecte un utilisateur avec email et mot de passe, retourne JWT tokens."""
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
            
            user_id, user_email, username, first_name, last_name, subscription, role, avatar_emoji, avatar_description, created_at = user_row
            
            # Vérifier le mot de passe depuis user_passwords
            cursor.execute("""
                SELECT password_hash, salt FROM user_passwords 
                WHERE user_id = %s
            """, (user_id,))
            
            password_row = cursor.fetchone()
            if not password_row:
                cursor.close()
                conn.close()
                return jsonify({'error': 'Email ou mot de passe incorrect'}), 401
            
            password_hash, salt = password_row
            
            # Vérifier le mot de passe
            if not verify_password(password, password_hash, salt):
                cursor.close()
                conn.close()
                return jsonify({'error': 'Email ou mot de passe incorrect'}), 401
            
            # Vérifier si l'email correspond à un directeur
            director_emails = ['mapevent777@gmail.com', 'directeur', 'director', 'admin']
            email_lower = email.lower()
            is_director = any(pattern in email_lower for pattern in director_emails)
            final_role = 'director' if is_director else (role or 'user')
            final_subscription = 'vip_plus' if is_director else (subscription or 'free')
            
            # Générer les tokens JWT
            access_token = generate_access_token(user_id, user_email, final_role)
            refresh_token = generate_refresh_token(user_id)
            
            cursor.close()
            conn.close()
            
            user_data = {
                'id': user_id,
                'email': user_email,
                'username': username,
                'name': f"{first_name} {last_name}".strip() if first_name and last_name else username,
                'firstName': first_name or '',
                'lastName': last_name or '',
                'subscription': final_subscription,
                'role': final_role,
                'avatar': avatar_emoji or '',
                'avatarDescription': avatar_description or '',
                'createdAt': created_at.isoformat() if created_at else None
            }
            
            return jsonify({
                'accessToken': access_token,
                'refreshToken': refresh_token,
                'user': user_data
            }), 200
            
        except Exception as e:
            logger.error(f"Erreur auth_login: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/auth/refresh', methods=['POST'])
    def auth_refresh():
        """Rafraîchit un access token avec un refresh token."""
        try:
            data = request.get_json()
            refresh_token = data.get('refreshToken', '')
            
            if not refresh_token:
                return jsonify({'error': 'refreshToken requis'}), 400
            
            # Vérifier le refresh token
            payload = verify_token(refresh_token, token_type='refresh')
            if not payload:
                return jsonify({'error': 'Refresh token invalide ou expiré'}), 401
            
            user_id = payload.get('user_id')
            
            # Récupérer les infos utilisateur pour générer le nouvel access token
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = conn.cursor()
            cursor.execute("""
                SELECT email, role FROM users WHERE id = %s
            """, (user_id,))
            
            user_row = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if not user_row:
                return jsonify({'error': 'Utilisateur non trouvé'}), 404
            
            user_email, user_role = user_row
            
            # Générer un nouvel access token
            access_token = generate_access_token(user_id, user_email, user_role or 'user')
            
            return jsonify({
                'accessToken': access_token
            }), 200
            
        except Exception as e:
            logger.error(f"Erreur auth_refresh: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/auth/logout', methods=['POST'])
    @require_auth
    def auth_logout():
        """
        Déconnecte l'utilisateur.
        
        NOTE IMPORTANTE: La déconnexion est actuellement "client-side only".
        Les refresh tokens ne sont PAS stockés dans la base de données.
        La déconnexion côté serveur consiste uniquement à valider le token d'accès.
        
        Pour invalider les refresh tokens côté serveur, il faudrait:
        1. Créer une table refresh_tokens (user_id, token_hash, expires_at)
        2. Stocker les refresh tokens lors de la génération
        3. Supprimer le refresh token de la table lors du logout
        
        Pour l'instant, la sécurité repose sur:
        - La durée de vie limitée des tokens (15min access, 30j refresh)
        - La suppression côté client des tokens dans localStorage
        """
        try:
            # Pour l'instant, on ne fait que valider le token
            # Plus tard, on pourra ajouter une table refresh_tokens pour invalider côté serveur
            # Pour l'instant, la déconnexion est gérée côté client (suppression des tokens)
            logger.info(f"Logout request from user_id: {request.user_id}")
            return jsonify({'message': 'Déconnexion réussie'}), 200
            
        except Exception as e:
            logger.error(f"Erreur auth_logout: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/user/me', methods=['GET'])
    @require_auth
    def user_me():
        """Récupère le profil de l'utilisateur courant (protégé par JWT)."""
        try:
            user_id = request.user_id
            user_email = request.user_email
            user_role = request.user_role
            is_cognito = getattr(request, 'cognito_token', False)
            
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = conn.cursor()
            
            # Vérifier et créer les colonnes si nécessaire
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS address_verified BOOLEAN DEFAULT false")
                cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_public BOOLEAN DEFAULT false")
                cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS show_name BOOLEAN DEFAULT false")
                cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS show_photo BOOLEAN DEFAULT false")
                cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS show_city_country_only BOOLEAN DEFAULT false")
                conn.commit()
            except Exception as alter_error:
                logger.debug(f"Colonnes privacy déjà existantes ou erreur: {alter_error}")
            
            # CORRECTION COGNITO: Pour les tokens Cognito, chercher par google_sub puis par email
            # car user_id contient le Cognito sub, pas l'ID de la base de données
            user_row = None
            
            if is_cognito:
                # Priorité 1: Chercher par google_sub (le Cognito sub)
                logger.info(f"[USER_ME] Token Cognito détecté, recherche par google_sub: {user_id}")
                cursor.execute("""
                    SELECT id, email, username, first_name, last_name, subscription, role,
                           avatar_emoji, avatar_description, profile_photo_url, postal_address,
                           postal_city, postal_zip, postal_country,
                           address_label, address_lat, address_lng, address_country_code,
                           address_city, address_postcode, address_street, address_verified,
                           profile_public, show_name, show_photo, show_city_country_only,
                           created_at, updated_at
                    FROM users 
                    WHERE google_sub = %s
                """, (user_id,))
                user_row = cursor.fetchone()
                
                # Priorité 2: Si non trouvé par google_sub, chercher par email
                if not user_row and user_email:
                    logger.info(f"[USER_ME] Non trouvé par google_sub, recherche par email: {user_email}")
                    email_canonical = normalize_email(user_email) if user_email else None
                    cursor.execute("""
                        SELECT id, email, username, first_name, last_name, subscription, role,
                               avatar_emoji, avatar_description, profile_photo_url, postal_address,
                               postal_city, postal_zip, postal_country,
                               address_label, address_lat, address_lng, address_country_code,
                               address_city, address_postcode, address_street, address_verified,
                               profile_public, show_name, show_photo, show_city_country_only,
                               created_at, updated_at
                        FROM users 
                        WHERE LOWER(TRIM(email)) = %s OR email_canonical = %s
                    """, (user_email.lower().strip(), email_canonical))
                    user_row = cursor.fetchone()
                    
                    # Si trouvé par email, mettre à jour google_sub pour les prochaines fois
                    if user_row:
                        logger.info(f"[USER_ME] Utilisateur trouvé par email, mise à jour google_sub: {user_id}")
                        try:
                            cursor.execute("UPDATE users SET google_sub = %s WHERE id = %s", (user_id, user_row[0]))
                            conn.commit()
                        except Exception as update_err:
                            logger.warning(f"[USER_ME] Impossible de mettre à jour google_sub: {update_err}")
            else:
                # Token standard (non Cognito): chercher par id
                logger.info(f"[USER_ME] Token standard, recherche par id: {user_id}")
                cursor.execute("""
                    SELECT id, email, username, first_name, last_name, subscription, role,
                           avatar_emoji, avatar_description, profile_photo_url, postal_address,
                           postal_city, postal_zip, postal_country,
                           address_label, address_lat, address_lng, address_country_code,
                           address_city, address_postcode, address_street, address_verified,
                           profile_public, show_name, show_photo, show_city_country_only,
                           created_at, updated_at
                    FROM users 
                    WHERE id = %s
                """, (user_id,))
                user_row = cursor.fetchone()
            
            if not user_row:
                cursor.close()
                conn.close()
                return jsonify({'error': 'Utilisateur non trouvé'}), 404
            
            (user_id_db, email, username, first_name, last_name, subscription, role,
             avatar_emoji, avatar_description, profile_photo_url, postal_address,
             postal_city, postal_zip, postal_country,
             address_label, address_lat, address_lng, address_country_code,
             address_city, address_postcode, address_street, address_verified,
             profile_public, show_name, show_photo, show_city_country_only,
             created_at, updated_at) = user_row
            
            # Récupérer le statut d'abonnement Stripe depuis la table subscriptions (si elle existe)
            # IMPORTANT: utiliser user_id_db (l'ID de la base de données), pas user_id (qui peut être le Cognito sub)
            subscription_status = None
            subscription_plan = None
            try:
                cursor.execute("""
                    SELECT plan, status FROM subscriptions 
                    WHERE user_id = %s AND status = 'active'
                    ORDER BY created_at DESC LIMIT 1
                """, (user_id_db,))
                subscription_row = cursor.fetchone()
                if subscription_row:
                    subscription_plan, subscription_status = subscription_row
            except Exception as sub_error:
                # Table subscriptions n'existe pas encore - ignorer silencieusement
                logger.debug(f"Table subscriptions non disponible: {sub_error}")
                pass
            
            # Vérifier si l'email correspond à un directeur
            director_emails = ['mapevent777@gmail.com', 'directeur', 'director', 'admin']
            email_lower = email.lower() if email else ''
            is_director = any(pattern in email_lower for pattern in director_emails)
            
            # Calculer le role et subscription depuis la DB (source de vérité)
            final_role = 'director' if is_director else (role or 'user')
            final_subscription = 'vip_plus' if is_director else (subscription or 'free')
            
            # Si un abonnement Stripe actif existe, utiliser son plan
            if subscription_status == 'active' and subscription_plan:
                final_subscription = subscription_plan
            
            cursor.close()
            conn.close()
            
            # Construire l'objet adresse si disponible
            address_data = None
            if address_label and address_lat and address_lng:
                address_data = {
                    'label': address_label,
                    'lat': float(address_lat) if address_lat else None,
                    'lng': float(address_lng) if address_lng else None,
                    'country_code': address_country_code or '',
                    'city': address_city or '',
                    'postcode': address_postcode or '',
                    'street': address_street or '',
                    'verified': bool(address_verified) if address_verified is not None else False
                }
            
            # IMPORTANT: avatarUrl unifié (un seul nom partout)
            avatar_url = profile_photo_url or ''
            
            # PRIORITY HOTFIX: Retourner payload MINIMAL par défaut pour /api/user/me
            # Champs essentiels uniquement: id, email, username, profileComplete, profile_photo_url
            # Les autres données peuvent être chargées à la demande via d'autres endpoints
            # 
            # CORRECTION 2026-01-28: profileComplete = True si l'utilisateur a un id, email, ET username
            # On ne bloque plus les utilisateurs Google qui ont un username = début de l'email
            has_valid_username = bool(username and username.strip() and len(username.strip()) > 0)
            has_valid_email = bool(email and email.strip() and '@' in email)
            user_data_minimal = {
                'id': user_id_db,
                'email': email,
                'username': username,
                'profileComplete': bool(has_valid_username and has_valid_email),  # Profil complet si username ET email valides
                'profile_photo_url': avatar_url,  # URL de la photo de profil
                'role': final_role,
                'subscription': final_subscription
            }
            
            # Log de la taille pour monitoring
            user_data_json = json.dumps(user_data_minimal, ensure_ascii=False, default=str)
            user_data_size_kb = len(user_data_json.encode('utf-8')) / 1024
            logger.info(f"✅ Payload minimal /api/user/me: {user_data_size_kb:.2f}KB")
            
            return jsonify({'user': user_data_minimal}), 200
            
        except Exception as e:
            logger.error(f"Erreur user_me: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/user/address', methods=['PUT'])
    @require_auth
    def update_user_address():
        """Met à jour l'adresse de l'utilisateur (protégé par JWT)."""
        try:
            user_id = request.user_id
            data = request.get_json()
            
            # Extraire les données d'adresse
            address_label = data.get('address_label') or data.get('label', '').strip()
            address_lat = data.get('address_lat') or data.get('lat')
            address_lng = data.get('address_lng') or data.get('lng')
            address_country_code = data.get('address_country_code') or data.get('country_code', '').strip().upper()
            address_city = data.get('address_city') or data.get('city', '').strip()
            address_postcode = data.get('address_postcode') or data.get('postcode', '').strip()
            address_street = data.get('address_street') or data.get('street', '').strip()
            address_verified = data.get('address_verified', True)  # Par défaut vérifiée si fournie
            
            # Validation
            if address_label and (not address_lat or not address_lng or not address_country_code):
                return jsonify({'error': 'Si une adresse est fournie, lat, lng et country_code sont requis'}), 400
            
            if address_lat:
                try:
                    lat = float(address_lat)
                    lng = float(address_lng)
                    if lat < -90 or lat > 90 or lng < -180 or lng > 180:
                        return jsonify({'error': 'Coordonnées invalides'}), 400
                except (ValueError, TypeError):
                    return jsonify({'error': 'Coordonnées invalides'}), 400
            
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = conn.cursor()
            
            # Vérifier et créer les colonnes d'adresse si nécessaire
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS address_label VARCHAR(500)")
                cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS address_lat DECIMAL(10, 8)")
                cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS address_lng DECIMAL(11, 8)")
                cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS address_country_code VARCHAR(2)")
                cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS address_city VARCHAR(100)")
                cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS address_postcode VARCHAR(20)")
                cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS address_street VARCHAR(200)")
                cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS address_verified BOOLEAN DEFAULT false")
                conn.commit()
            except Exception as alter_error:
                logger.debug(f"Colonnes adresse déjà existantes ou erreur: {alter_error}")
            
            # Mettre à jour l'adresse
            cursor.execute("""
                UPDATE users 
                SET address_label = %s,
                    address_lat = %s,
                    address_lng = %s,
                    address_country_code = %s,
                    address_city = %s,
                    address_postcode = %s,
                    address_street = %s,
                    address_verified = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, (address_label or None, address_lat, address_lng, address_country_code or None,
                 address_city or None, address_postcode or None, address_street or None, address_verified, user_id))
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Adresse mise à jour pour user_id: {user_id}")
            
            # Récupérer l'utilisateur mis à jour pour le retourner
            cursor.execute("""
                SELECT address_label, address_lat, address_lng, address_country_code,
                       address_city, address_postcode, address_street, address_verified
                FROM users WHERE id = %s
            """, (user_id,))
            updated_row = cursor.fetchone()
            
            return jsonify({
                'success': True,
                'message': 'Adresse mise à jour avec succès',
                'user': {
                    'address_verified': bool(updated_row[7]) if updated_row and updated_row[7] is not None else False,
                    'address_lat': float(updated_row[1]) if updated_row and updated_row[1] else None,
                    'address_lng': float(updated_row[2]) if updated_row and updated_row[2] else None,
                    'address_label': updated_row[0] if updated_row else None,
                    'address_country_code': updated_row[3] if updated_row else None,
                    'address_city': updated_row[4] if updated_row else None,
                    'address_postcode': updated_row[5] if updated_row else None,
                    'address_street': updated_row[6] if updated_row else None
                },
                'address': {
                    'label': address_label,
                    'lat': address_lat,
                    'lng': address_lng,
                    'country_code': address_country_code,
                    'city': address_city,
                    'postcode': address_postcode,
                    'street': address_street,
                    'verified': address_verified
                } if address_label else None
            }), 200
            
        except Exception as e:
            logger.error(f"Erreur update_user_address: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/user/upload-photo', methods=['PUT'])
    @require_auth
    def upload_user_photo():
        """Upload la photo de profil de l'utilisateur vers S3 (protégé par JWT)."""
        try:
            user_id = request.user_id
            data = request.get_json()
            
            # Extraire les données de photo (base64 ou URL)
            photo_data = data.get('photo') or data.get('photo_data') or data.get('image')
            
            if not photo_data:
                return jsonify({'error': 'Données photo manquantes'}), 400
            
            # Utiliser le service S3 pour uploader
            try:
                from services.s3_service import upload_avatar_to_s3
                s3_url = upload_avatar_to_s3(user_id, photo_data)
                
                if not s3_url:
                    return jsonify({'error': 'Échec de l\'upload vers S3'}), 500
                
                # Mettre à jour la base de données
                conn = get_db_connection()
                if not conn:
                    return jsonify({'error': 'Database connection failed'}), 500
                
                cursor = conn.cursor()
                
                # Vérifier et créer la colonne si nécessaire
                try:
                    cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_photo_url VARCHAR(500)")
                    conn.commit()
                except Exception as alter_error:
                    logger.debug(f"Colonne profile_photo_url déjà existante ou erreur: {alter_error}")
                
                # Mettre à jour la photo
                cursor.execute("""
                    UPDATE users 
                    SET profile_photo_url = %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (s3_url, user_id))
                
                conn.commit()
                cursor.close()
                conn.close()
                
                logger.info(f"Photo de profil mise à jour pour user_id: {user_id}, URL: {s3_url}")
                
                return jsonify({
                    'success': True,
                    'message': 'Photo de profil uploadée avec succès',
                    'user': {
                        'profile_photo_url': s3_url
                    },
                    'photo_url': s3_url
                }), 200
                
            except ImportError:
                logger.error("Service S3 non disponible")
                return jsonify({'error': 'Service S3 non disponible'}), 500
            except Exception as s3_error:
                logger.error(f"Erreur upload S3: {s3_error}")
                import traceback
                logger.error(traceback.format_exc())
                return jsonify({'error': f'Erreur upload S3: {str(s3_error)}'}), 500
            
        except Exception as e:
            logger.error(f"Erreur upload_user_photo: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/user/privacy', methods=['PUT'])
    @require_auth
    def update_user_privacy():
        """Met à jour les paramètres de confidentialité de l'utilisateur (protégé par JWT)."""
        try:
            user_id = request.user_id
            data = request.get_json()
            
            # Extraire les paramètres de confidentialité
            profile_public = data.get('profile_public')
            show_name = data.get('show_name')
            show_photo = data.get('show_photo')
            show_city_country_only = data.get('show_city_country_only')
            
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = conn.cursor()
            
            # Vérifier et créer les colonnes si nécessaire
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS profile_public BOOLEAN DEFAULT false")
                cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS show_name BOOLEAN DEFAULT false")
                cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS show_photo BOOLEAN DEFAULT false")
                cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS show_city_country_only BOOLEAN DEFAULT false")
                conn.commit()
            except Exception as alter_error:
                logger.debug(f"Colonnes privacy déjà existantes ou erreur: {alter_error}")
            
            # Construire la requête UPDATE dynamiquement
            updates = []
            params = []
            
            if profile_public is not None:
                updates.append("profile_public = %s")
                params.append(profile_public)
            if show_name is not None:
                updates.append("show_name = %s")
                params.append(show_name)
            if show_photo is not None:
                updates.append("show_photo = %s")
                params.append(show_photo)
            if show_city_country_only is not None:
                updates.append("show_city_country_only = %s")
                params.append(show_city_country_only)
            
            if not updates:
                cursor.close()
                conn.close()
                return jsonify({'error': 'Aucun paramètre à mettre à jour'}), 400
            
            params.append(user_id)
            
            cursor.execute(f"""
                UPDATE users 
                SET {', '.join(updates)},
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = %s
            """, params)
            
            conn.commit()
            
            # Récupérer les valeurs mises à jour
            cursor.execute("""
                SELECT profile_public, show_name, show_photo, show_city_country_only
                FROM users WHERE id = %s
            """, (user_id,))
            updated_row = cursor.fetchone()
            
            cursor.close()
            conn.close()
            
            logger.info(f"Paramètres de confidentialité mis à jour pour user_id: {user_id}")
            
            return jsonify({
                'success': True,
                'message': 'Paramètres de confidentialité mis à jour',
                'user': {
                    'profile_public': bool(updated_row[0]) if updated_row and updated_row[0] is not None else False,
                    'show_name': bool(updated_row[1]) if updated_row and updated_row[1] is not None else False,
                    'show_photo': bool(updated_row[2]) if updated_row and updated_row[2] is not None else False,
                    'show_city_country_only': bool(updated_row[3]) if updated_row and updated_row[3] is not None else False
                }
            }), 200
            
        except Exception as e:
            logger.error(f"Erreur update_user_privacy: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/user/oauth/google', methods=['POST'])
    def oauth_google():
        """Gère l'authentification OAuth Google."""
        # #region agent log
        import json as json_lib
        import os
        import time
        DEBUG_LOG_PATH = '/tmp/debug.log' if os.path.exists('/tmp') else r'c:\MapEventAI_NEW\frontend\.cursor\debug.log'
        def debug_log(hypothesis_id, location, message, data=None):
            try:
                log_entry = {
                    "sessionId": "debug-session",
                    "runId": "run1",
                    "hypothesisId": hypothesis_id,
                    "location": location,
                    "message": message,
                    "data": data or {},
                    "timestamp": int(time.time() * 1000)
                }
                with open(DEBUG_LOG_PATH, 'a', encoding='utf-8') as f:
                    f.write(json_lib.dumps(log_entry, ensure_ascii=False) + '\n')
                # Aussi logger dans CloudWatch pour visibilité
                print(f"[DEBUG {hypothesis_id}] {location}: {message} | {json_lib.dumps(data or {})}")
            except Exception as e:
                print(f"[DEBUG ERROR] Impossible d'écrire dans {DEBUG_LOG_PATH}: {e}")
        debug_log("H5", "main.py:oauth_google:entry", "oauth_google appelé", {})
        # #endregion
        
        try:
            data = request.get_json()
            # #region agent log
            debug_log("H5", "main.py:oauth_google:after_get_json", "Après get_json()", {
                "has_data": data is not None,
                "data_keys": list(data.keys()) if isinstance(data, dict) else None
            })
            # #endregion
            
            email = data.get('email', '').strip().lower()
            name_raw = data.get('name', '').strip()
            # NETTOYER le nom pour supprimer les caractères spéciaux indésirables
            name = clean_user_text(name_raw)
            picture = data.get('picture', '')
            sub = data.get('sub', '')  # Google user ID
            credential = data.get('credential', '')  # JWT token
            access_token = data.get('access_token', '')
            
            # LOGS CRITIQUES pour déboguer la photo
            logger.info(f"[PHOTO] OAuth Google - Donnees recues: email={email}, picture={'PRESENTE' if picture else 'ABSENTE'}")
            if picture:
                logger.info(f"[PHOTO] URL photo Google recue: {picture[:100]}...")
            else:
                logger.warning(f"[WARNING] Aucune photo Google recue dans la requete OAuth")
            
            if not email:
                return jsonify({'error': 'Email requis'}), 400
            
            # #region agent log
            debug_log("H5", "main.py:oauth_google:before_db_connection", "Avant connexion DB", {
                "email": email[:50] if email else None
            })
            # #endregion
            
            conn = get_db_connection()
            if not conn:
                # #region agent log
                debug_log("H5", "main.py:oauth_google:db_connection_failed", "Connexion DB échouée", {})
                # #endregion
                return jsonify({'error': 'Database connection failed'}), 500
            
            # FIX: Créer un cursor qui reste ouvert pour toute la fonction
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
                    -- Colonne google_sub (renommer oauth_google_id si existe, sinon créer)
                    IF EXISTS (SELECT 1 FROM information_schema.columns 
                               WHERE table_name = 'users' AND column_name = 'oauth_google_id') 
                       AND NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                      WHERE table_name = 'users' AND column_name = 'google_sub') THEN
                        ALTER TABLE users RENAME COLUMN oauth_google_id TO google_sub;
                    END IF;
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                  WHERE table_name = 'users' AND column_name = 'google_sub') THEN
                        ALTER TABLE users ADD COLUMN google_sub VARCHAR(255);
                    END IF;
                    -- Colonne email_canonical pour éviter les doublons
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns 
                                  WHERE table_name = 'users' AND column_name = 'email_canonical') THEN
                        ALTER TABLE users ADD COLUMN email_canonical VARCHAR(255);
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
                # Recréer le cursor si nécessaire (après commit/rollback, le cursor peut être fermé)
                if not cursor or (hasattr(cursor, 'closed') and cursor.closed):
                    cursor = conn.cursor()
                    logger.info("✅ Cursor recréé après erreur création colonnes")
            
            # BUG ROOT CAUSE FIX: Identity key = google_sub (primary) + email_canonical
            # 1) Normaliser l'email pour éviter les doublons (laetitia.imboden132@gmail.com = laetitiaimboden132@gmail.com)
            email_canonical = normalize_email(email)
            logger.info(f"🔑 Email normalisé: {email} -> {email_canonical}, google_sub={sub}")
            
            # 2) Chercher par google_sub EN PREMIER (clé primaire pour OAuth Google)
            user_row = None
            if sub:
                try:
                    # Recréer le cursor si nécessaire (après commit, le cursor peut être fermé)
                    if not cursor or (hasattr(cursor, 'closed') and cursor.closed):
                        cursor = conn.cursor()
                    cursor.execute("""
                        SELECT id, email, email_canonical,
                               COALESCE(username, '') as username, 
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
                               COALESCE(postal_country, '') as postal_country,
                               COALESCE(address_label, '') as address_label,
                               COALESCE(address_lat, 0) as address_lat,
                               COALESCE(address_lng, 0) as address_lng,
                               COALESCE(created_at, CURRENT_TIMESTAMP) as created_at, 
                               password_hash, google_sub
                        FROM users 
                        WHERE google_sub = %s
                        LIMIT 1
                    """, (sub,))
                    user_row = cursor.fetchone()
                    if user_row:
                        logger.info(f"✅ User trouvé par google_sub: {sub}")
                except Exception as e:
                    logger.error(f"Erreur recherche par google_sub: {e}")
                    # Recréer le cursor si nécessaire
                    try:
                        cursor = conn.cursor()
                    except:
                        pass
            
            # 3) Si pas trouvé par google_sub, chercher par email_canonical
            if not user_row:
                try:
                    # Recréer le cursor si nécessaire
                    if not cursor or (hasattr(cursor, 'closed') and cursor.closed):
                        cursor = conn.cursor()
                    cursor.execute("""
                        SELECT id, email, email_canonical,
                               COALESCE(username, '') as username, 
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
                               COALESCE(postal_country, '') as postal_country,
                               COALESCE(address_label, '') as address_label,
                               COALESCE(address_lat, 0) as address_lat,
                               COALESCE(address_lng, 0) as address_lng,
                               COALESCE(created_at, CURRENT_TIMESTAMP) as created_at, 
                               password_hash, google_sub
                        FROM users 
                        WHERE email_canonical = %s OR (email_canonical IS NULL AND LOWER(email) = %s)
                        LIMIT 1
                    """, (email_canonical, email_canonical))
                    user_row = cursor.fetchone()
                    if user_row:
                        logger.info(f"✅ User trouvé par email_canonical: {email_canonical}")
                except Exception as e:
                    logger.error(f"Erreur recherche par email_canonical: {e}")
                    # Recréer le cursor si nécessaire
                    try:
                        cursor = conn.cursor()
                    except:
                        pass
            
            is_new_user = False
            profile_complete = False
            
            if user_row:
                # Utilisateur existant - connexion
                # Vérifier le nombre de colonnes dans user_row pour éviter les erreurs
                # Format attendu avec nouvelles colonnes: id, email, email_canonical, username, first_name, last_name, subscription, role,
                # avatar_emoji, avatar_description, profile_photo_url, postal_address, postal_city, postal_zip,
                # postal_country, address_label, address_lat, address_lng, created_at, password_hash, google_sub (21 colonnes)
                try:
                    if len(user_row) >= 21:
                        # Format complet avec toutes les colonnes
                        user_id, user_email, user_email_canonical, username, first_name, last_name, subscription, role, \
                        avatar_emoji, avatar_description, profile_photo_url_db, postal_address_db, postal_city_db, \
                        postal_zip_db, postal_country_db, address_label_db, address_lat_db, address_lng_db, \
                        created_at, password_hash, existing_google_sub = user_row
                        logger.info(f"✅ Format complet détecté: {len(user_row)} colonnes")
                    elif len(user_row) >= 13:
                        # Format intermédiaire (sans adresses)
                        user_id, user_email, user_email_canonical, username, first_name, last_name, subscription, role, avatar_emoji, avatar_description, created_at, password_hash, existing_google_sub = user_row
                        profile_photo_url_db = ''
                        postal_address_db = ''
                        postal_city_db = ''
                        postal_zip_db = ''
                        postal_country_db = 'CH'
                        address_label_db = ''
                        address_lat_db = None
                        address_lng_db = None
                        logger.info(f"✅ Format intermédiaire détecté: {len(user_row)} colonnes")
                    elif len(user_row) >= 11:
                        # Format sans first_name et last_name (ancien format)
                        user_id, user_email, user_email_canonical, username, subscription, role, avatar_emoji, avatar_description, created_at, password_hash, existing_google_sub = user_row
                        first_name = ''
                        last_name = ''
                        profile_photo_url_db = ''
                        postal_address_db = ''
                        postal_city_db = ''
                        postal_zip_db = ''
                        postal_country_db = 'CH'
                        address_label_db = ''
                        address_lat_db = None
                        address_lng_db = None
                        logger.info(f"✅ Format ancien détecté: {len(user_row)} colonnes")
                    else:
                        logger.error(f"Format user_row inattendu: {len(user_row)} colonnes")
                        raise ValueError(f"Format user_row invalide: {len(user_row)} colonnes")
                except ValueError as ve:
                    logger.error(f"Erreur déballage user_row: {ve}")
                    # Essayer avec une requête explicite
                    cursor.execute("""
                        SELECT id, email, email_canonical, username, first_name, last_name, subscription, role,
                               avatar_emoji, avatar_description, profile_photo_url, postal_address, postal_city,
                               postal_zip, postal_country, address_label, address_lat, address_lng,
                               created_at, password_hash, google_sub
                        FROM users WHERE id = %s
                    """, (user_row[0],))
                    user_row = cursor.fetchone()
                    if user_row and len(user_row) >= 21:
                        user_id, user_email, user_email_canonical, username, first_name, last_name, subscription, role, \
                        avatar_emoji, avatar_description, profile_photo_url_db, postal_address_db, postal_city_db, \
                        postal_zip_db, postal_country_db, address_label_db, address_lat_db, address_lng_db, \
                        created_at, password_hash, existing_google_sub = user_row
                    else:
                        raise
                
                # Mettre à jour email_canonical si manquant
                if not user_email_canonical:
                    try:
                        cursor.execute("UPDATE users SET email_canonical = %s WHERE id = %s", (email_canonical, user_id))
                        conn.commit()
                        logger.info(f"✅ email_canonical mis à jour pour user_id={user_id}")
                    except Exception as e:
                        logger.warning(f"⚠️ Erreur mise à jour email_canonical: {e}")
                
                # Vérifier si le profil est vraiment complet :
                # - A un mot de passe défini (password_hash)
                # - A un username personnalisé (pas juste la partie avant @ de l'email)
                # - A une adresse postale (optionnel mais recommandé)
                has_password = bool(password_hash and password_hash.strip())
                email_prefix = email.split('@')[0][:20] if email else ''
                has_custom_username = bool(username and username.strip() and username != email_prefix)
                
                # Vérifier aussi si l'utilisateur a une adresse postale et profile_photo_url
                # Récupérer TOUTES les données d'adresse et photo pour le frontend
                # Inclure photoData si disponible (photo uploadée depuis le formulaire, stockée en base64)
                cursor.execute("""
                    SELECT COALESCE(postal_address, '') as postal_address,
                           COALESCE(postal_city, '') as postal_city,
                           COALESCE(postal_zip, '') as postal_zip,
                           COALESCE(postal_country, 'CH') as postal_country,
                           COALESCE(profile_photo_url, '') as profile_photo_url
                    FROM users WHERE id = %s
                """, (user_id,))
                extra_row = cursor.fetchone()
                postal_address_db = extra_row[0] if extra_row else ''
                postal_city_db = extra_row[1] if extra_row else ''
                postal_zip_db = extra_row[2] if extra_row else ''
                postal_country_db = extra_row[3] if extra_row else 'CH'
                profile_photo_url_db = extra_row[4] if extra_row else ''
                
                # Récupérer photoData depuis la requête si fourni (pour mise à jour)
                photo_data_from_form = data.get('photoData', '')
                # Si photoData est fourni dans la requête, l'utiliser (mise à jour de photo)
                if photo_data_from_form and photo_data_from_form.strip() and photo_data_from_form != 'null':
                    try:
                        from services.s3_service import upload_avatar_to_s3
                        logger.info(f"[PHOTO] Mise à jour photo uploadée vers S3 pour {email}...")
                        s3_url = upload_avatar_to_s3(user_id, photo_data_from_form)
                        if s3_url:
                            profile_photo_url_db = s3_url
                            # Mettre à jour la base de données avec la nouvelle URL S3
                            try:
                                cursor.execute("UPDATE users SET profile_photo_url = %s WHERE id = %s", (s3_url, user_id))
                                conn.commit()
                                logger.info(f"[OK] profile_photo_url mis à jour avec URL S3: {s3_url[:100]}...")
                            except Exception as update_error:
                                logger.error(f"[ERROR] Erreur mise à jour profile_photo_url: {update_error}")
                        else:
                            logger.warning(f"[WARNING] Échec upload photo vers S3, conservation photo existante")
                    except Exception as photo_error:
                        logger.error(f"[ERROR] Erreur upload photo vers S3: {photo_error}")
                        import traceback
                        logger.error(traceback.format_exc())
                has_postal_address = bool(postal_address_db and postal_address_db.strip())
                
                # Pour OAuth Google, vérifier les données obligatoires :
                # - Photo : OBLIGATOIRE (photo Google ou profile_photo_url)
                # - Adresse : OPTIONNELLE (peut être ajoutée plus tard)
                has_photo = bool(profile_photo_url_db and profile_photo_url_db.strip()) or bool(picture and picture.strip())
                
                # Le profil est complet seulement si la photo est présente
                profile_complete = has_photo
                
                # Préparer les flags pour le frontend
                missing_data = []
                if not has_photo:
                    missing_data.append('photo')
                
                # LOGS DÉTAILLÉS POUR DÉBOGAGE
                logger.info(f"🔍 Vérification profil complet pour {email}:")
                logger.info(f"   - password_hash présent: {bool(password_hash)}")
                logger.info(f"   - password_hash valeur: {password_hash[:20] if password_hash else 'NULL'}...")
                logger.info(f"   - has_password: {has_password}")
                logger.info(f"   - username: '{username}'")
                logger.info(f"   - email_prefix: '{email_prefix}'")
                logger.info(f"   - username != email_prefix: {username != email_prefix}")
                logger.info(f"   - has_custom_username: {has_custom_username}")
                logger.info(f"   - has_postal_address: {has_postal_address}")
                logger.info(f"   - profile_complete: {profile_complete}")
                logger.info(f"   - user_id: {user_id}")
                
                # BUG ROOT CAUSE FIX: Lier google_sub au user existant (ne pas créer de doublon)
                # Mettre à jour google_sub si manquant ou différent
                if sub and existing_google_sub != sub:
                    try:
                        cursor.execute("UPDATE users SET google_sub = %s WHERE id = %s", (sub, user_id))
                        conn.commit()
                        logger.info(f"✅ google_sub mis à jour pour user_id={user_id}: {existing_google_sub} -> {sub}")
                    except Exception as e:
                        logger.error(f"Erreur mise à jour google_sub: {e}")
                        pass
                
                # ⚠️⚠️⚠️ CRITIQUE : Mettre à jour le username avec celui du formulaire si fourni
                username_from_form = data.get('username', '').strip()
                if username_from_form and username_from_form != username:
                    try:
                        cleaned_username = clean_user_text(username_from_form)[:20]
                        if cleaned_username and cleaned_username != username:
                            cursor.execute("UPDATE users SET username = %s WHERE id = %s", (cleaned_username, user_id))
                            conn.commit()
                            username = cleaned_username  # Mettre à jour la variable locale
                            logger.info(f"[OK] Username mis à jour avec celui du formulaire pour {email}: {username} -> {cleaned_username}")
                    except Exception as e:
                        logger.error(f"[ERROR] Erreur mise à jour username: {e}")
                        import traceback
                        logger.error(traceback.format_exc())
                        pass
                
                # ⚠️⚠️⚠️ CRITIQUE : Gérer la photo uploadée depuis le formulaire pour les comptes existants
                photo_data_from_form = data.get('photoData', '')
                if photo_data_from_form and photo_data_from_form.strip() and photo_data_from_form != 'null':
                    try:
                        from services.s3_service import upload_avatar_to_s3
                        logger.info(f"[PHOTO] Upload photo formulaire vers S3 pour compte existant {email}...")
                        s3_url = upload_avatar_to_s3(user_id, photo_data_from_form)
                        if s3_url:
                            cursor.execute("UPDATE users SET profile_photo_url = %s WHERE id = %s", (s3_url, user_id))
                            conn.commit()
                            profile_photo_url_db = s3_url  # Mettre à jour la variable locale
                            logger.info(f"[OK] Photo uploadée vers S3 pour compte existant: {s3_url[:100]}...")
                        else:
                            logger.warning(f"[WARNING] Échec upload photo vers S3 pour compte existant")
                    except Exception as e:
                        logger.error(f"[ERROR] Erreur upload photo vers S3 pour compte existant: {e}")
                        import traceback
                        logger.error(traceback.format_exc())
                        pass
                
                # Mettre à jour profile_photo_url avec la photo Google UNIQUEMENT si aucune photo S3 n'existe
                # Ne pas écraser une photo uploadée (S3) avec la photo Google
                if picture and picture.strip():
                    # Vérifier si profile_photo_url contient déjà une URL S3 (amazonaws.com)
                    has_s3_photo = profile_photo_url_db and 'amazonaws.com' in profile_photo_url_db
                    
                    if not has_s3_photo:
                        # Pas de photo S3, utiliser la photo Google
                        try:
                            cursor.execute("UPDATE users SET profile_photo_url = %s WHERE id = %s", (picture, user_id))
                            conn.commit()
                            profile_photo_url_db = picture  # Mettre à jour la variable locale
                            logger.info(f"[OK] profile_photo_url mis a jour avec la photo Google pour {email}: {picture[:100]}...")
                        except Exception as e:
                            logger.error(f"[ERROR] Erreur mise a jour profile_photo_url: {e}")
                            import traceback
                            logger.error(traceback.format_exc())
                            pass
                    else:
                        logger.info(f"[INFO] Photo S3 déjà présente, conservation de {profile_photo_url_db[:100]}... (pas de remplacement par photo Google)")
                else:
                    logger.warning(f"⚠️ Pas de photo Google à mettre à jour pour {email} (picture vide ou None)")
            else:
                # Nouvel utilisateur - compte inexistant
                is_new_user = True
                
                # Vérifier si photo Google disponible
                has_photo = bool(picture and picture.strip())
                
                # Pour nouveau compte : profile_complete = False si photo manquante
                profile_complete = has_photo
                
                # Préparer les flags pour le frontend
                missing_data = []
                if not has_photo:
                    missing_data.append('photo')
                
                # Nouveau compte nécessitera confirmation email (sera défini après création)
                # account_needs_email_verification sera défini après l'envoi de l'email
                
                import secrets
                user_id = f"user_{int(datetime.utcnow().timestamp() * 1000)}_{secrets.token_hex(8)}"
                
                # Utiliser username du formulaire si fourni, sinon générer depuis email
                username_from_form = data.get('username', '').strip()
                if username_from_form:
                    username = clean_user_text(username_from_form)[:20]
                else:
                    username = email.split('@')[0][:20]  # Utiliser la partie avant @ comme username temporaire
                
                # Utiliser firstName et lastName du formulaire si fournis, sinon extraire du nom complet
                first_name_from_form = data.get('firstName', '').strip()
                last_name_from_form = data.get('lastName', '').strip()
                
                if first_name_from_form and last_name_from_form:
                    first_name = clean_user_text(first_name_from_form)
                    last_name = clean_user_text(last_name_from_form)
                else:
                    # Extraire prénom et nom du nom complet
                    name_parts = name.split(' ', 1) if name else ['', '']
                    first_name = name_parts[0] if len(name_parts) > 0 else username
                    last_name = name_parts[1] if len(name_parts) > 1 else ''
                
                # Gérer les adresses si fournies dans le formulaire
                addresses_from_form = data.get('addresses', [])
                address_label = None
                address_lat = None
                address_lng = None
                address_country_code = None
                address_city = None
                address_postcode = None
                address_street = None
                
                if addresses_from_form and len(addresses_from_form) > 0:
                    addr = addresses_from_form[0]
                    address_label = addr.get('label', '')
                    address_lat = addr.get('lat')
                    address_lng = addr.get('lng')
                    address_details = addr.get('addressDetails', {})
                    address_country_code = address_details.get('country_code', '').upper() if address_details else None
                    address_city = address_details.get('city', '') if address_details else None
                    address_postcode = address_details.get('postcode', '') if address_details else None
                    address_street = address_details.get('street', '') if address_details else None
                
                # Vérifier l'unicité du username - recréer le cursor si nécessaire
                try:
                    if not cursor or (hasattr(cursor, 'closed') and cursor.closed):
                        cursor = conn.cursor()
                    cursor.execute("SELECT id FROM users WHERE LOWER(username) = %s", (username.lower(),))
                    if cursor.fetchone():
                        username = f"{username}_{secrets.token_hex(4)}"
                except Exception as e:
                    logger.error(f"Erreur vérification unicité username: {e}")
                    cursor = conn.cursor()  # Recréer le cursor
                    try:
                        cursor.execute("SELECT id FROM users WHERE LOWER(username) = %s", (username.lower(),))
                        if cursor.fetchone():
                            username = f"{username}_{secrets.token_hex(4)}"
                    except:
                        pass
                
                # Les colonnes OAuth sont déjà créées dans le bloc DO $$ ci-dessus
                
                # Gérer la photo uploadée lors de la création du profil (photoData)
                photo_data_from_form = data.get('photoData', '')
                profile_photo_initial = picture if picture else ''
                
                # Si une photo a été uploadée dans le formulaire, l'uploader vers S3 et l'utiliser
                if photo_data_from_form and photo_data_from_form.strip() and photo_data_from_form != 'null':
                    try:
                        from services.s3_service import upload_avatar_to_s3
                        logger.info(f"[PHOTO] Upload photo formulaire vers S3 pour {email}...")
                        s3_url = upload_avatar_to_s3(user_id, photo_data_from_form)
                        if s3_url:
                            profile_photo_initial = s3_url
                            logger.info(f"[OK] Photo uploadée vers S3: {s3_url[:100]}...")
                        else:
                            logger.warning(f"[WARNING] Échec upload photo vers S3, utilisation photo Google")
                    except Exception as photo_error:
                        logger.error(f"[ERROR] Erreur upload photo vers S3: {photo_error}")
                        import traceback
                        logger.error(traceback.format_exc())
                        # Continuer avec la photo Google si l'upload échoue
                
                # Utiliser picture comme avatar_emoji si disponible, sinon chaîne vide
                avatar_emoji_value = picture if picture else ''
                try:
                    if not cursor or (hasattr(cursor, 'closed') and cursor.closed):
                        cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO users (id, email, email_canonical, username, first_name, last_name, subscription, role,
                                          avatar_emoji, profile_photo_url, google_sub, 
                                          address_label, address_lat, address_lng, address_country_code, 
                                          address_city, address_postcode, address_street, address_verified,
                                          created_at, updated_at, password_hash)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NULL)
                    """, (user_id, email, email_canonical, username, first_name, last_name, 'free', 'user', 
                          avatar_emoji_value, profile_photo_initial, sub,
                          address_label, address_lat, address_lng, address_country_code,
                          address_city, address_postcode, address_street, True if address_label else False,
                          datetime.utcnow(), datetime.utcnow()))
                    conn.commit()
                except Exception as e:
                    logger.error(f"Erreur INSERT utilisateur (première tentative): {e}")
                    # Réessayer une fois
                    try:
                        if not cursor or (hasattr(cursor, 'closed') and cursor.closed):
                            cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO users (id, email, email_canonical, username, first_name, last_name, subscription, role,
                                              avatar_emoji, profile_photo_url, google_sub, 
                                              address_label, address_lat, address_lng, address_country_code, 
                                              address_city, address_postcode, address_street, address_verified,
                                              created_at, updated_at, password_hash)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NULL)
                        """, (user_id, email, email_canonical, username, first_name, last_name, 'free', 'user', 
                              avatar_emoji_value, profile_photo_initial, sub,
                              address_label, address_lat, address_lng, address_country_code,
                              address_city, address_postcode, address_street, True if address_label else False,
                              datetime.utcnow(), datetime.utcnow()))
                        conn.commit()
                    except Exception as e2:
                        logger.error(f"Erreur INSERT utilisateur (deuxième tentative): {e2}")
                        raise
                
                # Après création réussie, initialiser les variables et envoyer email de confirmation
                created_at = datetime.utcnow()
                subscription = 'free'
                role = 'user'
                avatar_emoji = picture if picture else '👤'
                avatar_description = ''
                account_needs_email_verification = False
                
                # Envoyer un email de confirmation pour le nouveau compte OAuth Google
                try:
                    import secrets
                    verification_code = str(secrets.randbelow(900000) + 100000)  # Code à 6 chiffres
                    
                    # Stocker le code dans Redis (expire dans 15 minutes)
                    redis_conn = get_redis_connection()
                    if redis_conn:
                        code_key = f"email_verification_code:{email}"
                        redis_conn.setex(code_key, 15 * 60, verification_code)  # 15 minutes
                        logger.info(f"✅ Code de vérification stocké dans Redis pour {email}")
                    
                    # Envoyer l'email de confirmation
                    email_sent = send_translated_email(
                        to_email=email,
                        template_name='email_verification',
                        template_vars={
                            'username': username if username else 'Utilisateur',
                            'code': str(verification_code),  # Code à 6 chiffres
                            'expires_in': '15'  # minutes (string pour le template)
                        }
                    )
                    if email_sent:
                        logger.info(f"✅ Email de confirmation envoyé à {email}")
                        account_needs_email_verification = True
                    else:
                        logger.warning(f"⚠️ Impossible d'envoyer l'email de confirmation à {email} (SENDGRID_API_KEY peut-être non configurée)")
                        # Continuer quand même - l'utilisateur est créé, il pourra confirmer plus tard
                        account_needs_email_verification = False
                except Exception as email_error:
                    logger.error(f"❌ Erreur envoi email confirmation: {email_error}")
                    import traceback
                    logger.error(traceback.format_exc())
                    # Continuer quand même - l'utilisateur est créé
            
            # Récupérer aussi profile_photo_url et postal_address pour le frontend (si pas déjà récupéré)
            if user_row:
                # Déjà récupéré dans le bloc if user_row ci-dessus
                profile_photo_url = profile_photo_url_db if 'profile_photo_url_db' in locals() else ''
                # Si profile_photo_url est vide mais qu'on a une photo Google, l'utiliser
                if not profile_photo_url and picture:
                    profile_photo_url = picture
                    logger.info(f"[PHOTO] Utilisation photo Google directement car profile_photo_url_db vide: {picture[:100]}...")
                postal_address_db = postal_address_db if 'postal_address_db' in locals() else ''
                postal_city_db = postal_city_db if 'postal_city_db' in locals() else ''
                postal_zip_db = postal_zip_db if 'postal_zip_db' in locals() else ''
                postal_country_db = postal_country_db if 'postal_country_db' in locals() else 'CH'
                has_password = has_password if 'has_password' in locals() else False
                has_postal_address = has_postal_address if 'has_postal_address' in locals() else False
            else:
                # Nouvel utilisateur - pas encore de données supplémentaires
                profile_photo_url = picture if picture else ''
                if profile_photo_url:
                    logger.info(f"[PHOTO] Nouvel utilisateur - Photo Google initiale: {profile_photo_url[:100]}...")
                postal_address_db = ''
                postal_city_db = ''
                postal_zip_db = ''
                postal_country_db = 'CH'
                has_password = False
                has_postal_address = False
            
            # IMPORTANT: Ne pas uploader vers S3 pendant le login (ralentit)
            # On garde seulement profile_photo_url existant et on fera l'upload plus tard si nécessaire
            # Si profile_photo_url est vide mais qu'on a une photo Google, on la sauvegarde directement
            if picture and picture.strip() and not profile_photo_url:
                try:
                    cursor.execute("UPDATE users SET profile_photo_url = %s WHERE id = %s", (picture, user_id))
                    conn.commit()
                    profile_photo_url = picture
                    logger.info(f"[OK] profile_photo_url mis à jour avec photo Google: {picture[:100]}...")
                except Exception as e:
                    logger.warning(f"⚠️ Erreur sauvegarde photo Google: {e}")
            
            # Construire user_data_dict pour build_user_slim (après fermeture du cursor)
            # Vérifier si l'email correspond à un directeur
            director_emails = ['mapevent777@gmail.com', 'directeur', 'director', 'admin']
            email_lower = email.lower()
            is_director = any(pattern in email_lower for pattern in director_emails)
            
            # Construire user_data_dict avec les données récupérées
            # ⚠️⚠️⚠️ CRITIQUE : Déterminer photoData : utiliser photo_data_from_form si fourni (nouveaux ET existants)
            # Pour les comptes existants, retourner photoData si fourni dans la requête
            photo_data_for_response = None
            photo_data_from_request = data.get('photoData', '')
            if photo_data_from_request and photo_data_from_request.strip() and photo_data_from_request != 'null':
                photo_data_for_response = photo_data_from_request
                logger.info(f"[PHOTO] photoData inclus dans la réponse pour {email} (depuis formulaire)")
            elif 'photo_data_from_form' in locals() and photo_data_from_form and photo_data_from_form != 'null':
                photo_data_for_response = photo_data_from_form
                logger.info(f"[PHOTO] photoData inclus dans la réponse pour {email} (depuis photo_data_from_form)")
            
            user_data_dict = {
                'id': str(user_id) if user_id else '',
                'email': str(email) if email else '',
                'username': str(username) if username else '',
                'first_name': str(first_name) if first_name else '',
                'last_name': str(last_name) if last_name else '',
                'subscription': str('vip_plus' if is_director else (subscription or 'free')),
                'role': str('director' if is_director else (role or 'user')),
                'profile_photo_url': str(profile_photo_url_db) if profile_photo_url_db and not (profile_photo_url_db.startswith('data:image') and len(profile_photo_url_db) > 1000) else '',
                'password_hash': password_hash if 'password_hash' in locals() else None,
                'postal_address': postal_address_db if 'postal_address_db' in locals() and postal_address_db else None,
                'profileComplete': profile_complete,
                # Inclure photoData seulement si fourni dans la requête (mise à jour)
                'photoData': photo_data_for_response
            }
            
            # Utiliser build_user_slim pour créer un payload minimal
            user_slim = build_user_slim(user_data_dict)
            
            # Retourner les flags pour le frontend
            logger.info(f"🔍 Envoi réponse oauth_google: profileComplete={profile_complete}, isNewUser={is_new_user}, user_id={user_id}, username={username}")
            
            # Préparer payload avec détails des données manquantes
            # Initialiser account_needs_email_verification si pas déjà défini
            if 'account_needs_email_verification' not in locals():
                account_needs_email_verification = False
            
            payload = {
                'ok': True,
                'profileComplete': bool(profile_complete),
                'isNewUser': bool(is_new_user),
                'user': user_slim,
                'missingData': missing_data if 'missing_data' in locals() else [],
                'accountNotFound': False,  # Pour comptes existants (toujours False car on crée/connecte)
                'needsEmailVerification': bool(account_needs_email_verification)
            }
            
            # Vérifier la taille finale et logger
            try:
                response_json_str = json.dumps(payload, ensure_ascii=False, default=str)
                response_size_kb = len(response_json_str.encode('utf-8')) / 1024
                logger.info(f"✅ Payload slim /oauth/google: {response_size_kb:.2f}KB")
                
                if response_size_kb > 10:
                    logger.warn(f"⚠️ Payload toujours trop gros ({response_size_kb:.2f}KB) - version ultra-minimale")
                    payload['user'] = {
                        'id': str(user_id) if user_id else '',
                        'email': str(email) if email else '',
                        'username': str(username) if username else '',
                        'profileComplete': profile_complete,
                # Inclure photoData si une photo a Ã©tÃ© uploadÃ©e depuis le formulaire
                'photoData': photo_data_from_form if 'photo_data_from_form' in locals() and photo_data_from_form and photo_data_from_form != 'null' else None
            }
                    response_json_str = json.dumps(payload, ensure_ascii=False, default=str)
                    response_size_kb = len(response_json_str.encode('utf-8')) / 1024
                    logger.info(f"✅ Payload ultra-minimal: {response_size_kb:.2f}KB")
                
                return jsonify(payload), 200
            except Exception as serialization_error:
                logger.error(f"❌ Erreur sérialisation réponse oauth_google: {serialization_error}")
                import traceback
                logger.error(traceback.format_exc())
                # Fallback : renvoyer une réponse minimale
                fallback_payload = {
                    'ok': True,
                    'profileComplete': profile_complete,
                    'isNewUser': is_new_user,
                    'user': build_user_slim({
                        'id': str(user_id) if user_id else '',
                        'email': str(email) if email else '',
                        'username': str(username) if username else ''
                    })
                }
                return jsonify(fallback_payload), 200
        except Exception as oauth_error:
            # GESTION D'ERREUR GLOBALE : S'assurer que le compte est créé même en cas d'erreur
            logger.error(f"❌ ERREUR CRITIQUE dans oauth_google: {oauth_error}")
            import traceback
            logger.error(f"Traceback complet: {traceback.format_exc()}")
            
            # Si l'utilisateur a été créé mais qu'une erreur survient après, retourner quand même les infos
            if 'user_id' in locals() and user_id:
                logger.warning(f"⚠️ Utilisateur créé mais erreur après création - retour réponse minimale")
                minimal_user = build_user_slim({
                    'id': str(user_id),
                    'email': str(email) if 'email' in locals() else '',
                    'username': str(username) if 'username' in locals() else '',
                    'profileComplete': False
                })
                return jsonify({
                    'ok': True,
                    'profileComplete': False,
                    'isNewUser': True,
                    'user': minimal_user
                }), 200
            else:
                # Erreur avant création - retourner erreur
                logger.error(f"❌ Erreur avant création utilisateur - compte non créé")
                error_message = str(oauth_error)[:500]  # Limiter la longueur du message
                return jsonify({
                    'ok': False,
                    'error': 'Erreur lors de l\'authentification Google',
                    'message': error_message
                }), 500
        finally:
            # FIX: Fermer cursor et conn dans finally
            if 'cursor' in locals() and cursor:
                try:
                    cursor.close()
                    logger.debug("✅ Cursor fermé dans finally (oauth_google)")
                except Exception as close_error:
                    logger.warning(f"⚠️ Erreur fermeture cursor: {close_error}")
            if 'conn' in locals() and conn:
                try:
                    conn.close()
                    logger.debug("✅ Connexion DB fermée dans finally (oauth_google)")
                except Exception as close_error:
                    logger.warning(f"⚠️ Erreur fermeture connexion: {close_error}")
    
    @app.route('/api/user/oauth/google/complete', methods=['POST'])
    def oauth_google_complete():
        """Complète le profil d'un utilisateur Google avec nom d'utilisateur, photo, mot de passe et adresse."""
        import hashlib
        import secrets
        
        # FIX: Ouvrir conn une seule fois et la garder ouverte jusqu'à la fin
        conn = None
        try:
            data = request.get_json()
            user_id = data.get('userId')
            email = data.get('email', '').strip().lower()
            username_raw = data.get('username', '').strip()
            # NETTOYER le username pour supprimer les caractères spéciaux indésirables
            username = clean_user_text(username_raw)
            password = data.get('password', '')
            profile_photo = data.get('profilePhoto', '')
            postal_address = data.get('postalAddress')
            
            if not email:
                return jsonify({'error': 'Email requis'}), 400
            
            if not username or len(username) < 3 or len(username) > 20:
                return jsonify({'error': 'Nom d\'utilisateur invalide (3-20 caractères)'}), 400
            
            # Pour OAuth Google, le mot de passe est optionnel (peut être vide si OAuth uniquement)
            # Vérifier seulement si un mot de passe est fourni
            if password and len(password) < 8:
                return jsonify({'error': 'Mot de passe invalide (minimum 8 caractères)'}), 400
            
            # FIX: Ouvrir conn une seule fois au début
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database connection failed'}), 500
            
            # FIX: Utiliser un seul cursor pour toutes les requêtes
            with conn.cursor() as cursor:
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
                
                # BUG ROOT CAUSE FIX: /oauth/google/complete doit utiliser user_id du token (pas re-chercher par email)
                # PRIORITÉ 1: user_id du token (venant de /oauth/google)
                # PRIORITÉ 2: google_sub (clé primaire pour OAuth Google)
                # PRIORITÉ 3: email_canonical (jamais email brut)
                google_sub = data.get('googleSub') or data.get('sub')  # Accepter googleSub ou sub
                logger.info(f"🔍 Recherche utilisateur pour complete: email={email}, user_id={user_id}, google_sub={google_sub}")
                
                user_row = None
                if user_id:
                    # PRIORITÉ 1: Utiliser user_id du token (venant de /oauth/google)
                    cursor.execute("SELECT id, password_hash, username, email_canonical, google_sub FROM users WHERE id = %s", (user_id,))
                    user_row = cursor.fetchone()
                    if user_row:
                        logger.info(f"✅ User trouvé par user_id: {user_id}")
                
                if not user_row and google_sub:
                    # PRIORITÉ 2: Chercher par google_sub (clé primaire pour OAuth Google)
                    cursor.execute("SELECT id, password_hash, username, email_canonical, google_sub FROM users WHERE google_sub = %s", (google_sub,))
                    user_row = cursor.fetchone()
                    if user_row:
                        logger.info(f"✅ User trouvé par google_sub: {google_sub}")
                        user_id = user_row[0]  # Mettre à jour user_id pour la suite
                
                if not user_row:
                    # PRIORITÉ 3: Fallback: chercher par email_canonical (jamais email brut)
                    email_canonical = normalize_email(email)
                    cursor.execute("SELECT id, password_hash, username, email_canonical, google_sub FROM users WHERE email_canonical = %s OR (email_canonical IS NULL AND LOWER(email) = %s)", (email_canonical, email_canonical))
                    user_row = cursor.fetchone()
                    if user_row:
                        logger.info(f"✅ User trouvé par email_canonical: {email_canonical}")
                        user_id = user_row[0]  # Mettre à jour user_id pour la suite
            
                if not user_row:
                    # Si utilisateur non trouvé, créer un nouvel utilisateur avec les données du formulaire
                    logger.warn(f"⚠️ Utilisateur non trouvé pour email={email}, user_id={user_id}. Création d'un nouvel utilisateur.")
                    actual_user_id = f"user_{int(datetime.utcnow().timestamp() * 1000)}_{secrets.token_hex(8)}"
                    password_hash = hashlib.sha256(password.encode()).hexdigest()
                    
                    # Créer l'utilisateur avec les données du formulaire
                    # CORRECTION CRITIQUE : Récupérer firstName et lastName depuis data et NETTOYER
                    first_name_raw = data.get('firstName', '').strip()
                    last_name_raw = data.get('lastName', '').strip()
                    first_name = clean_user_text(first_name_raw)
                    last_name = clean_user_text(last_name_raw)
                    
                    try:
                        # Préparer l'adresse postale
                        postal_address_str = ''
                        postal_city_str = ''
                        postal_zip_str = ''
                        postal_country_str = 'CH'
                        
                        if postal_address:
                            if isinstance(postal_address, dict):
                                postal_address_str = postal_address.get('address', '')
                                postal_city_str = postal_address.get('city', '')
                                postal_zip_str = postal_address.get('zip', '')
                                postal_country_str = postal_address.get('country', 'CH')
                            else:
                                postal_address_str = str(postal_address)
                        
                        cursor.execute("""
                            INSERT INTO users (id, email, username, first_name, last_name, password_hash, 
                                             avatar_emoji, profile_photo_url, postal_address, postal_city, postal_zip, postal_country,
                                             subscription, role, created_at, updated_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 'free', 'user', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
                        """, (actual_user_id, email, username, first_name, last_name, 
                              password_hash, profile_photo, profile_photo, 
                              postal_address_str, postal_city_str, postal_zip_str, postal_country_str))
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
                    existing_email_canonical = user_row[3]
                    existing_google_sub = user_row[4]
                    logger.info(f"✅ Utilisateur trouvé: {actual_user_id}, a_password={bool(existing_password_hash)}, username={existing_username}, email_canonical={existing_email_canonical}, google_sub={existing_google_sub}")
                    
                    # Mettre à jour google_sub et email_canonical si manquants
                    if google_sub and not existing_google_sub:
                        try:
                            cursor.execute("UPDATE users SET google_sub = %s WHERE id = %s", (google_sub, actual_user_id))
                            conn.commit()
                            logger.info(f"✅ google_sub mis à jour pour {actual_user_id}")
                        except Exception as e:
                            logger.warning(f"⚠️ Erreur mise à jour google_sub: {e}")
                    
                    email_canonical = normalize_email(email)
                    if email_canonical and not existing_email_canonical:
                        try:
                            cursor.execute("UPDATE users SET email_canonical = %s WHERE id = %s", (email_canonical, actual_user_id))
                            conn.commit()
                            logger.info(f"✅ email_canonical mis à jour pour {actual_user_id}")
                        except Exception as e:
                            logger.warning(f"⚠️ Erreur mise à jour email_canonical: {e}")
                    
                    # Si l'utilisateur a déjà un profil complet, vérifier si on peut quand même mettre à jour
                    if existing_password_hash and existing_password_hash.strip():
                        logger.info(f"ℹ️ Utilisateur a déjà un mot de passe. Mise à jour autorisée pour compléter/modifier le profil.")
                
                # BUG ROOT CAUSE FIX: Vérifier l'unicité du username avec gestion du merge
                logger.info(f"🔍 Vérification unicité username: {username} pour user_id={actual_user_id}")
                
                # Vérifier si le username est déjà pris par un autre user_id
                cursor.execute("SELECT id, email_canonical, google_sub FROM users WHERE LOWER(username) = %s AND id != %s", 
                             (username.lower(), actual_user_id))
                existing_username_user = cursor.fetchone()
                
                if existing_username_user:
                    other_user_id, other_email_canonical, other_google_sub = existing_username_user
                    logger.warn(f"⚠️ Username déjà pris: {username} par utilisateur {other_user_id}")
                    
                    # Vérifier si c'est le même utilisateur (même email_canonical ou même google_sub)
                    email_canonical = normalize_email(email)
                    is_same_user = False
                    
                    if other_email_canonical and email_canonical == other_email_canonical:
                        is_same_user = True
                        logger.info(f"✅ Même email_canonical détecté: {email_canonical} -> merge nécessaire")
                    
                    if google_sub and other_google_sub and google_sub == other_google_sub:
                        is_same_user = True
                        logger.info(f"✅ Même google_sub détecté: {google_sub} -> merge nécessaire")
                    
                    if is_same_user:
                        # MERGE: Déplacer les données vers le user_id canonique
                        # Le user_id canonique est celui qui a google_sub (ou le plus ancien)
                        canonical_user_id = actual_user_id
                        duplicate_user_id = other_user_id
                        
                        # Si l'autre user a google_sub et pas nous, c'est lui le canonique
                        if other_google_sub and not google_sub:
                            canonical_user_id = other_user_id
                            duplicate_user_id = actual_user_id
                            logger.info(f"🔄 Merge: {duplicate_user_id} -> {canonical_user_id} (autre user a google_sub)")
                        else:
                            logger.info(f"🔄 Merge: {duplicate_user_id} -> {canonical_user_id} (notre user est canonique)")
                        
                        # Déplacer les données du duplicate vers le canonique
                        try:
                            # Mettre à jour google_sub si manquant
                            if google_sub and not other_google_sub:
                                cursor.execute("UPDATE users SET google_sub = %s WHERE id = %s", (google_sub, canonical_user_id))
                            
                            # Mettre à jour email_canonical si manquant
                            if email_canonical:
                                cursor.execute("UPDATE users SET email_canonical = %s WHERE id = %s", (email_canonical, canonical_user_id))
                            
                            # Supprimer le duplicate (ou le désactiver)
                            cursor.execute("DELETE FROM users WHERE id = %s", (duplicate_user_id,))
                            conn.commit()
                            logger.info(f"✅ Merge terminé: {duplicate_user_id} supprimé, données dans {canonical_user_id}")
                            
                            # Mettre à jour actual_user_id pour utiliser le canonique
                            actual_user_id = canonical_user_id
                        except Exception as merge_error:
                            logger.error(f"❌ Erreur lors du merge: {merge_error}")
                            import traceback
                            logger.error(traceback.format_exc())
                            # Continuer quand même, mais retourner une erreur
                            return jsonify({
                                'error': 'Erreur lors de la fusion des comptes. Veuillez contacter le support.',
                                'code': 'MERGE_ERROR'
                            }), 500
                    else:
                        # Username pris par un autre utilisateur différent
                        # Pour OAuth Google, on génère un username unique automatiquement
                        logger.warn(f"⚠️ Username déjà pris: {username} par utilisateur {other_user_id}. Génération d'un username unique...")
                        email_canonical = normalize_email(email)
                        base_username = email.split('@')[0][:15] if email else 'user'
                        # Ajouter un suffixe unique
                        import secrets
                        unique_suffix = secrets.token_hex(3)
                        username = f"{base_username}_{unique_suffix}"
                        # Vérifier que ce nouveau username est libre
                        cursor.execute("SELECT id FROM users WHERE LOWER(username) = %s", (username.lower(),))
                        if cursor.fetchone():
                            # Encore pris, utiliser timestamp
                            username = f"{base_username}_{int(datetime.utcnow().timestamp())}"
                        logger.info(f"✅ Username unique généré: {username}")
                
                # Si le username est déjà celui de l'utilisateur actuel, c'est OK (pas besoin de changer)
                # existing_username peut être None si c'est un nouvel utilisateur créé ci-dessus
                if 'existing_username' in locals() and existing_username and existing_username.lower() == username.lower():
                    logger.info(f"✅ Username inchangé: {username} (déjà celui de l'utilisateur)")
                else:
                    logger.info(f"✅ Username disponible ou mis à jour: {username}")
                
                # Hasher le mot de passe seulement s'il est fourni (pour OAuth Google, password est optionnel)
                password_hash = None
                if password and password.strip():
                    password_hash = hashlib.sha256(password.encode()).hexdigest()
                
                # Préparer les colonnes à mettre à jour
                updates = []
                params = []
                
                # CORRECTION CRITIQUE : Sauvegarder firstName et lastName (NETTOYÉS)
                first_name_raw = data.get('firstName', '').strip()
                last_name_raw = data.get('lastName', '').strip()
                first_name = clean_user_text(first_name_raw)
                last_name = clean_user_text(last_name_raw)
                
                if first_name:
                    updates.append("first_name = %s")
                    params.append(first_name)
                
                if last_name:
                    updates.append("last_name = %s")
                    params.append(last_name)
                
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
                        raise
                else:
                    logger.warn(f"⚠️ Aucune mise à jour à effectuer pour {actual_user_id}")
                
                # Récupérer l'utilisateur mis à jour (utiliser actual_user_id)
                # FIX: Récupérer password_hash dans la même requête pour éviter cursor_check
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
                           created_at, password_hash
                    FROM users 
                    WHERE id = %s
                """, (actual_user_id,))
                
                user_row = cursor.fetchone()
                
                if user_row:
                    user_id, user_email, username, first_name, last_name, subscription, role, \
                    avatar_emoji, avatar_description, profile_photo_url, \
                    postal_address_db, postal_city, postal_zip, postal_country, created_at, password_hash_db = user_row
                    
                    # Construire user_data_dict pour build_user_slim
                    user_data_dict = {
                        'id': str(user_id),
                        'email': str(user_email),
                        'username': str(username) if username else '',
                        'first_name': str(first_name) if first_name else '',
                        'last_name': str(last_name) if last_name else '',
                        'subscription': str(subscription) if subscription else 'free',
                        'role': str(role) if role else 'user',
                        'profile_photo_url': str(profile_photo_url) if profile_photo_url and not (profile_photo_url.startswith('data:image') and len(profile_photo_url) > 1000) else '',
                        'password_hash': password_hash_db,  # Pour hasPassword
                        'postal_address': postal_address_db if postal_address_db else None,
                        'profileComplete': True
                    }
                    
                    # Utiliser build_user_slim pour créer un payload minimal
                    user_slim = build_user_slim(user_data_dict)
                    
                    payload = {
                        'ok': True,
                        'profileComplete': True,
                        'user': user_slim
                    }
                    
                    # Vérifier la taille finale et logger
                    try:
                        response_json_str = json.dumps(payload, ensure_ascii=False, default=str)
                        response_size_kb = len(response_json_str.encode('utf-8')) / 1024
                        logger.info(f"✅ Payload slim /oauth/google/complete: {response_size_kb:.2f}KB")
                        
                        if response_size_kb > 10:
                            logger.warn(f"⚠️ Payload toujours trop gros ({response_size_kb:.2f}KB) - version ultra-minimale")
                            payload['user'] = {
                                'id': str(user_id),
                                'email': str(user_email),
                                'username': str(username) if username else '',
                                'profileComplete': True
                            }
                            response_json_str = json.dumps(payload, ensure_ascii=False, default=str)
                            response_size_kb = len(response_json_str.encode('utf-8')) / 1024
                            logger.info(f"✅ Payload ultra-minimal: {response_size_kb:.2f}KB")
                        
                        return jsonify(payload), 200
                    except Exception as serialization_error:
                        logger.error(f"❌ Erreur sérialisation réponse oauth_google_complete: {serialization_error}")
                        import traceback
                        logger.error(traceback.format_exc())
                        # Fallback : renvoyer une réponse minimale
                        fallback_payload = {
                            'ok': True,
                            'profileComplete': True,
                            'user': build_user_slim({
                                'id': str(user_id),
                                'email': str(user_email),
                                'username': str(username) if username else ''
                            })
                        }
                        return jsonify(fallback_payload), 200
                else:
                    return jsonify({'error': 'Erreur lors de la récupération de l\'utilisateur'}), 500
            # Fin du with conn.cursor() as cursor:
            
        except Exception as e:
            logger.error(f"Erreur complétion profil Google: {str(e)}")
            import traceback
            error_trace = traceback.format_exc()
            logger.error(error_trace)
            
            # Retourner une erreur plus détaillée pour le debug
            error_message = str(e)
            if 'timeout' in error_message.lower() or 'connection' in error_message.lower():
                return jsonify({'error': 'Timeout de connexion à la base de données. Veuillez réessayer.'}), 502
            elif 'does not exist' in error_message.lower() or 'not found' in error_message.lower():
                return jsonify({'error': 'Utilisateur non trouvé. Veuillez d\'abord vous connecter avec Google.'}), 404
            else:
                return jsonify({'error': f'Erreur serveur: {error_message}'}), 500
        finally:
            # FIX: Fermer conn uniquement dans finally, une seule fois à la fin
            if conn:
                try:
                    conn.close()
                    logger.debug("✅ Connexion DB fermée dans finally")
                except Exception as close_error:
                    logger.warning(f"⚠️ Erreur fermeture connexion: {close_error}")
    
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
                'avatar': avatar_emoji or '',
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
            # ⚠️ CRITIQUE : Vérifier que Stripe est configuré
            if not stripe.api_key:
                logger.error("STRIPE_SECRET_KEY non configurée!")
                return jsonify({'error': 'Stripe non configuré. Vérifiez STRIPE_SECRET_KEY dans les variables d\'environnement Lambda.'}), 500
            
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
        """
        Récupérer le profil d'un utilisateur (ROUTE PUBLIQUE).
        
        IMPORTANT: Ne JAMAIS renvoyer l'adresse complète (rue + numéro + code postal).
        Seulement ville/pays si show_city_country_only = true.
        """
        try:
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database unavailable'}), 500
            
            cursor = conn.cursor()
            
            # Récupérer les infos de base (sans adresse complète)
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
            
            # IMPORTANT: Ne JAMAIS renvoyer email ou adresse complète dans les routes publiques (RGPD)
            # Seulement les infos publiques autorisées
            profile = {
                'id': row[0],
                'username': row[1],
                'firstName': row[2] if row[2] else None,  # Seulement si show_name = true (à vérifier)
                'lastName': row[3] if row[3] else None,  # Seulement si show_name = true (à vérifier)
                # 'email': row[4],  # PRIVÉ - jamais public
                'createdAt': row[5].isoformat() if row[5] else None,
                'bio': row[6],
                'profilePhotos': json.loads(row[7]) if row[7] else [],
                'profileVideos': json.loads(row[8]) if row[8] else [],
                'profileLinks': json.loads(row[9]) if row[9] else []
                # Adresse complète (rue + numéro + code postal) : JAMAIS renvoyée dans les routes publiques
                # Ville/pays : seulement si show_city_country_only = true (à implémenter si nécessaire)
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
    
    @app.route('/api/user/account', methods=['DELETE'])
    @require_auth
    def delete_user_account():
        """
        Supprime définitivement le compte utilisateur (droit à l'oubli RGPD).
        Supprime toutes les données associées : profil, événements, reviews, etc.
        """
        try:
            user_id = request.user_id
            user_email = request.user_email
            
            # Vérifier que l'utilisateur confirme la suppression
            data = request.get_json() or {}
            confirm_delete = data.get('confirm', False)
            
            if not confirm_delete:
                return jsonify({
                    'error': 'Confirmation requise pour supprimer le compte',
                    'code': 'CONFIRMATION_REQUIRED'
                }), 400
            
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = conn.cursor()
            
            try:
                # Supprimer toutes les données associées à l'utilisateur
                # 1. Supprimer les événements créés par l'utilisateur
                cursor.execute("DELETE FROM events WHERE creator_id = %s", (user_id,))
                events_deleted = cursor.rowcount
                
                # 2. Supprimer les reviews de l'utilisateur
                cursor.execute("DELETE FROM reviews WHERE user_id = %s", (user_id,))
                reviews_deleted = cursor.rowcount
                
                # 3. Supprimer les participations
                cursor.execute("DELETE FROM user_events WHERE user_id = %s", (user_id,))
                participations_deleted = cursor.rowcount
                
                # 4. Supprimer les favoris
                cursor.execute("DELETE FROM user_favorites WHERE user_id = %s", (user_id,))
                favorites_deleted = cursor.rowcount
                
                # 5. Supprimer les alertes
                cursor.execute("DELETE FROM user_alerts WHERE user_id = %s", (user_id,))
                alerts_deleted = cursor.rowcount
                
                # 6. Supprimer les mots de passe
                cursor.execute("DELETE FROM user_passwords WHERE user_id = %s", (user_id,))
                passwords_deleted = cursor.rowcount
                
                # 7. Supprimer les tokens de vérification email
                cursor.execute("DELETE FROM email_verification_tokens WHERE email = %s", (user_email,))
                
                # 8. Supprimer l'utilisateur lui-même
                cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
                user_deleted = cursor.rowcount
                
                if user_deleted == 0:
                    cursor.close()
                    conn.close()
                    return jsonify({'error': 'Utilisateur non trouvé'}), 404
                
                # Commit toutes les suppressions
                conn.commit()
                
                logger.info(f"✅ Compte supprimé: {user_id} ({user_email})")
                logger.info(f"   - Événements supprimés: {events_deleted}")
                logger.info(f"   - Reviews supprimées: {reviews_deleted}")
                logger.info(f"   - Participations supprimées: {participations_deleted}")
                logger.info(f"   - Favoris supprimés: {favorites_deleted}")
                logger.info(f"   - Alertes supprimées: {alerts_deleted}")
                
                cursor.close()
                conn.close()
                
                return jsonify({
                    'success': True,
                    'message': 'Compte supprimé avec succès',
                    'deleted': {
                        'events': events_deleted,
                        'reviews': reviews_deleted,
                        'participations': participations_deleted,
                        'favorites': favorites_deleted,
                        'alerts': alerts_deleted
                    }
                }), 200
                
            except Exception as db_error:
                conn.rollback()
                cursor.close()
                conn.close()
                logger.error(f"Erreur suppression compte: {db_error}")
                import traceback
                logger.error(traceback.format_exc())
                return jsonify({'error': 'Erreur lors de la suppression du compte'}), 500
                
        except Exception as e:
            logger.error(f"Erreur delete_user_account: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/user/profile', methods=['PUT'])
    def update_user_profile_settings():
        """Met à jour le profil utilisateur (username, postalAddress, profilePhoto)"""
        try:
            data = request.get_json()
            user_id = data.get('userId')
            username = data.get('username')
            postal_address = data.get('postalAddress')
            profile_photo = data.get('profilePhoto')
            
            if not user_id:
                return jsonify({'error': 'userId requis'}), 400
            
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = conn.cursor()
            
            # SOLUTION S3 : Uploader automatiquement les avatars (base64 OU URL) vers S3
            profile_photo_url_final = profile_photo
            if profile_photo and (profile_photo.startswith('data:image') or 
                                profile_photo.startswith('http://') or 
                                profile_photo.startswith('https://')):
                try:
                    from services.s3_service import upload_avatar_to_s3
                    s3_url = upload_avatar_to_s3(user_id, profile_photo)
                    if s3_url:
                        profile_photo_url_final = s3_url
                        logger.info(f"✅ Avatar uploadé vers S3 lors de la mise à jour du profil: {s3_url}")
                except Exception as s3_error:
                    logger.error(f"❌ Erreur upload avatar vers S3: {s3_error}")
                    # En cas d'erreur, continuer avec l'originale
            
            # Construire la requête UPDATE dynamiquement
            updates = []
            params = []
            
            if username:
                # IMPORTANT: Vérifier l'unicité du username en excluant le user_id actuel
                cursor.execute("""
                    SELECT id FROM users 
                    WHERE LOWER(username) = LOWER(%s) AND id != %s
                    LIMIT 1
                """, (username, user_id))
                
                if cursor.fetchone():
                    cursor.close()
                    conn.close()
                    return jsonify({
                        'error': 'Ce nom est déjà pris. Essaie une variante.',
                        'code': 'USERNAME_ALREADY_EXISTS',
                        'field': 'username'
                    }), 409
                
                updates.append("username = %s")
                params.append(username)
            
            if postal_address is not None:
                # Extraire les composants de l'adresse si c'est un objet
                if isinstance(postal_address, dict):
                    address = postal_address.get('address', '')
                    city = postal_address.get('city', '')
                    zip_code = postal_address.get('zip', '')
                    country = postal_address.get('country', 'CH')
                    
                    updates.append("postal_address = %s")
                    updates.append("postal_city = %s")
                    updates.append("postal_zip = %s")
                    updates.append("postal_country = %s")
                    params.extend([address, city, zip_code, country])
                else:
                    updates.append("postal_address = %s")
                    params.append(str(postal_address))
            
            if profile_photo_url_final is not None:
                updates.append("profile_photo_url = %s")
                params.append(profile_photo_url_final)
            
            if not updates:
                return jsonify({'error': 'Aucune donnée à mettre à jour'}), 400
            
            updates.append("updated_at = CURRENT_TIMESTAMP")
            params.append(user_id)
            
            query = f"UPDATE users SET {', '.join(updates)} WHERE id = %s"
            cursor.execute(query, params)
            conn.commit()
            
            # Récupérer l'utilisateur mis à jour
            cursor.execute("""
                SELECT id, email, username, first_name, last_name, subscription, role,
                       avatar_emoji, avatar_description, profile_photo_url,
                       postal_address, postal_city, postal_zip, postal_country,
                       created_at, password_hash IS NOT NULL as has_password
                FROM users WHERE id = %s
            """, (user_id,))
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if not row:
                return jsonify({'error': 'User not found'}), 404
            
            # Construire la réponse
            user_data = {
                'id': str(row[0]),
                'email': str(row[1]) if row[1] else '',
                'username': str(row[2]) if row[2] else '',
                'firstName': str(row[3]) if row[3] else '',
                'lastName': str(row[4]) if row[4] else '',
                'subscription': str(row[5]) if row[5] else 'free',
                'role': str(row[6]) if row[6] else 'user',
                'avatar': str(row[7]) if row[7] else '👤',
                'avatarDescription': str(row[8]) if row[8] else '',
                'profilePhoto': str(row[9]) if row[9] else '',
                'profile_photo_url': str(row[9]) if row[9] else '',
                'hasPassword': bool(row[14])
            }
            
            # Construire postalAddress si disponible
            if row[10] or row[11] or row[12] or row[13]:
                user_data['postalAddress'] = {
                    'address': str(row[10]) if row[10] else '',
                    'city': str(row[11]) if row[11] else '',
                    'zip': str(row[12]) if row[12] else '',
                    'country': str(row[13]) if row[13] else 'CH'
                }
                user_data['postal_address'] = user_data['postalAddress']
            
            return jsonify({'user': user_data}), 200
            
        except Exception as e:
            logger.error(f"Erreur update_user_profile: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/user/<user_id>/avatar', methods=['GET'])
    @require_auth
    def get_user_avatar(user_id):
        """Récupère l'avatar d'un utilisateur (PROTÉGÉ par JWT et paramètres de confidentialité)."""
        try:
            requesting_user_id = request.user_id  # Utilisateur qui fait la requête
            
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = conn.cursor()
            
            # Récupérer l'avatar ET les paramètres de confidentialité
            cursor.execute("""
                SELECT profile_photo_url, show_photo, profile_public
                FROM users WHERE id = %s
            """, (user_id,))
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if not row:
                return jsonify({'error': 'User not found'}), 404
            
            profile_photo_url, show_photo, profile_public = row
            
            # Vérifier les paramètres de confidentialité
            # Si l'utilisateur demande son propre avatar, toujours autoriser
            is_own_avatar = (requesting_user_id == user_id)
            
            # Si ce n'est pas son propre avatar, vérifier les paramètres de confidentialité
            if not is_own_avatar:
                # Si show_photo est False, l'avatar est privé
                if show_photo is False:
                    return jsonify({'error': 'Avatar privé'}), 403
                
                # Si profile_public est False, le profil est privé
                if profile_public is False:
                    return jsonify({'error': 'Profil privé'}), 403
            
            if not profile_photo_url:
                return jsonify({'error': 'Avatar not found'}), 404
            
            # Vérifier que c'est bien une base64
            if profile_photo_url.startswith('data:image'):
                return jsonify({
                    'avatar': profile_photo_url,
                    'type': 'base64',
                    'size': len(profile_photo_url)
                }), 200
            elif profile_photo_url.startswith('http'):
                # C'est une URL S3, retourner l'URL directement
                return jsonify({
                    'avatar': profile_photo_url,
                    'type': 'url',
                    'url': profile_photo_url
                }), 200
            else:
                # Emoji ou autre
                return jsonify({
                    'avatar': profile_photo_url,
                    'type': 'emoji'
                }), 200
                
        except Exception as e:
            logger.error(f"Erreur get_user_avatar: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/migrate-address-fields', methods=['POST'])
    def admin_migrate_address_fields():
        """Exécute la migration pour ajouter les champs d'adresse et la table user_alert_settings."""
        try:
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = conn.cursor()
            results = []
            
            # Ajouter les colonnes d'adresse si elles n'existent pas
            try:
                cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS address_label VARCHAR(500)")
                cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS address_lat DECIMAL(10, 8)")
                cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS address_lng DECIMAL(11, 8)")
                cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS address_country_code VARCHAR(2)")
                cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS address_city VARCHAR(100)")
                cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS address_postcode VARCHAR(20)")
                cursor.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS address_street VARCHAR(200)")
                results.append("Colonnes d'adresse ajoutées/vérifiées dans users")
            except Exception as e:
                results.append(f"Erreur colonnes adresse: {e}")
            
            # Créer l'index sur les coordonnées
            try:
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_users_address_coords 
                    ON users(address_lat, address_lng) 
                    WHERE address_lat IS NOT NULL AND address_lng IS NOT NULL
                """)
                results.append("Index sur coordonnées créé/vérifié")
            except Exception as e:
                results.append(f"Erreur index coordonnées: {e}")
            
            # Créer la table user_alert_settings
            try:
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_alert_settings (
                        id SERIAL PRIMARY KEY,
                        user_id VARCHAR(255) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        alert_radius_km INTEGER DEFAULT 50,
                        categories TEXT[],
                        frequency VARCHAR(20) DEFAULT 'realtime',
                        enabled BOOLEAN DEFAULT true,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        UNIQUE(user_id)
                    )
                """)
                results.append("Table user_alert_settings créée/vérifiée")
            except Exception as e:
                results.append(f"Erreur table user_alert_settings: {e}")
            
            # Créer l'index sur user_id
            try:
                cursor.execute("""
                    CREATE INDEX IF NOT EXISTS idx_user_alert_settings_user_id 
                    ON user_alert_settings(user_id)
                """)
                results.append("Index sur user_alert_settings.user_id créé/vérifié")
            except Exception as e:
                results.append(f"Erreur index user_alert_settings: {e}")
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info("Migration adresse exécutée avec succès")
            
            return jsonify({
                'success': True,
                'message': 'Migration exécutée avec succès',
                'results': results
            }), 200
            
        except Exception as e:
            logger.error(f"Erreur migration adresse: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({'error': str(e), 'results': results if 'results' in locals() else []}), 500
    
    @app.route('/api/admin/create-user-passwords-table', methods=['POST'])
    def admin_create_user_passwords_table():
        """Endpoint admin pour créer la table user_passwords"""
        try:
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = conn.cursor()
            
            # Créer la table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_passwords (
                    user_id VARCHAR(255) PRIMARY KEY,
                    password_hash TEXT NOT NULL,
                    salt VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Ajouter la contrainte de clé étrangère
            cursor.execute("""
                DO $$
                BEGIN
                    IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users') THEN
                        IF NOT EXISTS (
                            SELECT 1 FROM information_schema.table_constraints 
                            WHERE constraint_name = 'user_passwords_user_id_fkey'
                        ) THEN
                            ALTER TABLE user_passwords 
                            ADD CONSTRAINT user_passwords_user_id_fkey 
                            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE;
                        END IF;
                    END IF;
                END $$;
            """)
            
            # Créer l'index
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_passwords_user ON user_passwords(user_id);
            """)
            
            conn.commit()
            
            # Vérifier que la table existe
            cursor.execute("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'user_passwords'
                )
            """)
            
            table_exists = cursor.fetchone()[0]
            
            cursor.close()
            conn.close()
            
            if table_exists:
                return jsonify({
                    'success': True,
                    'message': 'Table user_passwords créée avec succès'
                }), 200
            else:
                return jsonify({
                    'success': False,
                    'error': 'La table n\'a pas été créée'
                }), 500
                
        except Exception as e:
            logger.error(f"Erreur création table user_passwords: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/list-users', methods=['GET'])
    def admin_list_users():
        """
        Endpoint admin pour lister les utilisateurs (pour debug)
        Usage: GET /api/admin/list-users?email=<email> (optionnel)
        """
        try:
            email_filter = request.args.get('email', '').strip()
            
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = conn.cursor()
            
            if email_filter:
                cursor.execute("SELECT id, email, username, first_name, last_name, created_at FROM users WHERE email ILIKE %s ORDER BY created_at DESC LIMIT 10", (f'%{email_filter}%',))
            else:
                cursor.execute("SELECT id, email, username, first_name, last_name, created_at FROM users ORDER BY created_at DESC LIMIT 20")
            
            users = cursor.fetchall()
            cursor.close()
            conn.close()
            
            users_list = []
            for user in users:
                users_list.append({
                    'id': user[0],
                    'email': user[1],
                    'username': user[2],
                    'first_name': user[3],
                    'last_name': user[4],
                    'created_at': str(user[5]) if user[5] else None
                })
            
            return jsonify({
                'success': True,
                'count': len(users_list),
                'users': users_list
            }), 200
            
        except Exception as e:
            logger.error(f"Erreur admin_list_users: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/delete-all-users-simple', methods=['POST'])
    def admin_delete_all_users_simple():
        """
        Supprime TOUS les comptes utilisateurs (version simple sans authentification).
        ATTENTION: À protéger en production!
        """
        try:
            data = request.get_json() or {}
            confirm = data.get('confirm', '').lower()
            
            if confirm != 'yes':
                return jsonify({
                    'error': 'Confirmation requise. Envoyez {"confirm": "yes"} pour confirmer.',
                    'warning': 'Cette opération supprimera TOUS les comptes utilisateurs de manière IRRÉVERSIBLE!'
                }), 400
            
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = conn.cursor()
            
            # Compter avant suppression
            cursor.execute("SELECT COUNT(*) FROM users")
            total_before = cursor.fetchone()[0]
            
            if total_before == 0:
                cursor.close()
                conn.close()
                return jsonify({
                    'success': True,
                    'message': 'Aucun compte à supprimer',
                    'deleted_count': 0
                }), 200
            
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
                return jsonify({
                    'error': f'Erreur: {total_after} comptes restants'
                }), 500
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.warning(f"TOUS LES COMPTES ONT ÉTÉ SUPPRIMÉS: {deleted_count} supprimés")
            
            return jsonify({
                'success': True,
                'message': 'Tous les comptes ont été supprimés avec succès',
                'deleted_count': deleted_count
            }), 200
            
        except Exception as e:
            logger.error(f"Erreur admin_delete_all_users_simple: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/delete-all-users-except', methods=['POST'])
    def admin_delete_all_users_except():
        """
        Supprime tous les comptes SAUF celui spécifié.
        VERSION SIMPLE - Pas besoin d'authentification pour faciliter l'utilisation.
        ATTENTION: À protéger en production avec authentification!
        """
        try:
            data = request.get_json() or {}
            keep_email = data.get('keepEmail', '').strip().lower()
            
            if not keep_email:
                return jsonify({
                    'error': 'keepEmail requis. Exemple: {"keepEmail": "admin@example.com"}'
                }), 400
            
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = conn.cursor()
            
            # Vérifier que le compte à garder existe
            cursor.execute("SELECT id, email, username FROM users WHERE LOWER(email) = %s", (keep_email,))
            keep_user = cursor.fetchone()
            
            if not keep_user:
                cursor.close()
                conn.close()
                return jsonify({
                    'error': f'Le compte avec l\'email {keep_email} n\'existe pas'
                }), 404
            
            # Compter les comptes avant suppression
            cursor.execute("SELECT COUNT(*) FROM users")
            total_before = cursor.fetchone()[0]
            
            # Supprimer tous les comptes sauf celui à garder
            cursor.execute("DELETE FROM users WHERE LOWER(email) != %s", (keep_email,))
            deleted_count = cursor.rowcount
            
            # Vérifier
            cursor.execute("SELECT COUNT(*) FROM users")
            total_after = cursor.fetchone()[0]
            
            if total_after != 1:
                conn.rollback()
                cursor.close()
                conn.close()
                return jsonify({
                    'error': f'Erreur: {total_after} comptes restants au lieu de 1'
                }), 500
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.warning(f"TOUS LES COMPTES SAUF {keep_email} ONT ÉTÉ SUPPRIMÉS: {deleted_count} supprimés")
            
            return jsonify({
                'success': True,
                'message': f'Tous les comptes ont été supprimés sauf {keep_email}',
                'deleted_count': deleted_count,
                'kept_account': {
                    'email': keep_user[1],
                    'username': keep_user[2]
                }
            }), 200
            
        except Exception as e:
            logger.error(f"Erreur admin_delete_all_users_except: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/delete-all-users', methods=['POST'])
    @require_auth
    def admin_delete_all_users():
        """
        Supprime TOUS les comptes utilisateurs et leurs données associées.
        ATTENTION: Cette opération est IRRÉVERSIBLE!
        
        PROTECTION: Requiert authentification JWT avec rôle 'director' ou 'admin'.
        Requiert une confirmation via le paramètre confirm=true dans le body.
        """
        try:
            # Vérifier que l'utilisateur est un administrateur
            user_role = request.user_role
            if user_role not in ['director', 'admin']:
                logger.warning(f"Tentative d'accès non autorisée à delete-all-users par {request.user_id} (role: {user_role})")
                return jsonify({
                    'error': 'Accès refusé. Seuls les administrateurs peuvent supprimer tous les comptes.'
                }), 403
            
            data = request.get_json() or {}
            confirm = data.get('confirm', '').lower()
            
            if confirm != 'yes':
                return jsonify({
                    'error': 'Confirmation requise. Envoyez {"confirm": "yes"} pour confirmer.',
                    'warning': 'Cette opération supprimera TOUS les comptes utilisateurs de manière IRRÉVERSIBLE!'
                }), 400
            
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = conn.cursor()
            
            # 1. Récupérer tous les user_ids avant suppression
            cursor.execute("SELECT id, email, username, profile_photo_url FROM users")
            all_users = cursor.fetchall()
            user_count = len(all_users)
            
            if user_count == 0:
                cursor.close()
                conn.close()
                return jsonify({
                    'success': True,
                    'message': 'Aucun utilisateur à supprimer',
                    'deleted_count': 0
                }), 200
            
            user_ids = [user[0] for user in all_users]
            
            # 2. Compter les données associées
            cursor.execute("SELECT COUNT(*) FROM user_likes")
            likes_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM user_favorites")
            favorites_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM user_agenda")
            agenda_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM user_participations")
            participations_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM user_reviews")
            reviews_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM user_passwords")
            passwords_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM subscriptions")
            subscriptions_count = cursor.fetchone()[0]
            
            # 3. Supprimer tous les avatars S3
            deleted_avatars = 0
            try:
                from services.s3_service import delete_avatar_from_s3
                for user_id in user_ids:
                    if delete_avatar_from_s3(user_id):
                        deleted_avatars += 1
            except Exception as s3_error:
                logger.warning(f"Erreur suppression avatars S3: {s3_error}")
            
            # 4. Supprimer tous les utilisateurs (CASCADE supprimera automatiquement toutes les données liées)
            cursor.execute("DELETE FROM users")
            deleted_rows = cursor.rowcount
            
            # 5. Vérifier que tous les utilisateurs ont été supprimés
            cursor.execute("SELECT COUNT(*) FROM users")
            remaining = cursor.fetchone()[0]
            
            if remaining > 0:
                conn.rollback()
                cursor.close()
                conn.close()
                return jsonify({
                    'error': f'Échec de la suppression. {remaining} utilisateur(s) restant(s)'
                }), 500
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.warning(f"TOUS LES COMPTES UTILISATEURS ONT ÉTÉ SUPPRIMÉS: {deleted_rows} utilisateur(s)")
            
            return jsonify({
                'success': True,
                'message': 'Tous les comptes utilisateurs ont été supprimés avec succès',
                'deleted_count': deleted_rows,
                'deleted_data': {
                    'users': deleted_rows,
                    'likes': likes_count,
                    'favorites': favorites_count,
                    'agenda': agenda_count,
                    'participations': participations_count,
                    'reviews': reviews_count,
                    'passwords': passwords_count,
                    'subscriptions': subscriptions_count,
                    'avatars_s3': deleted_avatars
                }
            }), 200
            
        except Exception as e:
            logger.error(f"Erreur admin_delete_all_users: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/admin/delete-user', methods=['POST'])
    def admin_delete_user():
        """
        Endpoint admin pour supprimer un compte utilisateur
        Usage: POST /api/admin/delete-user
        Body: {"email": "user@example.com"}
        """
        try:
            data = request.get_json()
            email = data.get('email')
            
            if not email:
                return jsonify({'error': 'Email requis'}), 400
            
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = conn.cursor()
            
            # 1. Trouver l'utilisateur
            cursor.execute("SELECT id, username, email, profile_photo_url FROM users WHERE email = %s", (email,))
            user = cursor.fetchone()
            
            if not user:
                cursor.close()
                conn.close()
                return jsonify({'error': f'Utilisateur non trouvé avec l\'email: {email}'}), 404
            
            user_id, username, user_email, profile_photo_url = user
            
            # 2. Compter les données associées
            cursor.execute("SELECT COUNT(*) FROM user_likes WHERE user_id = %s", (user_id,))
            likes_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM user_favorites WHERE user_id = %s", (user_id,))
            favorites_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM user_participations WHERE user_id = %s", (user_id,))
            participations_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM user_reviews WHERE user_id = %s", (user_id,))
            reviews_count = cursor.fetchone()[0]
            
            # 3. Supprimer l'avatar S3 si présent
            if profile_photo_url:
                try:
                    from backend.services.s3_service import delete_avatar_from_s3
                    delete_avatar_from_s3(user_id)
                    logger.info(f"Avatar S3 supprimé pour user_id: {user_id}")
                except Exception as s3_error:
                    logger.warning(f"Erreur suppression avatar S3: {s3_error}")
            
            # 4. Supprimer l'utilisateur (CASCADE supprimera automatiquement toutes les données liées)
            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            
            # Vérifier que la suppression a réussi
            cursor.execute("SELECT COUNT(*) FROM users WHERE id = %s", (user_id,))
            remaining = cursor.fetchone()[0]
            
            if remaining > 0:
                conn.rollback()
                cursor.close()
                conn.close()
                return jsonify({'error': 'Échec de la suppression'}), 500
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"Compte utilisateur supprimé: {email} (user_id: {user_id})")
            
            return jsonify({
                'success': True,
                'message': f'Compte utilisateur supprimé avec succès',
                'deleted_user': {
                    'id': user_id,
                    'email': user_email,
                    'username': username
                },
                'deleted_data': {
                    'likes': likes_count,
                    'favorites': favorites_count,
                    'participations': participations_count,
                    'reviews': reviews_count
                }
            }), 200
            
        except Exception as e:
            logger.error(f"Erreur admin_delete_user: {e}")
            import traceback
            logger.error(traceback.format_exc())
            if conn:
                conn.rollback()
                cursor.close()
                conn.close()
            return jsonify({'error': str(e)}), 500
    
    # ⚠️⚠️⚠️ ENDPOINT DE DIAGNOSTIC ET CORRECTION USERNAME
    @app.route('/api/admin/fix-username', methods=['POST'])
    def admin_fix_username():
        """
        Endpoint pour diagnostiquer et corriger les problèmes de username.
        Permet de :
        1. Voir qui possède un username donné
        2. Forcer un username pour un utilisateur (en libérant le username si nécessaire)
        """
        try:
            data = request.get_json()
            target_email = data.get('email', '').strip().lower()
            target_username = data.get('username', '').strip()
            action = data.get('action', 'diagnose')  # 'diagnose' ou 'fix'
            
            if not target_email or not target_username:
                return jsonify({'error': 'email et username requis'}), 400
            
            conn = get_db_connection()
            if not conn:
                return jsonify({'error': 'Database connection failed'}), 500
            
            cursor = conn.cursor()
            
            # 1. Trouver l'utilisateur cible (par email)
            cursor.execute("""
                SELECT id, email, username, first_name, last_name, created_at
                FROM users WHERE LOWER(email) = LOWER(%s)
            """, (target_email,))
            target_user = cursor.fetchone()
            
            # 2. Trouver qui possède actuellement le username
            cursor.execute("""
                SELECT id, email, username, first_name, last_name, created_at
                FROM users WHERE LOWER(username) = LOWER(%s)
            """, (target_username,))
            username_owner = cursor.fetchone()
            
            result = {
                'target_user': {
                    'id': target_user[0] if target_user else None,
                    'email': target_user[1] if target_user else None,
                    'current_username': target_user[2] if target_user else None,
                    'name': f"{target_user[3] or ''} {target_user[4] or ''}".strip() if target_user else None,
                    'created_at': str(target_user[5]) if target_user else None
                } if target_user else None,
                'username_owner': {
                    'id': username_owner[0] if username_owner else None,
                    'email': username_owner[1] if username_owner else None,
                    'username': username_owner[2] if username_owner else None,
                    'name': f"{username_owner[3] or ''} {username_owner[4] or ''}".strip() if username_owner else None,
                    'created_at': str(username_owner[5]) if username_owner else None
                } if username_owner else None,
                'conflict': username_owner is not None and target_user is not None and username_owner[0] != target_user[0],
                'same_user': username_owner is not None and target_user is not None and username_owner[0] == target_user[0]
            }
            
            if action == 'diagnose':
                cursor.close()
                conn.close()
                return jsonify({
                    'action': 'diagnose',
                    'result': result,
                    'recommendation': 'Utilisez action=fix pour corriger' if result['conflict'] else 'Pas de conflit ou username libre'
                }), 200
            
            elif action == 'fix':
                if not target_user:
                    cursor.close()
                    conn.close()
                    return jsonify({'error': f'Utilisateur {target_email} non trouvé'}), 404
                
                target_user_id = target_user[0]
                
                # Si le username appartient à un autre utilisateur, le libérer
                if username_owner and username_owner[0] != target_user_id:
                    other_user_id = username_owner[0]
                    other_user_email = username_owner[1]
                    
                    # Générer un nouveau username pour l'autre utilisateur (basé sur son email)
                    new_username_for_other = other_user_email.split('@')[0] + '_' + str(int(datetime.now().timestamp()))[-6:]
                    
                    logger.info(f"[FIX-USERNAME] Libération du username '{target_username}' de {other_user_email} -> {new_username_for_other}")
                    
                    cursor.execute("""
                        UPDATE users SET username = %s, updated_at = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """, (new_username_for_other, other_user_id))
                    
                    result['freed_from'] = {
                        'user_id': other_user_id,
                        'email': other_user_email,
                        'new_username': new_username_for_other
                    }
                
                # Attribuer le username à l'utilisateur cible
                cursor.execute("""
                    UPDATE users SET username = %s, updated_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                """, (target_username, target_user_id))
                
                conn.commit()
                
                # Vérifier le résultat
                cursor.execute("SELECT username FROM users WHERE id = %s", (target_user_id,))
                updated_username = cursor.fetchone()
                
                cursor.close()
                conn.close()
                
                logger.info(f"[FIX-USERNAME] Username '{target_username}' attribué à {target_email}")
                
                return jsonify({
                    'action': 'fix',
                    'success': True,
                    'result': result,
                    'new_username': updated_username[0] if updated_username else None,
                    'message': f"Username '{target_username}' attribué avec succès à {target_email}"
                }), 200
            
            else:
                cursor.close()
                conn.close()
                return jsonify({'error': 'action doit être "diagnose" ou "fix"'}), 400
                
        except Exception as e:
            logger.error(f"Erreur admin_fix_username: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return jsonify({'error': str(e)}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)

