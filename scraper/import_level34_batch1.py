"""
Import events from level 3-4 sources (30% rule)
Sources: sierre.ch (site communal), agenda.culturevalais.ch (agenda culturel public)
"""
import requests, sys, io, json, time

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'

# Vérifier events existants
r = requests.get(f'{API_URL}/api/events', timeout=30)
data = r.json()
existing = data if isinstance(data, list) else data.get('events', [])
existing_titles = {e.get('title', '').lower().strip() for e in existing}
existing_urls = {e.get('source_url', '').lower().strip() for e in existing}
print(f"Events existants: {len(existing)}")

# ============================================================================
# SOURCE 1: sierre.ch (site communal, niveau 3)
# Total sur le site: 133 events | 30% = 40 max | On a 10 -> peut ajouter 30
# ============================================================================

# SOURCE 2: agenda.culturevalais.ch (agenda culturel public, niveau 3)  
# Total sur le site: ~300+ events | 30% = 90+ max | On a 8 -> peut ajouter 80+
# ============================================================================

events = [
    # ---- SIERRE.CH ----
    {
        'title': 'Carnaval de Sierre 2026',
        'location': 'Salle de gym de Muraz, Rue de Villa, 3960 Sierre',
        'date': '2026-02-13',
        'end_date': '2026-02-14',
        'time': '19:00',
        'end_time': None,
        'description': 'Le Carnaval de Sierre 2026 vous invite à un voyage dans le temps sur le thème des grandes civilisations. Deux jours de fête avec chars, guggenmusik, cortèges et soirées DJ. Cortège d\'ouverture vendredi soir à Muraz, grand cortège du samedi à 13h30. Entrée libre pour tous les cortèges et soirées.',
        'categories': ['Fête', 'Culture'],
        'source_url': 'https://www.sierre.ch/fr/calendrier-manifestations-1738/agenda-viewguidle-1228498920.html',
        'organizer_name': 'Ville de Sierre',
        'latitude': 46.2937,
        'longitude': 7.5314,
        'status': 'auto_validated'
    },
    {
        'title': 'Carnaval de Granges 2026',
        'location': 'Salle de gym, Rue du Coin 6, 3977 Granges VS',
        'date': '2026-02-14',
        'end_date': '2026-02-14',
        'time': '16:30',
        'end_time': None,
        'description': 'Carnaval de Granges sur le thème de l\'amour. Programme festif avec défilé des écoles sur l\'Avenue de la Gare à 16h30, suivi d\'une soirée familiale avec concours de déguisement et animation DJ. Petite restauration disponible sur place.',
        'categories': ['Fête', 'Famille'],
        'source_url': 'https://www.sierre.ch/fr/calendrier-manifestations-1738/agenda-viewguidle-1229477395.html',
        'organizer_name': 'Commune de Granges',
        'latitude': 46.2975,
        'longitude': 7.5032,
        'status': 'auto_validated'
    },
    {
        'title': 'JAM SESSION - EJMA Valais & Caves de Courten',
        'location': 'Les ARTS Caves de Courten, Rue du Bourg 30, 3960 Sierre',
        'date': '2026-02-13',
        'end_date': '2026-02-13',
        'time': '19:30',
        'end_time': None,
        'description': 'Soirée musicale conviviale organisée par l\'EJMA Valais, les ARTS Caves de Courten et la Jazz Station. L\'atelier Red Baron ouvre la scène à 19h30, suivi d\'une jam session libre et inclusive à 20h15. Musiciens confirmés, étudiants et amateurs bienvenus pour improviser et partager. Entrée libre, collecte à la sortie.',
        'categories': ['Musique', 'Culture'],
        'source_url': 'https://www.sierre.ch/fr/calendrier-manifestations-1738/agenda-viewguidle-1230898878.html',
        'organizer_name': 'EJMA Valais',
        'latitude': 46.2923,
        'longitude': 7.5350,
        'status': 'auto_validated'
    },
    {
        'title': 'Driftwood 4tet - Festival Diagonales Jazz',
        'location': 'Jazz Station, Route de la Mondérêche 7, 3960 Sierre',
        'date': '2026-02-20',
        'end_date': '2026-02-20',
        'time': None,
        'end_time': None,
        'description': 'Concert dans le cadre du Festival Suisse Diagonales Jazz. Le Driftwood 4tet propose un jazz contemporain teinté de rock, oscillant entre miniatures fragiles et paysages sonores orchestraux. Composé par Joa Frey, le répertoire puise dans les phénomènes naturels et les histoires personnelles pour créer un groove dynamique et accessible.',
        'categories': ['Musique', 'Concert'],
        'source_url': 'https://www.sierre.ch/fr/calendrier-manifestations-1738/agenda-viewguidle-1217935776.html',
        'organizer_name': 'Diagonales Jazz',
        'latitude': 46.2878,
        'longitude': 7.5289,
        'status': 'auto_validated'
    },
    {
        'title': 'Carte Blanche aux Jeunes Solistes - HEMU Valais',
        'location': 'Les ARTS Caves de Courten, Rue du Bourg 30, 3960 Sierre',
        'date': '2026-02-20',
        'end_date': '2026-02-20',
        'time': '18:30',
        'end_time': None,
        'description': 'Les jeunes solistes de la classe de guitare de l\'HEMU Valais investissent la scène des Caves de Courten pour partager leur univers musical. Au programme, une mosaïque d\'oeuvres classiques et contemporaines portée par la nouvelle génération de guitaristes. Avec Damien Theux, Bilyana Lazarova et d\'autres talents émergents. Entrée libre, collecte à la sortie.',
        'categories': ['Musique', 'Concert'],
        'source_url': 'https://www.sierre.ch/fr/calendrier-manifestations-1738/agenda-viewguidle-1230898884.html',
        'organizer_name': 'HEMU Valais',
        'latitude': 46.2923,
        'longitude': 7.5350,
        'status': 'auto_validated'
    },
    {
        'title': 'Initiation à la dégustation de vin - Colline de Daval',
        'location': 'Colline de Daval, Colline de Daval 5, 3960 Sierre',
        'date': '2026-02-26',
        'end_date': '2026-02-26',
        'time': None,
        'end_time': None,
        'description': 'Cours d\'initiation à la dégustation de vin animé par le sommelier Hugo Zufferey. Au programme : visite de la cave et du chai à barriques, dégustation de 3 vins blancs et 3 vins rouges, puis un apéritif avec plateau valaisan. Inscription et réservation requises.',
        'categories': ['Gastronomie', 'Culture'],
        'source_url': 'https://www.sierre.ch/fr/calendrier-manifestations-1738/agenda-viewguidle-1231561511.html',
        'organizer_name': 'Colline de Daval',
        'latitude': 46.2928,
        'longitude': 7.5301,
        'status': 'auto_validated'
    },
    {
        'title': 'Odyssée singulière - Spectacle de contes',
        'location': 'Rue Notre-Dame-des-Marais 5, 3960 Sierre',
        'date': '2026-02-28',
        'end_date': '2026-02-28',
        'time': None,
        'end_time': None,
        'description': 'Geneviève Boillat et Christine Métrailler unissent leurs voix et leurs imaginaires pour raconter un territoire réinventé. Un spectacle poétique où se mêlent merveilleux, poésie et humour pour redécouvrir la Suisse sous un jour étonnant et enchanté. Voyage entre Nord et Sud, entre Jura et Valais.',
        'categories': ['Culture', 'Spectacle'],
        'source_url': 'https://www.sierre.ch/fr/calendrier-manifestations-1738/agenda-viewguidle-1231350388.html',
        'organizer_name': 'Ville de Sierre',
        'latitude': 46.2914,
        'longitude': 7.5338,
        'status': 'auto_validated'
    },
    {
        'title': 'Terres Sonores - Dimitar Gougov & Alexandre Cellier',
        'location': 'Les ARTS Caves de Courten, Rue du Bourg 30, 3960 Sierre',
        'date': '2026-03-06',
        'end_date': '2026-03-06',
        'time': None,
        'end_time': None,
        'description': 'Concert exceptionnel réunissant Dimitar Gougov, virtuose de la gadulka bulgare, et Alexandre Cellier, multi-instrumentiste suisse passionné de jazz et de musiques balkaniques. Un univers musical d\'une rare intensité où se mêlent créativité, subtilité et profonde émotion.',
        'categories': ['Musique', 'Concert'],
        'source_url': 'https://www.sierre.ch/fr/calendrier-manifestations-1738/agenda-viewguidle-1230898876.html',
        'organizer_name': 'Les ARTS Caves de Courten',
        'latitude': 46.2923,
        'longitude': 7.5350,
        'status': 'auto_validated'
    },
    {
        'title': 'Kéduhaut - Jazz Pop à la Jazz Station Sierre',
        'location': 'Jazz Station, Route de la Mondérêche 7, 3960 Sierre',
        'date': '2026-03-13',
        'end_date': '2026-03-13',
        'time': None,
        'end_time': None,
        'description': 'Le compositeur et multi-instrumentiste Jean-Pierre Schaller présente son nouveau projet mêlant Pop et Jazz. Avec la talentueuse Joanne Gaillard à la composition et aux paroles, Camille Tissot (étudiante HEMU Jazz) et le batteur Johan Wermeille. Une aventure musicale captivante entre sincérité et générosité.',
        'categories': ['Musique', 'Concert'],
        'source_url': 'https://www.sierre.ch/fr/calendrier-manifestations-1738/agenda-viewguidle-1217935671.html',
        'organizer_name': 'Jazz Station Sierre',
        'latitude': 46.2878,
        'longitude': 7.5289,
        'status': 'auto_validated'
    },

    # ---- AGENDA.CULTUREVALAIS.CH ----
    {
        'title': 'Orchestre de Chambre de Lausanne & HEMU - Soirée Wagner',
        'location': 'NODA BCVS, Avenue de Tourbillon 22, 1950 Sion',
        'date': '2026-02-10',
        'end_date': '2026-02-10',
        'time': '19:30',
        'end_time': None,
        'description': 'Soirée symphonique d\'exception dédiée à Wagner. L\'OCL s\'associe à la HEMU pour un programme magistral sous la direction de Bertrand de Billy. Au programme : le Crépuscule des Dieux, Tristan und Isolde, Die Meistersinger von Nürnberg et Tannhäuser. Un grand voyage orchestral alliant talents confirmés et artistes émergents.',
        'categories': ['Musique', 'Concert'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/40025',
        'organizer_name': 'NODA BCVS',
        'latitude': 46.2339,
        'longitude': 7.3608,
        'status': 'auto_validated'
    },
    {
        'title': 'Exposition "De Manet à Kelly" - Fondation Pierre Gianadda',
        'location': 'Fondation Pierre Gianadda, Rue du Forum 59, 1920 Martigny',
        'date': '2026-01-01',
        'end_date': '2026-06-14',
        'time': '10:00',
        'end_time': '18:00',
        'description': 'Exposition exceptionnelle de 178 chefs-d\'oeuvre de la gravure des XIXe, XXe et XXIe siècles, issus de la bibliothèque de l\'Institut national d\'histoire de l\'art (INHA, Paris). De Francisco de Goya à Vera Molnar en passant par Edgar Degas, Mary Cassatt et Edouard Manet. L\'art de l\'estampe à travers l\'histoire dans toute sa créativité et sa modernité. Ouverte tous les jours de 10h à 18h.',
        'categories': ['Culture', 'Exposition'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/41813',
        'organizer_name': 'Fondation Pierre Gianadda',
        'latitude': 46.0960,
        'longitude': 7.0673,
        'status': 'auto_validated'
    },
    {
        'title': 'Saison musicale 2025/2026 - Fondation Pierre Gianadda',
        'location': 'Fondation Pierre Gianadda, Rue du Forum 59, 1920 Martigny',
        'date': '2026-02-01',
        'end_date': '2026-05-30',
        'time': None,
        'end_time': None,
        'description': '48e édition de la Saison musicale de la Fondation Pierre Gianadda. Treize concerts exceptionnels avec des artistes de renommée internationale : Cecilia Bartoli, Hélène Grimaud, Maria João Pires, Renaud Capuçon, Elisabeth Leonskaja et bien d\'autres. Un grand voyage musical entre audace et tradition dans l\'écrin de Martigny.',
        'categories': ['Musique', 'Concert'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/38842',
        'organizer_name': 'Fondation Pierre Gianadda',
        'latitude': 46.0960,
        'longitude': 7.0673,
        'status': 'auto_validated'
    },
    {
        'title': 'La poésie de l\'échec - Théâtre & beatbox au Spot Sion',
        'location': 'Le Spot Valère, Rue du Vieux-Collège 22, 1950 Sion',
        'date': '2026-02-11',
        'end_date': '2026-02-11',
        'time': '19:00',
        'end_time': None,
        'description': 'Spectacle de théâtre intime avec beatbox en live par la Cie Marjolaine Minot. Sur un simple canapé, les vérités éclatent et les émotions se percutent. Une forme hybride, inventive et joyeusement décalée qui bouscule les secrets de famille. Une symphonie des non-dits portée par l\'humour et l\'audace.',
        'categories': ['Culture', 'Spectacle'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/38682',
        'organizer_name': 'Le Spot - Pôle des théâtres de Sion',
        'latitude': 46.2328,
        'longitude': 7.3592,
        'status': 'auto_validated'
    },
]

# Filtrer les doublons
new_events = []
for e in events:
    url_lower = e['source_url'].lower().strip()
    title_lower = e['title'].lower().strip()
    
    if url_lower in existing_urls:
        print(f"  SKIP (URL existe): {e['title']}")
        continue
    
    # Check titre similaire
    skip = False
    for et in existing_titles:
        # Vérifier si le titre est très similaire
        title_words = set(title_lower.split())
        existing_words = set(et.split())
        common = title_words & existing_words
        if len(common) >= 3 and len(common) / max(len(title_words), 1) > 0.6:
            print(f"  SKIP (titre similaire): {e['title']} ~= {et}")
            skip = True
            break
    
    if not skip:
        new_events.append(e)
        print(f"  OK: {e['title']}")

print(f"\n{len(new_events)} nouveaux events à importer")

if new_events:
    # Import par batch de 5
    for i in range(0, len(new_events), 5):
        batch = new_events[i:i+5]
        print(f"\nImport batch {i//5 + 1} ({len(batch)} events)...")
        try:
            r = requests.post(
                f'{API_URL}/api/events/scraped/batch',
                json={'events': batch},
                timeout=30
            )
            result = r.json()
            print(f"  Status: {r.status_code}")
            if isinstance(result, dict):
                print(f"  Created: {result.get('created', 0)}")
                print(f"  Skipped: {result.get('skipped', 0)}")
                if result.get('errors'):
                    for err in result['errors'][:3]:
                        print(f"  Error: {err}")
            time.sleep(2)
        except Exception as ex:
            print(f"  ERREUR: {ex}")

# Vérification finale
time.sleep(2)
r = requests.get(f'{API_URL}/api/events', timeout=30)
data = r.json()
total = len(data if isinstance(data, list) else data.get('events', []))
print(f"\n=== TOTAL EVENTS: {total} ===")
