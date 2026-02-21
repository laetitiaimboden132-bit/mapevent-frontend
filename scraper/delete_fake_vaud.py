"""
Supprimer les 604 events Vaud avec des URLs inventées
"""
import requests, sys, io, json, time

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'

with open('vaud_fake_ids.json', 'r') as f:
    data = json.load(f)
    fake_ids = data['fake_ids']

print(f"Events FAUX à supprimer: {len(fake_ids)}")

# Supprimer par batch de 50
batch_size = 50
total_deleted = 0
for i in range(0, len(fake_ids), batch_size):
    batch = fake_ids[i:i+batch_size]
    try:
        r = requests.post(f'{API_URL}/api/events/delete-by-ids', 
                         json={'ids': batch}, timeout=30)
        result = r.json()
        deleted = result.get('deleted_count', 0)
        total_deleted += deleted
        print(f"  Batch {i//batch_size + 1}: supprimé {deleted}/{len(batch)} (total: {total_deleted})")
    except Exception as ex:
        print(f"  Batch {i//batch_size + 1}: ERREUR - {str(ex)[:50]}")
    time.sleep(1)

print(f"\nTOTAL SUPPRIMÉ: {total_deleted}/{len(fake_ids)}")

# Vérifier l'état final
r = requests.get(f'{API_URL}/api/events', timeout=30)
evts = r.json() if isinstance(r.json(), list) else r.json().get('events', [])
print(f"Events restants dans la DB: {len(evts)}")
