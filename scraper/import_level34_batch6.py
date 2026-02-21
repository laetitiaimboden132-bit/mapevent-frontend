"""
Import events from level 3-4 sources - Batch 6
Sources: agenda.culturevalais.ch (expositions, concerts, événements Valais)
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
    # ---- AGENDA.CULTUREVALAIS.CH ----
    {
        'title': 'Saison musicale 25/26 - Fondation Pierre Gianadda Martigny',
        'location': 'Fondation Pierre Gianadda, Rue du Forum 59, 1920 Martigny',
        'date': '2026-02-01',
        'end_date': '2026-05-30',
        'time': '20:00',
        'end_time': None,
        'description': '48e édition de la Saison musicale de la Fondation Pierre Gianadda à Martigny. Treize concerts exceptionnels avec des artistes de renommée internationale : Cecilia Bartoli, Hélène Grimaud, Maria João Pires, Renaud Capuçon, Elisabeth Leonskaja et bien d\'autres. Un voyage musical mêlant audace et tradition dans un cadre exceptionnel.',
        'categories': ['Musique', 'Concert'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/38842',
        'organizer_name': 'Fondation Pierre Gianadda',
        'latitude': 46.0964,
        'longitude': 7.0730,
        'status': 'auto_validated'
    },
    {
        'title': 'Tutoyer les limites - Erhard Loretan à la Médiathèque Sion',
        'location': 'Médiathèque Valais - Sion, Les Arsenaux, Rue de Lausanne 45, 1950 Sion',
        'date': '2026-01-30',
        'end_date': '2026-04-30',
        'time': '10:00',
        'end_time': '18:00',
        'description': 'Exposition "Tutoyer les limites - En expédition avec Erhard Loretan" à la Médiathèque Valais - Sion. Découvrez l\'univers du célèbre alpiniste fribourgeois, premier Suisse à gravir les 14 sommets de plus de 8000 mètres. Carnets de courses inédits, films originaux et borne interactive retraçant ses principales ascensions. Entrée libre.',
        'categories': ['Culture', 'Exposition'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/41834',
        'organizer_name': 'Médiathèque Valais - Sion',
        'latitude': 46.2337,
        'longitude': 7.3593,
        'status': 'auto_validated'
    },
    {
        'title': 'Exposition Yves Tauvel invite Ryan R - Art Métro Sierre',
        'location': 'Art Métro Sierre, Avenue Général Guisan 30, 3960 Sierre',
        'date': '2026-02-04',
        'end_date': '2026-05-30',
        'time': None,
        'end_time': None,
        'description': 'L\'artiste Yves Tauvel expose à Art Métro Sierre et invite Ryan R. Tauvel explore la notion de lieu et le déplacement dans l\'espace géographique à travers une oeuvre in situ mettant en évidence l\'axe longitudinal de six villes réalisées en plâtre brut. Son invité Ryan R présente une recherche autour des reCAPTCHA. Entrée libre.',
        'categories': ['Culture', 'Exposition'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/41989',
        'organizer_name': 'Art Métro Sierre',
        'latitude': 46.2918,
        'longitude': 7.5326,
        'status': 'auto_validated'
    },
    {
        'title': 'Parcours de sculptures en réalité augmentée - Zermatt',
        'location': 'Village de Zermatt, Bahnhofstrasse, 3920 Zermatt',
        'date': '2025-12-11',
        'end_date': '2026-03-31',
        'time': None,
        'end_time': None,
        'description': 'Premier parcours de sculptures en réalité augmentée de Suisse à Zermatt. L\'artiste valaisanne Sarah Montani fait voler des oeuvres d\'art numériques à travers le village, entre sommets et ruelles. Sans application ni code QR, sortez votre smartphone et les sculptures apparaissent, géolocalisées et visibles uniquement à Zermatt. Gratuit et accessible à tous.',
        'categories': ['Culture', 'Exposition'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/40943',
        'organizer_name': 'Verein Magic Mountain Zermatt',
        'latitude': 46.0207,
        'longitude': 7.7491,
        'status': 'auto_validated'
    },
    {
        'title': 'Exposition "Vieillir en Suisse en tant que personnes étrangères" - Martigny',
        'location': 'Médiathèque Valais - Martigny, Avenue de la Gare 15, 1920 Martigny',
        'date': '2026-02-01',
        'end_date': '2026-03-14',
        'time': None,
        'end_time': None,
        'description': 'Exposition photographique "Vieillir en Suisse en tant que personnes étrangères" à la Médiathèque Valais de Martigny. Un regard sensible et documentaire sur le parcours de vie des personnes âgées d\'origine étrangère vivant en Suisse. Entrée libre.',
        'categories': ['Culture', 'Exposition'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/41098',
        'organizer_name': 'Médiathèque Valais - Martigny',
        'latitude': 46.0993,
        'longitude': 7.0698,
        'status': 'auto_validated'
    },
    {
        'title': 'Exposition "Danse des Flocons de Neige" - Loèche-les-Bains',
        'location': 'Galerie St. Laurent, Dorfplatz, 3954 Loèche-les-Bains',
        'date': '2026-02-09',
        'end_date': '2026-02-28',
        'time': None,
        'end_time': None,
        'description': 'Exposition artistique "Danse des Flocons de Neige" à la Galerie St. Laurent de Loèche-les-Bains (Leukerbad). Une immersion poétique dans l\'univers hivernal au coeur de la station thermale valaisanne.',
        'categories': ['Culture', 'Exposition'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/41615',
        'organizer_name': 'Galerie St. Laurent',
        'latitude': 46.3795,
        'longitude': 7.6270,
        'status': 'auto_validated'
    },
    {
        'title': 'Jean-Marc Linder - Art Digital - Espace 100 titres Sierre',
        'location': 'Espace 100 titres, Rue du Bourg 30, 3960 Sierre',
        'date': '2026-02-09',
        'end_date': '2026-02-28',
        'time': None,
        'end_time': None,
        'description': 'Exposition d\'art digital de Jean-Marc Linder à l\'Espace 100 titres de Sierre. L\'artiste propose une exploration de l\'art numérique contemporain dans un espace dédié à la création visuelle et sonore.',
        'categories': ['Culture', 'Exposition'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/40860',
        'organizer_name': 'Espace 100 titres',
        'latitude': 46.2930,
        'longitude': 7.5340,
        'status': 'auto_validated'
    },
    {
        'title': 'ZONE 30 ART PUBLIC - Yan Muehlheim "Happy Bars" Sierre',
        'location': 'ZONE 30 ART PUBLIC, Rue du Marché, 3960 Sierre',
        'date': '2026-02-09',
        'end_date': '2026-02-24',
        'time': None,
        'end_time': None,
        'description': 'Intervention artistique de Yan Muehlheim intitulée "Happy Bars" dans le cadre de ZONE 30 ART PUBLIC à Sierre. Une installation d\'art contemporain dans l\'espace urbain sierrois qui invite à repenser le paysage quotidien.',
        'categories': ['Culture', 'Exposition'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/41494',
        'organizer_name': 'ZONE 30 ART PUBLIC',
        'latitude': 46.2920,
        'longitude': 7.5315,
        'status': 'auto_validated'
    },
    {
        'title': 'Ciné-Doc : La Vallée de Gwennaël Bolomey - Sion',
        'location': 'Salle Capitole, Rue de Lausanne 18, 1950 Sion',
        'date': '2026-02-09',
        'end_date': '2026-02-09',
        'time': None,
        'end_time': None,
        'description': 'Projection du documentaire "La Vallée" de Gwennaël Bolomey en présence du cinéaste à la Salle Capitole de Sion. Un regard intime et cinématographique sur la vie en vallée alpine valaisanne.',
        'categories': ['Culture', 'Film'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/41058',
        'organizer_name': 'Cinémas de Sion',
        'latitude': 46.2332,
        'longitude': 7.3598,
        'status': 'auto_validated'
    },
    {
        'title': 'Conférence : Oiseaux et agriculture en plaine du Rhône - Martigny',
        'location': 'Salle du Vampire, Rue du Forum 2, 1920 Martigny',
        'date': '2026-02-09',
        'end_date': '2026-02-09',
        'time': None,
        'end_time': None,
        'description': 'Conférence "Oiseaux et agriculture : 25 ans d\'engagement en plaine du Rhône" par Emmanuel Revaz, collaborateur de l\'Antenne régionale Valais. Retour sur un quart de siècle de travail pour la préservation de l\'avifaune dans la plaine du Rhône valaisanne.',
        'categories': ['Nature', 'Conférence'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/41740',
        'organizer_name': 'Salle du Vampire Martigny',
        'latitude': 46.0970,
        'longitude': 7.0740,
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
