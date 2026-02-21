"""
Supprime les events des sources niveau 2 via le nouvel endpoint delete-by-ids.
ATTENTION: exclut les faux positifs (traildugrandgeneve.ch, nuitdesmusees-geneve.ch)
"""
import requests, sys, io, json

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'

# Récupérer tous les events
r = requests.get(f'{API_URL}/api/events', timeout=30)
data = r.json()
events = data if isinstance(data, list) else data.get('events', [])
print(f"Total events avant: {len(events)}")

# Sources EXACTES à supprimer (niveau 2 - RISQUE ÉLEVÉ)
# On vérifie le domaine exact, pas juste une sous-chaîne
from urllib.parse import urlparse

RISKY_EXACT_DOMAINS = {
    'www.geneve.ch',
    'geneve.ch',
    'evenements.geneve.ch',
    'www.morges.ch',
    'morges.ch',
}

risky_events = []
for e in events:
    source_url = e.get('source_url', '') or ''
    if not source_url:
        continue
    try:
        domain = urlparse(source_url).netloc.lower()
        if domain in RISKY_EXACT_DOMAINS:
            risky_events.append(e)
    except:
        pass

print(f"\nEvents de sources niveau 2 (domaine exact): {len(risky_events)}")
for e in risky_events:
    source = e.get('source_url', '')
    domain = urlparse(source).netloc if source else '?'
    print(f"  ID={e.get('id')} | {domain} | {e.get('title')}")

if not risky_events:
    print("\nAucun event à supprimer!")
    sys.exit(0)

# Supprimer via le nouvel endpoint
event_ids = [e.get('id') for e in risky_events]
print(f"\nSuppression de {len(event_ids)} events: {event_ids}")

r = requests.post(
    f'{API_URL}/api/events/delete-by-ids',
    json={
        'event_ids': event_ids,
        'reason': 'Source niveau 2 RISQUE ÉLEVÉ - geneve.ch CGU restrictif + morges.ch robots.txt bloque AI'
    },
    timeout=30
)
print(f"Status: {r.status_code}")
result = r.json()
print(f"Résultat: {json.dumps(result, indent=2, ensure_ascii=False)}")

# Vérification finale
import time
time.sleep(2)
r = requests.get(f'{API_URL}/api/events', timeout=30)
data = r.json()
total = len(data if isinstance(data, list) else data.get('events', []))
print(f"\n=== TOTAL EVENTS APRÈS SUPPRESSION: {total} ===")
