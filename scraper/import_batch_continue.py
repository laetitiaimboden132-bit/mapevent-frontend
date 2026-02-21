"""
Batch continu - encore plus d'events confirmés 2026
Sources: sites officiels des événements (niveau 3-4)
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
    except Exception as e:
        print(f"  Geocode error: {e}")
    return fb_lat, fb_lon

events = []

# 1. SailGP Genève 2026
# Source: rts.ch + letemps.ch + ge.ch (autorisé par le canton)
events.append({
    'title': 'SailGP Genève 2026',
    'location': 'Rade de Genève, 1204 Genève',
    'date': '2026-09-19',
    'end_date': '2026-09-20',
    'time': None,
    'end_time': None,
    'description': 'Rolex Switzerland Sail Grand Prix Geneva. 12 équipages de 12 pays sur des catamarans F50 à foils dans la rade de Genève. 11e étape de la saison SailGP 2026 et dernière étape européenne. Compétition de voile de haut niveau spectaculaire.',
    'categories': ["Sport", "Sport > Aquatique"],
    'source_url': 'https://sailgp.com/races/switzerland/',
    'organizer_name': 'SailGP',
    'fallback_lat': 46.2050,
    'fallback_lon': 6.1520
})

# 2. Valais Triathlon Festival 2026
# Source: valaistriathlon.ch
events.append({
    'title': 'Valais Triathlon Festival 2026',
    'location': 'Domaine des Îles, 1950 Sion',
    'date': '2026-08-14',
    'end_date': '2026-08-16',
    'time': '07:00',
    'end_time': None,
    'description': '3e édition du Valais Triathlon Festival au Domaine des Îles à Sion. Distances Full, Half, Olympic, Short, Swimrun et courses enfants (6-13 ans). Concerts le samedi soir. Trois jours de compétition dans un cadre naturel exceptionnel.',
    'categories': ["Sport", "Sport > Aquatique", "Festival"],
    'source_url': 'https://valaistriathlon.ch/',
    'organizer_name': 'Valais Triathlon Festival',
    'fallback_lat': 46.2300,
    'fallback_lon': 7.3600
})

# 3. Tavolata des Vins du Valais 2026
# Source: estivales-valais.ch + tavolata-valais.ch
events.append({
    'title': 'Tavolata des Vins du Valais 2026',
    'location': 'Vignobles du Valais, divers lieux, Valais',
    'date': '2026-08-01',
    'end_date': '2026-08-31',
    'time': None,
    'end_time': None,
    'description': 'Repas en longue table au cœur des vignobles valaisans et lieux insolites. Plusieurs dates en août : 1-3, 8-9, 15-17, 22-24 et 28-31 août. Buffet valaisan, raclette, fondue, menus gastronomiques avec vins du terroir. La plus grande tavolata (350 convives) au Parc naturel Pfyn-Finges le 22 août.',
    'categories': ["Gastronomie", "Culture", "Vin"],
    'source_url': 'https://www.estivales-valais.ch/',
    'organizer_name': 'Tavolata des Vins du Valais',
    'fallback_lat': 46.3000,
    'fallback_lon': 7.5300
})

# 4. Urban Trail Lausanne 2026
# Source: urbantrail-lausanne.com + lausanne-tourisme.ch
events.append({
    'title': 'Urban Trail Lausanne 2026',
    'location': 'Stade Pierre-de-Coubertin, Avenue Pierre-de-Coubertin, 1007 Lausanne',
    'date': '2026-03-15',
    'end_date': '2026-03-15',
    'time': '09:00',
    'end_time': None,
    'description': '7e édition de l\'Urban Trail Lausanne. 3 parcours : 10 km (200m D+), 19 km (500m D+) et 31 km (900m D+) combinant ville, lac et montagne. Départ et arrivée au Stade Pierre-de-Coubertin. Inscriptions en ligne uniquement, places limitées.',
    'categories': ["Sport", "Sport > Terrestre"],
    'source_url': 'https://urbantrail-lausanne.com/',
    'organizer_name': 'Urban Trail Lausanne',
    'fallback_lat': 46.5150,
    'fallback_lon': 6.5970
})

# 5. Cyclotour du Léman 2026
# Source: cyclotourduleman.ch + battistrada.com
events.append({
    'title': 'Cyclotour du Léman 2026',
    'location': 'Place de la Navigation, 1006 Lausanne',
    'date': '2026-05-24',
    'end_date': '2026-05-24',
    'time': '06:00',
    'end_time': None,
    'description': 'Cyclosportive autour du Lac Léman. 3 parcours : 176 km (tour complet, 890m D+), 112 km (Évian-Lausanne, 640m D+) et 64 km (Lausanne-Évian, 250m D+). 4000 participants max. Gran Fondo World Tour. Départ Place de la Navigation, Lausanne-Ouchy.',
    'categories': ["Sport", "Sport > Terrestre", "Cyclisme"],
    'source_url': 'https://www.cyclotourduleman.ch/',
    'organizer_name': 'Cyclotour du Léman',
    'fallback_lat': 46.5050,
    'fallback_lon': 6.6280
})

# 6. Championnat du monde de curling double mixte 2026
# Source: rts.ch + curling.ca
events.append({
    'title': 'Championnat du monde de curling double mixte 2026',
    'location': 'Genève, 1200 Genève',
    'date': '2026-04-25',
    'end_date': '2026-05-02',
    'time': None,
    'end_time': None,
    'description': 'Championnat du monde de curling en double mixte à Genève. Compétition internationale réunissant les meilleures équipes de curling du monde. Genève accueille cet événement pour la deuxième fois après 2022.',
    'categories': ["Sport"],
    'source_url': 'https://worldcurling.org/events/wmdxcc2026/',
    'organizer_name': 'World Curling Federation',
    'fallback_lat': 46.2044,
    'fallback_lon': 6.1432
})

# 7. Fête de la Musique Genève 2026
# Source: evenements.geneve.ch/fetedelamusique + geneve.ch
events.append({
    'title': 'Fête de la Musique Genève 2026',
    'location': 'Divers lieux, 1200 Genève',
    'date': '2026-06-19',
    'end_date': '2026-06-21',
    'time': None,
    'end_time': None,
    'description': 'Trois jours de musique gratuite à Genève. Une trentaine de scènes en plein air et en salle : Parc des Bastions, Place de Neuve, Vieille-Ville, Parc La Grange, Rue des Rois. Tous les styles : musiques du monde, hip-hop, reggae, blues, jazz, électro, DJ sets.',
    'categories': ["Musique", "Festival"],
    'source_url': 'https://evenements.geneve.ch/fetedelamusique/',
    'organizer_name': 'Ville de Genève',
    'fallback_lat': 46.2001,
    'fallback_lon': 6.1463
})

# 8. Esprit Festif Le Festival 2026
# Source: espritfestif.ch
events.append({
    'title': 'Esprit Festif Le Festival 2026',
    'location': 'Parc des Evaux, 1213 Onex',
    'date': '2026-09-04',
    'end_date': '2026-09-05',
    'time': None,
    'end_time': None,
    'description': 'Festival de musique au Parc des Evaux à Onex, Genève. Retour après deux années d\'absence avec un nouveau lieu et de nouvelles dates.',
    'categories': ["Musique", "Festival"],
    'source_url': 'https://espritfestif.ch/',
    'organizer_name': 'Esprit Festif',
    'fallback_lat': 46.1830,
    'fallback_lon': 6.0980
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
        print(f"  DOUBLON: {ev['title']}")
    else:
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

print(f"\nGéocodés: {len(api_events)}/{len(new_events)}")

# === IMPORT ===
if api_events:
    print("\n=== Import ===")
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
    if any(x in loc for x in ['valais', 'sion', 'sierre', 'martigny', 'monthey', 'visp', 'brig', 'nendaz', 'zermatt', 'verbier', 'crans-montana', 'leukerbad', 'champéry', 'champery', 'collonges', 'troistorrents', 'saint-maurice', 'le châble', 'anniviers', 'grimentz']):
        regions['Valais'] += 1
    elif any(x in loc for x in ['genève', 'carouge', 'cologny', 'lancy', 'vernier', 'meyrin', 'grand-saconnex', 'saconnex', 'onex', 'rade']):
        regions['Genève'] += 1
    elif any(x in loc for x in ['vaud', 'lausanne', 'morges', 'nyon', 'montreux', 'vevey', 'aigle', 'yverdon', 'etoy', 'st-prex', 'tolochenaz', 'montricher', 'cully', 'pully', 'la tour-de-peilz', 'veytaux']):
        regions['Vaud'] += 1
    else:
        regions['Autre'] += 1

print(f"\nPar région:")
for r, c in regions.items():
    print(f"  {r}: {c}")
