"""
Import events from level 3-4 sources - Batch 9
Sources: lausanne (musées publics), morges.ch, artbrut.ch, olympics.com
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
    # ---- LAUSANNE - Musées publics ----
    {
        'title': 'Exposition "Art Brut Suisse" - 50 ans de la Collection Lausanne',
        'location': 'Collection de l\'Art Brut, Avenue des Bergières 11, 1004 Lausanne',
        'date': '2026-02-28',
        'end_date': '2026-09-27',
        'time': '11:00',
        'end_time': '18:00',
        'description': 'Pour ses 50 ans, la Collection de l\'Art Brut de Lausanne présente "Art Brut Suisse", une exposition anniversaire d\'oeuvres exclusivement issues de ses collections. Dessins, peintures, sculptures, broderies et assemblages d\'auteurs suisses, du noyau historique de Jean Dubuffet aux créations contemporaines. Un demi-siècle de création hors normes.',
        'categories': ['Culture', 'Exposition'],
        'source_url': 'https://www.artbrut.ch/fr_CH/expositions/art-brut-suisse-50-ans',
        'organizer_name': 'Collection de l\'Art Brut',
        'latitude': 46.5250,
        'longitude': 6.6240,
        'status': 'auto_validated'
    },
    {
        'title': '"Longueurs d\'avance" - Un siècle d\'innovations olympiques - Lausanne',
        'location': 'Musée Olympique, Quai d\'Ouchy 1, 1006 Lausanne',
        'date': '2025-09-18',
        'end_date': '2026-11-01',
        'time': '09:00',
        'end_time': '18:00',
        'description': 'Exposition temporaire "Longueurs d\'avance" au Musée Olympique de Lausanne, célébrant un siècle d\'innovations aux Jeux Olympiques. Des premières technologies aux avancées de pointe, découvrez comment l\'innovation a transformé le sport et les Jeux.',
        'categories': ['Sport', 'Exposition'],
        'source_url': 'https://www.olympics.com/musee/expositions/longueurs-avance',
        'organizer_name': 'Musée Olympique',
        'latitude': 46.5082,
        'longitude': 6.6340,
        'status': 'auto_validated'
    },
    # ---- MORGES.CH (site communal) ----
    {
        'title': 'Exposition Top Secret - Espionnage et résistance au Château de Morges',
        'location': 'Château de Morges, Rue du Château 1, 1110 Morges',
        'date': '2026-01-01',
        'end_date': '2026-12-20',
        'time': '10:00',
        'end_time': '17:00',
        'description': 'Exposition temporaire "Top Secret - Espionnage et résistance en Suisse et en Europe 1939-1945" au Château de Morges et ses Musées. Plongez dans l\'univers secret des espions et résistants pendant la Seconde Guerre mondiale. Adultes 10 CHF, gratuit pour les moins de 18 ans et le premier dimanche du mois.',
        'categories': ['Culture', 'Exposition'],
        'source_url': 'https://www.morges.ch/agenda/exposition-top-secret-2026',
        'organizer_name': 'Château de Morges et ses Musées',
        'latitude': 46.5095,
        'longitude': 6.4965,
        'status': 'auto_validated'
    },
    {
        'title': '"Un poisson comment ça marche?" - Exposition à la Maison de la Rivière',
        'location': 'La Maison de la Rivière, Chemin du Boiron 2, 1131 Tolochenaz',
        'date': '2025-11-01',
        'end_date': '2026-03-15',
        'time': '10:00',
        'end_time': '17:00',
        'description': 'Exposition interactive "Un poisson comment ça marche?" à la Maison de la Rivière de Tolochenaz. Poissons d\'eau douce, ces athlètes méconnus : découvrez leurs capacités extraordinaires à travers une exposition ludique et scientifique. Ouvert mercredi à dimanche.',
        'categories': ['Nature', 'Exposition'],
        'source_url': 'https://www.morges-tourisme.ch/fr/Z14671/un-poisson-comment-ca-marche',
        'organizer_name': 'La Maison de la Rivière',
        'latitude': 46.4967,
        'longitude': 6.4733,
        'status': 'auto_validated'
    },
    # ---- EVENEMENTS.GENEVE.CH (site communal) ----
    {
        'title': 'Geneva Lux 2026 - Festival de lumières Genève',
        'location': 'Rade de Genève et Vieille-Ville, Quai Gustave-Ador, 1207 Genève',
        'date': '2026-01-16',
        'end_date': '2026-02-01',
        'time': '18:00',
        'end_time': '23:00',
        'description': '12e édition du festival de lumières Geneva Lux. 17 oeuvres lumineuses illuminent la Rade et la Vieille-Ville. Parmi les nouveautés : "Ondulations", une oeuvre laser sur écran d\'eau, et "Halo", un spectacle immersif et musical dans la Cathédrale Saint-Pierre.',
        'categories': ['Culture', 'Festival'],
        'source_url': 'https://evenements.geneve.ch/genevalux-oeuvres/home',
        'organizer_name': 'Ville de Genève',
        'latitude': 46.2044,
        'longitude': 6.1500,
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
