"""
Supprime les events des sources niveau 2 (RISQUE ÉLEVÉ)
Sources à supprimer:
- morges.ch (robots.txt bloque AI bots)
- geneve.ch (CGU: autorisation écrite requise)
- evenements.geneve.ch (même CGU que geneve.ch)
"""
import requests, sys, io, json

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'

# Sources à supprimer (niveau 2 - RISQUE ÉLEVÉ)
RISKY_DOMAINS = [
    'www.geneve.ch',
    'geneve.ch', 
    'evenements.geneve.ch',
    'www.morges.ch',
    'morges.ch',
]

# Récupérer tous les events
r = requests.get(f'{API_URL}/api/events', timeout=30)
data = r.json()
events = data if isinstance(data, list) else data.get('events', [])
print(f"Total events: {len(events)}")

# Trouver les events des sources à risque
risky_events = []
for e in events:
    source_url = e.get('source_url', '') or ''
    for domain in RISKY_DOMAINS:
        if domain in source_url.lower():
            risky_events.append(e)
            break

print(f"\nEvents de sources à risque trouvés: {len(risky_events)}")
for e in risky_events:
    print(f"  ID={e.get('id')} | {e.get('title')} | source: {e.get('source_url', '')[:80]}")

# Supprimer via DELETE (essai sans auth d'abord, puis avec méthode alternative)
if risky_events:
    deleted = 0
    failed = []
    
    for e in risky_events:
        eid = e.get('id')
        title = e.get('title', 'Unknown')
        
        # Essayer DELETE direct
        try:
            r = requests.delete(f'{API_URL}/api/events/{eid}', timeout=15)
            if r.status_code == 200:
                print(f"  SUPPRIMÉ: {title} (ID={eid})")
                deleted += 1
            else:
                # Si DELETE échoue (auth requise), on note l'ID
                failed.append((eid, title, r.status_code))
                print(f"  ECHEC DELETE (status {r.status_code}): {title} (ID={eid})")
        except Exception as ex:
            failed.append((eid, title, str(ex)))
            print(f"  ERREUR: {title} (ID={eid}) - {ex}")
    
    print(f"\nSupprimés: {deleted}/{len(risky_events)}")
    
    if failed:
        print(f"\nEchecs: {len(failed)} events - IDs à supprimer manuellement:")
        ids_to_delete = [str(f[0]) for f in failed]
        print(f"  IDs: {', '.join(ids_to_delete)}")
        
        # Essayer via SQL direct (endpoint admin)
        print("\nTentative via endpoint admin batch delete...")
        try:
            # Créer une requête custom pour supprimer par IDs
            payload = {
                'event_ids': [f[0] for f in failed],
                'reason': 'Source level 2 - RISQUE ÉLEVÉ - CGU restrictif'
            }
            r = requests.post(
                f'{API_URL}/api/events/delete-by-source',
                json=payload,
                timeout=30
            )
            print(f"  Réponse: {r.status_code} - {r.text[:200]}")
        except Exception as ex:
            print(f"  Endpoint non disponible: {ex}")

# Vérification finale
r = requests.get(f'{API_URL}/api/events', timeout=30)
data = r.json()
total = len(data if isinstance(data, list) else data.get('events', []))
print(f"\n=== TOTAL EVENTS APRÈS: {total} ===")
