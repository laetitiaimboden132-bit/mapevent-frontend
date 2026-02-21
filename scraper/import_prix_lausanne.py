"""
Derniers events - Prix de Lausanne
"""
import requests, sys, io, json, time

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'

events = [
    {
        'title': 'Prix de Lausanne 2026 - 54e édition',
        'location': 'Théâtre de Beaulieu, Avenue des Bergières 10, 1004 Lausanne',
        'date': '2026-02-01',
        'end_date': '2026-02-08',
        'time': None,
        'end_time': None,
        'description': '54e édition du Prix de Lausanne, prestigieux concours international de danse classique pour jeunes danseurs de 15 à 18 ans. Cours et coaching du 2 au 5 février, sélection des finalistes le 6 février, finale le 7 février et spectacle "Étoiles Montantes" le 8 février au Théâtre de Beaulieu.',
        'categories': ["Danse", "Culture", "Spectacle"],
        'source_url': 'https://www.prixdelausanne.org/',
        'organizer_name': 'Prix de Lausanne',
        'latitude': 46.5294,
        'longitude': 6.6211,
        'status': 'auto_validated'
    },
]

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
