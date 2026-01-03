"""
Lambda Handler pour MapEventAI Backend
Adaptation du backend Flask pour Lambda
"""

import json
import os
import sys
from pathlib import Path

# Ajouter le chemin du backend au PYTHONPATH
backend_path = Path(__file__).parent.parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Importer l'application Flask
from main import create_app

# Créer l'application Flask
app = create_app()

def lambda_handler(event, context):
    """
    Handler Lambda pour API Gateway
    Convertit les événements API Gateway en requêtes Flask
    """
    try:
        # Extraire les informations de la requête depuis l'événement API Gateway
        http_method = event.get('httpMethod', 'GET')
        path = event.get('path', '/')
        query_string = event.get('queryStringParameters') or {}
        headers = event.get('headers') or {}
        body = event.get('body', '')
        
        # Convertir les headers en format Flask
        flask_headers = {}
        for key, value in headers.items():
            # API Gateway convertit les headers en minuscules
            flask_key = key.replace('-', '_').upper()
            if flask_key not in ['CONTENT_TYPE', 'CONTENT_LENGTH']:
                flask_key = 'HTTP_' + flask_key
            flask_headers[flask_key] = value
        
        # Préparer l'environnement WSGI
        environ = {
            'REQUEST_METHOD': http_method,
            'PATH_INFO': path,
            'QUERY_STRING': '&'.join([f'{k}={v}' for k, v in query_string.items()]),
            'CONTENT_TYPE': headers.get('content-type', ''),
            'CONTENT_LENGTH': str(len(body)) if body else '0',
            'SERVER_NAME': headers.get('host', 'localhost'),
            'SERVER_PORT': '443',
            'wsgi.version': (1, 0),
            'wsgi.url_scheme': 'https',
            'wsgi.input': body,
            'wsgi.errors': sys.stderr,
            'wsgi.multithread': False,
            'wsgi.multiprocess': False,
            'wsgi.run_once': False,
        }
        
        # Ajouter les headers
        environ.update(flask_headers)
        
        # Créer un wrapper pour la réponse
        response_data = {}
        
        def start_response(status, response_headers):
            response_data['status'] = status
            response_data['headers'] = dict(response_headers)
        
        # Appeler l'application Flask
        with app.app_context():
            response_body = app(environ, start_response)
        
        # Convertir la réponse en format API Gateway
        body_content = b''.join(response_body).decode('utf-8')
        
        # Convertir les headers pour API Gateway
        api_headers = {}
        for key, value in response_data.get('headers', {}).items():
            # Convertir les headers Flask en format API Gateway
            api_key = key.replace('_', '-').title()
            api_headers[api_key] = value
        
        # Extraire le status code
        status_code = int(response_data['status'].split()[0])
        
        return {
            'statusCode': status_code,
            'headers': api_headers,
            'body': body_content
        }
        
    except Exception as e:
        # Gérer les erreurs
        import traceback
        error_message = str(e)
        error_traceback = traceback.format_exc()
        
        print(f"Error: {error_message}")
        print(f"Traceback: {error_traceback}")
        
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'error': 'Internal Server Error',
                'message': error_message
            })
        }


