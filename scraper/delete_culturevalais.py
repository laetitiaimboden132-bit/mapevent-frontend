"""
Remove all culturevalais.ch events from the main MapEvent site.
These are NOT open data - no license, no public API, proprietary platform.
"""
import requests, sys, io, json, time
from urllib.parse import urlparse

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'

DOMAINS_TO_REMOVE = {
    'agenda.culturevalais.ch',
    'culturevalais.ch',
    'www.culturevalais.ch',
}

dry_run = "--delete" not in sys.argv

r = requests.get(f'{API_URL}/api/events', timeout=120)
raw = r.json()

if isinstance(raw, dict) and 'k' in raw and 'd' in raw:
    keys = raw['k']
    events = [dict(zip(keys, row)) for row in raw['d']]
elif isinstance(raw, list):
    events = raw
else:
    events = raw.get('events', [])

print(f"Total events sur le site: {len(events)}")

to_delete = []
for e in events:
    source_url = e.get('source_url', '') or ''
    if not source_url:
        continue
    try:
        domain = urlparse(source_url).netloc.lower()
        if domain in DOMAINS_TO_REMOVE:
            to_delete.append(e)
    except:
        pass

print(f"\nEvents culturevalais.ch trouvés: {len(to_delete)}")
for e in to_delete[:20]:
    title = e.get('title', '?') or '?'
    print(f"  ID={e.get('id')} | {title[:60]}")
if len(to_delete) > 20:
    print(f"  ... et {len(to_delete) - 20} de plus")

if not to_delete:
    print("\nAucun event culturevalais.ch à supprimer!")
    sys.exit(0)

if dry_run:
    print(f"\n[DRY-RUN] {len(to_delete)} events seraient supprimés.")
    print("Ajouter --delete pour supprimer réellement.")
    sys.exit(0)

event_ids = [e.get('id') for e in to_delete if e.get('id')]
print(f"\nSuppression de {len(event_ids)} events...")

BATCH = 50
deleted = 0
for i in range(0, len(event_ids), BATCH):
    batch = event_ids[i:i+BATCH]
    r = requests.post(
        f'{API_URL}/api/events/delete-by-ids',
        json={'ids': batch, 'reason': 'culturevalais.ch - not open data, no license'},
        timeout=30
    )
    if r.status_code == 200:
        deleted += len(batch)
        print(f"  Batch {i//BATCH+1}: {len(batch)} supprimés (total: {deleted})")
    else:
        print(f"  Batch {i//BATCH+1}: ERREUR {r.status_code} - {r.text[:200]}")

time.sleep(2)
r = requests.get(f'{API_URL}/api/events', timeout=60)
data = r.json()
total = len(data if isinstance(data, list) else data.get('events', []))
print(f"\n=== TOTAL EVENTS APRÈS SUPPRESSION: {total} ===")
print(f"=== SUPPRIMÉS: {deleted} ===")
