#!/usr/bin/env python3
"""
Appliquer les Security Headers dans CloudFront
Crée ou met à jour une Response Headers Policy
"""

import boto3
import json
from pathlib import Path

print("=" * 70)
print("APPLICATION SECURITY HEADERS DANS CLOUDFRONT")
print("=" * 70)
print()

# Lire les headers depuis le fichier
headers_file = Path('cloudfront-security-headers.json')
if not headers_file.exists():
    print("ERREUR: cloudfront-security-headers.json introuvable")
    exit(1)

with open(headers_file, 'r', encoding='utf-8') as f:
    security_headers = json.load(f)

cloudfront = boto3.client('cloudfront', region_name='us-east-1')  # CloudFront est global

# Distribution ID
distribution_id = 'EMB53HDL7VFIJ'

print(f"Distribution CloudFront: {distribution_id}")
print()

# Créer une Response Headers Policy
policy_name = 'mapevent-security-headers-policy'

try:
    # Vérifier si une policy existe déjà
    try:
        response = cloudfront.list_response_headers_policies(Type='custom')
        existing_policies = [p for p in response['ResponseHeadersPolicyList']['Items'] 
                           if p['ResponseHeadersPolicy']['ResponseHeadersPolicyConfig']['Name'] == policy_name]
        
        if existing_policies:
            policy_id = existing_policies[0]['ResponseHeadersPolicy']['Id']
            print(f"OK: Policy existante trouvee: {policy_id}")
            print("   Mise a jour de la policy...")
            
            # Mettre à jour la policy existante
            cloudfront.update_response_headers_policy(
                Id=policy_id,
                ResponseHeadersPolicyConfig={
                    'Name': policy_name,
                    'Comment': 'Security headers pour MapEvent - Niveau leader mondial',
                    'SecurityHeadersConfig': {
                        'StrictTransportSecurity': {
                            'Override': True,
                            'AccessControlMaxAgeSec': 31536000,
                            'IncludeSubdomains': True,
                            'Preload': True
                        },
                        'FrameOptions': {
                            'Override': True,
                            'FrameOption': 'DENY'
                        },
                        'ContentTypeOptions': {
                            'Override': True
                        },
                        'XSSProtection': {
                            'Override': True,
                            'ModeBlock': True,
                            'Protection': True
                        },
                        'ReferrerPolicy': {
                            'Override': True,
                            'ReferrerPolicy': 'strict-origin-when-cross-origin'
                        }
                    }
                }
            )
            print("   OK: Policy mise a jour")
            policy_id_to_use = policy_id
        else:
            raise Exception("Policy non trouvee")
            
    except:
        # Créer une nouvelle policy
        print("Creation d'une nouvelle Response Headers Policy...")
        response = cloudfront.create_response_headers_policy(
            ResponseHeadersPolicyConfig={
                'Name': policy_name,
                'Comment': 'Security headers pour MapEvent - Niveau leader mondial',
                'SecurityHeadersConfig': {
                    'StrictTransportSecurity': {
                        'Override': True,
                        'AccessControlMaxAgeSec': 31536000,
                        'IncludeSubdomains': True,
                        'Preload': True
                    },
                    'FrameOptions': {
                        'Override': True,
                        'FrameOption': 'DENY'
                    },
                    'ContentTypeOptions': {
                        'Override': True
                    },
                    'XSSProtection': {
                        'Override': True,
                        'ModeBlock': True,
                        'Protection': True
                    },
                    'ReferrerPolicy': {
                        'Override': True,
                        'ReferrerPolicy': 'strict-origin-when-cross-origin'
                    }
                }
            }
        )
        policy_id_to_use = response['ResponseHeadersPolicy']['Id']
        print(f"   OK: Policy creee: {policy_id_to_use}")
    
    print()
    print("=" * 70)
    print("PROCHAINES ETAPES")
    print("=" * 70)
    print()
    print("1. Associer la policy a la distribution CloudFront:")
    print("   AWS Console > CloudFront > Distributions > EMB53HDL7VFIJ")
    print("   Onglet 'Behaviors' > Editer un behavior")
    print(f"   Response Headers Policy: {policy_name}")
    print("   Sauvegarder")
    print()
    print("2. Creer une invalidation CloudFront:")
    print("   CloudFront > Invalidations > Creer")
    print("   Paths: /*")
    print()
    print(f"Policy ID: {policy_id_to_use}")
    print()
    
except Exception as e:
    print(f"ERREUR: {e}")
    print()
    print("ACTION MANUELLE REQUISE:")
    print("1. AWS Console > CloudFront > Response Headers Policies")
    print("2. Creer une nouvelle policy avec les headers suivants:")
    print("   - Strict-Transport-Security: max-age=31536000; includeSubDomains; preload")
    print("   - X-Frame-Options: DENY")
    print("   - X-Content-Type-Options: nosniff")
    print("   - X-XSS-Protection: 1; mode=block")
    print("   - Referrer-Policy: strict-origin-when-cross-origin")
    print("3. Associer la policy a la distribution")
    print()
