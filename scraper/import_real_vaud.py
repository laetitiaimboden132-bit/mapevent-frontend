"""
Importer les events Vaud RÉELS dans la DB
Éviter les doublons avec les events déjà en DB
"""
import requests, sys, io, json, time

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'

# Charger les events à importer
with open('real_vaud_events_v3.json', 'r', encoding='utf-8') as f:
    new_events = json.load(f)

print(f"Events à importer: {len(new_events)}")

# Charger les events existants pour éviter les doublons
r = requests.get(f'{API_URL}/api/events', timeout=30)
data = r.json()
existing = data if isinstance(data, list) else data.get('events', [])
existing_titles = set(e.get('title', '').lower().strip()[:50] for e in existing)
existing_urls = set(e.get('source_url', '') for e in existing)

print(f"Events déjà en DB: {len(existing)}")

# Filtrer les doublons
to_import = []
for e in new_events:
    title_key = e['title'].lower().strip()[:50]
    url = e.get('source_url', '')
    
    if title_key in existing_titles:
        print(f"  DOUBLON titre: {e['title'][:40]}")
        continue
    if url and url in existing_urls:
        print(f"  DOUBLON url: {e['title'][:40]}")
        continue
    
    to_import.append(e)

print(f"\nEvents uniques à importer: {len(to_import)}")

if not to_import:
    print("Rien à importer!")
    sys.exit(0)

# Importer par batch
batch_size = 20
total_created = 0
total_skipped = 0
total_failed = 0

for i in range(0, len(to_import), batch_size):
    batch = to_import[i:i+batch_size]
    
    payload = []
    for e in batch:
        payload.append({
            'title': e['title'],
            'description': e['description'],
            'date': e['date'],
            'end_date': e.get('end_date', e['date']),
            'location': e.get('location', 'Canton de Vaud'),
            'latitude': e['latitude'],
            'longitude': e['longitude'],
            'categories': e['categories'],
            'source_url': e['source_url'],
            'organizer_email': e.get('organizer_email', ''),
            'validation_status': e.get('validation_status', 'auto_validated'),
        })
    
    try:
        r = requests.post(f'{API_URL}/api/events/scraped/batch',
                         json={'events': payload, 'send_emails': False},
                         headers={"Content-Type": "application/json"},
                         timeout=120)
        
        if r.status_code != 200:
            print(f"  Batch {i//batch_size + 1}: HTTP {r.status_code} - {r.text[:100]}")
            continue
        
        result = r.json()
        created = result.get('results', result).get('created', result.get('created', 0))
        skipped = result.get('results', result).get('skipped', result.get('skipped', 0))
        failed = result.get('results', result).get('failed', result.get('failed', 0))
        
        total_created += created
        total_skipped += skipped
        total_failed += failed
        
        print(f"  Batch {i//batch_size + 1}: créé {created}, skip {skipped}, fail {failed}")
    except Exception as ex:
        print(f"  Batch {i//batch_size + 1}: ERREUR - {str(ex)[:60]}")
    
    time.sleep(2)

print(f"\n=== RÉSULTAT ===")
print(f"  Créés: {total_created}")
print(f"  Skippés: {total_skipped}")
print(f"  Échoués: {total_failed}")

# Vérification finale
r = requests.get(f'{API_URL}/api/events', timeout=30)
data = r.json()
final = data if isinstance(data, list) else data.get('events', [])
print(f"  TOTAL events en DB: {len(final)}")
