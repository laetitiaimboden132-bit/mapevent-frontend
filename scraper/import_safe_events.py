"""
Import d'événements depuis des sources sûres (niveaux 3-4).
Toutes les données proviennent directement des sites officiels des événements.
Ces sites de festivals/événements VEULENT être référencés (promotion).
robots.txt vérifiés: aucun blocage ou pas de robots.txt.
"""
import requests, sys, io, json, time
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'

def geocode(query, retries=2):
    for attempt in range(retries):
        try:
            resp = requests.get('https://nominatim.openstreetmap.org/search', params={
                'q': query, 'format': 'json', 'limit': 1
            }, headers={'User-Agent': 'MapEventAI-Bot/1.0'}, timeout=10)
            results = resp.json()
            if results:
                return float(results[0]['lat']), float(results[0]['lon'])
        except:
            pass
        time.sleep(2)
    return None, None

# ============================================================
# ÉVÉNEMENTS VÉRIFIÉS - Données directement des sites sources
# ============================================================
events_to_import = [
    # === VALAIS ===
    {
        'title': 'Festival du Mariage Valais',
        'description': 'Le Festival du Mariage Valais revient pour sa 5e édition au Pavillon des Mangettes à Monthey. Plus de 30 exposants choisis avec soin, mini-conférences, ateliers, défilés de mode et restauration. Entrée gratuite.',
        'start_date': '2026-04-10',
        'end_date': '2026-04-12',
        'location': 'Pavillon des Mangettes, Boeuferrant-Sud 45, 1870 Monthey',
        'categories': ['Culture > Festival', 'Famille > Fêtes'],
        'source_url': 'https://festivaldumariagevalais.ch/',
        'organizer_name': 'Festival du Mariage Valais',
        'validation_status': 'auto_validated',
    },
    {
        'title': 'FestiVal d\'Anniviers - Concert au Barrage de Moiry',
        'description': '17e édition du FestiVal d\'Anniviers. Concert exceptionnel au barrage de Moiry. Musique classique dans un cadre montagnard unique.',
        'start_date': '2026-08-05',
        'end_date': '2026-08-05',
        'location': 'Barrage de Moiry, 3961 Grimentz, Valais',
        'categories': ['Music > Classique / Baroque', 'Music > Concert'],
        'source_url': 'https://festivaldanniviers.ch/',
        'organizer_name': 'FestiVal d\'Anniviers',
        'validation_status': 'auto_validated',
    },
    {
        'title': 'FestiVal d\'Anniviers - Concert de clôture',
        'description': '17e édition du FestiVal d\'Anniviers. Concert de clôture à l\'église de Grimentz. Musique classique interprétée par des solistes et un orchestre.',
        'start_date': '2026-08-09',
        'end_date': '2026-08-09',
        'location': 'Église de Grimentz, 3961 Grimentz, Valais',
        'categories': ['Music > Classique / Baroque', 'Music > Concert'],
        'source_url': 'https://festivaldanniviers.ch/',
        'organizer_name': 'FestiVal d\'Anniviers',
        'validation_status': 'auto_validated',
    },
    {
        'title': 'Festival d\'Art de Rue de Sion',
        'description': '26e édition du Festival d\'Art de Rue de Sion. Festival gratuit depuis sa création, au cœur de la vieille ville de Sion. Les artistes sont rémunérés et autorisés à passer le chapeau. Labellisé Fiesta.',
        'start_date': '2026-06-05',
        'end_date': '2026-06-06',
        'location': 'Vieille ville de Sion, Rue du Grand-Pont, 1950 Sion',
        'categories': ['Culture > Festival', 'Culture > Spectacles', 'Famille > Fêtes'],
        'source_url': 'https://www.festival-sion.ch/',
        'organizer_name': 'Festival d\'Art de Rue de Sion',
        'organizer_email': 'info@artderuesion.ch',
        'validation_status': 'auto_validated',
    },
    {
        'title': 'Sion sous les étoiles 2026',
        'description': '11e édition de Sion sous les étoiles. Festival de musique en plein air avec Julien Doré, Christophe Maé, Vitaa, GIMS, Louane, Umberto Tozzi et Superbus.',
        'start_date': '2026-07-16',
        'end_date': '2026-07-18',
        'location': 'Place de la Planta, 1950 Sion, Valais',
        'categories': ['Music > Festival', 'Music > Concert', 'Music > Rock / Pop'],
        'source_url': 'https://www.sionsouslesetoiles.ch/',
        'organizer_name': 'Sion sous les étoiles',
        'validation_status': 'auto_validated',
    },
    # === VAUD ===
    {
        'title': 'Polymanga 2026',
        'description': '20e édition de Polymanga. Plus de 50\'000 visiteurs attendus sur 25\'000 m². Invités dont Cyprien, défilés de cosplay, concerts, tournois de jeux vidéo, grande galerie de shopping. Pass 1 jour CHF 35, enfants < 9 ans gratuit.',
        'start_date': '2026-04-03',
        'end_date': '2026-04-06',
        'location': 'Théâtre de Beaulieu, Avenue des Bergières 10, 1004 Lausanne',
        'categories': ['Culture > Festival', 'Famille > Activités'],
        'source_url': 'https://www.polymanga.com/',
        'organizer_name': 'Polymanga',
        'validation_status': 'auto_validated',
    },
    {
        'title': 'Caves Ouvertes Vaudoises 2026',
        'description': 'Les Caves Ouvertes Vaudoises : environ 250 caves participantes dans les 6 régions viticoles vaudoises (La Côte, Lavaux, Chablais, Bonvillars, Côtes de l\'Orbe, Vully). Ticket CHF 20 incluant verre de dégustation et transports publics gratuits.',
        'start_date': '2026-05-23',
        'end_date': '2026-05-24',
        'location': 'Canton de Vaud, Suisse - plusieurs régions viticoles',
        'categories': ['Gastronomie > Dégustation', 'Gastronomie > Gastronomie', 'Nature > Randonnées'],
        'source_url': 'https://www.mescavesouvertes.ch/',
        'organizer_name': 'Office des Vins Vaudois',
        'validation_status': 'auto_validated',
    },
    {
        'title': 'Montreux Jazz Festival 2026',
        'description': '60e édition du Montreux Jazz Festival. Le plus célèbre festival de musique de Suisse. Deux semaines de concerts à l\'Auditorium Stravinski (4000 places) et sur les scènes gratuites au bord du lac.',
        'start_date': '2026-07-03',
        'end_date': '2026-07-18',
        'location': 'Auditorium Stravinski, Rue du Théâtre 5, 1820 Montreux',
        'categories': ['Music > Festival', 'Music > Jazz', 'Music > Concert'],
        'source_url': 'https://www.montreuxjazzfestival.com/',
        'organizer_name': 'Montreux Jazz Festival',
        'validation_status': 'auto_validated',
    },
    {
        'title': 'Visions du Réel - Festival international du cinéma',
        'description': 'Festival international de cinéma documentaire à Nyon. Parmi les plus importants au monde, accueillant environ 45\'000 entrées.',
        'start_date': '2026-04-17',
        'end_date': '2026-04-26',
        'location': 'Usine à Gaz, Place du Château, 1260 Nyon',
        'categories': ['Culture > Cinéma', 'Culture > Festival'],
        'source_url': 'https://www.visionsdureel.ch/',
        'organizer_name': 'Visions du Réel',
        'validation_status': 'auto_validated',
    },
    {
        'title': 'Caribana Festival 2026',
        'description': 'Festival musical pop, rock, électro et rap au Port de Crans près de Nyon. Environ 30\'000 spectateurs attendus sur 4 jours au bord du lac Léman.',
        'start_date': '2026-06-17',
        'end_date': '2026-06-20',
        'location': 'Port de Crans, 1260 Nyon, Vaud',
        'categories': ['Music > Festival', 'Music > Rock / Pop', 'Music > Electro / DJ'],
        'source_url': 'https://www.caribana-festival.ch/',
        'organizer_name': 'Caribana Festival',
        'validation_status': 'auto_validated',
    },
    {
        'title': 'Vevey Spring Classic 2026',
        'description': '5e édition du Vevey Spring Classic. Festival de musique classique avec mentors musiciens prestigieux.',
        'start_date': '2026-05-06',
        'end_date': '2026-05-12',
        'location': 'Vevey, Rue du Théâtre 4, 1800 Vevey, Vaud',
        'categories': ['Music > Classique / Baroque', 'Music > Concert', 'Music > Festival'],
        'source_url': 'https://veveyspringclassic.ch/',
        'organizer_name': 'Vevey Spring Classic',
        'validation_status': 'auto_validated',
    },
    {
        'title': 'Festival Rive Jazzy - Nyon 2026',
        'description': 'Plus de 30 ans de concerts jazz au bord du lac Léman. Concerts gratuits sur les terrasses du Quartier de Rive à Nyon.',
        'start_date': '2026-07-02',
        'end_date': '2026-08-09',
        'location': 'Quartier de Rive, 1260 Nyon, Vaud',
        'categories': ['Music > Jazz', 'Music > Concert', 'Music > Festival'],
        'source_url': 'https://rivejazzy.ch/',
        'organizer_name': 'Rive Jazzy',
        'validation_status': 'auto_validated',
    },
    # === GENÈVE ===
    {
        'title': 'Salon du Livre de Genève 2026',
        'description': '40e édition du Salon du Livre de Genève à Palexpo. Le plus grand événement littéraire de Suisse romande.',
        'start_date': '2026-03-18',
        'end_date': '2026-03-22',
        'location': 'Palexpo, Route François-Peyrot 30, 1218 Le Grand-Saconnex',
        'categories': ['Culture > Littérature', 'Culture > Festival'],
        'source_url': 'https://www.palexpo.ch/agenda/',
        'organizer_name': 'Palexpo SA',
        'validation_status': 'auto_validated',
    },
    {
        'title': 'Watches and Wonders Geneva 2026',
        'description': 'Le plus grand événement horloger de l\'année. Nouvelles marques dont Audemars Piguet, espaces LAB d\'innovations technologiques et programme culturel. Ouvert au public du 18 au 20 avril.',
        'start_date': '2026-04-14',
        'end_date': '2026-04-20',
        'location': 'Palexpo, Route François-Peyrot 30, 1218 Le Grand-Saconnex',
        'categories': ['Culture > Expositions', 'Culture > Festival'],
        'source_url': 'https://www.watchesandwonders.com/fr/geneva-2026',
        'organizer_name': 'Watches and Wonders',
        'validation_status': 'auto_validated',
    },
    {
        'title': 'Salon International des Inventions de Genève 2026',
        'description': '51e édition du Salon International des Inventions. Plus de 1000 inventions de 40 pays, ateliers scientifiques, rencontres avec inventeurs et pavillon suisse.',
        'start_date': '2026-03-11',
        'end_date': '2026-03-15',
        'location': 'Palexpo, Halle 2, Route François-Peyrot 30, 1218 Le Grand-Saconnex',
        'categories': ['Culture > Expositions', 'Culture > Conférence', 'Famille > Activités'],
        'source_url': 'https://www.inventions-geneva.ch/',
        'organizer_name': 'Salon International des Inventions',
        'validation_status': 'auto_validated',
    },
    {
        'title': 'GemGenève 2026',
        'description': 'Salon international de la gemmologie et de la joaillerie à Palexpo. Exposition de pierres précieuses, bijoux et objets d\'art.',
        'start_date': '2026-05-07',
        'end_date': '2026-05-10',
        'location': 'Palexpo, Route François-Peyrot 30, 1218 Le Grand-Saconnex',
        'categories': ['Culture > Expositions'],
        'source_url': 'https://www.palexpo.ch/agenda/',
        'organizer_name': 'GemGenève',
        'validation_status': 'auto_validated',
    },
    {
        'title': 'autoXpérience Genève 2026',
        'description': 'Salon automobile de Genève, nouvelle formule avec expériences immersives et découverte des dernières innovations automobiles.',
        'start_date': '2026-03-05',
        'end_date': '2026-03-08',
        'location': 'Palexpo, Route François-Peyrot 30, 1218 Le Grand-Saconnex',
        'categories': ['Culture > Expositions', 'Culture > Festival'],
        'source_url': 'https://www.palexpo.ch/agenda/',
        'organizer_name': 'Palexpo SA',
        'validation_status': 'auto_validated',
    },
]

# ============================================================
# GÉOCODAGE
# ============================================================
print(f"=== GÉOCODAGE DE {len(events_to_import)} ÉVÉNEMENTS ===\n")

for ev in events_to_import:
    loc = ev['location']
    lat, lon = geocode(loc)
    if lat and lon:
        ev['latitude'] = lat
        ev['longitude'] = lon
        print(f"  ✅ {ev['title'][:45]} → {lat:.4f}, {lon:.4f}")
    else:
        # Fallback: essayer avec juste ville + code postal
        parts = loc.split(',')
        for part in reversed(parts):
            part = part.strip()
            if any(c.isdigit() for c in part):
                lat2, lon2 = geocode(part)
                if lat2:
                    ev['latitude'] = lat2
                    ev['longitude'] = lon2
                    print(f"  ⚠️ {ev['title'][:45]} → {lat2:.4f}, {lon2:.4f} (fallback)")
                    break
        if 'latitude' not in ev:
            print(f"  ❌ {ev['title'][:45]} → ÉCHEC GÉOCODAGE")
    time.sleep(1.5)

# ============================================================
# PRÉPARER POUR L'API
# ============================================================
print(f"\n=== PRÉPARATION POUR L'API ===")

api_events = []
for ev in events_to_import:
    if 'latitude' not in ev:
        print(f"  Ignoré (pas de GPS): {ev['title'][:45]}")
        continue
    
    api_event = {
        'title': ev['title'],
        'description': ev['description'],
        'date': ev['start_date'],
        'end_date': ev.get('end_date'),
        'time': None,
        'end_time': None,
        'location': ev['location'],
        'latitude': ev['latitude'],
        'longitude': ev['longitude'],
        'categories': ev['categories'],
        'source_url': ev['source_url'],
        'organizer_name': ev.get('organizer_name', ''),
        'organizer_email': ev.get('organizer_email', ''),
        'validation_status': 'auto_validated',
    }
    api_events.append(api_event)

print(f"Événements prêts: {len(api_events)}")

# ============================================================
# IMPORT
# ============================================================
print(f"\n=== IMPORT ===")
resp = requests.post(f'{API_URL}/api/events/scraped/batch', 
                     json={'events': api_events}, timeout=30)
if resp.status_code == 200:
    result = resp.json()
    print(f"  ✅ Importés: {result.get('created', result.get('imported', '?'))}")
    if result.get('errors'):
        for err in result['errors'][:5]:
            print(f"    ⚠️ {err}")
else:
    print(f"  ❌ Erreur: {resp.status_code}")
    print(f"  {resp.text[:300]}")

# ============================================================
# VÉRIFICATION
# ============================================================
print(f"\n=== VÉRIFICATION FINALE ===")
r = requests.get(f'{API_URL}/api/events', timeout=30)
data = r.json()
events_final = data if isinstance(data, list) else data.get('events', [])
print(f"Total events: {len(events_final)}")

from urllib.parse import urlparse
sources = {}
regions = {'Valais': 0, 'Vaud': 0, 'Genève': 0, 'Autre': 0}
for ev in events_final:
    src = ev.get('source_url', '') or ''
    domain = urlparse(src).netloc if src else 'SANS_SOURCE'
    sources[domain] = sources.get(domain, 0) + 1
    loc = (ev.get('location', '') or '').lower()
    if any(x in loc for x in ['valais', 'sion', 'sierre', 'martigny', 'monthey', 'grimentz', 'champéry', 'nendaz', 'champoussin', 'troistorrents', 'saint-maurice', 'riddes', 'st-pierre-de-clages', 'grächen']):
        regions['Valais'] += 1
    elif any(x in loc for x in ['genève', 'carouge', 'saconnex', 'grand-saconnex', 'cologny', 'meyrin', 'veyrier', 'onex']):
        regions['Genève'] += 1
    elif any(x in loc for x in ['vaud', 'lausanne', 'montreux', 'nyon', 'vevey', 'morges', 'yverdon', 'les mosses', 'bonvillars', 'cully', 'canton de vaud']):
        regions['Vaud'] += 1
    else:
        regions['Autre'] += 1

print(f"\nPar région:")
for r, c in regions.items():
    print(f"  {r}: {c}")

print(f"\nNouvelles sources ajoutées:")
for domain, count in sorted(sources.items(), key=lambda x: -x[1]):
    print(f"  {domain}: {count}")
