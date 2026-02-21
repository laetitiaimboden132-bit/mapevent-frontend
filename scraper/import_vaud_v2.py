"""Import des 503 événements Vaud - sans envoi de mails - v2"""
import requests, json, sys, io, time

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

API_URL = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"

with open("vaud_events_final.json", "r", encoding="utf-8") as f:
    events = json.load(f)

print(f"{len(events)} evenements Vaud a importer")

# Formatter pour l'API - s'assurer que les champs sont conformes
for e in events:
    if 'location' not in e:
        e['location'] = f"{e.get('city', 'Vaud')}, Vaud, Suisse"
    if 'categories' not in e:
        e['categories'] = ['Événement']
    # Convertir start_date en date (le champ attendu par l'API)
    if 'date' not in e and 'start_date' in e:
        e['date'] = e['start_date']

# Batch de 80 (max API = 100)
BATCH_SIZE = 80
total_created = 0
total_skipped = 0
total_failed = 0

for i in range(0, len(events), BATCH_SIZE):
    batch = events[i:i+BATCH_SIZE]
    batch_num = i // BATCH_SIZE + 1
    total_batches = (len(events) + BATCH_SIZE - 1) // BATCH_SIZE
    
    print(f"\nBatch {batch_num}/{total_batches} ({len(batch)} events)...")
    
    payload = {"events": batch, "send_emails": False}
    
    try:
        r = requests.post(
            f"{API_URL}/api/events/scraped/batch",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=120
        )
        
        print(f"  Status: {r.status_code}")
        
        if r.status_code == 200:
            data = r.json()
            created = data.get('created', 0)
            skipped = data.get('skipped', 0)
            failed = data.get('failed', 0)
            errors = data.get('errors', [])
            
            total_created += created
            total_skipped += skipped
            total_failed += failed
            
            print(f"  Crees: {created}, Dupliques: {skipped}, Echoues: {failed}")
            if errors:
                for err in errors[:3]:
                    print(f"  ERR: {err}")
        else:
            print(f"  ERREUR: {r.text[:300]}")
            total_failed += len(batch)
    except Exception as e:
        print(f"  EXCEPTION: {e}")
        total_failed += len(batch)
    
    time.sleep(2)

print(f"\n{'='*60}")
print(f"RESULTAT FINAL")
print(f"  Crees: {total_created}")
print(f"  Dupliques ignores: {total_skipped}")
print(f"  Echoues: {total_failed}")
print(f"{'='*60}")
