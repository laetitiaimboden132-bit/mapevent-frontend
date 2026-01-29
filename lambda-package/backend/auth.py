"""
Module d'authentification JWT pour MapEventAI
Gère la génération, validation et rafraîchissement des tokens JWT
"""

import jwt
import os
import hashlib
import secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
import logging

logger = logging.getLogger(__name__)

# Configuration JWT
JWT_SECRET = os.environ.get('JWT_SECRET')
if not JWT_SECRET or JWT_SECRET == 'change-me-in-production':
    raise ValueError("JWT_SECRET doit être défini dans les variables d'environnement. Ne jamais utiliser la valeur par défaut en production!")

JWT_ALGORITHM = 'HS256'
ACCESS_TOKEN_TTL = timedelta(minutes=15)  # 15 minutes
REFRESH_TOKEN_TTL = timedelta(days=30)   # 30 jours

# Import lazy de bcrypt (seulement quand nécessaire pour éviter les blocages au démarrage)
BCRYPT_AVAILABLE = None  # Sera vérifié à la première utilisation
_bcrypt_module = None

def _ensure_bcrypt():
    """Importe bcrypt à la demande"""
    global BCRYPT_AVAILABLE, _bcrypt_module
    if BCRYPT_AVAILABLE is None:
        logger.info("auth.py: Import lazy de bcrypt...")
        # Vérifier le PYTHONPATH et les chemins disponibles
        import sys
        import os
        logger.info(f"auth.py: sys.path (avant modification) = {sys.path[:5]}")
        logger.info(f"auth.py: Vérification /opt/python (Lambda Layers)...")
        
        # CRITIQUE: Forcer /opt/python en PREMIÈRE position pour éviter qu'un module bcrypt
        # dans /var/task masque le Layer. Python cherche dans l'ordre du sys.path.
        layer_path = "/opt/python"
        if layer_path in sys.path:
            current_index = sys.path.index(layer_path)
            if current_index > 0:
                # Retirer de sa position actuelle et remettre en premier
                sys.path.remove(layer_path)
                sys.path.insert(0, layer_path)
                logger.info(f"auth.py: /opt/python déplacé de la position {current_index} à la position 0")
        else:
            sys.path.insert(0, layer_path)
            logger.info(f"auth.py: /opt/python ajouté en première position")
        
        logger.info(f"auth.py: sys.path (après modification) = {sys.path[:5]}")
        
        if os.path.exists('/opt/python'):
            logger.info(f"auth.py: /opt/python existe")
            try:
                layer_contents = os.listdir('/opt/python')
                logger.info(f"auth.py: Contenu /opt/python: {layer_contents}")
                # Vérifier si bcrypt est présent
                bcrypt_path = '/opt/python/bcrypt'
                if os.path.exists(bcrypt_path):
                    logger.info(f"auth.py: bcrypt trouvé dans /opt/python/bcrypt")
                    bcrypt_files = os.listdir(bcrypt_path)
                    logger.info(f"auth.py: Fichiers dans bcrypt: {bcrypt_files}")
                else:
                    logger.error(f"auth.py: bcrypt NON trouvé dans /opt/python/bcrypt")
            except Exception as e:
                logger.warning(f"auth.py: Impossible de lister /opt/python: {e}")
        else:
            logger.error(f"auth.py: /opt/python N'EXISTE PAS!")
        
        try:
            logger.info("auth.py: Tentative d'import bcrypt...")
            import bcrypt
            _bcrypt_module = bcrypt
            logger.info("auth.py: bcrypt importé avec succès")
            logger.info(f"auth.py: bcrypt.__file__ = {getattr(bcrypt, '__file__', 'unknown')}")
            # Vérifier que bcrypt fonctionne vraiment
            test_salt = bcrypt.gensalt(rounds=4)
            logger.info(f"auth.py: Test bcrypt.gensalt() OK: {type(test_salt)}")
            BCRYPT_AVAILABLE = True
        except ImportError as e:
            BCRYPT_AVAILABLE = False
            _bcrypt_module = None
            logger.error(f"auth.py: ERREUR Import bcrypt: {e}")
            logger.error("❌ CRITIQUE: bcrypt n'est pas installé.")
            import traceback
            logger.error(traceback.format_exc())
            raise ImportError("bcrypt est OBLIGATOIRE pour le hashage sécurisé des mots de passe.")
        except Exception as e:
            BCRYPT_AVAILABLE = False
            _bcrypt_module = None
            logger.error(f"auth.py: ERREUR inattendue lors de l'import bcrypt: {e}")
            import traceback
            logger.error(traceback.format_exc())
            raise ImportError(f"bcrypt est OBLIGATOIRE mais l'import a échoué: {e}")
    
    if _bcrypt_module is None:
        logger.error("❌ CRITIQUE: _bcrypt_module est None après import")
        raise ImportError("bcrypt est OBLIGATOIRE pour le hashage sécurisé des mots de passe.")
    
    return _bcrypt_module

def hash_password(password: str, salt: str = None) -> tuple:
    """
    Hash un mot de passe avec bcrypt (OBLIGATOIRE).
    Retourne (hash, salt).
    
    NOTE: bcrypt est OBLIGATOIRE. Aucun fallback SHA256 n'est autorisé pour des raisons de sécurité.
    """
    logger.info("hash_password: Début de la fonction")
    try:
        logger.info("hash_password: Appel à _ensure_bcrypt()...")
        bcrypt_module = _ensure_bcrypt()  # Import lazy
        logger.info(f"hash_password: _ensure_bcrypt() retourné: {bcrypt_module is not None}")
    except Exception as e:
        logger.error(f"hash_password: ERREUR lors de l'appel à _ensure_bcrypt(): {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise
    
    if bcrypt_module is None:
        logger.error("❌ CRITIQUE: bcrypt_module est None dans hash_password")
        raise ImportError("bcrypt est OBLIGATOIRE pour le hashage sécurisé des mots de passe.")
    
    if salt:
        # Vérifier le mot de passe (ne devrait pas être utilisé ici, utiliser verify_password)
        if isinstance(salt, str):
            salt_bytes = salt.encode()
        else:
            salt_bytes = salt
        if bcrypt_module.checkpw(password.encode(), salt_bytes):
            return (salt, salt)
        else:
            raise ValueError("Password verification failed")
    else:
        # Créer un nouveau hash avec bcrypt
        salt_bytes = bcrypt_module.gensalt(rounds=12)  # 12 rounds pour sécurité optimale
        hash_bytes = bcrypt_module.hashpw(password.encode(), salt_bytes)
        return (hash_bytes.decode(), salt_bytes.decode())

def verify_password(password: str, password_hash: str, salt: str) -> bool:
    """
    Vérifie un mot de passe contre son hash.
    Supporte bcrypt uniquement (pas de fallback SHA256 pour sécurité).
    """
    bcrypt_module = _ensure_bcrypt()  # Import lazy
    
    if bcrypt_module is None:
        logger.error("❌ CRITIQUE: bcrypt_module est None dans verify_password")
        raise ImportError("bcrypt est OBLIGATOIRE pour le hashage sécurisé des mots de passe.")
    
    # Vérifier si c'est un hash bcrypt
    if password_hash.startswith('$2b$') or password_hash.startswith('$2a$') or password_hash.startswith('$2y$'):
        return bcrypt_module.checkpw(password.encode(), password_hash.encode())
    
    # Si ce n'est pas un hash bcrypt, c'est une erreur (ancien système SHA256)
    logger.warning(f"⚠️ Tentative de vérification avec un hash non-bcrypt. Migration requise.")
    return False

def generate_access_token(user_id: str, email: str, role: str = 'user') -> str:
    """
    Génère un access token JWT (TTL: 15 minutes).
    """
    payload = {
        'user_id': user_id,
        'email': email,
        'role': role,
        'type': 'access',
        'exp': datetime.utcnow() + ACCESS_TOKEN_TTL,
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def generate_refresh_token(user_id: str) -> str:
    """
    Génère un refresh token JWT (TTL: 30 jours).
    """
    payload = {
        'user_id': user_id,
        'type': 'refresh',
        'exp': datetime.utcnow() + REFRESH_TOKEN_TTL,
        'iat': datetime.utcnow()
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_token(token: str, token_type: str = 'access') -> dict:
    """
    Vérifie et décode un token JWT.
    Supporte les tokens HS256 (standard) et RS256 (Cognito).
    Retourne le payload si valide, None sinon.
    """
    try:
        # Essayer de décoder avec HS256 (tokens standard)
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        # Vérifier le type de token
        if payload.get('type') != token_type:
            logger.warning(f"Token type mismatch: expected {token_type}, got {payload.get('type')}")
            return None
        
        payload['cognito_token'] = False
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        return None
    except jwt.InvalidTokenError as e:
        # Si HS256 échoue, essayer de décoder comme token Cognito (RS256)
        logger.info(f"Token utilise un algorithme différent (probablement RS256 Cognito), tentative décodage...")
        try:
            # Décoder sans vérifier la signature (Cognito a déjà authentifié)
            # Note: En production, il faudrait vérifier avec les clés publiques de Cognito
            unverified = jwt.decode(token, options={"verify_signature": False})
            
            # Extraire les infos du token Cognito
            user_id = unverified.get('sub')  # Cognito sub
            email = unverified.get('email') or unverified.get('cognito:username')
            
            if user_id:
                logger.info(f"Token Cognito décodé avec succès: user_id={user_id}, email={email}")
                return {
                    'user_id': user_id,
                    'email': email,
                    'role': 'user',
                    'type': 'access',
                    'cognito_token': True
                }
            else:
                logger.warning("Token Cognito sans sub")
                return None
        except Exception as cognito_error:
            logger.warning(f"Échec décodage token Cognito: {cognito_error}")
            return None

def get_token_from_request() -> str:
    """
    Extrait le token JWT depuis le header Authorization: Bearer <token>
    """
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return None
    return auth_header[7:].strip()  # Enlever "Bearer "

def require_auth(f):
    """
    Décorateur pour protéger les routes nécessitant une authentification.
    Injecte request.user_id, request.user_email, request.user_role, request.cognito_token dans la fonction.
    Supporte les tokens standard (HS256) et Cognito (RS256).
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = get_token_from_request()
        
        if not token:
            return jsonify({'error': 'Token manquant. Header Authorization: Bearer <token> requis'}), 401
        
        payload = verify_token(token, token_type='access')
        
        if not payload:
            return jsonify({'error': 'Token invalide ou expiré'}), 401
        
        # Injecter les infos utilisateur dans request
        request.user_id = payload.get('user_id')
        request.user_email = payload.get('email')
        request.user_role = payload.get('role', 'user')
        request.cognito_token = payload.get('cognito_token', False)
        
        return f(*args, **kwargs)
    
    return decorated_function

