#!/usr/bin/env python3
"""
Script pour vérifier les logs Lambda récents
"""
import boto3
from datetime import datetime, timedelta
import sys

client = boto3.client('logs', region_name='eu-west-1')
log_group = '/aws/lambda/mapevent-backend'

# Récupérer les logs des 3 dernières minutes
start_time = int((datetime.utcnow() - timedelta(minutes=3)).timestamp() * 1000)

try:
    response = client.filter_log_events(
        logGroupName=log_group,
        startTime=start_time
    )
    
    print("=== DERNIERS LOGS LAMBDA ===")
    events = response.get('events', [])
    if not events:
        print("Aucun log récent trouvé")
    else:
        for event in events[-50:]:
            message = event.get('message', '')
            # Encoder en UTF-8 avec gestion d'erreurs
            try:
                message_safe = message.encode('utf-8', errors='replace').decode('utf-8', errors='replace')
                timestamp = datetime.fromtimestamp(event['timestamp']/1000)
                print(f"[{timestamp.strftime('%H:%M:%S')}] {message_safe[:300]}")
            except:
                pass
            
except Exception as e:
    print(f"Erreur: {e}")
    import traceback
    traceback.print_exc()



