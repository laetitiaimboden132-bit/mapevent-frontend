"""
Import batch final - events confirmés 2026 depuis sites officiels
Sources: sites des festivals (niveau 3-4 sûres)
"""
import requests, sys, io, json, time

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'
NOMINATIM_URL = 'https://nominatim.openstreetmap.org/search'
HEADERS = {'User-Agent': 'MapEventAI/1.0 (contact@mapevent.ai)'}

def geocode(address, fallback_lat=None, fallback_lon=None):
    try:
        time.sleep(1.5)
        r = requests.get(NOMINATIM_URL, params={'q': address, 'format': 'json', 'limit': 1, 'countrycodes': 'ch'}, headers=HEADERS, timeout=10)
        results = r.json()
        if results:
            return float(results[0]['lat']), float(results[0]['lon'])
    except Exception as e:
        print(f"  Geocode error: {e}")
    return fallback_lat, fallback_lon

events = []

# 1. Patrouille des Glaciers 2026
# Source: pdg.ch + rts.ch + lenouvelliste.ch
# Dates: 13-19 avril 2026, Zermatt-Verbier
events.append({
    'title': 'Patrouille des Glaciers 2026',
    'location': 'Zermatt - Verbier, Valais',
    'date': '2026-04-13',
    'end_date': '2026-04-19',
    'time': None,
    'end_time': None,
    'description': '41e édition de la Patrouille des Glaciers. Course mythique de ski-alpinisme reliant Zermatt à Verbier via Arolla (57,5 km) et d\'Arolla à Verbier (29,6 km). Jusqu\'à 1600 patrouilles de 3 coureurs. Première catégorie féminine avec classement séparé. Courses les 14-15 et 17-18 avril.',
    'categories': ["Sport", "Sport > Terrestre"],
    'source_url': 'https://www.pdg.ch/',
    'organizer_name': 'Patrouille des Glaciers',
    'fallback_lat': 46.0207,
    'fallback_lon': 7.7491
})

# 2. Montreux International Guitar Show 2026
# Source: migs.ch
# Dates: 24-26 avril 2026, Montreux
events.append({
    'title': 'Montreux International Guitar Show 2026',
    'location': 'Montreux, 1820 Montreux',
    'date': '2026-04-24',
    'end_date': '2026-04-26',
    'time': None,
    'end_time': None,
    'description': 'Salon international de la guitare à Montreux. Exposition de guitares et accessoires, plus de 3000 visiteurs. Concerts : Dan Patlansky (blues, samedi 25 avril) et Mike Dawes (guitare acoustique, dimanche 26 avril). Vue sur le lac Léman.',
    'categories': ["Musique", "Exposition"],
    'source_url': 'https://www.migs.ch/',
    'organizer_name': 'MIGS',
    'fallback_lat': 46.4312,
    'fallback_lon': 6.9107
})

# 3. Bol d'Or Mirabaud 2026
# Source: boldorduleman.ch + nautique.ch
# Dates: 5-7 juin 2026, Genève/Lac Léman
events.append({
    'title': 'Bol d\'Or Mirabaud 2026',
    'location': 'Société Nautique de Genève, Port Noir, 1207 Genève',
    'date': '2026-06-05',
    'end_date': '2026-06-07',
    'time': '10:00',
    'end_time': None,
    'description': '85e édition du Bol d\'Or Mirabaud, la plus grande régate en bassin fermé du monde. Environ 500 bateaux (monocoques et multicoques) parcourent 123 km sur le Lac Léman, de Genève au Bouveret et retour. Animations et stands au bord du lac.',
    'categories': ["Sport", "Sport > Aquatique"],
    'source_url': 'https://boldorduleman.ch/',
    'organizer_name': 'Société Nautique de Genève',
    'fallback_lat': 46.2022,
    'fallback_lon': 6.1602
})

# 4. Voix de Fête 2026
# Source: voixdefete.com + onefm.ch + loisirs.ch
# Dates: 14-21 mars 2026, Genève
events.append({
    'title': 'Festival Voix de Fête 2026',
    'location': 'Alhambra, Rue de la Rôtisserie 10, 1204 Genève',
    'date': '2026-03-14',
    'end_date': '2026-03-21',
    'time': None,
    'end_time': None,
    'description': '28e édition du festival de musique francophone de Genève. Concerts à l\'Alhambra, Salle Communale de Plainpalais, Chat Noir et autres lieux. Avec Oxmo Puccino, Vincent Delerm, Marguerite, GiedRé, La Mano 1.9 et bien d\'autres. "Bars en Fête" du 11 au 21 mars.',
    'categories': ["Musique", "Festival"],
    'source_url': 'https://www.voixdefete.com/',
    'organizer_name': 'Festival Voix de Fête',
    'fallback_lat': 46.2012,
    'fallback_lon': 6.1472
})

# 5. Festival de la Cité 2026
# Source: festivalcite.ch
# Dates: 30 juin - 5 juillet 2026, Lausanne
events.append({
    'title': 'Festival de la Cité 2026',
    'location': 'Cité de Lausanne, Place de la Cathédrale, 1005 Lausanne',
    'date': '2026-06-30',
    'end_date': '2026-07-05',
    'time': None,
    'end_time': None,
    'description': '54e édition du Festival de la Cité de Lausanne. Festival gratuit en plein air dans la Cité historique de Lausanne. Musique, théâtre, danse, cirque et arts visuels. L\'un des plus anciens festivals de plein air de Suisse.',
    'categories': ["Festival", "Culture", "Musique"],
    'source_url': 'https://festivalcite.ch/',
    'organizer_name': 'Festival de la Cité',
    'fallback_lat': 46.5227,
    'fallback_lon': 6.6347
})

# === VÉRIFICATION DOUBLONS ===
print("=== Vérification doublons ===")
r = requests.get(f'{API_URL}/api/events', timeout=30)
data = r.json()
existing = data if isinstance(data, list) else data.get('events', [])
existing_urls = {e.get('source_url', '').lower().strip() for e in existing}
print(f"Events existants: {len(existing)}")

new_events = []
for ev in events:
    url_lower = ev['source_url'].lower().strip()
    if url_lower in existing_urls:
        print(f"  DOUBLON URL: {ev['title']}")
    else:
        new_events.append(ev)

print(f"\nEvents à importer: {len(new_events)}/{len(events)}")

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

print(f"\nGéocodés: {len(api_events)}/{len(new_events)}")

# === IMPORT ===
if api_events:
    print("\n=== Import ===")
    r = requests.post(
        f'{API_URL}/api/events/scraped/batch',
        json={'events': api_events},
        timeout=60
    )
    print(f"Status: {r.status_code}")
    try:
        result = r.json()
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except:
        print(r.text[:500])

# === VÉRIFICATION ===
print("\n=== Vérification finale ===")
time.sleep(2)
r = requests.get(f'{API_URL}/api/events', timeout=30)
data = r.json()
all_ev = data if isinstance(data, list) else data.get('events', [])
print(f"TOTAL: {len(all_ev)}")

regions = {'Valais': 0, 'Vaud': 0, 'Genève': 0, 'Autre': 0}
for ev in all_ev:
    loc = (ev.get('location', '') or '').lower()
    if any(x in loc for x in ['valais', 'sion', 'sierre', 'martigny', 'monthey', 'visp', 'brig', 'nendaz', 'zermatt', 'verbier', 'crans-montana', 'leukerbad', 'champéry', 'champery', 'collonges', 'troistorrents', 'saint-maurice', 'le châble', 'anniviers']):
        regions['Valais'] += 1
    elif any(x in loc for x in ['genève', 'carouge', 'cologny', 'lancy', 'vernier', 'meyrin', 'grand-saconnex', 'saconnex']):
        regions['Genève'] += 1
    elif any(x in loc for x in ['vaud', 'lausanne', 'morges', 'nyon', 'montreux', 'vevey', 'aigle', 'yverdon', 'etoy', 'st-prex', 'tolochenaz', 'montricher', 'cully', 'pully', 'la tour-de-peilz', 'veytaux']):
        regions['Vaud'] += 1
    else:
        regions['Autre'] += 1

print(f"Par région:")
for r, c in regions.items():
    print(f"  {r}: {c}")
