"""Import des 503 événements Vaud - sans envoi de mails"""
import requests, json, sys, io, time

if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

API_URL = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"

with open("vaud_events_final.json", "r", encoding="utf-8") as f:
    events = json.load(f)

print(f"{len(events)} evenements Vaud a importer")

# Formatter pour l'API
for e in events:
    # Assurer le format attendu
    if 'location' not in e:
        city = e.get('city', 'Vaud')
        e['location'] = f"{city}, Vaud, Suisse"
    if 'categories' not in e:
        e['categories'] = ['Événement']

# Importer par batch de 50 pour éviter les timeout
BATCH_SIZE = 50
total_imported = 0
total_skipped = 0
total_errors = 0

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
        
        if r.status_code == 200:
            data = r.json()
            imported = data.get('imported', 0)
            skipped = data.get('skipped', 0)
            emails_sent = data.get('emails_sent', 0)
            total_imported += imported
            total_skipped += skipped
            print(f"  OK: {imported} importes, {skipped} dupliques ignores")
        else:
            print(f"  ERREUR HTTP {r.status_code}: {r.text[:300]}")
            total_errors += len(batch)
    except Exception as e:
        print(f"  ERREUR: {e}")
        total_errors += len(batch)
    
    # Petite pause entre batches
    if i + BATCH_SIZE < len(events):
        time.sleep(2)

print(f"\n{'='*60}")
print(f"RESULTAT FINAL")
print(f"  Importes: {total_imported}")
print(f"  Dupliques ignores: {total_skipped}")
print(f"  Erreurs: {total_errors}")
print(f"  Total: {total_imported + total_skipped + total_errors}")
print(f"{'='*60}")
