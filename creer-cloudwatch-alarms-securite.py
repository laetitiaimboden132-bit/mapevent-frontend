#!/usr/bin/env python3
"""
Créer des alarmes CloudWatch pour la sécurité
Détecte les attaques et activités suspectes
"""

import boto3
import json

print("=" * 70)
print("CREATION DES ALARMES CLOUDWATCH SECURITE")
print("=" * 70)
print()

cloudwatch = boto3.client('cloudwatch', region_name='eu-west-1')
sns = boto3.client('sns', region_name='eu-west-1')

# Créer un topic SNS pour les alertes (si n'existe pas)
topic_name = 'mapevent-security-alerts'
try:
    response = sns.create_topic(Name=topic_name)
    topic_arn = response['TopicArn']
    print(f"OK: Topic SNS cree: {topic_arn}")
except Exception as e:
    # Le topic existe peut-être déjà
    try:
        response = sns.list_topics()
        topics = [t for t in response['Topics'] if topic_name in t['TopicArn']]
        if topics:
            topic_arn = topics[0]['TopicArn']
            print(f"OK: Topic SNS existant: {topic_arn}")
        else:
            print(f"ERREUR: Impossible de creer/trouver le topic SNS: {e}")
            exit(1)
    except:
        print(f"ERREUR: {e}")
        exit(1)

print()
print("NOTE: Pour recevoir les alertes, abonnez-vous au topic SNS:")
print(f"  SNS > Topics > {topic_name} > Create subscription")
print("  Choisir: Email ou SMS")
print()

# Nom de la fonction Lambda
lambda_function_name = 'mapevent-backend'

# Alarms à créer
alarms = [
    {
        'name': 'mapevent-security-401-errors',
        'metric': 'Errors',
        'namespace': 'AWS/Lambda',
        'dimensions': [{'Name': 'FunctionName', 'Value': lambda_function_name}],
        'statistic': 'Sum',
        'period': 300,  # 5 minutes
        'threshold': 50,  # 50 erreurs en 5 minutes
        'comparison': 'GreaterThanThreshold',
        'description': 'Trop d\'erreurs 401 (tentatives de connexion suspectes)'
    },
    {
        'name': 'mapevent-security-403-errors',
        'metric': 'Errors',
        'namespace': 'AWS/Lambda',
        'dimensions': [{'Name': 'FunctionName', 'Value': lambda_function_name}],
        'statistic': 'Sum',
        'period': 300,
        'threshold': 30,  # 30 erreurs en 5 minutes
        'comparison': 'GreaterThanThreshold',
        'description': 'Trop d\'erreurs 403 (accès non autorisés)'
    },
    {
        'name': 'mapevent-security-high-invocations',
        'metric': 'Invocations',
        'namespace': 'AWS/Lambda',
        'dimensions': [{'Name': 'FunctionName', 'Value': lambda_function_name}],
        'statistic': 'Sum',
        'period': 60,  # 1 minute
        'threshold': 1000,  # 1000 invocations par minute
        'comparison': 'GreaterThanThreshold',
        'description': 'Utilisation anormale de l\'API (possible attaque DDoS)'
    }
]

created = []
skipped = []

for alarm_config in alarms:
    alarm_name = alarm_config['name']
    
    try:
        # Vérifier si l'alarme existe déjà
        try:
            existing = cloudwatch.describe_alarms(AlarmNames=[alarm_name])
            if existing['MetricAlarms']:
                print(f"SKIP: {alarm_name} (existe deja)")
                skipped.append(alarm_name)
                continue
        except:
            pass
        
        # Créer l'alarme
        print(f"Creation: {alarm_name}...", end=" ")
        
        cloudwatch.put_metric_alarm(
            AlarmName=alarm_name,
            AlarmDescription=alarm_config['description'],
            MetricName=alarm_config['metric'],
            Namespace=alarm_config['namespace'],
            Statistic=alarm_config['statistic'],
            Dimensions=alarm_config['dimensions'],
            Period=alarm_config['period'],
            EvaluationPeriods=1,
            Threshold=alarm_config['threshold'],
            ComparisonOperator=alarm_config['comparison'],
            AlarmActions=[topic_arn],
            OKActions=[topic_arn],
            TreatMissingData='notBreaching'
        )
        
        print("OK")
        created.append(alarm_name)
        
    except Exception as e:
        print(f"ERREUR: {e}")
        skipped.append(alarm_name)

print()
print("=" * 70)
print("RESUME")
print("=" * 70)
print()
print(f"Alarmes creees: {len(created)}")
for name in created:
    print(f"  - {name}")
print()
print(f"Alarmes ignores: {len(skipped)}")
for name in skipped:
    print(f"  - {name}")
print()
print("IMPORTANT:")
print(f"1. Abonnez-vous au topic SNS: {topic_arn}")
print("2. Les alertes seront envoyees par email/SMS")
print("3. Vous serez alerte en cas d'attaque ou d'activite suspecte")
print()
