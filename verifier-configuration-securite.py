#!/usr/bin/env python3
"""
Vérifier que toutes les configurations de sécurité sont en place
"""

import boto3
import json

print("=" * 70)
print("VERIFICATION CONFIGURATION SECURITE")
print("=" * 70)
print()

all_ok = True

# 1. Vérifier Secrets Manager
print("1. SECRETS MANAGER...")
try:
    secrets = boto3.client('secretsmanager', region_name='eu-west-1')
    required_secrets = [
        '/mapevent/rds/password',
        '/mapevent/sendgrid/api-key',
        '/mapevent/stripe/secret-key',
        '/mapevent/jwt/secret'
    ]
    
    found = 0
    for secret_name in required_secrets:
        try:
            secrets.describe_secret(SecretId=secret_name)
            print(f"   OK: {secret_name}")
            found += 1
        except:
            print(f"   MANQUANT: {secret_name}")
            all_ok = False
    
    if found == len(required_secrets):
        print(f"   OK: Tous les secrets sont presents ({found}/{len(required_secrets)})")
    else:
        print(f"   ATTENTION: Secrets manquants: {found}/{len(required_secrets)}")
    print()
except Exception as e:
    print(f"   ERREUR: {e}")
    all_ok = False
    print()

# 2. Vérifier CloudWatch Alarms
print("2. CLOUDWATCH ALARMS...")
try:
    cloudwatch = boto3.client('cloudwatch', region_name='eu-west-1')
    alarms = cloudwatch.describe_alarms(AlarmNamePrefix='mapevent-security')
    
    if alarms['MetricAlarms']:
        print(f"   OK: {len(alarms['MetricAlarms'])} alarme(s) trouvee(s):")
        for alarm in alarms['MetricAlarms']:
            print(f"      - {alarm['AlarmName']}")
    else:
        print("   ATTENTION: Aucune alarme trouvee")
        all_ok = False
    print()
except Exception as e:
    print(f"   ERREUR: {e}")
    all_ok = False
    print()

# 3. Vérifier SNS Topic et abonnements
print("3. SNS TOPIC ET ABONNEMENTS...")
try:
    sns = boto3.client('sns', region_name='eu-west-1')
    topics = sns.list_topics()
    
    mapevent_topic = None
    for topic in topics['Topics']:
        if 'mapevent-security-alerts' in topic['TopicArn']:
            mapevent_topic = topic
            break
    
    if mapevent_topic:
        print(f"   OK: Topic trouve: {mapevent_topic['TopicArn']}")
        
        # Vérifier les abonnements
        subscriptions = sns.list_subscriptions_by_topic(TopicArn=mapevent_topic['TopicArn'])
        confirmed = [s for s in subscriptions['Subscriptions'] if s['SubscriptionArn'] != 'PendingConfirmation']
        
        if confirmed:
            print(f"   OK: {len(confirmed)} abonnement(s) confirme(s):")
            for sub in confirmed:
                print(f"      - {sub['Protocol']}: {sub['Endpoint']}")
        else:
            print("   ATTENTION: Aucun abonnement confirme")
            print("   ACTION REQUISE: S'abonner au topic SNS (voir guide)")
            all_ok = False
    else:
        print("   ATTENTION: Topic non trouve")
        all_ok = False
    print()
except Exception as e:
    print(f"   ERREUR: {e}")
    all_ok = False
    print()

# 4. Vérifier Security Headers Policy
print("4. SECURITY HEADERS POLICY...")
try:
    cloudfront = boto3.client('cloudfront', region_name='us-east-1')
    
    # Vérifier si la policy existe
    policies = cloudfront.list_response_headers_policies(Type='custom')
    mapevent_policy = None
    for policy in policies['ResponseHeadersPolicyList']['Items']:
        if policy['ResponseHeadersPolicy']['ResponseHeadersPolicyConfig']['Name'] == 'mapevent-security-headers-policy':
            mapevent_policy = policy
            break
    
    if mapevent_policy:
        policy_id = mapevent_policy['ResponseHeadersPolicy']['Id']
        print(f"   OK: Policy trouvee: {policy_id}")
        
        # Vérifier si elle est associée à la distribution
        distribution_id = 'EMB53HDL7VFIJ'
        try:
            config = cloudfront.get_distribution_config(Id=distribution_id)
            default_behavior = config['DistributionConfig']['DefaultCacheBehavior']
            associated_policy = default_behavior.get('ResponseHeadersPolicyId', '')
            
            if associated_policy == policy_id:
                print(f"   OK: Policy associee a CloudFront")
            else:
                print(f"   ATTENTION: Policy NON associee a CloudFront")
                print("   ACTION REQUISE: Associer la policy (voir guide)")
                all_ok = False
        except Exception as e:
            print(f"   ATTENTION: Impossible de verifier l'association: {e}")
            all_ok = False
    else:
        print("   ATTENTION: Policy non trouvee")
        all_ok = False
    print()
except Exception as e:
    print(f"   ERREUR: {e}")
    all_ok = False
    print()

# 5. Vérifier RDS chiffrement
print("5. CHIFFREMENT RDS...")
try:
    rds = boto3.client('rds', region_name='eu-west-1')
    response = rds.describe_db_instances(DBInstanceIdentifier='mapevent-db')
    db = response['DBInstances'][0]
    
    if db.get('StorageEncrypted', False):
        print("   OK: RDS est chiffre")
        if db.get('KmsKeyId'):
            print(f"   OK: KMS Key: {db['KmsKeyId']}")
    else:
        print("   ATTENTION: RDS n'est PAS chiffre")
        all_ok = False
    print()
except Exception as e:
    print(f"   ERREUR: {e}")
    all_ok = False
    print()

# Résumé
print("=" * 70)
if all_ok:
    print("OK: TOUT EST CONFIGURE CORRECTEMENT !")
    print("   Votre systeme est au niveau de securite d'un leader mondial !")
else:
    print("ATTENTION: CERTAINES CONFIGURATIONS SONT MANQUANTES")
    print("   Consultez le guide pour finaliser:")
    print("   GUIDE_ACTIONS_MANUELLES_SECURITE.md")
print("=" * 70)
