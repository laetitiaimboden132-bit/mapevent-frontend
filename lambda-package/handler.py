"""
Lambda Handler pour MapEventAI Backend
Handler simple avec Flask test client - version ultra-simplifiée
"""

import sys
import json
from pathlib import Path

# Ajouter le chemin du backend au PYTHONPATH
backend_path = Path(__file__).parent / "backend"
backend_path_str = str(backend_path.resolve())
if backend_path_str not in sys.path:
    sys.path.insert(0, backend_path_str)

# Importer la fonction de création de l'app Flask (mais ne pas créer l'app maintenant)
try:
    from main import create_app
except ImportError as e:
    print(f"Import error: {e}")
    print(f"Python path: {sys.path}")
    # Ne pas lever l'erreur ici, on gérera OPTIONS même sans Flask

# Variable globale pour l'app Flask (créée à la demande)
app = None

def lambda_handler(event, context):
    """
    Handler Lambda pour API Gateway
    Version ultra-simplifiée avec Flask test client
    """
    # Gérer OPTIONS AVANT TOUT, même avant de créer l'app Flask
    try:
        method = event.get('httpMethod', event.get('requestContext', {}).get('http', {}).get('method', 'GET'))
        
        if method == 'OPTIONS':
            print(f"OK: Requete OPTIONS detectee")
            print(f"🔍 Event keys: {list(event.keys())}")
            
            # Extraire headers de différentes façons possibles
            headers = event.get('headers', {}) or {}
            if not headers:
                headers = event.get('multiValueHeaders', {}) or {}
            
            # Normaliser les clés de headers en minuscules
            headers_lower = {}
            if isinstance(headers, dict):
                headers_lower = {str(k).lower(): str(v) if v else '' for k, v in headers.items()}
            
            # Extraire l'origine
            origin = headers_lower.get('origin', '') or headers_lower.get('Origin', '')
            if not origin or origin.lower() in ['null', 'none', 'undefined']:
                origin = 'https://mapevent.world'
            
            allowed_origins = ['https://mapevent.world', 'http://localhost:8000', 'http://localhost:3000']
            cors_origin = origin if origin in allowed_origins else 'https://mapevent.world'
            
            print(f"🔍 Origin: {origin} -> CORS Origin: {cors_origin}")
            
            response = {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': cors_origin,
                    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS, PATCH',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization, Origin, X-Requested-With, Accept, X-Amz-Date, X-Api-Key, X-Amz-Security-Token',
                    'Access-Control-Allow-Credentials': 'true',
                    'Access-Control-Max-Age': '3600'
                },
                'body': ''
            }
            
            print(f"✅ Réponse OPTIONS: {json.dumps(response)}")
            return response
            
    except Exception as e:
        import traceback
        error_msg = f"Erreur dans OPTIONS: {str(e)}\n{traceback.format_exc()}"
        print(f"❌ {error_msg}")
        
        # Retourner quand même une réponse CORS valide même en cas d'erreur
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': 'https://mapevent.world',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS, PATCH',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization, Origin, X-Requested-With, Accept, X-Amz-Date, X-Api-Key, X-Amz-Security-Token',
                'Access-Control-Allow-Credentials': 'true',
                'Access-Control-Max-Age': '3600'
            },
            'body': ''
        }
    
    # Pour les autres méthodes, continuer avec Flask
    try:
        # Créer l'app Flask seulement maintenant (après avoir géré OPTIONS)
        global app
        if app is None:
            try:
                app = create_app()
                print("OK: Application Flask creee")
            except Exception as e:
                print(f"❌ Erreur création app Flask: {e}")
                import traceback
                print(traceback.format_exc())
                raise
        
        # Normaliser les headers (API Gateway peut les mettre en minuscules)
        headers = event.get('headers', {}) or {}
        # Normaliser les clés de headers en minuscules pour la recherche
        headers_lower = {k.lower(): v for k, v in headers.items()}
        
        # Extraire le chemin
        path = event.get('path', '/')
        print(f"🔍 Path reçu: {path}")  # Log pour diagnostic
        if path.startswith('/default'):
            path = path.replace('/default', '', 1)
        if not path.startswith('/'):
            path = '/' + path
        print(f"🔍 Path traité: {path}")  # Log pour diagnostic
        
        method = event.get('httpMethod', 'GET')
        print(f"🔍 Méthode: {method}")  # Log pour diagnostic
        
        query_params = event.get('queryStringParameters') or {}
        body = event.get('body', '')
        print(f"🔍 Body: {body[:100] if body else 'vide'}")  # Log pour diagnostic
        
        # Utiliser Flask test client avec gestion d'erreur robuste
        print(f"🔍 Appel Flask: {method} {path}")  # Log pour diagnostic
        
        try:
            with app.test_client() as client:
                try:
                    if method == 'GET':
                        response = client.get(path, query_string=query_params)
                    elif method == 'POST':
                        # Parser le body JSON si nécessaire
                        if body and isinstance(body, str):
                            try:
                                json_data = json.loads(body)
                                response = client.post(path, json=json_data, content_type='application/json')
                            except json.JSONDecodeError:
                                # Si ce n'est pas du JSON, envoyer tel quel
                                response = client.post(path, data=body, content_type='application/json')
                        else:
                            response = client.post(path, data=body, content_type='application/json')
                    else:
                        response = client.open(path, method=method, data=body)
                    
                    print(f"🔍 Réponse Flask: {response.status_code}")  # Log pour diagnostic
                    
                    # Récupérer le body avec gestion d'erreur
                    try:
                        body_content = response.get_data(as_text=True).rstrip('\n\r')
                        if not body_content:
                            body_content = '{}'
                        
                        # Vérifier la taille du body (limite Lambda: 6MB)
                        body_size_mb = len(body_content.encode('utf-8')) / (1024 * 1024)
                        if body_size_mb > 5.5:  # Limite à 5.5MB pour être sûr
                            print(f"⚠️ Body trop volumineux: {body_size_mb:.2f}MB - Tronquage")
                            # Si c'est du JSON, essayer de le réduire
                            try:
                                body_json = json.loads(body_content)
                                # Réduire les données si possible
                                if isinstance(body_json, dict):
                                    # Supprimer les champs volumineux inutiles
                                    for key in list(body_json.keys()):
                                        if isinstance(body_json[key], (list, dict)) and len(str(body_json[key])) > 10000:
                                            body_json[key] = f"[{type(body_json[key]).__name__} - {len(body_json[key])} items]"
                                    body_content = json.dumps(body_json)
                            except:
                                # Si ce n'est pas du JSON, tronquer
                                body_content = body_content[:5000000]  # Limiter à ~5MB
                    except Exception as body_error:
                        print(f"⚠️ Erreur récupération body: {body_error}")
                        body_content = '{"error": "Erreur lors de la récupération de la réponse"}'
                    
                    body_size_mb = len(body_content.encode('utf-8')) / (1024 * 1024)
                    print(f"🔍 Body réponse: {body_size_mb:.2f}MB (premiers 200 chars): {body_content[:200]}")  # Log pour diagnostic
                    
                    # Retourner la réponse avec headers CORS complets
                    # Utiliser l'origine spécifique pour une meilleure sécurité
                    origin = headers_lower.get('origin', 'https://mapevent.world')
                    if not origin or origin == 'null':
                        origin = 'https://mapevent.world'
                    allowed_origins = ['https://mapevent.world', 'http://localhost:8000', 'http://localhost:3000']
                    cors_origin = origin if origin in allowed_origins else 'https://mapevent.world'
                    
                    # Vérifier la taille finale avant de retourner (limite Lambda: 6MB)
                    final_body_size = len(body_content.encode('utf-8'))
                    final_body_size_mb = final_body_size / (1024 * 1024)
                    
                    if final_body_size_mb > 5.5:  # Limite à 5.5MB pour être sûr
                        print(f"⚠️ ATTENTION: Body final trop volumineux: {final_body_size_mb:.2f}MB")
                        # Retourner une erreur plutôt qu'une réponse trop grande
                        body_content = json.dumps({
                            'error': 'Response too large',
                            'message': f'La réponse dépasse la limite de taille ({final_body_size_mb:.2f}MB > 5.5MB)',
                            'size_mb': round(final_body_size_mb, 2)
                        })
                        response.status_code = 500
                    
                    return {
                        'statusCode': response.status_code,
                        'headers': {
                            'Content-Type': 'application/json',
                            'Access-Control-Allow-Origin': cors_origin,
                            'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS, PATCH',
                            'Access-Control-Allow-Headers': 'Content-Type, Authorization, Origin, X-Requested-With, Accept, X-Amz-Date, X-Api-Key, X-Amz-Security-Token',
                            'Access-Control-Allow-Credentials': 'true',
                            'Access-Control-Max-Age': '3600'
                        },
                        'body': body_content
                    }
                except Exception as flask_error:
                    import traceback
                    print(f"❌ Erreur dans Flask test client: {flask_error}")
                    print(traceback.format_exc())
                    raise
        except Exception as client_error:
            import traceback
            print(f"❌ Erreur création/utilisation test client: {client_error}")
            print(traceback.format_exc())
            raise
            
    except Exception as e:
        import traceback
        error_type = type(e).__name__
        error_message = str(e)
        error_traceback = traceback.format_exc()
        
        print(f"❌ ERREUR CRITIQUE dans lambda_handler: {error_type}")
        print(f"❌ Message: {error_message}")
        print(f"❌ Traceback complet:\n{error_traceback}")
        
        # TOUJOURS retourner une réponse valide, même en cas d'erreur
        try:
            error_body = json.dumps({
                'error': 'Internal Server Error',
                'message': error_message[:200],  # Limiter la longueur
                'type': error_type
            })
        except:
            error_body = json.dumps({'error': 'Internal Server Error'})
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS, PATCH',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization, Origin, X-Requested-With, Accept, X-Amz-Date, X-Api-Key, X-Amz-Security-Token',
                'Access-Control-Allow-Credentials': 'true',
                'Access-Control-Max-Age': '3600'
            },
            'body': error_body
        }
