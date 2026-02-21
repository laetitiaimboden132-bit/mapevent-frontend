"""
Import batch 5 - événements supplémentaires confirmés 2026.
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
    # VAUD
    # ═══════════════════════════════

    # Source: imagine-monet.ch → "11 mars au 28 juin 2026"
    # 200+ œuvres de Monet en projection 360°, réservation obligatoire
    {
        'title': 'Imagine Monet - Exposition immersive',
        'description': "Exposition immersive dédiée à Claude Monet à Beaulieu Lausanne. Plus de 200 œuvres projetées à 360° avec la technologie Image Totale. Parcours: entrée fleurie inspirée de Giverny, espace pédagogique, salle immersive de 30 minutes, espace InnerVision en avant-première mondiale et espace enfants.",
        'start_date': '2026-03-11',
        'end_date': '2026-06-28',
        'location': 'Beaulieu Lausanne, Avenue des Bergières 10, 1004 Lausanne, Vaud',
        'latitude': 46.5265,
        'longitude': 6.6195,
        'categories': ['Art et Culture > Exposition', 'Famille > Activités'],
        'source_url': 'https://imagine-monet.ch/',
        'organizer_name': 'Imagine Monet',
    },

    # Source: lausanneartfair.com → "7 au 10 mai 2026"
    # 8e édition, galeries internationales, peinture, sculpture, photographie
    {
        'title': 'Lausanne Art Fair 2026',
        'description': "8e édition de la foire internationale d'art contemporain à Beaulieu Lausanne. Galeries internationales présentant peinture, sculpture et photographie. Vernissage jeudi 18h. Adultes CHF 20, mineurs accompagnés gratuit.",
        'start_date': '2026-05-07',
        'end_date': '2026-05-10',
        'location': 'Beaulieu Lausanne, Hall 35A, Avenue des Bergières 10, 1004 Lausanne, Vaud',
        'latitude': 46.5265,
        'longitude': 6.6195,
        'categories': ['Art et Culture > Exposition', 'Art et Culture > Festival'],
        'source_url': 'https://www.lausanneartfair.com/',
        'organizer_name': 'Lausanne Art Fair',
    },

    # Source: em-l.ch + fetemusiquelausanne.ch → "21 juin 2026"
    # Gratuit, divers lieux à Lausanne, solstice d'été
    {
        'title': 'Fête de la Musique Lausanne 2026',
        'description': "Fête de la Musique à Lausanne le jour du solstice d'été. Concerts gratuits dans les rues, places, jardins publics et églises de la ville. Tous les genres musicaux représentés.",
        'start_date': '2026-06-21',
        'end_date': '2026-06-21',
        'location': 'Divers lieux, 1003 Lausanne, Vaud',
        'latitude': 46.5197,
        'longitude': 6.6323,
        'categories': ['Musique > Concert', 'Musique > Festival'],
        'source_url': 'https://fetemusiquelausanne.ch/',
        'organizer_name': 'Fête de la Musique Lausanne',
    },

    # ═══════════════════════════════
    # GENÈVE
    # ═══════════════════════════════

    # Source: gonetgenevaopen.com → "May 16-23, 2026"
    # ATP 250, terre battue, Tennis Club de Genève
    {
        'title': 'Gonet Geneva Open 2026',
        'description': "Tournoi de tennis ATP 250 sur terre battue au Tennis Club de Genève dans le Parc des Eaux-Vives. Une semaine de tennis professionnel au bord du Lac Léman.",
        'start_date': '2026-05-16',
        'end_date': '2026-05-23',
        'location': 'Tennis Club de Genève, Parc des Eaux-Vives, 1207 Genève',
        'latitude': 46.2022,
        'longitude': 6.1620,
        'categories': ['Sport > Terrestre'],
        'source_url': 'https://gonetgenevaopen.com/',
        'organizer_name': 'Gonet Geneva Open',
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
     'veytaux', 'chillon', 'lutry', 'gland', 'beaulieu lausanne', 'morges',
     'leysin']
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
