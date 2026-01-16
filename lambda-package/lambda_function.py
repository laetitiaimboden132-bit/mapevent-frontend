"""
Lambda Handler pour MapEventAI Backend
Réintroduction progressive des imports - Étape 5: DB + JWT
"""
import json
import logging
import sys
from pathlib import Path

# Configuration logging ASCII-safe
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.info("handler.py: Module init - ASCII-safe logging only")
logger.info("step=5 ok")

# Ajouter le chemin du backend au PYTHONPATH (sans importer)
backend_path = Path(__file__).parent / "backend"
backend_path_str = str(backend_path.resolve())
if backend_path_str not in sys.path:
    sys.path.insert(0, backend_path_str)
    logger.info(f"PYTHONPATH updated: {backend_path_str}")

# Variables globales pour l'app Flask (créée à la demande)
create_app_func = None
app = None

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
            headers = event.get("headers", {}) or {}
            headers_lower = {k.lower(): v for k, v in headers.items()}
            origin = headers_lower.get("origin", "")
            allowed_origins = ["https://mapevent.world", "http://localhost:8000", "http://127.0.0.1:8000"]
            cors_origin = origin if origin in allowed_origins else "https://mapevent.world"
            
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": cors_origin
                },
                "body": json.dumps({"ok": True})
            }
        
        # Gérer OPTIONS pour CORS
        if method == "OPTIONS":
            logger.info("lambda_handler: OPTIONS request - returning CORS headers")
            headers = event.get("headers", {}) or {}
            headers_lower = {k.lower(): v for k, v in headers.items()}
            origin = headers_lower.get("origin", "")
            
            # Whitelist des origines autorisées
            allowed_origins = ["https://mapevent.world", "http://localhost:8000", "http://127.0.0.1:8000"]
            
            # Autoriser mapevent.world explicitement
            if origin in allowed_origins:
                allowed_origin = origin
            else:
                # En production, ne pas autoriser "*" - seulement les origines whitelistées
                allowed_origin = "https://mapevent.world" if origin else "*"
            
            logger.info(f"lambda_handler: OPTIONS - origin={origin}, allowed_origin={allowed_origin}")
            
            return {
                "statusCode": 200,
                "headers": {
                    "Access-Control-Allow-Origin": allowed_origin,  # UNE SEULE valeur, jamais "origin1, *"
                    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
                    "Access-Control-Allow-Headers": "Content-Type, Authorization, Origin, X-Requested-With, Accept",
                    "Access-Control-Max-Age": "3600",
                    "Access-Control-Allow-Credentials": "false"
                },
                "body": ""
            }
        
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
                    return {
                        "statusCode": 500,
                        "headers": {
                            "Content-Type": "application/json",
                            "Access-Control-Allow-Origin": "*"
                        },
                        "body": json.dumps({"error": "Failed to import create_app", "details": str(e2)})
                    }
        
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
                headers = event.get("headers", {}) or {}
                headers_lower = {k.lower(): v for k, v in headers.items()}
                origin = headers_lower.get("origin", "")
                allowed_origins = ["https://mapevent.world", "http://localhost:8000", "http://127.0.0.1:8000"]
                cors_origin = origin if origin in allowed_origins else "https://mapevent.world"
                
                return {
                    "statusCode": 500,
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": cors_origin
                    },
                    "body": json.dumps({"error": "Failed to create Flask app", "details": str(e)})
                }
        
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
                headers = event.get("headers", {}) or {}
                headers_lower = {k.lower(): v for k, v in headers.items()}
                origin = headers_lower.get("origin", "")
                allowed_origins = ["https://mapevent.world", "http://localhost:8000", "http://127.0.0.1:8000"]
                cors_origin = origin if origin in allowed_origins else "https://mapevent.world"
                
                return {
                    "statusCode": 500,
                    "headers": {
                        "Content-Type": "application/json",
                        "Access-Control-Allow-Origin": cors_origin
                    },
                    "body": json.dumps({"error": "Flask routing error", "details": str(flask_error)})
                }
            
            # Récupérer le body de la réponse
            body_content = response.get_data(as_text=True)
            if not body_content:
                body_content = '{}'
            
            # Headers CORS - IMPORTANT: Ne jamais créer "origin1, *"
            origin = headers_lower.get('origin', '')
            allowed_origins = ['https://mapevent.world', 'http://localhost:8000', 'http://127.0.0.1:8000']
            
            # Autoriser mapevent.world explicitement
            if origin in allowed_origins:
                cors_origin = origin
            else:
                # En production, ne pas autoriser "*" - seulement les origines whitelistées
                cors_origin = "https://mapevent.world" if origin else "*"
            
            logger.info(f"lambda_handler: Response CORS - origin={origin}, cors_origin={cors_origin}, status={response.status_code}")
            
            # Construire les headers finaux
            # IMPORTANT: Supprimer TOUS les headers CORS de Flask avant d'ajouter les nôtres
            # Flask peut créer des doublons comme "https://mapevent.world, *" si plusieurs headers sont ajoutés
            final_headers = {}
            cors_headers_to_ignore = ['access-control-allow-origin', 'access-control-allow-methods', 
                                     'access-control-allow-headers', 'access-control-max-age', 
                                     'access-control-allow-credentials', 'access-control-expose-headers']
            
            # Log tous les headers Flask pour debug
            flask_cors_headers = []
            for key, value in response.headers:
                key_lower = key.lower()
                if key_lower in cors_headers_to_ignore:
                    flask_cors_headers.append(f"{key}={value}")
                else:
                    # Éviter les doublons : si la clé existe déjà, ne pas l'ajouter
                    if key not in final_headers:
                        final_headers[key] = value
            
            if flask_cors_headers:
                logger.warning(f"lambda_handler: Flask a ajoute des headers CORS: {', '.join(flask_cors_headers)}")
            
            # FORCER la suppression de tous les headers CORS (au cas où Flask les aurait ajoutés)
            # On les supprime explicitement même s'ils ne sont pas dans final_headers
            cors_keys_to_remove = ['Access-Control-Allow-Origin', 'Access-Control-Allow-Methods', 
                                  'Access-Control-Allow-Headers', 'Access-Control-Max-Age', 
                                  'Access-Control-Allow-Credentials', 'Access-Control-Expose-Headers']
            for cors_key in cors_keys_to_remove:
                # Supprimer toutes les variantes (majuscules, minuscules, etc.)
                keys_to_del = [k for k in final_headers.keys() if k.lower() == cors_key.lower()]
                for k in keys_to_del:
                    del final_headers[k]
            
            # CORS géré par Lambda Function URL - ne pas ajouter de headers CORS ici
            # Lambda Function URL ajoute automatiquement les headers CORS selon sa configuration
            # Ajouter nos propres headers CORS créerait des doublons comme "https://mapevent.world, *"
            if 'Content-Type' not in final_headers:
                final_headers['Content-Type'] = 'application/json'
            
            # Ne PAS ajouter de headers CORS - Lambda Function URL les gère automatiquement
            logger.info(f"lambda_handler: CORS gere par Lambda Function URL - pas de headers CORS ajoutes dans le handler")
            
            return {
                'statusCode': response.status_code,
                'headers': final_headers,
                'body': body_content
            }
        
    except Exception as e:
        logger.error(f"lambda_handler: Exception = {str(e)}")
        import traceback
        logger.error(f"lambda_handler: Traceback = {traceback.format_exc()}")
        headers = event.get("headers", {}) or {}
        headers_lower = {k.lower(): v for k, v in headers.items()}
        origin = headers_lower.get("origin", "")
        allowed_origins = ["https://mapevent.world", "http://localhost:8000", "http://127.0.0.1:8000"]
        cors_origin = origin if origin in allowed_origins else "https://mapevent.world"
        
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": cors_origin
            },
            "body": json.dumps({"error": "Internal server error", "details": str(e)})
        }
