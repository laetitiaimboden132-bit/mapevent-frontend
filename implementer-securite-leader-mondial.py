#!/usr/bin/env python3
"""
Script pour implémenter les améliorations de sécurité critiques
Niveau leader mondial
"""

import boto3
import json
from pathlib import Path

print("=" * 70)
print("IMPLEMENTATION SECURITE - NIVEAU LEADER MONDIAL")
print("=" * 70)
print()

# 1. Vérifier chiffrement RDS
print("1. VERIFICATION CHIFFREMENT RDS...")
try:
    rds = boto3.client('rds', region_name='eu-west-1')
    response = rds.describe_db_instances(DBInstanceIdentifier='mapevent-db')
    db = response['DBInstances'][0]
    
    storage_encrypted = db.get('StorageEncrypted', False)
    kms_key_id = db.get('KmsKeyId', None)
    
    if storage_encrypted:
        print("   OK: RDS est chiffre")
        if kms_key_id:
            print(f"   KMS Key: {kms_key_id}")
    else:
        print("   ATTENTION: RDS n'est PAS chiffre")
        print("   ACTION REQUISE: Activer le chiffrement dans AWS Console")
        print("   RDS > mapevent-db > Modifier > Chiffrement > Cocher 'Activer'")
    print()
except Exception as e:
    print(f"   ERREUR: {e}")
    print()

# 2. Créer Security Headers Policy pour CloudFront
print("2. CREATION SECURITY HEADERS POLICY...")
security_headers = {
    "Strict-Transport-Security": {
        "Value": "max-age=31536000; includeSubDomains; preload",
        "Override": True
    },
    "X-Frame-Options": {
        "Value": "DENY",
        "Override": True
    },
    "X-Content-Type-Options": {
        "Value": "nosniff",
        "Override": True
    },
    "X-XSS-Protection": {
        "Value": "1; mode=block",
        "Override": True
    },
    "Referrer-Policy": {
        "Value": "strict-origin-when-cross-origin",
        "Override": True
    },
    "Permissions-Policy": {
        "Value": "geolocation=(), microphone=(), camera=()",
        "Override": True
    }
}

headers_file = Path("cloudfront-security-headers.json")
with open(headers_file, 'w', encoding='utf-8') as f:
    json.dump(security_headers, f, indent=2)

print(f"   OK: Fichier cree: {headers_file}")
print("   ACTION REQUISE: Appliquer ces headers dans CloudFront")
print("   CloudFront > Response Headers Policies > Creer/Modifier")
print()

# 3. Vérifier WAF
print("3. VERIFICATION WAF...")
try:
    wafv2 = boto3.client('wafv2', region_name='us-east-1')  # WAF global
    response = wafv2.list_web_acls(Scope='CLOUDFRONT')
    
    if response['WebACLs']:
        print(f"   OK: {len(response['WebACLs'])} Web ACL(s) trouve(s)")
        for acl in response['WebACLs']:
            print(f"      - {acl['Name']} ({acl['Id']})")
    else:
        print("   ATTENTION: Aucun WAF configure")
        print("   ACTION REQUISE: Creer un WAF dans AWS Console")
        print("   WAF > Web ACLs > Creer")
    print()
except Exception as e:
    print(f"   ERREUR: {e}")
    print("   (WAF peut ne pas etre configure)")
    print()

# 4. Vérifier Secrets Manager
print("4. VERIFICATION SECRETS MANAGER...")
try:
    secrets = boto3.client('secretsmanager', region_name='eu-west-1')
    response = secrets.list_secrets()
    
    mapevent_secrets = [s for s in response['SecretList'] if 'mapevent' in s['Name'].lower()]
    
    if mapevent_secrets:
        print(f"   OK: {len(mapevent_secrets)} secret(s) trouve(s)")
        for secret in mapevent_secrets:
            print(f"      - {secret['Name']}")
    else:
        print("   ATTENTION: Aucun secret dans Secrets Manager")
        print("   ACTION REQUISE: Migrer les cles API vers Secrets Manager")
        print("   Secrets Manager > Creer un secret")
        print("   Secrets a creer:")
        print("      - /mapevent/rds/password")
        print("      - /mapevent/sendgrid/api-key")
        print("      - /mapevent/stripe/secret-key")
        print("      - /mapevent/jwt/secret")
    print()
except Exception as e:
    print(f"   ERREUR: {e}")
    print()

# 5. Vérifier CloudWatch Alarms
print("5. VERIFICATION CLOUDWATCH ALARMS...")
try:
    cloudwatch = boto3.client('cloudwatch', region_name='eu-west-1')
    response = cloudwatch.describe_alarms(AlarmNamePrefix='mapevent-security')
    
    if response['MetricAlarms']:
        print(f"   OK: {len(response['MetricAlarms'])} alarme(s) de securite trouvee(s)")
    else:
        print("   ATTENTION: Aucune alarme de securite configuree")
        print("   ACTION REQUISE: Creer des alarmes CloudWatch")
        print("   Alarmes a creer:")
        print("      - Erreurs 401/403 massives")
        print("      - Tentatives de connexion suspectes")
        print("      - Utilisation anormale de l'API")
    print()
except Exception as e:
    print(f"   ERREUR: {e}")
    print()

print("=" * 70)
print("RESUME")
print("=" * 70)
print()
print("Actions a faire manuellement dans AWS Console:")
print()
print("1. SECRETS MANAGER:")
print("   - Creer /mapevent/rds/password")
print("   - Creer /mapevent/sendgrid/api-key")
print("   - Creer /mapevent/stripe/secret-key")
print("   - Creer /mapevent/jwt/secret")
print()
print("2. WAF:")
print("   - WAF > Web ACLs > Creer")
print("   - Associer a CloudFront distribution")
print()
print("3. SECURITY HEADERS:")
print("   - CloudFront > Response Headers Policies")
print("   - Utiliser le fichier: cloudfront-security-headers.json")
print()
print("4. CLOUDWATCH ALARMS:")
print("   - Creer des alarmes sur erreurs 401/403")
print()
print("5. CHIFFREMENT RDS:")
print("   - Verifier dans RDS > mapevent-db")
print("   - Activer si non active")
print()
