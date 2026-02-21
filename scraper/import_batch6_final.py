"""
Import batch 6 (final) - derniers événements confirmés 2026.
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

    # Source: beaulieu-lausanne.com → "February 20-22, 2026"
    # 3 spectacles, CHF 77-193
    {
        'title': 'Shen Yun 2026 - Lausanne',
        'description': "Spectacle de danse classique chinoise à Beaulieu Lausanne. 3 représentations: vendredi 20 et samedi 21 février à 19h30, dimanche 22 février à 15h. Durée: 2h15 avec entracte.",
        'start_date': '2026-02-20',
        'end_date': '2026-02-22',
        'location': 'Théâtre de Beaulieu, Avenue des Bergières 10, 1004 Lausanne, Vaud',
        'latitude': 46.5265,
        'longitude': 6.6195,
        'categories': ['Art et Culture > Spectacle'],
        'source_url': 'https://beaulieu-lausanne.com/en/calendar/shen-yun-2026/',
        'organizer_name': 'Shen Yun Performing Arts',
    },

    # Source: finishers.com → "14 mars 2026"
    # 24e édition, 4 distances + relais, Dardagny/Genève
    {
        'title': 'Run Evasion Rhône 2026',
        'description': "24e édition du trail Run Evasion Rhône. 4 distances: 9 km, 15 km, 24 km et 48 km, plus un relais 24 km. Parcours dans la campagne genevoise entre vignes et bords du Rhône.",
        'start_date': '2026-03-14',
        'end_date': '2026-03-14',
        'location': 'Dardagny, 1283 Dardagny, Genève',
        'latitude': 46.1912,
        'longitude': 6.0080,
        'categories': ['Sport > Terrestre', 'Sport > Course à pied'],
        'source_url': 'https://www.finishers.com/en/event/run-evasion-rhone',
        'organizer_name': 'Run Evasion',
    },

    # Source: 20kmgeneve.com → "1er novembre 2026"
    # 8000+ coureurs, 20km/10km/relais/marche/juniors
    {
        'title': 'Balexert 20km de Genève 2026',
        'description': "Course populaire de Genève avec plus de 8000 coureurs. Formats: 20 km, 10 km, relais, marche, Nordic walking et courses juniors. Pré-inscriptions ouvertes.",
        'start_date': '2026-11-01',
        'end_date': '2026-11-01',
        'location': 'Genève',
        'latitude': 46.2044,
        'longitude': 6.1432,
        'categories': ['Sport > Course à pied', 'Sport > Terrestre'],
        'source_url': 'https://www.20kmgeneve.com/',
        'organizer_name': 'Balexert 20km de Genève',
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

print(f"\n=== IMPORT DE {len(api_events)} EVENTS ===")
resp = requests.post(f'{API_URL}/api/events/scraped/batch',
                     json={'events': api_events}, timeout=30)
if resp.status_code == 200:
    result = resp.json()
    print(f"✅ Importés: {result.get('created', result.get('imported', '?'))}")
else:
    print(f"❌ Erreur: {resp.status_code} - {resp.text[:300]}")

# État final complet
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
     'veytaux', 'chillon', 'lutry', 'gland', 'beaulieu lausanne', 'morges',
     'leysin']
geneve_kw = ['genève', 'geneva', 'meyrin', 'le grand-saconnex', 'saconnex', 'cologny',
     'plainpalais', 'onex', 'carouge', 'vessy', 'palexpo', 'dardagny']

valais = [e for e in scraped if any(v in (e.get('location', '') or '').lower() for v in valais_kw)]
vaud = [e for e in scraped if any(v in (e.get('location', '') or '').lower() for v in vaud_kw)]
geneve = [e for e in scraped if any(v in (e.get('location', '') or '').lower() for v in geneve_kw)]

print(f"\nTotal events scrapés: {len(scraped)}")
print(f"  Valais: {len(valais)}")
print(f"  Vaud: {len(vaud)}")
print(f"  Genève: {len(geneve)}")
print(f"  Autre: {len(scraped) - len(valais) - len(vaud) - len(geneve)}")
print(f"\n=== 100 events atteint ? {'OUI ✅' if len(scraped) >= 100 else 'Non, ' + str(100 - len(scraped)) + ' manquants'} ===")
