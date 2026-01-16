#!/usr/bin/env python3
"""
Script pour vérifier les logs Lambda pour les erreurs 400
"""
import boto3
import json
from datetime import datetime, timedelta

client = boto3.client('logs', region_name='eu-west-1')
log_group = '/aws/lambda/mapevent-backend'

# Récupérer les logs des 5 dernières minutes
start_time = int((datetime.utcnow() - timedelta(minutes=5)).timestamp() * 1000)

try:
    response = client.filter_log_events(
        logGroupName=log_group,
        startTime=start_time,
        filterPattern='400'
    )
    
    print("=== LOGS AVEC 400 ===")
    for event in response.get('events', [])[-20:]:
        message = event.get('message', '')
        try:
            message_safe = message.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
            if '400' in message_safe or 'error' in message_safe.lower() or 'Body' in message_safe:
                print(f"[{datetime.fromtimestamp(event['timestamp']/1000)}] {message_safe}")
        except:
            pass
    
    # Aussi récupérer les logs récents sans filtre
    print("\n=== DERNIERS LOGS (sans filtre) ===")
    response_all = client.filter_log_events(
        logGroupName=log_group,
        startTime=start_time
    )
    
    for event in response_all.get('events', [])[-30:]:
        message = event.get('message', '')
        try:
            message_safe = message.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
            if any(keyword in message_safe for keyword in ['Body', 'error', '400', 'status_code', 'response.get_json', 'Body final']):
                print(f"[{datetime.fromtimestamp(event['timestamp']/1000)}] {message_safe[:300]}")
        except:
            pass
            
except Exception as e:
    print(f"Erreur: {e}")

