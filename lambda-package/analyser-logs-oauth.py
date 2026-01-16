#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Script pour analyser les logs CloudWatch concernant OAuth Google et les photos"""

import subprocess
import sys
import re
import os
from datetime import datetime, timedelta

def get_cloudwatch_logs(hours=2):
    """Récupère les logs CloudWatch des dernières heures"""
    print(f"[INFO] Recuperation des logs CloudWatch des {hours} dernieres heures...")
    
    try:
        # Essayer d'abord avec boto3 (plus fiable pour l'encodage)
        try:
            import boto3
            from datetime import datetime, timedelta
            
            logs_client = boto3.client('logs', region_name='eu-west-1')
            log_group = '/aws/lambda/mapevent-backend'
            
            # Calculer le timestamp de début
            start_time = int((datetime.now() - timedelta(hours=hours)).timestamp() * 1000)
            
            # Récupérer les log streams récents
            streams_response = logs_client.describe_log_streams(
                logGroupName=log_group,
                orderBy='LastEventTime',
                descending=True,
                limit=10
            )
            
            all_events = []
            for stream in streams_response['logStreams']:
                try:
                    events_response = logs_client.get_log_events(
                        logGroupName=log_group,
                        logStreamName=stream['logStreamName'],
                        startTime=start_time
                    )
                    all_events.extend(events_response['events'])
                except Exception as e:
                    print(f"[WARNING] Erreur lors de la recuperation du stream {stream['logStreamName']}: {e}")
                    continue
            
            # Trier par timestamp
            all_events.sort(key=lambda x: x['timestamp'])
            
            # Formater les logs
            logs_text = '\n'.join([
                f"{datetime.fromtimestamp(event['timestamp']/1000).isoformat()} {event['message']}"
                for event in all_events
            ])
            
            print(f"[OK] {len(all_events)} evenements recuperes")
            return logs_text
            
        except ImportError:
            print("[INFO] boto3 non disponible, utilisation de AWS CLI...")
            # Fallback sur AWS CLI avec redirection vers fichier
            import tempfile
            
            with tempfile.NamedTemporaryFile(mode='w+', encoding='utf-8', errors='replace', delete=False, suffix='.txt') as tmp:
                tmp_file = tmp.name
            
            try:
                # Rediriger la sortie vers un fichier pour éviter les problèmes d'encodage
                cmd = [
                    'aws', 'logs', 'tail', '/aws/lambda/mapevent-backend',
                    '--since', f'{hours}h',
                    '--region', 'eu-west-1',
                    '--format', 'short'
                ]
                
                env = os.environ.copy()
                env['AWS_PAGER'] = ''
                env['PYTHONIOENCODING'] = 'utf-8'
                
                with open(tmp_file, 'w', encoding='utf-8', errors='replace') as f:
                    result = subprocess.run(
                        cmd,
                        stdout=f,
                        stderr=subprocess.PIPE,
                        text=True,
                        encoding='utf-8',
                        errors='replace',
                        env=env
                    )
                
                if result.returncode != 0:
                    print(f"[ERROR] Erreur AWS CLI: {result.stderr}")
                    return None
                
                # Lire le fichier
                with open(tmp_file, 'r', encoding='utf-8', errors='replace') as f:
                    logs_text = f.read()
                
                os.unlink(tmp_file)
                return logs_text
                
            except Exception as e:
                print(f"[ERROR] Erreur lors de la recuperation des logs: {e}")
                if os.path.exists(tmp_file):
                    os.unlink(tmp_file)
                return None
                
    except Exception as e:
        print(f"[ERROR] Erreur generale: {e}")
        import traceback
        traceback.print_exc()
        return None

def analyze_oauth_logs(logs_text):
    """Analyse les logs pour trouver les informations OAuth Google"""
    if not logs_text:
        print("[WARNING] Aucun log a analyser")
        return
    
    print("\n" + "="*80)
    print("[ANALYSE] ANALYSE DES LOGS OAUTH GOOGLE")
    print("="*80 + "\n")
    
    # Rechercher les requêtes OAuth Google
    oauth_patterns = [
        r'/api/user/oauth/google',
        r'oauth_google',
        r'picture',
        r'profile_photo',
        r'laetitiaimboden',
        r'Imboden',
    ]
    
    lines = logs_text.split('\n')
    relevant_lines = []
    
    for i, line in enumerate(lines):
        for pattern in oauth_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                # Prendre 5 lignes avant et après pour le contexte
                start = max(0, i - 5)
                end = min(len(lines), i + 6)
                context = '\n'.join(lines[start:end])
                relevant_lines.append((i, line, context))
                break
    
    if not relevant_lines:
        print("[WARNING] Aucune ligne OAuth Google trouvee dans les logs recents")
        print("\n[INFO] Essayez de vous connecter avec Google maintenant, puis relancez ce script")
        return
    
    print(f"[OK] {len(relevant_lines)} lignes pertinentes trouvees\n")
    
    # Analyser chaque ligne pertinente
    for idx, (line_num, line, context) in enumerate(relevant_lines[:50], 1):  # Limiter à 50 pour la lisibilité
        print(f"\n{'-'*80}")
        print(f"[LIGNE] Ligne {line_num} (occurrence {idx}):")
        print(f"{'-'*80}")
        print(context)
        print()
    
    # Recherche spécifique pour la photo
    print("\n" + "="*80)
    print("[PHOTO] ANALYSE SPECIFIQUE - PHOTO GOOGLE")
    print("="*80 + "\n")
    
    photo_patterns = [
        (r'picture.*PRÉSENTE|picture.*ABSENTE', 'Vérification présence photo'),
        (r'URL photo Google reçue', 'URL photo reçue'),
        (r'profile_photo_url.*mis à jour', 'Mise à jour profile_photo_url'),
        (r'profile_photo_url.*dans réponse', 'profile_photo_url dans réponse'),
        (r'https://.*googleusercontent\.com', 'URL Google photo'),
    ]
    
    for pattern, description in photo_patterns:
        matches = re.findall(pattern, logs_text, re.IGNORECASE)
        if matches:
            print(f"[OK] {description}: {len(matches)} occurrence(s) trouvee(s)")
            for match in matches[:5]:  # Afficher les 5 premières
                print(f"   - {match[:100]}...")
        else:
            print(f"[WARNING] {description}: Aucune occurrence trouvee")
    
    # Rechercher les erreurs liées à la photo
    print("\n" + "="*80)
    print("[ERREURS] ERREURS POTENTIELLES")
    print("="*80 + "\n")
    
    error_patterns = [
        (r'Erreur.*profile_photo|Erreur.*picture', 'Erreurs photo'),
        (r'profile_photo_url.*VIDE|profile_photo_url.*vide', 'profile_photo_url vide'),
        (r'Pas de photo Google', 'Photo Google absente'),
    ]
    
    for pattern, description in error_patterns:
        matches = re.findall(pattern, logs_text, re.IGNORECASE)
        if matches:
            print(f"[WARNING] {description}: {len(matches)} occurrence(s)")
            for match in matches[:5]:
                print(f"   - {match[:100]}...")

if __name__ == '__main__':
    hours = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    logs = get_cloudwatch_logs(hours)
    if logs:
        analyze_oauth_logs(logs)
        # Sauvegarder aussi dans un fichier
        with open('lambda-package/logs-oauth-analyzed.txt', 'w', encoding='utf-8', errors='replace') as f:
            f.write(logs)
        print(f"\n[OK] Logs complets sauvegardes dans: lambda-package/logs-oauth-analyzed.txt")

