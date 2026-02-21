"""
Import de nouveaux events confirmés 2026 depuis des sources individuelles (niveau 3-4 sûres)
Chaque event a ses dates confirmées sur le site officiel de l'organisateur.
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

# === NOUVEAUX EVENTS CONFIRMÉS ===
events = []

# 1. Maxi-Rires Festival 2026 - Champéry, Valais
# Source: maxi-rires.ch + radiochablais.ch + rhonefm.ch
# 18e édition confirmée, artistes annoncés
events.append({
    'title': 'Maxi-Rires Festival 2026',
    'location': 'Palladium de Champéry, Route du Centre Sportif 1, 1874 Champéry',
    'date': '2026-03-23',
    'end_date': '2026-03-28',
    'time': None,
    'end_time': None,
    'description': '18e édition du festival d\'humour international de Champéry. Dix spectacles mêlant stand-up, magie, humour musical et comédie. Avec Dany Boon, Camille Lellouche, Alex Vizorek, Thomas Wiesel, Olivier de Benoist, David Castello-Lopes et bien d\'autres.',
    'categories': ["Festival", "Humour", "Spectacle"],
    'source_url': 'https://www.maxi-rires.ch/',
    'organizer_name': 'Maxi-Rires Festival',
    'fallback_lat': 46.1744,
    'fallback_lon': 6.8700
})

# 2. 92ème Festival des Musiques du Bas-Valais - Collonges, Valais
# Source: festival2026.ch + echodelamontagne.ch
# Dates confirmées: 29-31 mai 2026
events.append({
    'title': '92ème Festival des Musiques du Bas-Valais',
    'location': 'Collonges, 1903 Collonges, Valais',
    'date': '2026-05-29',
    'end_date': '2026-05-31',
    'time': None,
    'end_time': None,
    'description': '92e édition du Festival des Musiques du Bas-Valais à Collonges. Thème "Ça souffle !". 23 sociétés de musique réunies, environ 1000 musiciens, 150 jeunes solistes, 250-300 bénévoles. Parade, concours en salle de concert, concours de jeunes solistes. La Collongienne organise et fête ses 125 ans.',
    'categories': ["Musique", "Festival", "Culture"],
    'source_url': 'https://www.festival2026.ch/',
    'organizer_name': 'Fédération des Musiques du Bas-Valais',
    'fallback_lat': 46.1666,
    'fallback_lon': 7.0416
})

# 3. Groove'N'Move Festival 2026 - Genève
# Source: groove-n-move.ch
# 16e édition confirmée, 4-15 mars 2026
events.append({
    'title': 'Groove\'N\'Move Festival 2026',
    'location': 'Divers lieux, 1200 Genève',
    'date': '2026-03-04',
    'end_date': '2026-03-15',
    'time': None,
    'end_time': None,
    'description': '16e édition du festival de danse urbaine et hip-hop de Genève. Battles de popping, hip-hop all style, kids & juniors. Spectacles de danse dont "Sol Invictus" de la Cie Hervé Koubi. Stages d\'initiation, projections de films, conférences. Salle du Lignon, Forum Meyrin, Théâtre Nebia.',
    'categories': ["Danse", "Festival", "Culture"],
    'source_url': 'https://groove-n-move.ch/',
    'organizer_name': 'Groove\'N\'Move',
    'fallback_lat': 46.2044,
    'fallback_lon': 6.1432
})

# 4. Salon du Livre Genève 2026 - Palexpo
# Source: salondulivre.ch + geneve.ch/agenda + palexpo.ch
# 40e édition confirmée, 18-22 mars 2026, gratuit
events.append({
    'title': 'Salon du Livre de Genève 2026',
    'location': 'Palexpo, Route François-Peyrot 30, 1218 Le Grand-Saconnex',
    'date': '2026-03-18',
    'end_date': '2026-03-22',
    'time': '09:30',
    'end_time': '19:00',
    'description': '40e édition du Salon du Livre de Genève à Palexpo. Entrée gratuite sur inscription. Plus de 200 exposants, centaines d\'auteurs, dédicaces, débats et animations. Invités d\'honneur : Laure Adler, Patrick Chappatte, Hélène Dorion et Douglas Kennedy.',
    'categories': ["Culture", "Exposition", "Littérature"],
    'source_url': 'https://www.salondulivre.ch/',
    'organizer_name': 'Salon du Livre de Genève',
    'fallback_lat': 46.2339,
    'fallback_lon': 6.1138
})

# 5. Rencontres Musicales de Champéry 2026 - Champéry, Valais
# Source: rencontres-musicales.ch
# 27e édition, dates confirmées: 31 jul - 14 aug 2026
events.append({
    'title': 'Rencontres Musicales de Champéry 2026',
    'location': 'Champéry, 1874 Champéry, Valais',
    'date': '2026-07-31',
    'end_date': '2026-08-14',
    'time': None,
    'end_time': None,
    'description': '27e édition des Rencontres Musicales de Champéry. Festival de musique classique au pied des Dents du Midi. Orchestre, musique de chambre et artistes de renommée internationale. Programme détaillé à venir.',
    'categories': ["Musique", "Festival", "Classique"],
    'source_url': 'https://www.rencontres-musicales.ch/',
    'organizer_name': 'Rencontres Musicales de Champéry',
    'fallback_lat': 46.1744,
    'fallback_lon': 6.8700
})

# 6. Caprices Festival 2026 - Gstaad (nouveau lieu)
# Source: capricesfestival.com + myswitzerland.com
# Deux weekends confirmés: 13-15 et 20-22 mars 2026
events.append({
    'title': 'Caprices Festival 2026',
    'location': 'Eggli, 3780 Gstaad',
    'date': '2026-03-13',
    'end_date': '2026-03-22',
    'time': None,
    'end_time': None,
    'description': 'Le Caprices Festival déménage à Eggli (Gstaad) à 2000m d\'altitude. Deux weekends (13-15 et 20-22 mars) de musique électronique. Trois scènes en verre avec vue alpine : Peak Stage, CNTRL Stage et Ridge Stage. Avec Ricardo Villalobos, Sven Väth, Vintage Culture et plus. Télécabines en continu de midi à 4h du matin.',
    'categories': ["Musique", "Festival", "Électronique"],
    'source_url': 'https://capricesfestival.com/',
    'organizer_name': 'Caprices Festival',
    'fallback_lat': 46.4750,
    'fallback_lon': 7.2850
})

# 7. Champéry Film Festival 2026 - Champéry, Valais
# Source: champeryfilmfestival.ch - besoin de vérifier les dates
# Skipped: dates 2026 pas encore annoncées

# === VÉRIFICATION DOUBLONS ===
print("=== Vérification doublons ===")
r = requests.get(f'{API_URL}/api/events', timeout=30)
data = r.json()
existing = data if isinstance(data, list) else data.get('events', [])
existing_titles = [e.get('title', '').lower().strip() for e in existing]
existing_urls = [e.get('source_url', '').lower().strip() for e in existing]
print(f"Events existants: {len(existing)}")

new_events = []
for ev in events:
    title_lower = ev['title'].lower().strip()
    url_lower = ev['source_url'].lower().strip()
    is_dup = False
    
    if url_lower in existing_urls:
        print(f"  DOUBLON URL: {ev['title']}")
        is_dup = True
    
    if not is_dup:
        for et in existing_titles:
            # Check partial match
            words = title_lower.split()
            key_words = [w for w in words if len(w) > 4 and w not in ('2026', 'festival', 'de', 'du', 'des', 'la', 'le', 'les')]
            if any(kw in et for kw in key_words[:3]):
                # Double check
                if sum(1 for kw in key_words if kw in et) >= 2:
                    print(f"  DOUBLON TITRE: {ev['title']} ≈ {et[:50]}")
                    is_dup = True
                    break
    
    if not is_dup:
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
print(f"TOTAL EVENTS: {len(all_ev)}")

regions = {'Valais': 0, 'Vaud': 0, 'Genève': 0, 'Autre': 0}
for ev in all_ev:
    loc = (ev.get('location', '') or '').lower()
    if any(x in loc for x in ['valais', 'sion', 'sierre', 'martigny', 'monthey', 'visp', 'brig', 'nendaz', 'zermatt', 'verbier', 'crans-montana', 'leukerbad', 'champéry', 'champery', 'gryon', 'collonges', 'troistorrents', 'saint-maurice', 'le châble', 'anniviers']):
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
