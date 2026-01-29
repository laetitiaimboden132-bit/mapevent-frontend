"""
Lambda Handler pour MapEventAI Backend
Réintroduction progressive des imports - Étape 5: DB + JWT
"""
import sys
import os

# CRITIQUE: Ajouter /opt/python EN PREMIER avant TOUT autre import
# Cela garantit que les Lambda Layers (bcrypt, psycopg2) sont prioritaires
# sur tout module dans /var/task qui pourrait masquer le Layer
layer_path = "/opt/python"
if layer_path not in sys.path:
    sys.path.insert(0, layer_path)
elif sys.path.index(layer_path) > 0:
    # Si /opt/python existe mais n'est pas en première position, le déplacer
    sys.path.remove(layer_path)
    sys.path.insert(0, layer_path)

# Vérifier que /opt/python existe et contient bcrypt
if os.path.exists('/opt/python'):
    try:
        contents = os.listdir('/opt/python')
        if 'bcrypt' in contents:
            print(f"[INIT] /opt/python existe et contient bcrypt: {contents}")
        else:
            print(f"[INIT] /opt/python existe mais ne contient pas bcrypt: {contents}")
    except Exception as e:
        print(f"[INIT] Erreur lors de la vérification /opt/python: {e}")
else:
    print("[INIT] ATTENTION: /opt/python n'existe pas!")

import json
import logging
from pathlib import Path

# Configuration logging ASCII-safe
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.info("handler.py: Module init - ASCII-safe logging only")
logger.info("step=5 ok")
logger.info(f"PYTHONPATH (premiers 3): {sys.path[:3]}")

# CRITIQUE: Ajouter /opt/python EN PREMIER pour les Lambda Layers (bcrypt, psycopg2, etc.)
# Cela garantit que les modules du Layer sont utilisés avant ceux du code déployé
layer_path = "/opt/python"
if layer_path in sys.path:
    # Si déjà présent, le déplacer au début
    sys.path.remove(layer_path)
    sys.path.insert(0, layer_path)
    logger.info(f"PYTHONPATH: /opt/python déplacé en première position")
else:
    sys.path.insert(0, layer_path)
    logger.info(f"PYTHONPATH updated with Lambda Layers (PRIORITÉ): {layer_path}")

# Ajouter le chemin du backend au PYTHONPATH (sans importer)
backend_path = Path(__file__).parent / "backend"
backend_path_str = str(backend_path.resolve())
if backend_path_str not in sys.path:
    sys.path.insert(1, backend_path_str)  # Insérer après /opt/python
    logger.info(f"PYTHONPATH updated: {backend_path_str}")

# Variables globales pour l'app Flask (créée à la demande)
create_app_func = None
app = None

# =============================================================================
# CORS : Géré UNIQUEMENT par AWS Function URL (pas de headers ici)
# IMPORTANT: Ne PAS ajouter Access-Control-Allow-Origin ici sinon doublon !
# La config AWS Function URL doit avoir: Allow origin = https://mapevent.world
# =============================================================================

def _cors_response(status_code, body="", as_json=True, headers=None):
    """Réponse SANS headers CORS (AWS Function URL les ajoute)."""
    h = {"Content-Type": "application/json"} if body else {}
    payload = json.dumps(body) if as_json and body and not isinstance(body, str) else body
    return {"statusCode": status_code, "headers": h, "body": payload or ""}


def lambda_handler(event, context):
    """
    Handler Lambda avec routage Flask complet (DB + JWT)
    """
    logger.info("lambda_handler: Entry point called")
    
    try:
        # Extraire le chemin et la méthode
        path = event.get("rawPath") or event.get("path") or event.get("rawPathString") or "/"
        method = event.get("httpMethod") or event.get("requestContext", {}).get("http", {}).get("method", "GET")
        
        # Normaliser le chemin
        if path.startswith("/default"):
            path = path.replace("/default", "", 1)
        if not path.startswith("/"):
            path = "/" + path
        
        logger.info(f"lambda_handler: Path = {path}, Method = {method}")
        
        # Gérer /health AVANT tout import Flask
        if path == "/health" or path == "/api/health":
            logger.info("lambda_handler: /health endpoint - returning 200")
            return _cors_response(200, {"ok": True})

        # Gérer OPTIONS pour CORS (AWS Function URL ajoute les headers CORS)
        if method == "OPTIONS":
            logger.info("lambda_handler: OPTIONS request - returning 200 (CORS via AWS Function URL)")
            return {"statusCode": 200, "headers": {}, "body": ""}
        
        # Pour les autres routes, créer l'app Flask si nécessaire
        global app, create_app_func
        
        # Import lazy de create_app
        if create_app_func is None:
            logger.info("lambda_handler: Lazy import of create_app...")
            try:
                from main import create_app as create_app_func
                logger.info("lambda_handler: create_app imported successfully from main")
            except ImportError as e:
                logger.warning(f"lambda_handler: Import from main failed: {e}")
                try:
                    from backend.main import create_app as create_app_func
                    logger.info("lambda_handler: create_app imported successfully from backend.main")
                except ImportError as e2:
                    logger.error(f"lambda_handler: Import from backend.main failed: {e2}")
                    return _cors_response(500, {"error": "Failed to import create_app", "details": str(e2)})
        
        # Créer l'app Flask si nécessaire
        if app is None:
            logger.info("lambda_handler: Creating Flask app...")
            try:
                app = create_app_func()
                logger.info("lambda_handler: Flask app created successfully")
            except Exception as e:
                logger.error(f"lambda_handler: Failed to create Flask app: {e}")
                import traceback
                logger.error(f"lambda_handler: Traceback = {traceback.format_exc()}")
                return _cors_response(500, {"error": "Failed to create Flask app", "details": str(e)})
        
        # Utiliser Flask test client pour router les requêtes
        logger.info("lambda_handler: Using Flask test client for routing")
        with app.test_client() as client:
            # Préparer les headers
            headers = event.get('headers', {}) or {}
            headers_lower = {k.lower(): v for k, v in headers.items()}
            
            # Préparer le body
            body = event.get('body', '')
            query_params = event.get('queryStringParameters') or {}
            
            # Construire les headers Flask
            flask_headers = {}
            if 'authorization' in headers_lower:
                flask_headers['Authorization'] = headers_lower['authorization']
            
            # Appeler Flask
            try:
                if method == 'GET':
                    response = client.get(path, query_string=query_params, headers=flask_headers)
                elif method == 'POST':
                    if body:
                        try:
                            json_data = json.loads(body)
                            response = client.post(path, json=json_data, content_type='application/json', headers=flask_headers)
                        except json.JSONDecodeError:
                            response = client.post(path, data=body, content_type='application/json', headers=flask_headers)
                    else:
                        response = client.post(path, data=body, content_type='application/json', headers=flask_headers)
                elif method == 'PUT':
                    if body:
                        try:
                            json_data = json.loads(body)
                            response = client.put(path, json=json_data, content_type='application/json', headers=flask_headers)
                        except json.JSONDecodeError:
                            response = client.put(path, data=body, content_type='application/json', headers=flask_headers)
                    else:
                        response = client.put(path, data=body, content_type='application/json', headers=flask_headers)
                elif method == 'DELETE':
                    response = client.delete(path, headers=flask_headers)
                else:
                    response = client.open(path, method=method, data=body, headers=flask_headers)
            except Exception as flask_error:
                logger.error(f"lambda_handler: Flask routing error: {flask_error}")
                import traceback
                logger.error(f"lambda_handler: Traceback = {traceback.format_exc()}")
                return _cors_response(500, {"error": "Flask routing error", "details": str(flask_error)})
            
            # Récupérer le body de la réponse
            body_content = response.get_data(as_text=True)
            if not body_content:
                body_content = '{}'

            # PAS de headers CORS ici : AWS Function URL les ajoute
            logger.info(f"lambda_handler: Response status={response.status_code}")
            return {
                "statusCode": response.status_code,
                "headers": {"Content-Type": "application/json"},
                "body": body_content,
            }
        
    except Exception as e:
        logger.error(f"lambda_handler: Exception = {str(e)}")
        import traceback
        logger.error(f"lambda_handler: Traceback = {traceback.format_exc()}")
        # PAS de headers CORS ici : AWS Function URL les ajoute
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Internal server error", "details": str(e)})
        }
