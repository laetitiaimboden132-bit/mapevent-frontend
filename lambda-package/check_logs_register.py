#!/usr/bin/env python3
import boto3
import time
from datetime import datetime

logs = boto3.client('logs', region_name='eu-west-1')

# Récupérer les logs des 2 dernières minutes
start_time = int((time.time() - 120) * 1000)

events = logs.filter_log_events(
    logGroupName='/aws/lambda/mapevent-backend',
    limit=50,
    startTime=start_time
)

print("=== Derniers logs (20 derniers) ===\n")
for event in events['events'][-20:]:
    timestamp = datetime.fromtimestamp(event['timestamp'] / 1000).strftime('%H:%M:%S')
    message = event['message'].replace('🔍', '[DEBUG]').replace('✅', '[OK]').replace('❌', '[ERROR]').replace('⚠️', '[WARN]')
    print(f"{timestamp}: {message}")




