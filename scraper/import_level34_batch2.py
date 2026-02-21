"""
Import events from level 3-4 sources - Batch 2
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

events = [
    # ---- SIERRE.CH (suite) ----
    {
        'title': 'Concert apéritif du Conservatoire Cantonal - Sierre',
        'location': 'Château de Villa, Montée du Château 19, 3960 Sierre',
        'date': '2026-03-16',
        'end_date': '2026-03-16',
        'time': None,
        'end_time': None,
        'description': 'Concert apéritif offert par le Conservatoire Cantonal de Musique au Château de Villa à Sierre. Au programme : Lisa Bressoud-Biard à l\'accordéon, Elise Lehec au violon et alto, Didier Métrailler aux percussions et Manuel Castan à la guitare. Verrée offerte à la fin du concert. Entrée libre avec chapeau à la sortie.',
        'categories': ['Musique', 'Concert'],
        'source_url': 'https://www.sierre.ch/fr/calendrier-manifestations-1738/agenda-viewguidle-1146882929.html',
        'organizer_name': 'Conservatoire Cantonal de Musique',
        'latitude': 46.2905,
        'longitude': 7.5320,
        'status': 'auto_validated'
    },
    {
        'title': 'Vernissage Serge et Michel Kliaving - Espace 100 titres',
        'location': 'Espace 100 titres, Rue du Bourg 30, 3960 Sierre',
        'date': '2026-03-05',
        'end_date': '2026-04-25',
        'time': None,
        'end_time': None,
        'description': 'Vernissage de la nouvelle exposition de Serge et Michel Kliaving à l\'espace 100 titres de Sierre. L\'exposition se tiendra du 6 mars au 25 avril 2026. Vernissage le 5 mars.',
        'categories': ['Culture', 'Exposition'],
        'source_url': 'https://www.sierre.ch/fr/calendrier-manifestations-1738/agenda-viewguidle-1231561519.html',
        'organizer_name': 'Espace 100 titres Sierre',
        'latitude': 46.2923,
        'longitude': 7.5350,
        'status': 'auto_validated'
    },
    {
        'title': 'THE LOCOS + JOOL & THE COOLZ - Concert rock à Sierre',
        'location': 'Sierre, Rue du Bourg 30, 3960 Sierre',
        'date': '2026-03-28',
        'end_date': '2026-03-28',
        'time': None,
        'end_time': None,
        'description': 'Soirée rock à Sierre avec THE LOCOS, JOOL & THE COOLZ et ANARCHIST FOR PEACE. Trois groupes pour une soirée de rock et d\'énergie dans le centre de Sierre.',
        'categories': ['Musique', 'Concert'],
        'source_url': 'https://www.sierre.ch/fr/calendrier-manifestations-1738/agenda-viewguidle-1208104048.html',
        'organizer_name': 'Ville de Sierre',
        'latitude': 46.2923,
        'longitude': 7.5350,
        'status': 'auto_validated'
    },
    {
        'title': 'Exposition ABSTRACTION - Jean-Marc Linder à Sierre',
        'location': 'Sierre, 3960 Sierre',
        'date': '2026-02-13',
        'end_date': '2026-03-20',
        'time': None,
        'end_time': None,
        'description': 'Exposition d\'art abstrait de Jean-Marc Linder, artiste peintre sierrois résolument tourné vers l\'abstraction. Jean-Marc Linder explore l\'éphémère à travers ses oeuvres : une idée, un rêve, une émotion capturée sur toile.',
        'categories': ['Culture', 'Exposition'],
        'source_url': 'https://www.sierre.ch/fr/calendrier-manifestations-1738/agenda-viewguidle-1230898879.html',
        'organizer_name': 'Ville de Sierre',
        'latitude': 46.2920,
        'longitude': 7.5340,
        'status': 'auto_validated'
    },

    # ---- AGENDA.CULTUREVALAIS.CH (suite) ----
    {
        'title': 'Steps Festival : tanzmainz "Sphynx" - Théâtre du Crochetan',
        'location': 'Théâtre du Crochetan, Avenue du Théâtre 9, 1870 Monthey',
        'date': '2026-03-13',
        'end_date': '2026-03-13',
        'time': '20:00',
        'end_time': None,
        'description': 'Spectacle de danse dans le cadre du Festival Steps (Pour-cent culturel Migros). Quatorze danseurs de tanzmainz explorent le mouvement humain dans "Sphynx", chorégraphie primée (prix DER FAUST 2022) de Rafaële Giovanola. Marcher, courir, trébucher : chaque pas devient une fascinante interrogation sur notre humanité. Alliance d\'intelligence, de précision et d\'inventivité gestuelle.',
        'categories': ['Culture', 'Spectacle'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/38904',
        'organizer_name': 'Théâtre du Crochetan',
        'latitude': 46.2534,
        'longitude': 6.9564,
        'status': 'auto_validated'
    },
    {
        'title': 'La vérité - Florian Zeller au Théâtre du Martolet',
        'location': 'Théâtre du Martolet, Rue Charles-Emmanuel de Rivaz, 1890 St-Maurice',
        'date': '2026-03-18',
        'end_date': '2026-03-18',
        'time': '20:30',
        'end_time': None,
        'description': 'Pièce de Florian Zeller mise en scène par Ladislas Chollat. Avec Stéphane De Groodt, Sylvie Testud, Clotilde Courau et Stéphane Facco. Comédie brillante sur les mensonges et la vérité dans les relations de couples. Michel, menteur invétéré, tente de convaincre chacun des avantages de taire la vérité, mais la connaît-il vraiment lui-même ?',
        'categories': ['Culture', 'Spectacle'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/39100',
        'organizer_name': 'Saint-Maurice Tourisme',
        'latitude': 46.2195,
        'longitude': 7.0034,
        'status': 'auto_validated'
    },
    {
        'title': 'Schubertiade Sion - Trio Atanassov',
        'location': 'Maison de Wolff, Rue de Savièse 16, 1950 Sion',
        'date': '2026-04-03',
        'end_date': '2026-04-03',
        'time': '19:00',
        'end_time': '20:15',
        'description': 'Concert de musique de chambre avec le Trio Atanassov (Sarah Sultan au violoncelle, Perceval Gilles au violon, Pierre-Kaloyann Atanassov au piano). Formation distinguée depuis 2007, reconnue pour son intégrité et sa curiosité musicale. Au programme : oeuvres de Franz Schubert et George Onslow. Réservation recommandée.',
        'categories': ['Musique', 'Concert'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/42114',
        'organizer_name': 'Schubertiade Sion',
        'latitude': 46.2337,
        'longitude': 7.3586,
        'status': 'auto_validated'
    },
    {
        'title': 'Musique côté jardin - HEMU à la Fondation Louis Moret',
        'location': 'Fondation Louis Moret, Chemin des Barrières 33, 1920 Martigny',
        'date': '2026-03-01',
        'end_date': '2026-06-07',
        'time': '11:00',
        'end_time': None,
        'description': 'Série de concerts offerts par les musiciens de la HEMU dans le cadre enchanteur de la Fondation Louis Moret, espace dédié à l\'art contemporain avec jardin d\'arbres fruitiers. Quatre dimanches musicaux : 1er mars, 26 avril, 10 mai et 7 juin 2026 à 11h. Entrée libre.',
        'categories': ['Musique', 'Concert'],
        'source_url': 'https://agenda.culturevalais.ch/fr/event/show/41274',
        'organizer_name': 'HEMU - Haute Ecole de Musique',
        'latitude': 46.1025,
        'longitude': 7.0788,
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
