"""
Encore plus d'events confirmés 2026
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

# 1. Country Valais 2026 - Anzère
# Source: countryvalais.ch + anzere.ch
events.append({
    'title': 'Country Valais 2026',
    'location': 'Salle du Zodiaque, 1972 Anzère',
    'date': '2026-08-30',
    'end_date': '2026-09-06',
    'time': None,
    'end_time': None,
    'description': '2e édition du festival country et line dance à Anzère. Workshops pour tous niveaux avec 3 chorégraphes internationaux (Claudine Burket, Arnaud Marraffa, Agnès Gauthier). Soirées Wish & Dance avec DJ, soirée orchestre live le 4 septembre, après-midi dansant le 6 septembre.',
    'categories': ["Musique", "Festival", "Danse"],
    'source_url': 'https://countryvalais.ch/',
    'organizer_name': 'Country Valais',
    'fallback_lat': 46.3024,
    'fallback_lon': 7.4044
})

# 2. GIFF - Geneva International Film Festival 2026
# Source: giff.ch
events.append({
    'title': 'Geneva International Film Festival (GIFF) 2026',
    'location': 'Maison Communale de Plainpalais, Rue de Carouge 52, 1205 Genève',
    'date': '2026-10-30',
    'end_date': '2026-11-08',
    'time': None,
    'end_time': None,
    'description': '32e édition du Geneva International Film Festival. Festival de cinéma et arts numériques dans plusieurs lieux : Maison Communale de Plainpalais, Théâtre Pitoëff, Cinérama Empire, Cinémas du Grütli. Films, installations immersives, XR Roadshow et performances.',
    'categories': ["Cinéma", "Festival", "Culture"],
    'source_url': 'https://www.giff.ch/',
    'organizer_name': 'GIFF',
    'fallback_lat': 46.1975,
    'fallback_lon': 6.1420
})

# 3. Raid Evolénard FMV 2026 - Championnats Suisses VTT Marathon
# Source: raidevolenard-fmv.ch
events.append({
    'title': 'Raid Evolénard FMV 2026 - Championnats Suisses VTT',
    'location': 'Evolène, 1983 Evolène, Valais',
    'date': '2026-06-21',
    'end_date': '2026-06-21',
    'time': None,
    'end_time': None,
    'description': 'Championnats Suisses de VTT Marathon XCM à Evolène. Parcours de 62 km, 35 km, 24 km et KidsCup. Course à travers les paysages spectaculaires du Val d\'Hérens en Valais.',
    'categories': ["Sport", "Sport > Terrestre", "Cyclisme"],
    'source_url': 'https://raidevolenard-fmv.ch/',
    'organizer_name': 'Raid Evolénard',
    'fallback_lat': 46.1130,
    'fallback_lon': 7.4940
})

# 4. MJF Spotlight Sessions 2026
# Source: montreuxjazzfestival.com
events.append({
    'title': 'MJF Spotlight Sessions 2026',
    'location': 'Théâtre du Villars Palace, 1884 Villars-sur-Ollon',
    'date': '2026-03-06',
    'end_date': '2026-04-04',
    'time': None,
    'end_time': None,
    'description': 'MJF Spotlight Sessions au Villars Palace. Six artistes émergents se produisent sur trois weekends entre mars et avril. Découvrez les stars de demain sélectionnées par le Montreux Jazz Festival.',
    'categories': ["Musique", "Concert"],
    'source_url': 'https://www.montreuxjazzfestival.com/spotlight-sessions/',
    'organizer_name': 'Montreux Jazz Festival',
    'fallback_lat': 46.2994,
    'fallback_lon': 7.0545
})

# 5. Visions du Réel 2026 (57e édition) - Nyon
# Check si pas déjà en DB via l'URL
events.append({
    'title': 'Visions du Réel 2026 - 57e édition',
    'location': 'Nyon, Place du Marché 2, 1260 Nyon',
    'date': '2026-04-17',
    'end_date': '2026-04-26',
    'time': None,
    'end_time': None,
    'description': '57e édition du festival international de cinéma documentaire. 50 000 visiteurs attendus sur 10 jours. Compétitions internationales (longs, moyens, courts métrages), sélections Grand Angle, Opening Scenes, Highlights. Invités d\'honneur, activités professionnelles et événements parallèles.',
    'categories': ["Cinéma", "Festival", "Culture"],
    'source_url': 'https://www.visionsdureel.ch/2026/',
    'organizer_name': 'Visions du Réel',
    'fallback_lat': 46.3833,
    'fallback_lon': 6.2398
})

# === VÉRIFICATION DOUBLONS ===
print("=== Vérification doublons ===")
r = requests.get(f'{API_URL}/api/events', timeout=30)
data = r.json()
existing = data if isinstance(data, list) else data.get('events', [])
existing_urls = {e.get('source_url', '').lower().strip() for e in existing}
existing_titles_lower = [e.get('title', '').lower() for e in existing]
print(f"Events existants: {len(existing)}")

new_events = []
for ev in events:
    url_lower = ev['source_url'].lower().strip()
    title_lower = ev['title'].lower()
    is_dup = False
    
    if url_lower in existing_urls:
        print(f"  DOUBLON URL: {ev['title']}")
        is_dup = True
    
    if not is_dup:
        for et in existing_titles_lower:
            # Visions du Réel check
            if 'visions du réel' in title_lower and 'visions du réel' in et:
                print(f"  DOUBLON TITRE: {ev['title']}")
                is_dup = True
                break
    
    if not is_dup:
        new_events.append(ev)

print(f"\nÀ importer: {len(new_events)}/{len(events)}")

if not new_events:
    print("Rien à importer!")
    sys.exit(0)

# === GÉOCODAGE ===
print("\n=== Géocodage ===")
api_events = []
for ev in new_events:
    fb_lat = ev.pop('fallback_lat', None)
    fb_lon = ev.pop('fallback_lon', None)
    lat, lon = geocode(ev['location'], fb_lat, fb_lon)
    if lat is None:
        parts = ev['location'].split(',')
        if len(parts) > 1:
            lat, lon = geocode(parts[-1].strip(), fb_lat, fb_lon)
    if lat and lon:
        print(f"  ✓ {ev['title'][:50]}: {lat:.4f}, {lon:.4f}")
        ev['latitude'] = lat
        ev['longitude'] = lon
        ev['status'] = 'auto_validated'
        api_events.append(ev)
    else:
        print(f"  ✗ ÉCHEC: {ev['title']}")

# === IMPORT ===
if api_events:
    print(f"\n=== Import ({len(api_events)} events) ===")
    r = requests.post(f'{API_URL}/api/events/scraped/batch', json={'events': api_events}, timeout=60)
    print(f"Status: {r.status_code}")
    try:
        print(json.dumps(r.json(), indent=2, ensure_ascii=False))
    except:
        print(r.text[:500])

# === VÉRIFICATION ===
print("\n=== Vérification ===")
time.sleep(2)
r = requests.get(f'{API_URL}/api/events', timeout=30)
data = r.json()
all_ev = data if isinstance(data, list) else data.get('events', [])
print(f"TOTAL: {len(all_ev)}")

regions = {'Valais': 0, 'Vaud': 0, 'Genève': 0, 'Autre': 0}
for ev in all_ev:
    loc = (ev.get('location', '') or '').lower()
    if any(x in loc for x in ['valais', 'sion', 'sierre', 'martigny', 'monthey', 'visp', 'brig', 'nendaz', 'zermatt', 'verbier', 'crans-montana', 'leukerbad', 'champéry', 'champery', 'collonges', 'troistorrents', 'saint-maurice', 'le châble', 'anniviers', 'grimentz', 'evolène', 'anzère']):
        regions['Valais'] += 1
    elif any(x in loc for x in ['genève', 'carouge', 'cologny', 'lancy', 'vernier', 'meyrin', 'grand-saconnex', 'saconnex', 'onex', 'plainpalais']):
        regions['Genève'] += 1
    elif any(x in loc for x in ['vaud', 'lausanne', 'morges', 'nyon', 'montreux', 'vevey', 'aigle', 'yverdon', 'etoy', 'st-prex', 'tolochenaz', 'montricher', 'cully', 'pully', 'la tour-de-peilz', 'veytaux', 'villars']):
        regions['Vaud'] += 1
    else:
        regions['Autre'] += 1

print(f"\nPar région:")
for r, c in regions.items():
    print(f"  {r}: {c}")
