"""
Import events from level 3-4 sources - Batch 3
Sources: agenda.culturevalais.ch (expositions Bas-Valais + Valais central)
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
    # ---- EXPOSITIONS BAS-VALAIS (agenda.culturevalais.ch) ----
    {
        'title': 'Exposition PRESENCES - Musée de Bagnes',
        'location': 'Musée de Bagnes, Route de Clouchèvre 30, 1934 Le Châble',
        'date': '2026-02-08',
        'end_date': '2026-11-15',
        'time': None,
        'end_time': None,
        'description': 'Exposition temporaire "Présences" au Musée de Bagnes dans le Val de Bagnes. Une exploration artistique originale dans le cadre authentique de ce musée de montagne, du 8 février au 15 novembre 2026.',
        'categories': ['Culture', 'Exposition'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/41680',
        'organizer_name': 'Musée de Bagnes',
        'latitude': 46.0811,
        'longitude': 7.2134,
        'status': 'auto_validated'
    },
    {
        'title': 'Michel Favre - Sculptures au Musée des Sciences de la Terre',
        'location': 'Musée des Sciences de la Terre, Rue des Epineys 6, 1920 Martigny',
        'date': '2026-02-10',
        'end_date': '2026-06-21',
        'time': None,
        'end_time': None,
        'description': 'Exposition de sculptures de l\'artiste Michel Favre au Musée cantonal des Sciences de la Terre à Martigny. Un dialogue entre l\'art sculptural et les richesses géologiques du Valais, du 10 février au 21 juin 2026.',
        'categories': ['Culture', 'Exposition'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/41743',
        'organizer_name': 'Musée des Sciences de la Terre',
        'latitude': 46.0949,
        'longitude': 7.0652,
        'status': 'auto_validated'
    },
    {
        'title': 'ART AS LIFE - Nelly Haliti au Manoir de Martigny',
        'location': 'Le Manoir de la Ville de Martigny, Rue du Manoir 3, 1920 Martigny',
        'date': '2026-02-11',
        'end_date': '2026-03-31',
        'time': None,
        'end_time': None,
        'description': 'Exposition de l\'artiste Nelly Haliti intitulée "ART AS LIFE" au Manoir de la Ville de Martigny. Un regard contemporain unique où l\'art se mêle à la vie quotidienne, du 11 février au 31 mars 2026.',
        'categories': ['Culture', 'Exposition'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/38851',
        'organizer_name': 'Le Manoir de Martigny',
        'latitude': 46.1003,
        'longitude': 7.0690,
        'status': 'auto_validated'
    },
    {
        'title': 'REVENIR SUR TERRE - Exposition au Manoir de Martigny',
        'location': 'Le Manoir de la Ville de Martigny, Rue du Manoir 3, 1920 Martigny',
        'date': '2026-02-11',
        'end_date': '2026-05-10',
        'time': None,
        'end_time': None,
        'description': 'Exposition "Revenir sur Terre" au Manoir de la Ville de Martigny. Une réflexion artistique sur notre rapport à la terre et à l\'environnement, présentée du 11 février au 10 mai 2026.',
        'categories': ['Culture', 'Exposition'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/41291',
        'organizer_name': 'Le Manoir de Martigny',
        'latitude': 46.1003,
        'longitude': 7.0690,
        'status': 'auto_validated'
    },
    {
        'title': 'L\'eau de lumière - Musée de Fully',
        'location': 'Musée de Fully, Place de l\'Eglise 6, 1926 Fully',
        'date': '2026-02-11',
        'end_date': '2026-05-31',
        'time': None,
        'end_time': None,
        'description': 'Nouvelle exposition permanente "L\'eau de lumière" et exposition temporaire "Un Valais d\'Epopée" au Musée de Fully. Deux parcours pour découvrir l\'histoire et le patrimoine de la région, du 11 février au 31 mai 2026.',
        'categories': ['Culture', 'Exposition'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/40630',
        'organizer_name': 'Musée de Fully',
        'latitude': 46.1350,
        'longitude': 7.1102,
        'status': 'auto_validated'
    },
    {
        'title': 'Domestiques photogéniques - Médiathèque Valais Martigny',
        'location': 'Médiathèque Valais, Rue du Bourg 1, 1920 Martigny',
        'date': '2026-02-11',
        'end_date': '2026-03-28',
        'time': None,
        'end_time': None,
        'description': 'Exposition photographique "Domestiques photogéniques" à la Médiathèque Valais de Martigny. Un regard sur la photographie domestique et son évolution au fil du temps.',
        'categories': ['Culture', 'Exposition'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/37703',
        'organizer_name': 'Médiathèque Valais',
        'latitude': 46.1016,
        'longitude': 7.0700,
        'status': 'auto_validated'
    },
    {
        'title': 'Visites guidées de l\'insula 14 - Quartier romain de Martigny',
        'location': 'Martigny Tourisme, Place Centrale 9, 1920 Martigny',
        'date': '2026-02-11',
        'end_date': '2026-03-11',
        'time': None,
        'end_time': None,
        'description': 'Visites guidées pour découvrir l\'insula 14, un quartier romain inédit récemment mis au jour à Martigny. Plongez dans l\'histoire antique de cette cité fondée il y a plus de 2000 ans. Organisé par Martigny Tourisme.',
        'categories': ['Culture', 'Visite'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/41876',
        'organizer_name': 'Martigny Tourisme',
        'latitude': 46.1019,
        'longitude': 7.0713,
        'status': 'auto_validated'
    },
    {
        'title': 'Prix RTS Littérature Ados 2026 - St-Maurice',
        'location': 'Médiathèque Valais, Rue de la Gare 1, 1890 St-Maurice',
        'date': '2026-02-09',
        'end_date': '2026-02-14',
        'time': None,
        'end_time': None,
        'description': 'Semaine dédiée au Prix RTS Littérature Ados 2026 à la Médiathèque Valais de St-Maurice. Un événement annuel qui met en lumière la littérature jeunesse et encourage la lecture chez les adolescents.',
        'categories': ['Culture', 'Famille'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/39523',
        'organizer_name': 'Médiathèque Valais',
        'latitude': 46.2179,
        'longitude': 7.0015,
        'status': 'auto_validated'
    },
    {
        'title': 'Oiseaux et agriculture - Conférence à Martigny',
        'location': 'Salle du Vampire, Rue de la Fontaine 6, 1920 Martigny',
        'date': '2026-02-09',
        'end_date': '2026-02-09',
        'time': None,
        'end_time': None,
        'description': 'Conférence "Oiseaux et agriculture : 25 ans d\'engagement en plaine du Rhône" par Emmanuel Revaz, collaborateur de l\'Antenne régionale Valais. Retour sur un quart de siècle de travail de conservation pour la biodiversité aviaire dans la plaine valaisanne.',
        'categories': ['Nature', 'Conférence'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/41740',
        'organizer_name': 'Antenne régionale Valais',
        'latitude': 46.1015,
        'longitude': 7.0690,
        'status': 'auto_validated'
    },
    {
        'title': 'Le monde à travers l\'objectif - Exposition photo en ligne',
        'location': 'En ligne, Valais',
        'date': '2026-02-09',
        'end_date': '2026-03-31',
        'time': None,
        'end_time': None,
        'description': 'Exposition photographique en ligne "Le monde à travers l\'objectif : trois approches photographiques en Valais". Avec les photographes Olivier Lovey, David Zehnder et Florence Zufferey, trois regards singuliers sur le Valais et le monde.',
        'categories': ['Culture', 'Exposition'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/41439',
        'organizer_name': 'Culture Valais',
        'latitude': 46.2328,
        'longitude': 7.3596,
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
