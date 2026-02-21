"""
Supprime les events des sources niveau 2 via l'endpoint existant delete-by-ids.
Utilise le format {"ids": [...]} comme attendu par l'endpoint existant.
"""
import requests, sys, io, json, time
from urllib.parse import urlparse

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'

# Attendre le cold start
print("Attente cold start Lambda...")
time.sleep(5)

# Récupérer tous les events
r = requests.get(f'{API_URL}/api/events', timeout=30)
if r.status_code != 200:
    print(f"ERREUR API: {r.status_code} - {r.text[:200]}")
    time.sleep(10)
    r = requests.get(f'{API_URL}/api/events', timeout=30)

data = r.json()
events = data if isinstance(data, list) else data.get('events', [])
print(f"Total events avant: {len(events)}")

# Sources EXACTES à supprimer (niveau 2 - RISQUE ÉLEVÉ)
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

print(f"\nEvents de sources niveau 2 trouvés: {len(risky_events)}")
for e in risky_events:
    source = e.get('source_url', '')
    domain = urlparse(source).netloc if source else '?'
    print(f"  ID={e.get('id')} | {domain} | {e.get('title')}")

if not risky_events:
    print("\nAucun event à supprimer!")
    sys.exit(0)

# Supprimer via l'endpoint existant (format: {"ids": [...]})
event_ids = [e.get('id') for e in risky_events]
print(f"\nSuppression de {len(event_ids)} events...")

r = requests.post(
    f'{API_URL}/api/events/delete-by-ids',
    json={'ids': event_ids},
    timeout=30
)
print(f"Status: {r.status_code}")
print(f"Réponse: {r.text[:500]}")

# Vérification finale
time.sleep(3)
r = requests.get(f'{API_URL}/api/events', timeout=30)
data = r.json()
total = len(data if isinstance(data, list) else data.get('events', []))
print(f"\n=== TOTAL EVENTS APRÈS SUPPRESSION: {total} ===")
