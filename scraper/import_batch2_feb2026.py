"""
Import batch 2 - événements supplémentaires confirmés 2026.
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
print(f"Events existants: {len(existing)}")

events_to_import = [

    # Source: autoxperience.ch → "5 au 8 mars 2026"
    # Confirmé sur geneve.ch, palexpo.ch. 2e édition, 240+ véhicules, 45 marques
    {
        'title': 'autoXpérience Genève 2026',
        'description': "2e édition du salon automobile à Palexpo. Plus de 240 véhicules de 45 marques, essais et démonstrations. Du jeudi au dimanche. Adultes CHF 13 sur place, CHF 10 en ligne.",
        'start_date': '2026-03-05',
        'end_date': '2026-03-08',
        'location': 'Palexpo, Route François-Peyrot 30, 1218 Le Grand-Saconnex, Genève',
        'latitude': 46.2342,
        'longitude': 6.1137,
        'categories': ['Art et Culture > Exposition'],
        'source_url': 'https://www.autoxperience.ch/',
        'organizer_name': 'UPSA Genève & Palexpo SA',
    },

    # Source: habitat-jardin.events → "12 au 15 mars 2026"
    # 150 exposants, 10000 m², 4 pôles conseils, 40 conférences
    {
        'title': 'Habitat-Jardin 2026',
        'description': "Salon de la construction, rénovation et aménagement à Beaulieu Lausanne. 150 exposants sur 10000 m², 4 pôles conseils (énergie, matériaux, sécurité, jardin) et 40 conférences.",
        'start_date': '2026-03-12',
        'end_date': '2026-03-15',
        'location': 'Beaulieu Lausanne, Avenue des Bergières 10, 1004 Lausanne, Vaud',
        'latitude': 46.5265,
        'longitude': 6.6195,
        'categories': ['Foire > Marché', 'Art et Culture > Exposition'],
        'source_url': 'https://www.habitat-jardin.events/',
        'organizer_name': 'Beaulieu Lausanne',
    },

    # Source: morges-tourisme.ch → "27 mars au 10 mai 2026"
    # 56e édition, 140000 fleurs, 350 variétés, thème "Contes et Légendes", entrée libre
    {
        'title': 'Fête de la Tulipe Morges 2026',
        'description': "56e édition de la Fête de la Tulipe au Parc de l'Indépendance et dans les rues de Morges. Plus de 140000 fleurs et environ 350 variétés de tulipes. Thème 2026: \"Contes et Légendes\". Entrée gratuite.",
        'start_date': '2026-03-27',
        'end_date': '2026-05-10',
        'location': "Parc de l'Indépendance, 1110 Morges, Vaud",
        'latitude': 46.5114,
        'longitude': 6.4980,
        'categories': ['Nature > Jardin', 'Famille > Activités'],
        'source_url': 'https://www.morges-tourisme.ch/fr/Z14689/fete-de-la-tulipe',
        'organizer_name': 'Morges Région Tourisme',
    },

    # Source: palexpo.ch/evenement/gemgeneve → "7 au 10 mai 2026"
    # Salon international gemmologie et joaillerie
    {
        'title': 'GemGenève 2026',
        'description': "Salon international de la gemmologie et de la joaillerie à Palexpo. Expositions de pierres précieuses, bijoux et objets d'art. Professionnels, créateurs, collectionneurs et passionnés.",
        'start_date': '2026-05-07',
        'end_date': '2026-05-10',
        'location': 'Palexpo, Route François-Peyrot 30, 1218 Le Grand-Saconnex, Genève',
        'latitude': 46.2342,
        'longitude': 6.1137,
        'categories': ['Art et Culture > Exposition', 'Foire > Marché'],
        'source_url': 'https://www.palexpo.ch/evenement/gemgeneve/',
        'organizer_name': 'GemGenève',
    },

    # Source: montreuxjazzfestival.com → "3 au 18 juillet 2026, 60e édition"
    # Dates MAINTENANT CONFIRMÉES sur le site officiel
    {
        'title': 'Montreux Jazz Festival 2026',
        'description': "60e édition du Montreux Jazz Festival. Deux semaines de concerts à l'Auditorium Stravinski et sur les scènes gratuites au bord du Lac Léman.",
        'start_date': '2026-07-03',
        'end_date': '2026-07-18',
        'location': 'Auditorium Stravinski, Rue du Théâtre 5, 1820 Montreux, Vaud',
        'latitude': 46.4349,
        'longitude': 6.9118,
        'categories': ['Musique > Jazz', 'Musique > Festival'],
        'source_url': 'https://www.montreuxjazzfestival.com/',
        'organizer_name': 'Montreux Jazz Festival',
    },
]

# Filtrer doublons
new_events = []
for ev in events_to_import:
    if ev['title'].lower().strip() not in existing_titles:
        new_events.append(ev)
        print(f"  + {ev['title']}")
    else:
        print(f"  DOUBLON: {ev['title']}")

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
