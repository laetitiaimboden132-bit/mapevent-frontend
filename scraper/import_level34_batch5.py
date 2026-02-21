"""
Import events from level 3-4 sources - Batch 5
Sources: morges-tourisme.ch (reproduction libre 80%), agenda.culturevalais.ch
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
    # ---- MORGES-TOURISME.CH (reproduction libre, max 80%) ----
    {
        'title': 'Fête de la Tulipe 2026 - Morges',
        'location': 'Parc de l\'Indépendance, Quai Lochmann, 1110 Morges',
        'date': '2026-03-27',
        'end_date': '2026-05-10',
        'time': None,
        'end_time': None,
        'description': '56e édition de la Fête de la Tulipe à Morges, placée sous le thème enchanteur des "Contes et Légendes". Plus de 140 000 fleurs et près de 350 variétés de tulipes mises en scène dans le Parc de l\'Indépendance et les rues de la ville. Entrée gratuite au parc.',
        'categories': ['Nature', 'Fête'],
        'source_url': 'https://www.morges-tourisme.ch/fr/Z14689/fete-de-la-tulipe',
        'organizer_name': 'Morges Région Tourisme',
        'latitude': 46.5078,
        'longitude': 6.4980,
        'status': 'auto_validated'
    },
    {
        'title': 'Bastian Baker - Tournée acoustique solo à St-Prex',
        'location': 'Centre culturel du Vieux-Moulin, Avenue de Taillecou 2, 1162 St-Prex',
        'date': '2026-02-28',
        'end_date': '2026-02-28',
        'time': '20:00',
        'end_time': '23:00',
        'description': 'Bastian Baker en tournée acoustique solo au Centre culturel du Vieux-Moulin de St-Prex. Concert intimiste dans le cadre de St-Prex Passion Culture. L\'artiste suisse se produit dans un format épuré et proche du public. Billets : plein tarif 49 CHF, réduit 45 CHF.',
        'categories': ['Musique', 'Concert'],
        'source_url': 'https://www.morges-tourisme.ch/fr/Z14671/bastian-baker-tournee-solo',
        'organizer_name': 'St-Prex Passion Culture',
        'latitude': 46.4827,
        'longitude': 6.4582,
        'status': 'auto_validated'
    },
    {
        'title': 'Exposition Stéphanie Solinas "Jouer le je" - Fondation Michalski',
        'location': 'Fondation Jan Michalski, Chemin de Bois Désert 10, 1147 Montricher',
        'date': '2026-01-15',
        'end_date': '2026-03-01',
        'time': '11:00',
        'end_time': '18:00',
        'description': 'Exposition de Stéphanie Solinas intitulée "Jouer le je" à la Fondation Jan Michalski de Montricher. L\'artiste interroge le "je" et nos identités multiples, du personnel au collectif, à travers différents médiums artistiques. Plein tarif 8 CHF, gratuit pour les moins de 25 ans.',
        'categories': ['Culture', 'Exposition'],
        'source_url': 'https://www.morges-tourisme.ch/fr/Z14671/stephanie-solinas-jouer-le-je',
        'organizer_name': 'Fondation Jan Michalski',
        'latitude': 46.5940,
        'longitude': 6.3710,
        'status': 'auto_validated'
    },
    {
        'title': 'Les Fleurs du Mal - Lecture musicale au Musée Forel Morges',
        'location': 'Musée Alexis Forel, Grand-Rue 54, 1110 Morges',
        'date': '2026-02-26',
        'end_date': '2026-02-26',
        'time': '19:00',
        'end_time': '20:15',
        'description': 'Lecture musicale de "Les Fleurs du Mal" de Charles Baudelaire par la Compagnie La Renaissance au Musée Alexis Forel de Morges. Une soirée mêlant littérature et musique dans le cadre historique du musée. Tarif adulte 25 CHF, étudiant 20 CHF.',
        'categories': ['Culture', 'Spectacle'],
        'source_url': 'https://www.morges-tourisme.ch/fr/Z14671/fleurs-du-mal-musee-forel',
        'organizer_name': 'Musée Alexis Forel',
        'latitude': 46.5112,
        'longitude': 6.4988,
        'status': 'auto_validated'
    },
    {
        'title': 'Exposition "Les yeux de la terre" - Galerie La Chaumière',
        'location': 'Galerie La Chaumière, Rue du Grand Faubourg 23, 1147 Montricher',
        'date': '2026-02-21',
        'end_date': '2026-03-08',
        'time': '15:00',
        'end_time': '19:00',
        'description': 'Exposition des peintures à l\'huile de Nicolas Bonneau à l\'Espace culturel de la Chaumière à Montricher. "Les yeux de la terre" offre un regard sensible sur la nature et les paysages. Entrée gratuite. Ouvert les vendredis, samedis et dimanches.',
        'categories': ['Culture', 'Exposition'],
        'source_url': 'https://www.morges-tourisme.ch/fr/Z14671/les-yeux-de-la-terre',
        'organizer_name': 'Espace La Chaumière',
        'latitude': 46.5955,
        'longitude': 6.3727,
        'status': 'auto_validated'
    },
    {
        'title': 'Concerts Classiques de la Région Morgienne',
        'location': 'CCRM, Rue de la Tour 2, 1162 St-Prex',
        'date': '2026-02-08',
        'end_date': '2026-02-08',
        'time': '17:00',
        'end_time': '19:00',
        'description': 'Concert de musique classique organisé par les Concerts Classiques de la Région Morgienne (CCRM) à St-Prex. Une programmation de qualité dans un cadre intime au coeur de la côte vaudoise.',
        'categories': ['Musique', 'Concert'],
        'source_url': 'https://www.morges-tourisme.ch/fr/Z14671/ccrm-concerts-classiques',
        'organizer_name': 'CCRM',
        'latitude': 46.4845,
        'longitude': 6.4600,
        'status': 'auto_validated'
    },
    {
        'title': 'Délégation du Souvenir napoléonien - Château de Morges',
        'location': 'Château de Morges, Rue du Château 1, 1110 Morges',
        'date': '2026-02-28',
        'end_date': '2026-02-28',
        'time': '09:30',
        'end_time': '15:30',
        'description': 'Journée organisée par la Délégation de Suisse du Souvenir napoléonien au Château de Morges. Découvrez des aspects fascinants de l\'époque napoléonienne et du patrimoine militaire suisse à travers conférences et présentations.',
        'categories': ['Culture', 'Conférence'],
        'source_url': 'https://www.morges-tourisme.ch/fr/Z14671/souvenir-napoleonien-morges',
        'organizer_name': 'Château de Morges et ses Musées',
        'latitude': 46.5095,
        'longitude': 6.4965,
        'status': 'auto_validated'
    },
    {
        'title': 'Jakadi Comedy Club - Stand-up à Morges',
        'location': 'Lykke café-bar-boutique, Grand-Rue 89, 1110 Morges',
        'date': '2026-02-27',
        'end_date': '2026-02-27',
        'time': '20:00',
        'end_time': '21:00',
        'description': 'Soirée stand-up comedy avec le Jakadi Comedy Club au Lykke de Morges. Humoristes confirmés, talents locaux et artistes émergents se succèdent sur scène pour des rires garantis du début à la fin.',
        'categories': ['Culture', 'Spectacle'],
        'source_url': 'https://www.morges-tourisme.ch/fr/Z14671/jakadi-comedy-club-morges',
        'organizer_name': 'Lykke concept store',
        'latitude': 46.5108,
        'longitude': 6.4975,
        'status': 'auto_validated'
    },

    # ---- AGENDA.CULTUREVALAIS.CH (suite - Maxi-Rires détaillé) ----
    {
        'title': 'Maxi-Rires Festival 2026 - Programme détaillé Champéry',
        'location': 'Palladium de Champéry, Route du Centre Sportif 1, 1874 Champéry',
        'date': '2026-03-23',
        'end_date': '2026-03-28',
        'time': '19:00',
        'end_time': None,
        'description': 'Semaine d\'humour au Palladium de Champéry avec la crème des humoristes francophones. Au programme : Gus, Marine Leonardi, Olivier de Benoist, David Castello Lopes, Thomas Wiesel, Camille Lellouche et Dany Boon en clôture le samedi. Une semaine d\'éclats de rires dans un cadre alpin exceptionnel.',
        'categories': ['Culture', 'Spectacle'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/41502',
        'organizer_name': 'Maxi-Rires Festival',
        'latitude': 46.1751,
        'longitude': 6.8717,
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
