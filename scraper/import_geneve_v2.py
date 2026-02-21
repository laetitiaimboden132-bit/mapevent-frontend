"""
Importer les events Genève V2 (avec dates fixées) dans la DB
Filtrer: mars 2026+ seulement, pas de doublons, end_date != 2026-05-31 sauf si start=05-31
"""
import requests, sys, io, json

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'

# Charger les events fixés
with open('geneve_events_v2_fixed.json', 'r', encoding='utf-8') as f:
    events = json.load(f)

print(f"Total events V2 fixés: {len(events)}")

# Filtrer: garder seulement ceux dont start_date >= 2026-02-08 (aujourd'hui)
# Pour les events dont end_date est 2026-05-31 mais start_date est différent:
#   garder si start_date >= 2026-02-08
#   mettre end_date = start_date + 1 jour si end_date == 2026-05-31 et c'est un event ponctuel
filtered = []
for e in events:
    start = e.get('start_date', '')
    end = e.get('end_date', start)
    
    if not start:
        continue
    
    # Garder les events du futur (aujourd'hui = 2026-02-08)
    if start < '2026-02-08':
        continue
    
    # Corriger les end_date fallback
    if end == '2026-05-31' and start != '2026-05-31':
        # Si start est loin de mai, c'est probablement un event ponctuel
        if start < '2026-05-01':
            end = start
            e['end_date'] = start
    
    filtered.append(e)

print(f"Events après filtre date (>= 2026-02-08): {len(filtered)}")

# Charger les events existants pour éviter les doublons
r = requests.get(f'{API_URL}/api/events', timeout=30)
existing = r.json() if isinstance(r.json(), list) else r.json().get('events', [])
existing_titles = set(e.get('title', '').lower().strip() for e in existing)
existing_urls = set(e.get('source_url', '').lower().strip() for e in existing if e.get('source_url'))

new_events = []
for e in filtered:
    t = e['title'].lower().strip()
    u = e.get('source_url', '').lower().strip()
    if t not in existing_titles and (not u or u not in existing_urls):
        new_events.append(e)

print(f"Nouveaux events uniques: {len(new_events)}")

if not new_events:
    print("Aucun nouvel event à importer")
    sys.exit(0)

# Importer par batch
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

print(f"\nRÉSULTAT FINAL: {created} créés, {failed} échoués sur {len(new_events)}")

# Stats par catégorie des importés
cat_count = {}
month_count = {}
for e in new_events:
    for c in e.get('categories', []):
        cat_count[c] = cat_count.get(c, 0) + 1
    month = e.get('start_date', '')[:7]
    month_count[month] = month_count.get(month, 0) + 1

print(f"\nDistribution mensuelle:")
for m, cnt in sorted(month_count.items()):
    print(f"  {m}: {cnt}")

print(f"\nCatégories:")
for cat, cnt in sorted(cat_count.items(), key=lambda x: -x[1])[:15]:
    print(f"  {cat}: {cnt}")
