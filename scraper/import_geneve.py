"""
Importer les events Genève dans la DB
"""
import requests, sys, io, json

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'

# Charger les events
with open('geneve_events.json', 'r', encoding='utf-8') as f:
    events = json.load(f)

print(f"Events à importer: {len(events)}")

# Charger les events existants pour éviter les doublons
r = requests.get(f'{API_URL}/api/events', timeout=30)
existing = r.json() if isinstance(r.json(), list) else r.json().get('events', [])
existing_titles = set(e.get('title', '').lower().strip() for e in existing)
existing_urls = set(e.get('source_url', '').lower().strip() for e in existing if e.get('source_url'))

new_events = []
for e in events:
    t = e['title'].lower().strip()
    u = e.get('source_url', '').lower().strip()
    if t not in existing_titles and (not u or u not in existing_urls):
        new_events.append(e)

print(f"Nouveaux events (pas de doublons): {len(new_events)}")

if not new_events:
    print("Aucun nouvel event à importer")
    sys.exit(0)

# Formatter pour l'API
batch_size = 20
created = 0
failed = 0

for i in range(0, len(new_events), batch_size):
    batch = new_events[i:i+batch_size]
    
    payload = []
    for e in batch:
        payload.append({
            'title': e['title'],
            'description': e.get('description', ''),
            'date': e['start_date'],
            'end_date': e.get('end_date', e['start_date']),
            'time': None,
            'location': e.get('location', e.get('address', 'Genève')),
            'city': e.get('city', 'Genève'),
            'latitude': e['latitude'],
            'longitude': e['longitude'],
            'categories': e.get('categories', ['Culture > Divers']),
            'source_url': e.get('source_url', ''),
            'organizer_email': e.get('organizer_email', ''),
            'validation_status': 'auto_validated' if not e.get('organizer_email') else 'pending'
        })
    
    try:
        r = requests.post(f'{API_URL}/api/events/scraped/batch',
                         json={'events': payload, 'send_emails': False},
                         headers={"Content-Type": "application/json"},
                         timeout=120)
        
        if r.status_code == 200 or r.status_code == 201:
            result = r.json()
            res = result.get('results', result)
            c = res.get('created', 0)
            s = res.get('skipped', 0)
            f_count = res.get('failed', 0)
            created += c
            failed += f_count
            print(f"  Batch {i//batch_size + 1}: {c} créés, {s} ignorés, {f_count} échoués")
        else:
            print(f"  Batch {i//batch_size + 1}: ERREUR {r.status_code} - {r.text[:200]}")
            failed += len(batch)
    except Exception as ex:
        print(f"  Batch {i//batch_size + 1}: ERREUR - {str(ex)[:80]}")
        failed += len(batch)

print(f"\nRÉSULTAT: {created} créés, {failed} échoués sur {len(new_events)}")
