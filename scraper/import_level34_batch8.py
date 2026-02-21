"""
Import events from level 3-4 sources - Batch 8
Sources: geneve.ch (site communal, max 30%), lacote-tourisme.ch
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

events = [
    # ---- GENEVE.CH (site communal, max 30%) ----
    {
        'title': 'Exposition "Elles" - Peinture aborigène contemporaine au Musée Rath',
        'location': 'Musée Rath, Place Neuve 1, 1204 Genève',
        'date': '2025-12-11',
        'end_date': '2026-04-19',
        'time': '11:00',
        'end_time': '18:00',
        'description': 'Le Musée d\'art et d\'histoire, avec la Fondation Opale, consacre une exposition à la peinture aborigène contemporaine. Découvrez les oeuvres de grandes figures artistiques féminines qui réinventent les récits culturels et spirituels de leurs communautés à travers des créations puissantes et colorées.',
        'categories': ['Culture', 'Exposition'],
        'source_url': 'https://www.geneve.ch/actualites/expositions-voir-moment-geneve#elles',
        'organizer_name': 'Musée d\'art et d\'histoire de Genève',
        'latitude': 46.1994,
        'longitude': 6.1421,
        'status': 'auto_validated'
    },
    {
        'title': 'Exposition "Anatomie" - Corps humain au Musée d\'histoire des sciences',
        'location': 'Musée d\'histoire des sciences, Rue de Lausanne 128, 1202 Genève',
        'date': '2025-10-01',
        'end_date': '2026-04-17',
        'time': '10:00',
        'end_time': '17:00',
        'description': 'L\'exposition "Anatomie" vous emmène dans l\'exploration du corps humain et de son étude, de la Renaissance à nos jours. Modèles anatomiques spectaculaires, explorations microscopiques et histoire fascinante de la médecine au Musée d\'histoire des sciences de Genève.',
        'categories': ['Culture', 'Exposition'],
        'source_url': 'https://www.geneve.ch/actualites/exposition-anatomie-musee-histoire-sciences-geneve',
        'organizer_name': 'Musée d\'histoire des sciences de Genève',
        'latitude': 46.2200,
        'longitude': 6.1488,
        'status': 'auto_validated'
    },
    {
        'title': 'Exposition "Observatoires" - John M Armleder au MAH Genève',
        'location': 'Musée d\'art et d\'histoire, Rue Charles-Galland 2, 1206 Genève',
        'date': '2026-01-29',
        'end_date': '2026-10-25',
        'time': '11:00',
        'end_time': '18:00',
        'description': 'Carte blanche à l\'artiste genevois John M Armleder au Musée d\'art et d\'histoire. L\'exposition "Observatoires" fait dialoguer oeuvres contemporaines et objets historiques des collections du musée. Une invitation à parcourir le musée autrement.',
        'categories': ['Culture', 'Exposition'],
        'source_url': 'https://www.geneve.ch/actualites/exposition-observatoires-mah-carte-blanche-john-armleder',
        'organizer_name': 'Musée d\'art et d\'histoire de Genève',
        'latitude': 46.1990,
        'longitude': 6.1530,
        'status': 'auto_validated'
    },
    {
        'title': 'Exposition "Tender buttons" - L\'art du bouton au Musée Ariana',
        'location': 'Musée Ariana, Avenue de la Paix 10, 1202 Genève',
        'date': '2025-09-19',
        'end_date': '2026-10-04',
        'time': '10:00',
        'end_time': '18:00',
        'description': 'L\'exposition "Tender buttons" explore le bouton comme objet d\'art et de société. Plus de 300 pièces dialoguent avec les collections du Musée Ariana, musée suisse de la céramique et du verre. Une traversée poétique et inattendue.',
        'categories': ['Culture', 'Exposition'],
        'source_url': 'https://www.geneve.ch/actualites/exposition-tender-buttons-musee-ariana',
        'organizer_name': 'Musée Ariana Genève',
        'latitude': 46.2233,
        'longitude': 6.1400,
        'status': 'auto_validated'
    },
    {
        'title': '"Dans les coulisses" - Making of "Sauvage" de Claude Barras - Genève',
        'location': 'Bibliothèque de la Cité - Le Multi, Place des Trois-Perdrix 5, 1204 Genève',
        'date': '2025-11-01',
        'end_date': '2026-05-23',
        'time': '10:00',
        'end_time': '19:00',
        'description': 'Exposition immersive plongeant dans la forêt de Bornéo et les coulisses du film d\'animation "Sauvage" de Claude Barras. Découvrez la genèse du film en stop motion, de l\'écriture du scénario à la naissance des personnages. Une expérience unique mêlant art, cinéma et nature.',
        'categories': ['Culture', 'Exposition'],
        'source_url': 'https://www.geneve.ch/actualites/exposition-sauvages-coulisses-film-claude-barras-bibliotheque-cite',
        'organizer_name': 'Bibliothèque de la Cité Genève',
        'latitude': 46.2013,
        'longitude': 6.1451,
        'status': 'auto_validated'
    },
    {
        'title': '"Temps entrelacés" - Angélica Serech au Musée Croix-Rouge',
        'location': 'Musée international de la Croix-Rouge, Avenue de la Paix 17, 1202 Genève',
        'date': '2026-01-01',
        'end_date': '2026-08-30',
        'time': '10:00',
        'end_time': '18:00',
        'description': 'Première exposition personnelle d\'Angélica Serech en Europe au Musée de la Croix-Rouge. L\'artiste guatémaltèque construit ses propres métiers à tisser pour relier des gestes ancestraux à son histoire personnelle marquée par la guerre civile. Art textile, mémoire et résilience.',
        'categories': ['Culture', 'Exposition'],
        'source_url': 'https://redcrossmuseum.ch/fr/expositions/angelica-serech-pachun-qijul/',
        'organizer_name': 'Musée international de la Croix-Rouge',
        'latitude': 46.2260,
        'longitude': 6.1380,
        'status': 'auto_validated'
    },
    {
        'title': 'Exposition "Quel froid!" - L\'hiver à travers l\'art à la Maison Tavel',
        'location': 'Maison Tavel, Rue du Puits-Saint-Pierre 6, 1204 Genève',
        'date': '2025-12-01',
        'end_date': '2026-05-31',
        'time': '11:00',
        'end_time': '18:00',
        'description': 'La Maison Tavel, plus ancienne maison privée de Genève, consacre une exposition à l\'hiver. "Quel froid!" propose de redécouvrir cette saison à travers le regard d\'artistes du 17e siècle à nos jours. Peintures, gravures et photographies dans un cadre historique unique.',
        'categories': ['Culture', 'Exposition'],
        'source_url': 'https://www.geneve.ch/actualites/exposition-froid-maison-tavel',
        'organizer_name': 'Maison Tavel - Musées de Genève',
        'latitude': 46.2010,
        'longitude': 6.1487,
        'status': 'auto_validated'
    },
    # ---- LA COTE TOURISME / NYON ----
    {
        'title': 'Festival Les Hivernales 2026 - Nyon',
        'location': 'Centre-ville de Nyon, Place du Marché, 1260 Nyon',
        'date': '2026-02-26',
        'end_date': '2026-03-01',
        'time': '18:00',
        'end_time': None,
        'description': 'Festival musical hivernal à Nyon avec concerts dans divers lieux partenaires, un Village avec braseros et boissons chaudes, un Comedy Club le jeudi, et des concerts pop-rock, rap/RnB et électro les vendredi et samedi. Ambiance conviviale au coeur de la ville.',
        'categories': ['Musique', 'Festival'],
        'source_url': 'https://www.nyon.ch/agenda/festival-les-hivernales-18931',
        'organizer_name': 'Ville de Nyon',
        'latitude': 46.3833,
        'longitude': 6.2396,
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
    
    skip = False
    for et in existing_titles:
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

print(f"\n{len(new_events)} nouveaux events a importer")

if new_events:
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
