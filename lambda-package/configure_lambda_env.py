#!/usr/bin/env python3
"""
Script Python pour configurer les variables d'environnement Lambda
Évite les problèmes d'échappement PowerShell sur Windows
"""

import json
import os
import sys
import boto3
from botocore.exceptions import ClientError

FUNCTION_NAME = "mapevent-backend"
REGION = "eu-west-1"

def read_env_file(env_file="lambda.env"):
    """Lire le fichier lambda.env et retourner un dictionnaire"""
    env_vars = {}
    
    if not os.path.exists(env_file):
        print(f"ERREUR: Fichier {env_file} non trouvé!", file=sys.stderr)
        sys.exit(1)
    
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Ignorer les lignes vides et les commentaires
            if not line or line.startswith('#'):
                continue
            # Parser KEY=VALUE
            if '=' in line:
                key, value = line.split('=', 1)
                env_vars[key.strip()] = value.strip()
    
    return env_vars

def main():
    # Configurer l'encodage UTF-8 pour Windows
    if sys.platform == 'win32':
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except AttributeError:
            # Python < 3.7
            import codecs
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    
    print("Configuration des variables d'environnement Lambda...")
    print("")
    
    # Lire les variables depuis lambda.env
    print(f"Lecture du fichier lambda.env...")
    env_vars = read_env_file()
    
    # Exclure les variables réservées par AWS Lambda
    reserved_vars = ['AWS_REGION', 'AWS_LAMBDA_FUNCTION_NAME', 'AWS_LAMBDA_FUNCTION_VERSION', 
                     'AWS_LAMBDA_FUNCTION_MEMORY_SIZE', 'AWS_LAMBDA_LOG_GROUP_NAME', 
                     'AWS_LAMBDA_LOG_STREAM_NAME', 'AWS_EXECUTION_ENV']
    for reserved_var in reserved_vars:
        env_vars.pop(reserved_var, None)
    
    # Vérifier les variables essentielles
    required_vars = ['RDS_HOST', 'RDS_USER', 'RDS_PASSWORD', 'REDIS_HOST']
    missing_vars = [var for var in required_vars if var not in env_vars or not env_vars[var]]
    
    if missing_vars:
        print(f"ERREUR: Variables manquantes dans lambda.env:", file=sys.stderr)
        for var in missing_vars:
            print(f"  - {var}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Mise à jour Lambda: {FUNCTION_NAME}")
    print(f"Région: {REGION}")
    print("")
    
    # Créer le client Lambda
    try:
        lambda_client = boto3.client('lambda', region_name=REGION)
        
        # Mettre à jour la configuration
        print("Mise à jour des variables d'environnement...")
        response = lambda_client.update_function_configuration(
            FunctionName=FUNCTION_NAME,
            Environment={
                'Variables': env_vars
            }
        )
        
        print("")
        print("[OK] Variables d'environnement configurees avec succes!")
        print("")
        print(f"Fonction: {response['FunctionName']}")
        print(f"Status: {response['LastUpdateStatus']}")
        print("")
        print("Variables configurées:")
        for key in sorted(env_vars.keys()):
            value = env_vars[key]
            if 'PASSWORD' in key or 'SECRET' in key or 'KEY' in key:
                display_value = "***" + value[-4:] if len(value) > 4 else "***"
            else:
                display_value = value
            print(f"  {key} = {display_value}")
        
        print("")
        print("Configuration terminée!")
        
    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        print(f"ERREUR AWS: {error_code} - {error_message}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERREUR: {str(e)}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()

