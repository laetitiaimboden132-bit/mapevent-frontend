"""
Import batch 3 - événements supplémentaires confirmés 2026.
Chaque donnée provient DIRECTEMENT des sites officiels.
"""
import requests, sys, io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'

# Vérifier doublons
print("=== Vérification des doublons ===")
r = requests.get(f'{API_URL}/api/events', timeout=30)
data = r.json()
existing = data if isinstance(data, list) else data.get('events', [])
existing_titles = set(e.get('title', '').lower().strip() for e in existing)
existing_sources = set((e.get('source_url', '') or '').lower().strip() for e in existing)
print(f"Events existants: {len(existing)}")

events_to_import = [

    # ═══════════════════════════════
    # VALAIS
    # ═══════════════════════════════

    # Source: artderuesion.ch → "5 et 6 juin 2026"
    # 26e édition, gratuit, vieille ville de Sion
    {
        'title': "Festival d'Art de Rue de Sion 2026",
        'description': "26e édition du Festival d'Art de Rue au cœur de la vieille ville de Sion. Spectacles de rue gratuits avec artistes rémunérés. Chaque premier vendredi et samedi de juin depuis 1999.",
        'start_date': '2026-06-05',
        'end_date': '2026-06-06',
        'location': 'Vieille ville de Sion, 1950 Sion, Valais',
        'latitude': 46.2333,
        'longitude': 7.3597,
        'categories': ['Art et Culture > Spectacle', 'Art et Culture > Festival'],
        'source_url': 'https://artderuesion.ch/',
        'organizer_name': "Festival d'Art de Rue de Sion",
    },

    # Source: verbier.utmb.world → "10-12 juillet 2026"
    # 17e édition, 4 courses: X-Alpine 140km, X-Traversée 76km, Marathon 43km, X-Plore 28km
    {
        'title': 'Trail Verbier Saint-Bernard by UTMB 2026',
        'description': "17e édition du plus ancien ultra-trail de Suisse. 4 courses: X-Alpine (140 km, 9300m D+), X-Traversée (76 km), Marathon (43 km) et X-Plore (28 km). Parcours entre Verbier, le Grand Saint-Bernard et les vallées de Bagnes, Ferret et Entremont.",
        'start_date': '2026-07-10',
        'end_date': '2026-07-12',
        'location': "Place de l'Ermitage, Verbier, 1936 Bagnes, Valais",
        'latitude': 46.0968,
        'longitude': 7.2286,
        'categories': ['Sport > Terrestre', 'Sport > Course à pied'],
        'source_url': 'https://verbier.utmb.world/fr',
        'organizer_name': 'Trail Verbier Saint-Bernard by UTMB',
    },

    # Source: sionsouslesetoiles.ch → "16 au 18 juillet 2026"
    # Programme: Julien Doré, Christophe Maé, GIMS, Louane, Star Academy Tour, Superbus
    {
        'title': 'Sion sous les étoiles 2026',
        'description': "11e édition de Sion sous les étoiles à la Plaine du Tourbillon. Programmation: Julien Doré, Christophe Maé, Vitaa, GIMS, Louane, Star Academy Tour 2026, Superbus, Umberto Tozzi.",
        'start_date': '2026-07-16',
        'end_date': '2026-07-18',
        'location': 'Plaine du Tourbillon, 1950 Sion, Valais',
        'latitude': 46.2324,
        'longitude': 7.3710,
        'categories': ['Musique > Concert', 'Musique > Festival'],
        'source_url': 'https://sionsouslesetoiles.ch/programmation/',
        'organizer_name': 'Sion sous les étoiles',
    },

    # Source: sion-festival.ch → "21 août au 6 septembre 2026"
    # 62e édition, festival de musique classique
    {
        'title': 'Sion Festival 2026',
        'description': "62e édition du Sion Festival, festival international de musique classique.",
        'start_date': '2026-08-21',
        'end_date': '2026-09-06',
        'location': 'Sion, 1950 Sion, Valais',
        'latitude': 46.2333,
        'longitude': 7.3597,
        'categories': ['Musique > Classique / Baroque', 'Musique > Festival'],
        'source_url': 'https://sion-festival.ch/',
        'organizer_name': 'Sion Festival',
    },

    # Source: festivaldumariagevalais.ch → "10 au 12 avril 2026"
    # 5e édition, Pavillon des Mangettes, Monthey, entrée gratuite
    {
        'title': 'Festival du Mariage Valais 2026',
        'description': "5e édition du Festival du Mariage Valais au Pavillon des Mangettes à Monthey. Entrée gratuite. Plus de 30 exposants, mini-conférences, mini-ateliers et défilés de mode.",
        'start_date': '2026-04-10',
        'end_date': '2026-04-12',
        'location': 'Pavillon des Mangettes, 1870 Monthey, Valais',
        'latitude': 46.2536,
        'longitude': 6.9556,
        'categories': ['Foire > Marché', 'Famille > Fêtes'],
        'source_url': 'https://festivaldumariagevalais.ch/',
        'organizer_name': 'Festival du Mariage Valais',
    },

    # ═══════════════════════════════
    # VAUD
    # ═══════════════════════════════

    # Source: montreux-trail.ch → "24-26 juillet 2026"
    # 9e édition, 6 courses dont MXTREME 100km, MXALPS 66km, MXSKY 30km
    {
        'title': 'Montreux Trail Festival 2026',
        'description': "9e édition du Montreux Trail Festival. 6 courses sur sentiers 100% non pavés: MXTREME (100 km), MXALPS (66 km), MXSKY (30 km), Freddie's Night (15 km), MXFAMILY (relais) et MXKIDS (2 km).",
        'start_date': '2026-07-24',
        'end_date': '2026-07-26',
        'location': 'Montreux, 1820 Montreux, Vaud',
        'latitude': 46.4312,
        'longitude': 6.9105,
        'categories': ['Sport > Terrestre', 'Sport > Course à pied'],
        'source_url': 'https://www.montreux-trail.ch/',
        'organizer_name': 'Montreux Trail Festival',
    },

    # Source: mescavesouvertes.ch → "23 et 24 mai 2026"
    # Plus de 250 caves vaudoises, ticket ~20 CHF avec transports inclus
    {
        'title': 'Caves Ouvertes Vaudoises 2026',
        'description': "Plus de 250 caves vaudoises ouvrent leurs portes pour des dégustations. Le billet inclut un verre de dégustation, des vouchers et les transports publics gratuits dans les zones Mobilis.",
        'start_date': '2026-05-23',
        'end_date': '2026-05-24',
        'location': 'Vignobles du canton de Vaud, Vaud',
        'latitude': 46.4887,
        'longitude': 6.7297,
        'categories': ['Gastronomie > Vin', 'Gastronomie > Gastronomie'],
        'source_url': 'https://www.mescavesouvertes.ch/',
        'organizer_name': 'Union des Vignerons du Canton de Vaud',
    },

    # ═══════════════════════════════
    # GENÈVE
    # ═══════════════════════════════

    # Source: generaligenevemarathon.com → "May 9-10, 2026"
    # 20e édition, départ Cologny, arrivée Jet d'Eau
    # (re-check si déjà en DB - le script gère les doublons)
    {
        'title': 'Generali Marathon de Genève 2026',
        'description': "20e édition du Marathon de Genève. Départ dans les vignobles de Cologny, arrivée au Jet d'Eau. Marathon, semi-marathon, 10 km, 5 km et marche/Nordic walking.",
        'start_date': '2026-05-09',
        'end_date': '2026-05-10',
        'location': 'Quai Gustave-Ador, 1207 Genève',
        'latitude': 46.2022,
        'longitude': 6.1580,
        'categories': ['Sport > Course à pied', 'Sport > Terrestre'],
        'source_url': 'https://www.generaligenevemarathon.com/en',
        'organizer_name': 'Generali Marathon de Genève',
    },
]

# Filtrer doublons
new_events = []
for ev in events_to_import:
    title_lower = ev['title'].lower().strip()
    source_lower = (ev.get('source_url', '') or '').lower().strip()
    
    is_dup = False
    if title_lower in existing_titles:
        print(f"  DOUBLON (titre): {ev['title']}")
        is_dup = True
    elif source_lower and source_lower in existing_sources:
        print(f"  DOUBLON (source): {ev['title']}")
        is_dup = True
    
    if not is_dup:
        new_events.append(ev)
        print(f"  + {ev['title']} ({ev['start_date']})")

if not new_events:
    print("\nAucun nouvel event.")
    sys.exit(0)

# Préparer API
api_events = []
for ev in new_events:
    api_events.append({
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
        'organizer_email': '',
        'validation_status': 'auto_validated',
    })

# Import
print(f"\n=== IMPORT DE {len(api_events)} EVENTS ===")
resp = requests.post(f'{API_URL}/api/events/scraped/batch',
                     json={'events': api_events}, timeout=30)
if resp.status_code == 200:
    result = resp.json()
    print(f"✅ Importés: {result.get('created', result.get('imported', '?'))}")
else:
    print(f"❌ Erreur: {resp.status_code} - {resp.text[:300]}")

# État final
print(f"\n=== ÉTAT FINAL ===")
r = requests.get(f'{API_URL}/api/events', timeout=30)
data = r.json()
events_final = data if isinstance(data, list) else data.get('events', [])
scraped = [e for e in events_final if e.get('source_url')]

valais_kw = ['valais', 'sierre', 'monthey', 'sion', 'martigny', 'champéry', 'morgins',
     'troistorrents', 'anniviers', 'grimentz', 'nendaz', 'aproz', 'grächen',
     'bagnes', 'port-valais', 'bouveret', 'verbier', 'zermatt', 'gampel',
     'crans-montana', 'visp', 'brig']
vaud_kw = ['vaud', 'lausanne', 'vevey', 'nyon', 'montreux', 'cully', "l'abbaye",
     'bonvillars', 'les mosses', 'diablerets', 'crans-près-céligny', 'céligny',
     'veytaux', 'chillon', 'lutry', 'gland', 'beaulieu lausanne', 'morges']
geneve_kw = ['genève', 'geneva', 'meyrin', 'le grand-saconnex', 'saconnex', 'cologny',
     'plainpalais', 'onex', 'carouge', 'vessy', 'palexpo']

valais = [e for e in scraped if any(v in (e.get('location', '') or '').lower() for v in valais_kw)]
vaud = [e for e in scraped if any(v in (e.get('location', '') or '').lower() for v in vaud_kw)]
geneve = [e for e in scraped if any(v in (e.get('location', '') or '').lower() for v in geneve_kw)]

print(f"\nTotal events scrapés: {len(scraped)}")
print(f"  Valais: {len(valais)}")
print(f"  Vaud: {len(vaud)}")
print(f"  Genève: {len(geneve)}")
print(f"  Autre: {len(scraped) - len(valais) - len(vaud) - len(geneve)}")
