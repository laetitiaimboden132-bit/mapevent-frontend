"""
Batch extra - Geneva Artistink + quelques events supplémentaires
"""
import requests, sys, io, json, time

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'

events = [
    # 1. Geneva Artistink 2026 - Palexpo
    # Source: palexpo.ch + ink-conv.com
    {
        'title': 'Geneva Artistink 2026',
        'location': 'Palexpo, Route François-Peyrot 30, 1218 Le Grand-Saconnex',
        'date': '2026-02-13',
        'end_date': '2026-02-15',
        'time': '11:00',
        'end_time': '22:00',
        'description': 'Festival mêlant tatouage, art contemporain, musique live et performances créatives à Palexpo. Plus de 250 artistes : tatoueurs, peintres, sculpteurs, photographes et performeurs. 3 jours de création en direct. Pass 1 jour 30 CHF, 3 jours 65 CHF.',
        'categories': ["Art", "Festival", "Culture"],
        'source_url': 'https://www.palexpo.ch/evenement/geneva-artistink/',
        'organizer_name': 'Geneva Artistink',
        'latitude': 46.2339,
        'longitude': 6.1138,
        'status': 'auto_validated'
    },
]

# Check doublons et import
print("=== Check doublons ===")
r = requests.get(f'{API_URL}/api/events', timeout=30)
data = r.json()
existing = data if isinstance(data, list) else data.get('events', [])
existing_urls = {e.get('source_url', '').lower().strip() for e in existing}
print(f"Events existants: {len(existing)}")

new_events = [ev for ev in events if ev['source_url'].lower().strip() not in existing_urls]
print(f"À importer: {len(new_events)}")

if new_events:
    r = requests.post(f'{API_URL}/api/events/scraped/batch', json={'events': new_events}, timeout=30)
    print(f"Status: {r.status_code} - {r.json()}")

time.sleep(1)
r = requests.get(f'{API_URL}/api/events', timeout=30)
data = r.json()
all_ev = data if isinstance(data, list) else data.get('events', [])
print(f"\nTOTAL: {len(all_ev)}")
