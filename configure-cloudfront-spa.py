#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Configure CloudFront pour SPA routing (404 -> mapevent.html)"""

import json
import boto3
import sys

DISTRIBUTION_ID = "EMB53HDL7VFIJ"

def configure_cloudfront_spa():
    cloudfront = boto3.client('cloudfront', region_name='us-east-1')
    
    # Récupérer la configuration actuelle
    print("Récupération de la configuration CloudFront...")
    dist_config = cloudfront.get_distribution_config(Id=DISTRIBUTION_ID)
    etag = dist_config['ETag']
    config = dist_config['DistributionConfig']
    
    # Vérifier si CustomErrorResponses existe déjà
    if 'CustomErrorResponses' not in config:
        config['CustomErrorResponses'] = {'Quantity': 0, 'Items': []}
    
    # Vérifier si les erreurs 404 et 403 sont déjà configurées
    existing_errors = {item['ErrorCode'] for item in config['CustomErrorResponses'].get('Items', [])}
    
    if 404 not in existing_errors or 403 not in existing_errors:
        # Ajouter les CustomErrorResponses pour SPA routing
        error_responses = config['CustomErrorResponses'].get('Items', [])
        
        # Supprimer les anciennes entrées 404 et 403 si elles existent
        error_responses = [e for e in error_responses if e['ErrorCode'] not in [404, 403]]
        
        # Ajouter les nouvelles configurations
        error_responses.append({
            'ErrorCode': 404,
            'ResponsePagePath': '/mapevent.html',
            'ResponseCode': '200',
            'ErrorCachingMinTTL': 300
        })
        error_responses.append({
            'ErrorCode': 403,
            'ResponsePagePath': '/mapevent.html',
            'ResponseCode': '200',
            'ErrorCachingMinTTL': 300
        })
        
        config['CustomErrorResponses'] = {
            'Quantity': len(error_responses),
            'Items': error_responses
        }
        
        # Mettre à jour CloudFront
        print("Mise à jour de CloudFront pour SPA routing...")
        try:
            response = cloudfront.update_distribution(
                Id=DISTRIBUTION_ID,
                IfMatch=etag,
                DistributionConfig=config
            )
            print("\n" + "="*50)
            print("[OK] CLOUDFRONT CONFIGURE POUR SPA ROUTING!")
            print("="*50)
            print(f"Distribution ID: {response['Distribution']['Id']}")
            print(f"Status: {response['Distribution']['Status']}")
            print(f"ETag: {response['ETag']}")
            print("\nLes erreurs 404 et 403 serviront maintenant mapevent.html")
            print("Il faut attendre 5-15 minutes pour la propagation.")
            print("\nAprès propagation, le lien /verify-email fonctionnera!")
            return True
        except Exception as e:
            print(f"\n[ERREUR] Erreur lors de la mise a jour: {e}")
            return False
    else:
        print("[OK] La configuration SPA est deja presente dans CloudFront.")
        return True

if __name__ == '__main__':
    success = configure_cloudfront_spa()
    sys.exit(0 if success else 1)
