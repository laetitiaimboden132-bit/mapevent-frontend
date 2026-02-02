#!/usr/bin/env python3
"""
Associer la Response Headers Policy à la distribution CloudFront
"""

import boto3
import json

print("=" * 70)
print("ASSOCIATION SECURITY HEADERS A CLOUDFRONT")
print("=" * 70)
print()

cloudfront = boto3.client('cloudfront', region_name='us-east-1')
distribution_id = 'EMB53HDL7VFIJ'
policy_id = '0a16a09f-06c9-4bad-975f-caa6a710939b'

try:
    # Récupérer la configuration actuelle
    print("Recuperation de la configuration CloudFront...")
    config = cloudfront.get_distribution_config(Id=distribution_id)
    etag = config['ETag']
    distribution_config = config['DistributionConfig']
    
    # Trouver le behavior par défaut (*)
    default_behavior = None
    for behavior in distribution_config['CacheBehaviors']['Items']:
        if behavior['PathPattern'] == '*':
            default_behavior = behavior
            break
    
    if not default_behavior:
        # Utiliser le DefaultCacheBehavior
        default_behavior = distribution_config['DefaultCacheBehavior']
    
    # Associer la Response Headers Policy
    print(f"Association de la policy {policy_id} au behavior...")
    default_behavior['ResponseHeadersPolicyId'] = policy_id
    
    # Mettre à jour la distribution
    print("Mise a jour de la distribution CloudFront...")
    cloudfront.update_distribution(
        Id=distribution_id,
        DistributionConfig=distribution_config,
        IfMatch=etag
    )
    
    print()
    print("=" * 70)
    print("OK: SECURITY HEADERS ASSOCIES")
    print("=" * 70)
    print()
    print("La distribution CloudFront est en cours de mise a jour...")
    print("Temps estime: 5-15 minutes")
    print()
    print("PROCHAINE ETAPE:")
    print("Creer une invalidation CloudFront pour appliquer les changements")
    print()
    
except Exception as e:
    print(f"ERREUR: {e}")
    print()
    print("ACTION MANUELLE REQUISE:")
    print("1. AWS Console > CloudFront > Distributions > EMB53HDL7VFIJ")
    print("2. Onglet 'Behaviors'")
    print("3. Selectionner le behavior (souvent le premier)")
    print("4. Editer")
    print(f"5. Response Headers Policy: mapevent-security-headers-policy")
    print("6. Sauvegarder")
    print()
