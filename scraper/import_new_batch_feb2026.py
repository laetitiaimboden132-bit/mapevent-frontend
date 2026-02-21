"""
Import de nouveaux événements confirmés 2026 - Batch février 2026
Chaque événement a été vérifié sur son site officiel.
Toutes les données proviennent DIRECTEMENT des pages source.
RIEN n'est inventé.
"""
import requests, sys, io, time

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'

# ============================================================
# Vérifier d'abord les events existants pour éviter les doublons
# ============================================================
print("=== Vérification des doublons ===")
r = requests.get(f'{API_URL}/api/events', timeout=30)
data = r.json()
existing = data if isinstance(data, list) else data.get('events', [])
existing_titles = set(e.get('title', '').lower().strip() for e in existing)
existing_sources = set((e.get('source_url', '') or '').lower().strip() for e in existing)
print(f"Events existants: {len(existing)}")

# ============================================================
# NOUVEAUX EVENTS CONFIRMÉS 2026
# ============================================================
events_to_import = [

    # ═══════════════════════════════
    # VALAIS (6 nouveaux)
    # ═══════════════════════════════

    # Source: zermatt-unplugged.ch → "April 7-11, 2026"
    # Confirmé aussi sur myswitzerland.com et valais.ch
    {
        'title': 'Zermatt Unplugged 2026',
        'description': "Festival de musique acoustique à Zermatt. Plus de 130 concerts sur 17 scènes différentes pendant 5 jours. Concerts sur la scène principale dès 20h30.",
        'start_date': '2026-04-07',
        'end_date': '2026-04-11',
        'location': 'Zermatt, 3920 Zermatt, Valais',
        'latitude': 46.0207,
        'longitude': 7.7491,
        'categories': ['Musique > Festival', 'Musique > Concert'],
        'source_url': 'https://zermatt-unplugged.ch/en/',
        'organizer_name': 'Zermatt Unplugged',
    },

    # Source: sierreblues.ch → "June 18 to 20, 2026, on the legendary Plaine Bellevue"
    # Artistes confirmés: Rag'n'Bone Man, Dogstar (Keanu Reeves), Paul Mac Bonvin
    {
        'title': 'Sierre Blues Festival 2026',
        'description': "17e édition du Sierre Blues Festival à Plaine Bellevue. Têtes d'affiche: Rag'n'Bone Man et Dogstar avec Keanu Reeves à la basse. Également Paul Mac Bonvin, Spoonful of Blues, Koko-Jean & The Tonics et DK Harrell.",
        'start_date': '2026-06-18',
        'end_date': '2026-06-20',
        'location': 'Plaine Bellevue, 3960 Sierre, Valais',
        'latitude': 46.2920,
        'longitude': 7.5350,
        'categories': ['Musique > Festival', 'Musique > Blues'],
        'source_url': 'https://www.sierreblues.ch/en/news/sierre-blues-festival-2026-568',
        'organizer_name': 'Sierre Blues Festival',
    },

    # Source: verbierfestival.com → "July 16 to August 2 2026, 33rd edition"
    # Programme complet publié, billetterie ouverte
    {
        'title': 'Verbier Festival 2026',
        'description': "33e édition du Verbier Festival. Plus de 60 concerts et 100 masterclasses gratuites en 18 jours. Artistes: Martha Argerich, Evgeny Kissin, Simon Rattle, Esa-Pekka Salonen, Janine Jansen, Joshua Bell. 3 opéras: La Traviata, Bluebeard's Castle, Così fan tutte.",
        'start_date': '2026-07-16',
        'end_date': '2026-08-02',
        'location': 'Salle des Combins, Verbier, 1936 Bagnes, Valais',
        'latitude': 46.0968,
        'longitude': 7.2286,
        'categories': ['Musique > Classique / Baroque', 'Musique > Festival'],
        'source_url': 'https://verbierfestival.com/en/annonce-programmation-et-ouverture-billetterie-2026-2/',
        'organizer_name': 'Fondation du Verbier Festival',
    },

    # Source: openairgampel.ch → "August 19-23, 2026"
    # Confirmé sur myswitzerland.com: jusqu'à 25000 par jour
    {
        'title': 'Open Air Gampel 2026',
        'description': "Festival rock à Gampel-Bratsch en Valais. Jusqu'à 25000 festivaliers par jour. Deux scènes principales, cinq tentes DJ, fête foraine, marché aux puces, stands de nourriture et camping gratuit.",
        'start_date': '2026-08-19',
        'end_date': '2026-08-23',
        'location': 'Gampel-Bratsch, 3945 Gampel, Valais',
        'latitude': 46.3170,
        'longitude': 7.7430,
        'categories': ['Musique > Festival', 'Musique > Rock / Pop'],
        'source_url': 'https://www.openairgampel.ch/en/home',
        'organizer_name': 'Open Air Gampel',
    },

    # Source: omegaeuropeanmasters.com → "September 3-6, 2026"
    # Tournoi du DP World Tour, organisé depuis 1939
    {
        'title': 'Omega European Masters 2026',
        'description': "Tournoi professionnel de golf du DP World Tour au Golf Club de Crans-sur-Sierre. L'un des tournois de golf les plus prestigieux d'Europe, organisé depuis 1939.",
        'start_date': '2026-09-03',
        'end_date': '2026-09-06',
        'location': 'Golf Club Crans-sur-Sierre, 3963 Crans-Montana, Valais',
        'latitude': 46.3070,
        'longitude': 7.4790,
        'categories': ['Sport > Terrestre'],
        'source_url': 'https://www.omegaeuropeanmasters.com/',
        'organizer_name': 'Omega European Masters',
    },

    # Source: foireduvalais.ch → "October 2-11, 2026"
    # 66e édition, confirmé aussi sur myswitzerland.com
    {
        'title': '66e Foire du Valais 2026',
        'description': "66e édition de la Foire du Valais à Martigny. L'une des plus importantes foires de Suisse romande. 10 jours de célébration de l'artisanat, des produits locaux et de la culture valaisanne.",
        'start_date': '2026-10-02',
        'end_date': '2026-10-11',
        'location': 'CERM, Rue du Forum 3, 1920 Martigny, Valais',
        'latitude': 46.1019,
        'longitude': 7.0724,
        'categories': ['Foire > Marché', 'Gastronomie > Gastronomie', 'Tradition > Folklore'],
        'source_url': 'https://foireduvalais.ch/',
        'organizer_name': 'Foire du Valais',
    },

    # ═══════════════════════════════
    # VAUD (10 nouveaux)
    # ═══════════════════════════════

    # Source: festivalsnyon.ch → "26 février au 1er mars 2026"
    {
        'title': 'Les Hivernales Festival 2026',
        'description': "Festival musical varié avec concerts gratuits et payants à Nyon et Gland. Accent sur la découverte musicale avec une approche sociale et environnementale.",
        'start_date': '2026-02-26',
        'end_date': '2026-03-01',
        'location': 'Divers lieux, Nyon et Gland, Vaud',
        'latitude': 46.3830,
        'longitude': 6.2394,
        'categories': ['Musique > Festival', 'Musique > Concert'],
        'source_url': 'https://festivalsnyon.ch/',
        'organizer_name': 'Les Hivernales',
    },

    # Source: chillon.ch → "21 mars 2026, 18h-23h"
    # Réservation obligatoire, dès 14 ans
    {
        'title': 'Médiéval Fantastique à Chillon',
        'description': "Nuit médiévale fantastique au Château de Chillon de 18h à 23h. Jeux de plateau, jeux de rôle, war games, cosplay et concerts inspirés du roi Arthur. Dès 14 ans, réservation obligatoire. CHF 22.- adulte.",
        'start_date': '2026-03-21',
        'end_date': '2026-03-21',
        'location': 'Château de Chillon, Avenue de Chillon 21, 1820 Veytaux, Vaud',
        'latitude': 46.4143,
        'longitude': 6.9274,
        'categories': ['Art et Culture > Spectacle', 'Famille > Activités'],
        'source_url': 'https://www.chillon.ch/monagenda/medieval-fantastique-a-chillon/',
        'organizer_name': 'Château de Chillon',
    },

    # Source: polymanga.com → "3-6 avril (Pâques) à Lausanne"
    # 20e édition, billets en vente
    {
        'title': 'Polymanga 2026',
        'description': "20e édition du festival manga, jeux vidéo et pop culture à Beaulieu Lausanne. Billets 1 jour et 4 jours en vente.",
        'start_date': '2026-04-03',
        'end_date': '2026-04-06',
        'location': 'Beaulieu Lausanne, Avenue des Bergières 10, 1004 Lausanne, Vaud',
        'latitude': 46.5265,
        'longitude': 6.6195,
        'categories': ['Art et Culture > Festival', 'Famille > Activités'],
        'source_url': 'https://www.polymanga.com/',
        'organizer_name': 'Polymanga',
    },

    # Source: cullyjazz.ch → "April 10-18, 2026"
    # 35 concerts payants, ~100 concerts gratuits
    {
        'title': 'Cully Jazz Festival 2026',
        'description': "35 concerts payants et environ 100 concerts gratuits dans le village viticole de Cully au bord du Lac Léman, en Lavaux. Jazz dans les caves à vin, sur la scène principale et dans des espaces intimistes.",
        'start_date': '2026-04-10',
        'end_date': '2026-04-18',
        'location': 'Cully, 1096 Cully, Vaud',
        'latitude': 46.4887,
        'longitude': 6.7297,
        'categories': ['Musique > Jazz', 'Musique > Festival'],
        'source_url': 'https://cullyjazz.ch/en/',
        'organizer_name': 'Cully Jazz Festival',
    },

    # Source: lausanne-tourisme.ch → "April 25-26, 2026"
    # 44e édition, 5km/10km/20km
    {
        'title': '20km de Lausanne 2026',
        'description': "44e édition. Plusieurs distances: 5 km, 10 km et 20 km, courses juniors, marche et Nordic walking. Parcours à travers Lausanne et le long du Lac Léman.",
        'start_date': '2026-04-25',
        'end_date': '2026-04-26',
        'location': 'Stade Pierre-de-Coubertin, 1007 Lausanne, Vaud',
        'latitude': 46.5222,
        'longitude': 6.6140,
        'categories': ['Sport > Course à pied', 'Sport > Terrestre'],
        'source_url': 'https://www.lausanne-tourisme.ch/en/event/the-lausanne-20km/',
        'organizer_name': '20km de Lausanne',
    },

    # Source: xtratraillavaux.ch → "30-31 mai 2026"
    # 10e anniversaire, 7 distances, bénéfices caritatifs
    {
        'title': 'Xtratrail Lavaux 2026',
        'description': "10e anniversaire du Xtratrail Lavaux. 7 distances de 1 km (enfants) à 50 km à travers les vignobles de Lavaux (UNESCO). Vues sur les Alpes et le Lac Léman. Bénéfices reversés à des œuvres caritatives.",
        'start_date': '2026-05-30',
        'end_date': '2026-05-31',
        'location': 'Collège du Grand-Pont, 1095 Lutry, Vaud',
        'latitude': 46.5033,
        'longitude': 6.6857,
        'categories': ['Sport > Terrestre', 'Sport > Course à pied'],
        'source_url': 'https://www.xtratraillavaux.ch/',
        'organizer_name': 'Xtratrail Lavaux',
    },

    # Source: lausanne.diamondleague.com → "21 August 2026"
    # Wanda Diamond League
    {
        'title': 'Athletissima 2026',
        'description': "Meeting international d'athlétisme du circuit Wanda Diamond League au Stade de la Pontaise à Lausanne.",
        'start_date': '2026-08-21',
        'end_date': '2026-08-21',
        'location': 'Stade Olympique de la Pontaise, 1018 Lausanne, Vaud',
        'latitude': 46.5418,
        'longitude': 6.6174,
        'categories': ['Sport > Terrestre'],
        'source_url': 'https://lausanne.diamondleague.com/',
        'organizer_name': 'Athletissima',
    },

    # Source: en.lausanne-marathon.com → "October 25, 2026"
    # 32e édition, marathon/semi/10km à travers Lavaux
    {
        'title': 'Lausanne Marathon 2026',
        'description': "32e édition. Marathon (42.195 km), semi-marathon et 10 km entre Lausanne et La Tour-de-Peilz à travers les vignobles de Lavaux (UNESCO) et le long du Lac Léman.",
        'start_date': '2026-10-25',
        'end_date': '2026-10-25',
        'location': 'Place Bellerive, Ouchy, 1006 Lausanne, Vaud',
        'latitude': 46.5088,
        'longitude': 6.6310,
        'categories': ['Sport > Course à pied', 'Sport > Terrestre'],
        'source_url': 'https://en.lausanne-marathon.com/',
        'organizer_name': 'Lausanne Marathon',
    },

    # Source: myswitzerland.com → "November 11-22, 2026"
    # Plus grand festival d'humour francophone
    {
        'title': 'Montreux Comedy Festival 2026',
        'description': "Le plus grand festival d'humour francophone de Suisse et d'Europe. Galas et spectacles avec humoristes confirmés et talents émergents à Montreux et Lausanne.",
        'start_date': '2026-11-11',
        'end_date': '2026-11-22',
        'location': 'Auditorium Stravinski, Rue du Théâtre 5, 1820 Montreux, Vaud',
        'latitude': 46.4349,
        'longitude': 6.9118,
        'categories': ['Art et Culture > Spectacle', 'Art et Culture > Festival'],
        'source_url': 'https://www.montreuxriviera.com/en/E1146/montreux-comedy',
        'organizer_name': 'Montreux Comedy Festival',
    },

    # Source: montreuxnoel.ch → "November 20 to December 24, 2026"
    {
        'title': 'Montreux Noël 2026',
        'description': "Marché de Noël au bord du Lac Léman à Montreux. Grande roue, Maison du Père Noël aux Rochers-de-Naye, Père Noël volant, stands d'artisans et restaurants sur les quais.",
        'start_date': '2026-11-20',
        'end_date': '2026-12-24',
        'location': 'Quai de Montreux, 1820 Montreux, Vaud',
        'latitude': 46.4346,
        'longitude': 6.9090,
        'categories': ['Foire > Marché', 'Famille > Fêtes', 'Gastronomie > Gastronomie'],
        'source_url': 'https://www.montreuxnoel.ch/',
        'organizer_name': 'Montreux Noël',
    },

    # ═══════════════════════════════
    # GENÈVE (1 nouveau)
    # ═══════════════════════════════

    # Source: traildugrandgeneve.ch → "31 mai 2026"
    # Départ Centre sportif de Vessy, arrivée Villa La Grange
    {
        'title': 'Trail du Grand Genève 2026',
        'description': "Trail entre Suisse et France. 4 distances: 8 km, 12 km, 25 km et 40 km avec option relais. Parcours entre le Lac Léman, le Salève, l'Arve et les vignes. Départ à Vessy, arrivée à la Villa La Grange.",
        'start_date': '2026-05-31',
        'end_date': '2026-05-31',
        'location': 'Centre sportif de Vessy, Route de Vessy 31, 1234 Vessy, Genève',
        'latitude': 46.1740,
        'longitude': 6.1690,
        'categories': ['Sport > Terrestre', 'Sport > Course à pied'],
        'source_url': 'https://traildugrandgeneve.ch/',
        'organizer_name': 'Trail du Grand Genève',
    },
]

# ============================================================
# FILTRER LES DOUBLONS
# ============================================================
print(f"\n=== FILTRAGE DES DOUBLONS ===")
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

print(f"\nEvents à importer (après filtrage): {len(new_events)}")

if not new_events:
    print("Aucun nouvel event à importer.")
    sys.exit(0)

# ============================================================
# PRÉPARER POUR L'API
# ============================================================
print(f"\n=== PRÉPARATION ===")
api_events = []
for ev in new_events:
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
    print(f"  + {ev['title']}")
    print(f"    {ev['start_date']} → {ev.get('end_date', '')} | {ev['location'][:60]}")

# ============================================================
# IMPORT
# ============================================================
print(f"\n=== IMPORT DE {len(api_events)} EVENTS ===")
resp = requests.post(f'{API_URL}/api/events/scraped/batch',
                     json={'events': api_events}, timeout=30)
if resp.status_code == 200:
    result = resp.json()
    created = result.get('created', result.get('imported', '?'))
    print(f"✅ Importés: {created}")
    if result.get('errors'):
        for err in result['errors'][:10]:
            print(f"  ⚠️ {err}")
else:
    print(f"❌ Erreur: {resp.status_code}")
    print(f"  {resp.text[:500]}")

# ============================================================
# VÉRIFICATION FINALE
# ============================================================
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
     'veytaux', 'chillon', 'lutry', 'gland', 'beaulieu lausanne']
geneve_kw = ['genève', 'geneva', 'meyrin', 'le grand-saconnex', 'saconnex', 'cologny',
     'plainpalais', 'onex', 'carouge', 'vessy']

valais = [e for e in scraped if any(v in (e.get('location', '') or '').lower() for v in valais_kw)]
vaud = [e for e in scraped if any(v in (e.get('location', '') or '').lower() for v in vaud_kw)]
geneve = [e for e in scraped if any(v in (e.get('location', '') or '').lower() for v in geneve_kw)]

print(f"\nTotal events scrapés: {len(scraped)}")
print(f"  Valais: {len(valais)}")
print(f"  Vaud: {len(vaud)}")
print(f"  Genève: {len(geneve)}")
print(f"  Autre: {len(scraped) - len(valais) - len(vaud) - len(geneve)}")
