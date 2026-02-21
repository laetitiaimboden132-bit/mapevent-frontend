"""
Ré-import des events supprimés à tort dont les dates 2026 sont CONFIRMÉES
sur leurs sites source respectifs.

Chaque event a été vérifié manuellement sur son site officiel.
Toutes les données (dates, descriptions, adresses) proviennent DIRECTEMENT des pages source.
"""
import requests, sys, io, time

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'

# ============================================================
# 11 EVENTS CONFIRMÉS 2026 - données vérifiées sur les sites
# ============================================================
events_to_import = [

    # ─── 1. ANTIGEL FESTIVAL ───
    # Source: antigel.ch → "16ème édition du 5 au 28 février 2026, Genève"
    # Artistes confirmés sur le site: Sébastien Tellier, Sofiane Pamart, Odezenne,
    # Anna von Hausswolff, Israel Galván, Earl Sweatshirt, Jeff Tweedy, Tamino, etc.
    {
        'title': 'Antigel Festival 2026',
        'description': "16ème édition du festival Antigel à Genève. Programmation éclectique dans divers lieux genevois avec Sébastien Tellier, Sofiane Pamart, Odezenne, Anna von Hausswolff, Israel Galván, Earl Sweatshirt, Jeff Tweedy, Tamino et de nombreux autres artistes.",
        'start_date': '2026-02-05',
        'end_date': '2026-02-28',
        'location': 'Divers lieux, Genève',
        'latitude': 46.2103,
        'longitude': 6.1498,
        'categories': ['Musique > Festival'],
        'source_url': 'https://antigel.ch/',
        'organizer_name': 'Festival Antigel',
    },

    # ─── 2. COMBAT DE REINES - FINALE NATIONALE ───
    # Source: raceherens.ch + lenouvelliste.ch
    # "Finale nationale 2026 à Aproz les 9 et 10 mai"
    # Organisé par les syndicats d'élevage du Haut-Valais, ~13000 spectateurs
    {
        'title': 'Finale nationale des Combats de reines 2026',
        'description': "Finale nationale des combats de reines de la race d'Hérens à Aproz. Plus de 200 bêtes s'affrontent sous les yeux de milliers de spectateurs. Organisé par les syndicats d'élevage de la race d'Hérens du Haut-Valais.",
        'start_date': '2026-05-09',
        'end_date': '2026-05-10',
        'location': 'Arène de Praz-Bardi, Aproz, 1994 Nendaz, Valais',
        'latitude': 46.2186,
        'longitude': 7.3330,
        'categories': ['Tradition > Folklore'],
        'source_url': 'https://www.raceherens.ch/fr/news/2025/combats/tour-2026-359327',
        'organizer_name': 'Fédération Suisse de la Race d\'Hérens',
    },

    # ─── 3. NUIT DES MUSÉES GENÈVE ───
    # Source: nuitdesmusees-geneve.ch → "30 mai 2026"
    # ~21000 entrées en 2025
    {
        'title': 'Nuit des Musées Genève 2026',
        'description': "La Nuit des Musées invite le public à découvrir les musées genevois de nuit avec des animations, expositions et événements spéciaux dans de nombreux musées de la ville.",
        'start_date': '2026-05-30',
        'end_date': '2026-05-30',
        'location': 'Divers musées, Genève',
        'latitude': 46.1988,
        'longitude': 6.1528,
        'categories': ['Art et Culture > Exposition'],
        'source_url': 'https://nuitdesmusees-geneve.ch/',
        'organizer_name': 'Nuit des Musées Genève',
    },

    # ─── 4. BOL D'OR DU LÉMAN ───
    # Source: bouveret.ch → "5, 6 et 7 juin 2026"
    # ~500 voiliers, 123 km de parcours, plus grande régate en bassin fermé
    {
        'title': 'Bol d\'Or du Léman 2026',
        'description': "La plus importante régate du monde en bassin fermé. Environ 500 voiliers traversent le Lac Léman de Genève au Bouveret et retour, soit environ 123 km de parcours.",
        'start_date': '2026-06-05',
        'end_date': '2026-06-07',
        'location': 'Société Nautique de Genève, Port-Noir, 1223 Cologny, Genève',
        'latitude': 46.2078,
        'longitude': 6.1647,
        'categories': ['Sport > Aquatique'],
        'source_url': 'https://www.bouveret.ch/fr/bol-d-or-du-leman-2026-2411/',
        'organizer_name': 'Société Nautique de Genève',
    },

    # ─── 5. CARIBANA FESTIVAL ───
    # Source: caribana-festival.ch → "17 — 20 juin 2026 | Crans, Suisse"
    # Artistes: Mika, Niska, Lost Frequencies, Louane, Purple Disco Machine,
    # Soolking, Etienne de Crécy, KeBlack, Trinix, etc.
    {
        'title': 'Caribana Festival 2026',
        'description': "Festival musical au bord du Lac Léman à Crans-près-Céligny. Programmation 2026 avec Mika, Niska, Lost Frequencies, Louane, Purple Disco Machine, Soolking et de nombreux artistes sur trois scènes.",
        'start_date': '2026-06-17',
        'end_date': '2026-06-20',
        'location': 'Plage de Crans-près-Céligny, Route Suisse 16, 1299 Crans-près-Céligny, Vaud',
        'latitude': 46.3719,
        'longitude': 6.1862,
        'categories': ['Musique > Festival', 'Musique > Rock / Pop', 'Musique > Electro / DJ'],
        'source_url': 'https://www.caribana-festival.ch/fr',
        'organizer_name': 'Caribana Festival',
    },

    # ─── 6. FÊTE DE LA MUSIQUE GENÈVE ───
    # Source: ville-ge.ch/fetedelamusique → "19, 20 et 21 juin 2026"
    # Gratuit, depuis 1992
    {
        'title': 'Fête de la Musique Genève 2026',
        'description': "Événement gratuit célébrant la musique dans toute la ville de Genève. Depuis 1992, la Fête de la Musique propose des concerts et animations sur de nombreuses scènes en plein air à travers toute la ville.",
        'start_date': '2026-06-19',
        'end_date': '2026-06-21',
        'location': 'Divers lieux en plein air, Genève',
        'latitude': 46.2044,
        'longitude': 6.1432,
        'categories': ['Musique > Festival', 'Musique > Concert'],
        'source_url': 'https://www.ville-ge.ch/fetedelamusique/',
        'organizer_name': 'Ville de Genève',
    },

    # ─── 7. TRIATHLON DE GENÈVE ───
    # Source: genevetriathlon.ch → "4 & 5 JUILLET 2026"
    # Inscriptions 2026 déjà ouvertes, 6 formats de course
    {
        'title': 'Genève Triathlon 2026',
        'description': "Le Genève Triathlon propose six formats de course adaptés à tous les niveaux : Découverte, Short, Standard, Half, en solo ou en relais, plus des courses Juniors pour les 6-13 ans. Parcours au cœur de la rade de Genève avec natation dans le Lac Léman, vélo en ville et course à pied le long du lac.",
        'start_date': '2026-07-04',
        'end_date': '2026-07-05',
        'location': 'Plage des Eaux-Vives, Genève',
        'latitude': 46.2022,
        'longitude': 6.1643,
        'categories': ['Sport > Terrestre', 'Sport > Aquatique'],
        'source_url': 'https://www.genevetriathlon.ch/',
        'organizer_name': 'Genève Triathlon',
    },

    # ─── 8. SWISS PEAKS TRAIL ───
    # Source: swisspeaks.ch → "25 août au 6 septembre 2026"
    # Inscriptions ouvertes, parcours de 10 à 700 km
    {
        'title': 'Swiss Peaks Trail 2026',
        'description': "Ultra-trail mythique au cœur des Alpes suisses. Parcours de 10 à 700 km entre lac et sommets, des rives du Léman aux glaciers du Valais. Inscriptions ouvertes pour la Discovery (10 km), Marathon, 70K, 100K, 170K, 380K et la légendaire 700K.",
        'start_date': '2026-08-25',
        'end_date': '2026-09-06',
        'location': 'Le Bouveret, 1897 Port-Valais, Valais',
        'latitude': 46.3487,
        'longitude': 6.8570,
        'categories': ['Sport > Terrestre', 'Sport > Course à pied'],
        'source_url': 'https://swisspeaks.ch/',
        'organizer_name': 'Swiss Peaks Trail',
    },

    # ─── 9. FESTIVAL DE LA BÂTIE ───
    # Source: batie.ch → "La Bâtie-Festival de Genève 2026 dès le 26 août"
    # Festival multidisciplinaire
    {
        'title': 'La Bâtie-Festival de Genève 2026',
        'description': "Festival multidisciplinaire de Genève proposant des spectacles de théâtre, danse, musique et arts visuels dans divers lieux de la ville. Nouveau directeur Stéphane Malfettes pour cette édition.",
        'start_date': '2026-08-26',
        'end_date': '2026-09-12',
        'location': 'Bâtiment des Forces Motrices, Place des Volontaires 2, 1204 Genève',
        'latitude': 46.2013,
        'longitude': 6.1399,
        'categories': ['Art et Culture > Spectacle', 'Musique > Festival'],
        'source_url': 'https://www.batie.ch/fr/interedition',
        'organizer_name': 'La Bâtie-Festival de Genève',
    },

    # ─── 10. JOURNÉES DU PATRIMOINE ───
    # Source: decouvrir-le-patrimoine.ch → "12 et 13 septembre 2026"
    # Thème 2026: "En péril ?"
    {
        'title': 'Journées européennes du patrimoine Genève 2026',
        'description': "Les Journées européennes du patrimoine 2026 ont pour thème \"En péril ?\". Elles mettent en lumière les menaces pesant sur le patrimoine culturel : bâtiments historiques menacés de démolition, découvertes archéologiques oubliées et traditions artisanales supplantées par les techniques modernes.",
        'start_date': '2026-09-12',
        'end_date': '2026-09-13',
        'location': 'Divers lieux patrimoniaux, Genève',
        'latitude': 46.2013,
        'longitude': 6.1486,
        'categories': ['Art et Culture > Patrimoine'],
        'source_url': 'https://decouvrir-le-patrimoine.ch/2026/',
        'organizer_name': 'Journées européennes du patrimoine',
    },

    # ─── 11. SOIRÉE FONDUE ET LUGE NOCTURNE ───
    # Source: lesmazots.ch → "du 25 décembre 2025 au 19 mars 2026, tous les jeudis"
    # 7.2 km de piste de luge, fondue au sommet
    {
        'title': 'Soirée Fondue et Luge nocturne aux Diablerets',
        'description': "Descente de la plus longue piste de luge de Suisse (7.2 km) en nocturne avec lampe frontale, précédée d'une fondue au fromage suisse au sommet. Tous les jeudis de 18h30 à 21h00 du 25 décembre au 19 mars 2026.",
        'start_date': '2025-12-25',
        'end_date': '2026-03-19',
        'location': 'Les Mazots, Col du Pillon, 1865 Les Diablerets, Vaud',
        'latitude': 46.3357,
        'longitude': 7.2033,
        'categories': ['Gastronomie > Fondue', 'Sport > Glisse', 'Famille > Activités'],
        'source_url': 'https://lesmazots.ch/',
        'organizer_name': 'Les Mazots - Les Diablerets',
    },
]

# ============================================================
# PRÉPARER POUR L'API
# ============================================================
print(f"=== IMPORT DE {len(events_to_import)} EVENTS CONFIRMÉS 2026 ===\n")

api_events = []
for ev in events_to_import:
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
    print(f"  Prêt: {ev['title']}")
    print(f"         Dates: {ev['start_date']} → {ev.get('end_date', '')}")
    print(f"         Lieu: {ev['location']}")
    print(f"         GPS: {ev['latitude']:.4f}, {ev['longitude']:.4f}")
    print(f"         Source: {ev['source_url']}")
    print()

# ============================================================
# IMPORT BATCH
# ============================================================
print(f"=== ENVOI À L'API ===")
resp = requests.post(f'{API_URL}/api/events/scraped/batch',
                     json={'events': api_events}, timeout=30)
if resp.status_code == 200:
    result = resp.json()
    created = result.get('created', result.get('imported', '?'))
    print(f"✅ Importés: {created} events")
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

print(f"Total events scrapés: {len(scraped)}")

# Compter par région
valais = [e for e in scraped if any(v in (e.get('location', '') or '').lower() for v in
    ['valais', 'sierre', 'monthey', 'sion', 'martigny', 'champéry', 'morgins',
     'troistorrents', 'anniviers', 'grimentz', 'nendaz', 'aproz', 'grächen',
     'bagnes', 'port-valais', 'bouveret'])]
vaud = [e for e in scraped if any(v in (e.get('location', '') or '').lower() for v in
    ['vaud', 'lausanne', 'vevey', 'nyon', 'montreux', 'cully', "l'abbaye",
     'bonvillars', 'les mosses', 'diablerets', 'crans-près-céligny', 'céligny'])]
geneve = [e for e in scraped if any(v in (e.get('location', '') or '').lower() for v in
    ['genève', 'geneva', 'meyrin', 'le grand-saconnex', 'saconnex', 'cologny',
     'plainpalais', 'onex', 'carouge'])]

print(f"\n  Valais: {len(valais)}")
print(f"  Vaud: {len(vaud)}")
print(f"  Genève: {len(geneve)}")
print(f"  Total scrapés: {len(scraped)}")

# Lister les nouveaux events
print(f"\nListe des events scrapés:")
for ev in sorted(scraped, key=lambda e: e.get('date', '')):
    title = ev.get('title', '')[:55]
    date = ev.get('date', '')
    end = ev.get('end_date', '')
    loc = (ev.get('location', '') or '')[:45]
    print(f"  ID {ev['id']:5d} | {date} → {end or '          '} | {title}")
