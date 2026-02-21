"""
Import events from level 3-4 sources - Batch 4
Sources: agenda.culturevalais.ch (Valais central - expositions et events)
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
    # ---- VALAIS CENTRAL (agenda.culturevalais.ch) ----
    {
        'title': 'Tutoyer les limites - Exposition Erhard Loretan',
        'location': 'Médiathèque Valais, Rue de Pratifori 18, 1950 Sion',
        'date': '2026-02-09',
        'end_date': '2026-04-30',
        'time': None,
        'end_time': None,
        'description': 'Exposition "Tutoyer les limites : en expédition avec Erhard Loretan" à la Médiathèque Valais de Sion. Hommage au célèbre alpiniste valaisan, troisième homme à avoir gravi les 14 sommets de plus de 8000 mètres. Découvrez ses expéditions extraordinaires à travers photos, documents et objets personnels.',
        'categories': ['Culture', 'Exposition'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/41834',
        'organizer_name': 'Médiathèque Valais',
        'latitude': 46.2319,
        'longitude': 7.3582,
        'status': 'auto_validated'
    },
    {
        'title': 'Expo Focus "Océan au sommet" - Musée de la Nature Sion',
        'location': 'Musée de la nature du Valais, Rue des Châteaux 12, 1950 Sion',
        'date': '2026-02-10',
        'end_date': '2026-09-13',
        'time': None,
        'end_time': None,
        'description': 'Exposition "Océan au sommet" au Musée de la nature du Valais à Sion. Comment des fossiles marins se retrouvent-ils au sommet des Alpes ? Une exploration fascinante de l\'histoire géologique des montagnes valaisannes, de l\'ancien océan Téthys aux sommets actuels. Pour tous les âges.',
        'categories': ['Nature', 'Exposition'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/40581',
        'organizer_name': 'Musée de la nature du Valais',
        'latitude': 46.2329,
        'longitude': 7.3602,
        'status': 'auto_validated'
    },
    {
        'title': 'Les Restants de la Colère de Dieu - Ferme-Asile Sion',
        'location': 'Ferme-Asile La Grenette, Promenade des Pêcheurs 10, 1950 Sion',
        'date': '2026-02-11',
        'end_date': '2026-04-26',
        'time': None,
        'end_time': None,
        'description': 'Exposition "Les Restants de la Colère de Dieu" des artistes Caroline Tschumi et Lucie Kohler à la Ferme-Asile de Sion. Un dialogue artistique puissant entre deux créatrices contemporaines dans ce lieu d\'art emblématique de la capitale valaisanne.',
        'categories': ['Culture', 'Exposition'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/41590',
        'organizer_name': 'Ferme-Asile Sion',
        'latitude': 46.2278,
        'longitude': 7.3562,
        'status': 'auto_validated'
    },
    {
        'title': 'Ciné-Doc : La Vallée de Gwennaël Bolomey - Sion',
        'location': 'Salle Capitole, Rue de Lausanne 20, 1950 Sion',
        'date': '2026-02-09',
        'end_date': '2026-02-09',
        'time': None,
        'end_time': None,
        'description': 'Projection-débat du documentaire "La Vallée" de Gwennaël Bolomey en présence du cinéaste. Un regard intime sur la vie dans une vallée alpine suisse, entre tradition et modernité. Organisé dans le cadre de la série Ciné-Doc.',
        'categories': ['Culture', 'Cinéma'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/41058',
        'organizer_name': 'Cinémas de Sion',
        'latitude': 46.2326,
        'longitude': 7.3573,
        'status': 'auto_validated'
    },
    {
        'title': 'Francis Dayer "Le vin se voit" - Tour Lombarde',
        'location': 'Galerie de la Tour Lombarde, 3975 Conthey',
        'date': '2026-02-11',
        'end_date': '2026-03-21',
        'time': None,
        'end_time': None,
        'description': 'Exposition de Francis Dayer intitulée "Le vin se voit" à la Galerie de la Tour Lombarde. L\'artiste valaisan explore les liens entre l\'art et le vin à travers ses oeuvres, dans le cadre historique de cette galerie unique.',
        'categories': ['Culture', 'Exposition'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/41466',
        'organizer_name': 'Galerie de la Tour Lombarde',
        'latitude': 46.2259,
        'longitude': 7.2979,
        'status': 'auto_validated'
    },
    {
        'title': 'Raffaella Bruzzi & Romain Tornay - La Vidondée Riddes',
        'location': 'La Vidondée, 1908 Riddes',
        'date': '2026-02-11',
        'end_date': '2026-02-28',
        'time': None,
        'end_time': None,
        'description': 'Exposition "Lumière et Matière" avec Raffaella Bruzzi (peinture) et Romain Tornay (photographie) à La Vidondée de Riddes. Un dialogue entre deux médiums artistiques explorant la lumière sous toutes ses formes.',
        'categories': ['Culture', 'Exposition'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/41776',
        'organizer_name': 'La Vidondée',
        'latitude': 46.1698,
        'longitude': 7.2258,
        'status': 'auto_validated'
    },
    {
        'title': 'Yves Tauvel invite Ryan R - Art Métro Sierre',
        'location': 'Art Métro Sierre, 3960 Sierre',
        'date': '2026-02-09',
        'end_date': '2026-05-30',
        'time': None,
        'end_time': None,
        'description': 'Exposition de l\'artiste Yves Tauvel qui invite Ryan R à Art Métro Sierre. Un dialogue artistique entre deux créateurs dans cet espace d\'art contemporain sierrois, jusqu\'au 30 mai 2026.',
        'categories': ['Culture', 'Exposition'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/41989',
        'organizer_name': 'Art Métro Sierre',
        'latitude': 46.2915,
        'longitude': 7.5325,
        'status': 'auto_validated'
    },
    {
        'title': 'Jean-Claude Roh "Fragments d\'existence" - Sion',
        'location': 'Galerie Les Dilettantes, 1950 Sion',
        'date': '2026-02-11',
        'end_date': '2026-03-07',
        'time': None,
        'end_time': None,
        'description': 'Exposition de Jean-Claude Roh intitulée "Fragments d\'existence et spectre du même" à la galerie Les Dilettantes de Sion. Exploration artistique de la condition humaine à travers fragments et reflets.',
        'categories': ['Culture', 'Exposition'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/41721',
        'organizer_name': 'Galerie Les Dilettantes',
        'latitude': 46.2325,
        'longitude': 7.3580,
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

print(f"\n{len(new_events)} nouveaux events à importer")

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
