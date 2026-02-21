"""
Batch final 2 - derniers events confirmés
"""
import requests, sys, io, json, time

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'
NOMINATIM_URL = 'https://nominatim.openstreetmap.org/search'
HEADERS = {'User-Agent': 'MapEventAI/1.0 (contact@mapevent.ai)'}

def geocode(address, fb_lat=None, fb_lon=None):
    try:
        time.sleep(1.5)
        r = requests.get(NOMINATIM_URL, params={'q': address, 'format': 'json', 'limit': 1, 'countrycodes': 'ch'}, headers=HEADERS, timeout=10)
        results = r.json()
        if results:
            return float(results[0]['lat']), float(results[0]['lon'])
    except:
        pass
    return fb_lat, fb_lon

events = []

# 1. Vevey StrEAT Food Festival 2026
# Source: vevey-streatfoodfest.ch
events.append({
    'title': 'Vevey StrEAT Food Festival 2026',
    'location': 'Quais de Vevey, 1800 Vevey',
    'date': '2026-06-24',
    'end_date': '2026-06-28',
    'time': None,
    'end_time': None,
    'description': 'Festival de street food sur les quais de Vevey. Foodtrucks innovants, la plus longue table de Suisse entre le lac et les installations culinaires. Master Class by Léguriviera animées par des chefs, accords mets-vin pour chaque recette.',
    'categories': ["Gastronomie", "Festival"],
    'source_url': 'https://www.vevey-streatfoodfest.ch/',
    'organizer_name': 'Vevey StrEAT Food Festival',
    'fallback_lat': 46.4602,
    'fallback_lon': 6.8427
})

# 2. Fête du Poulet Sierre 2026
# Source: fetedupoulet.ch
events.append({
    'title': 'Fête du Poulet Sierre 2026',
    'location': 'Place de l\'Hôtel-de-Ville, 3960 Sierre',
    'date': '2026-08-28',
    'end_date': '2026-08-30',
    'time': None,
    'end_time': None,
    'description': '27e édition de la Fête du Poulet à Sierre. Trois jours de fête sur la Place de l\'Hôtel-de-Ville. Ambiance festive, gastronomie et animations.',
    'categories': ["Gastronomie", "Festival", "Fête"],
    'source_url': 'https://fetedupoulet.ch/',
    'organizer_name': 'Fête du Poulet Sierre',
    'fallback_lat': 46.2920,
    'fallback_lon': 7.5340
})

# 3. Jazz Day Valais 2026 - Sierre
# Source: jazzdayvalais.ch
events.append({
    'title': 'Jazz Day Valais 2026',
    'location': 'Divers lieux, 3960 Sierre',
    'date': '2026-04-25',
    'end_date': '2026-04-25',
    'time': None,
    'end_time': None,
    'description': 'Sierre devient la capitale du jazz le 25 avril 2026. Concerts gratuits au buffet de la gare, à l\'Hacienda et à la bibliothèque-médiathèque de Sierre. Journée internationale du jazz célébrée en Valais.',
    'categories': ["Musique", "Jazz", "Culture"],
    'source_url': 'https://www.jazzdayvalais.ch/',
    'organizer_name': 'Jazz Day Valais',
    'fallback_lat': 46.2920,
    'fallback_lon': 7.5340
})

# 4. Montreux Jazz Festival 2026 - 60e édition (mise à jour dates)
# Déjà en DB, skip

# === DOUBLONS ===
print("=== Check doublons ===")
r = requests.get(f'{API_URL}/api/events', timeout=30)
data = r.json()
existing = data if isinstance(data, list) else data.get('events', [])
existing_urls = {e.get('source_url', '').lower().strip() for e in existing}
print(f"Events existants: {len(existing)}")

new_events = [ev for ev in events if ev['source_url'].lower().strip() not in existing_urls]
print(f"À importer: {len(new_events)}/{len(events)}")

if not new_events:
    print("Rien à importer!")
    sys.exit(0)

# === GÉOCODAGE + IMPORT ===
print("\n=== Géocodage ===")
api_events = []
for ev in new_events:
    fb_lat = ev.pop('fallback_lat', None)
    fb_lon = ev.pop('fallback_lon', None)
    lat, lon = geocode(ev['location'], fb_lat, fb_lon)
    if lat and lon:
        print(f"  ✓ {ev['title'][:50]}: {lat:.4f}, {lon:.4f}")
        ev['latitude'] = lat
        ev['longitude'] = lon
        ev['status'] = 'auto_validated'
        api_events.append(ev)
    else:
        print(f"  ✗ {ev['title']}")

if api_events:
    print(f"\n=== Import ({len(api_events)}) ===")
    r = requests.post(f'{API_URL}/api/events/scraped/batch', json={'events': api_events}, timeout=60)
    print(f"Status: {r.status_code} - {r.json()}")

time.sleep(1)
r = requests.get(f'{API_URL}/api/events', timeout=30)
data = r.json()
all_ev = data if isinstance(data, list) else data.get('events', [])
print(f"\nTOTAL: {len(all_ev)}")
