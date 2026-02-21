"""
Import batch 4 - derniers événements confirmés 2026.
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

    # Source: tourderomandie.ch → "28 avril - 3 mai 2026"
    # 6 étapes, 853.8 km, 14193m D+. Étape à Martigny (Valais).
    {
        'title': 'Tour de Romandie 2026',
        'description': "Course cycliste professionnelle à travers la Suisse romande. 6 étapes pour 853.8 km et 14193 m de dénivelé. Prologue à Villars-sur-Glâne, étapes par Martigny, Rue, Orbe, étape reine Broc-Charmey, arrivée à Leysin.",
        'start_date': '2026-04-28',
        'end_date': '2026-05-03',
        'location': 'Leysin, 1854 Leysin, Vaud',
        'latitude': 46.3414,
        'longitude': 7.0059,
        'categories': ['Sport > Terrestre'],
        'source_url': 'https://tdr26.ch/',
        'organizer_name': 'Tour de Romandie',
    },

    # Source: mescavesouvertes.ch / montreuxriviera.com → "28 juin au 30 août 2026"
    # Tous les samedis, Grande Place et Place de l'Hôtel de Ville, plus de 40 ans
    {
        'title': 'Marchés Folkloriques Vevey 2026',
        'description': "Marchés folkloriques traditionnels à Vevey, chaque samedi de 10h à 13h du 28 juin au 30 août 2026. Produits du terroir, musique folklorique, danseurs traditionnels, cors des Alpes et dégustations de vins Lavaux et Chablais. Plus de 40 ans de tradition.",
        'start_date': '2026-06-28',
        'end_date': '2026-08-30',
        'location': 'Grande Place, 1800 Vevey, Vaud',
        'latitude': 46.4617,
        'longitude': 6.8430,
        'categories': ['Tradition > Folklore', 'Gastronomie > Vin', 'Foire > Marché'],
        'source_url': 'https://www.montreuxriviera.com/fr/E1083/marches-folkloriques-vevey-la-tour',
        'organizer_name': 'Marchés Folkloriques Vevey',
    },

    # Source: nyonstreetfoodfest.ch → "20 au 23 août 2026"
    # Près de 40 food trucks, entrée gratuite
    {
        'title': 'Nyon Street Food Festival 2026',
        'description': "Près de 40 food trucks et stands proposant des recettes du monde avec des produits locaux, vins, bières et cocktails du terroir. Entrée gratuite. Après une année de pause.",
        'start_date': '2026-08-20',
        'end_date': '2026-08-23',
        'location': 'Quai de Rive, 1260 Nyon, Vaud',
        'latitude': 46.3804,
        'longitude': 6.2382,
        'categories': ['Gastronomie > Gastronomie', 'Foire > Marché'],
        'source_url': 'https://www.nyonstreetfoodfest.ch/',
        'organizer_name': 'Nyon Street Food Festival',
    },

    # Source: images.ch → "5 au 27 septembre 2026"
    # 10e édition, gratuit, en plein air
    {
        'title': 'Biennale Images Vevey 2026',
        'description': "10e édition de la plus importante Biennale d'arts visuels de Suisse. Expositions de photographie en plein air dans les rues, parcs, façades, musées et galeries de Vevey. Entrée gratuite. Festival international de photographie contemporaine.",
        'start_date': '2026-09-05',
        'end_date': '2026-09-27',
        'location': 'Rues et parcs de Vevey, 1800 Vevey, Vaud',
        'latitude': 46.4617,
        'longitude': 6.8430,
        'categories': ['Art et Culture > Exposition', 'Art et Culture > Festival'],
        'source_url': 'https://www.images.ch/en/biennale/',
        'organizer_name': 'Images Vevey',
    },

    # ═══════════════════════════════
    # VALAIS
    # ═══════════════════════════════

    # Source: ultratourmonterosa.com → "2-5 septembre 2026"
    # Grächen, 4 courses: Stage Race, UTMR 170, Mischabel 60, Grächen Berglauf
    {
        'title': 'Ultra Tour Monte Rosa 2026',
        'description': "Ultra-trail au pied du Mont Rose à Grächen. 4 épreuves: UTMR Stage Race (4 étapes), UTMR 170 km, Mischabel 60 et Grächen Berglauf.",
        'start_date': '2026-09-02',
        'end_date': '2026-09-05',
        'location': 'Grächen, 3925 Grächen, Valais',
        'latitude': 46.1940,
        'longitude': 7.8380,
        'categories': ['Sport > Terrestre', 'Sport > Course à pied'],
        'source_url': 'https://www.ultratourmonterosa.com/fr/',
        'organizer_name': 'Ultra Tour Monte Rosa',
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

# État final détaillé
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

# Liste par source unique
sources = {}
for e in scraped:
    src = (e.get('source_url', '') or '')
    domain = src.split('/')[2] if src.count('/') >= 2 else 'inconnu'
    sources[domain] = sources.get(domain, 0) + 1

print(f"\n=== SOURCES ({len(sources)} sites) ===")
for domain, count in sorted(sources.items(), key=lambda x: -x[1]):
    print(f"  {domain}: {count}")
