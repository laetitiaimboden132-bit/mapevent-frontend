"""
Import events from level 3-4 sources - Batch 7
Sources: agenda.culturevalais.ch (expositions, spectacles, Bas-Valais & Valais central)
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
    # ---- AGENDA.CULTUREVALAIS.CH - Batch 7 ----
    {
        'title': 'Exposition "Les ateliers de Janebé" - St-Maurice',
        'location': 'Fondation Ateliers d\'Artiste, Grand Rue 78, 1890 St-Maurice',
        'date': '2026-03-28',
        'end_date': '2026-06-27',
        'time': '14:00',
        'end_time': '18:00',
        'description': 'Exposition consacrée à Jeanne Barraud-Pellet, dite Janebé, figure singulière de la scène artistique romande du XXe siècle. Autodidacte et profondément attachée au monde rural, elle a construit une oeuvre libre et exigeante. Peintures, dessins et documents retraçant 60 ans de création. Entrée libre, ouvert vendredi et samedi.',
        'categories': ['Culture', 'Exposition'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/41987',
        'organizer_name': 'Fondation Ateliers d\'Artiste',
        'latitude': 46.2185,
        'longitude': 7.0030,
        'status': 'auto_validated'
    },
    {
        'title': 'Primevère la géante - Exposition Elodie Balandras à St-Maurice',
        'location': 'Médiathèque Valais - St-Maurice, Avenue du Simplon 6, 1890 St-Maurice',
        'date': '2026-04-22',
        'end_date': '2026-05-22',
        'time': '12:30',
        'end_time': '18:00',
        'description': 'Exposition de dessins originaux d\'Elodie Balandras à la Médiathèque Valais St-Maurice. L\'illustratrice, engagée pour l\'environnement, présente les originaux de "Primevère: la géante du Lac de Vallon", un album mêlant nature, transmission et savoirs médicinaux dans les alpages savoyards. Entrée libre, dans le cadre du salon Littéra Découverte.',
        'categories': ['Culture', 'Exposition'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/41838',
        'organizer_name': 'Médiathèque Valais - St-Maurice',
        'latitude': 46.2195,
        'longitude': 7.0030,
        'status': 'auto_validated'
    },
    {
        'title': 'Nuit des galeries à Sierre - Madeleine Gay sculptures',
        'location': 'Atelier galerie la Zîle, Rue de l\'île Falcon 27, 3960 Sierre',
        'date': '2026-05-28',
        'end_date': '2026-05-31',
        'time': '15:00',
        'end_time': '20:00',
        'description': 'La Nuit des galeries de Sierre : un événement fédérateur invitant à pousser les portes des espaces d\'exposition de la ville. L\'atelier galerie de la Zîle accueille les sculptures de Madeleine Gay. Entrée libre. Basé sur le principe de la Nuit des Musées.',
        'categories': ['Culture', 'Exposition'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/41300',
        'organizer_name': 'Atelier galerie la Zîle',
        'latitude': 46.2930,
        'longitude': 7.5360,
        'status': 'auto_validated'
    },
    {
        'title': 'DÉSORIENTÉ - Spectacle de danse contemporaine à Sion',
        'location': 'Pôle musique - Black Box, Rue du Rawil 47, 1950 Sion',
        'date': '2026-05-22',
        'end_date': '2026-05-23',
        'time': '20:00',
        'end_time': None,
        'description': 'Spectacle de danse jazz contemporaine par la Compagnie trèze. Un parcours chorégraphique au coeur des complexes et de la désorientation, où les danseuses explorent la perte de repères pour transformer fragilité en force. Un spectacle intense et bouleversant. Sur réservation.',
        'categories': ['Culture', 'Spectacle'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/41342',
        'organizer_name': 'Compagnie trèze',
        'latitude': 46.2310,
        'longitude': 7.3550,
        'status': 'auto_validated'
    },
    {
        'title': 'Histoires climatiques du Valais - Exposition Laura Ferrarello',
        'location': 'Médiathèque Valais - Sion, Les Arsenaux, Rue de Lausanne 45, 1950 Sion',
        'date': '2026-02-13',
        'end_date': '2026-04-11',
        'time': None,
        'end_time': None,
        'description': 'Exposition "Histoires climatiques du Valais" de Laura Ferrarello à la Médiathèque Valais-Sion. Une exploration artistique et documentaire des changements climatiques et de leur impact sur le paysage et la vie quotidienne en Valais.',
        'categories': ['Culture', 'Exposition'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/41861',
        'organizer_name': 'Médiathèque Valais - Sion',
        'latitude': 46.2337,
        'longitude': 7.3593,
        'status': 'auto_validated'
    },
    {
        'title': 'MERGERS AND ACQUISITION - Cruces & Gagliardi à Sierre',
        'location': 'Manoir de la Ville, Rue du Manoir 1, 3960 Sierre',
        'date': '2026-03-01',
        'end_date': '2026-06-28',
        'time': None,
        'end_time': None,
        'description': 'Exposition d\'art contemporain "MERGERS AND ACQUISITION" réunissant Adam Cruces et Louisa Gagliardi au Manoir de la Ville de Sierre. Deux artistes de renommée internationale présentent une oeuvre dialogue entre peinture et installation.',
        'categories': ['Culture', 'Exposition'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/41819',
        'organizer_name': 'Manoir de la Ville de Sierre',
        'latitude': 46.2925,
        'longitude': 7.5345,
        'status': 'auto_validated'
    },
    {
        'title': 'Pedro Rodrigues "Control of Natural Space" - Martigny',
        'location': 'Manoir de la Ville, Avenue de la Gare 1, 1920 Martigny',
        'date': '2026-03-06',
        'end_date': '2026-05-10',
        'time': None,
        'end_time': None,
        'description': 'Exposition de Pedro Rodrigues "Control of Natural Space" au Manoir de la Ville de Martigny. L\'artiste propose une réflexion visuelle sur le contrôle et la transformation des espaces naturels, entre paysage et intervention humaine.',
        'categories': ['Culture', 'Exposition'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/41865',
        'organizer_name': 'Manoir de la Ville de Martigny',
        'latitude': 46.0987,
        'longitude': 7.0712,
        'status': 'auto_validated'
    },
    {
        'title': 'Patrick Thomas & Pierre-Antoine Moix "Altitude" - Exposition peinture',
        'location': 'Galerie du Rhône, Rue du Marché 6, 3960 Sierre',
        'date': '2026-03-07',
        'end_date': '2026-03-28',
        'time': None,
        'end_time': None,
        'description': 'Exposition de peinture "Altitude" réunissant Patrick Thomas et Pierre-Antoine Moix. Deux regards picturaux croisés sur les sommets et paysages valaisans dans un dialogue artistique en altitude.',
        'categories': ['Culture', 'Exposition'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/41959',
        'organizer_name': 'Galerie du Rhône Sierre',
        'latitude': 46.2925,
        'longitude': 7.5330,
        'status': 'auto_validated'
    },
    {
        'title': 'Coup de bluff au cabaret - Spectacle à Sion',
        'location': 'Théâtre de Valère, Rue de Lausanne 45a, 1950 Sion',
        'date': '2026-04-16',
        'end_date': '2026-04-16',
        'time': None,
        'end_time': None,
        'description': 'Spectacle "Coup de bluff au cabaret" proposé en après-midi et en soirée au Théâtre de Valère à Sion. Un moment de divertissement mêlant humour et mise en scène de cabaret.',
        'categories': ['Culture', 'Spectacle'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/39734',
        'organizer_name': 'Théâtre de Valère',
        'latitude': 46.2335,
        'longitude': 7.3600,
        'status': 'auto_validated'
    },
    {
        'title': 'Fertik - Spectacle clown à Sion',
        'location': 'Petithéâtre, Rue de la Tour 10, 1950 Sion',
        'date': '2026-02-09',
        'end_date': '2026-03-17',
        'time': None,
        'end_time': None,
        'description': 'Spectacle "Fertik" : deux clowns et un musicien à la dérive pour un naufrage salutaire et percutant. Un spectacle délicat et puissant qui aborde la fragilité humaine avec humour et tendresse.',
        'categories': ['Culture', 'Spectacle'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/38700',
        'organizer_name': 'Petithéâtre Sion',
        'latitude': 46.2330,
        'longitude': 7.3585,
        'status': 'auto_validated'
    },
    {
        'title': 'Exposition France Schmid "Ivresse" - Sierre',
        'location': 'Galerie de la Grenette, Place de la Grenette, 3960 Sierre',
        'date': '2026-02-13',
        'end_date': '2026-03-01',
        'time': None,
        'end_time': None,
        'description': 'Exposition "Ivresse" de France Schmid à Sierre. L\'artiste explore le thème de l\'ivresse à travers une série d\'oeuvres plastiques entre figuration et abstraction, dans un des espaces d\'art contemporain de la ville.',
        'categories': ['Culture', 'Exposition'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/41570',
        'organizer_name': 'Galerie de la Grenette Sierre',
        'latitude': 46.2922,
        'longitude': 7.5335,
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
