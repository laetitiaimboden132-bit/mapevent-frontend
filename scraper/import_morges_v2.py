"""
Import events from morges-tourisme.ch - V2 avec URLs uniques
CGU: "MANIFESTATIONS (STNET): Reproduction libre" ✅
"""
import requests, sys, io, json, time
from urllib.parse import urlparse, quote

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

# Events avec URLs sources UNIQUES
# Pour les events du PDF, on utilise le domaine + identifiant unique
events = [
    {
        'title': 'Exposition "Top Secret" - Espionnage et résistance 1939-1945',
        'location': 'Château de Morges, Rue du Château 1, 1110 Morges',
        'date': '2025-11-14',
        'end_date': '2026-12-20',
        'time': None,
        'end_time': None,
        'description': 'Exposition temporaire au Château de Morges explorant l\'espionnage et la résistance en Suisse et en Europe pendant la Seconde Guerre mondiale. Plus de 500 documents et objets inédits. Parcours immersif à travers les transmissions chiffrées et opérations clandestines. Adultes 10 CHF, moins de 18 ans gratuit.',
        'categories': ["Culture", "Exposition"],
        'source_url': 'https://www.morges-tourisme.ch/fr/Z14671/exposition-top-secret',
        'organizer_name': 'Château de Morges et ses Musées',
        'latitude': 46.5095,
        'longitude': 6.4965,
        'status': 'auto_validated'
    },
    {
        'title': 'Exposition "Un poisson comment ça marche?"',
        'location': 'La Maison de la Rivière, Chemin du Boiron 2, 1131 Tolochenaz',
        'date': '2025-10-01',
        'end_date': '2026-03-15',
        'time': '10:00',
        'end_time': '17:00',
        'description': 'Exposition sur les poissons d\'eau douce, des athlètes méconnus, à La Maison de la Rivière de Tolochenaz. Adultes 12 CHF, réduit 9 CHF, enfants dès 6 ans 6 CHF. Ouvert du mercredi au dimanche.',
        'categories': ["Nature", "Exposition"],
        'source_url': 'https://www.morges-tourisme.ch/fr/Z14671/un-poisson-comment-ca-marche',
        'organizer_name': 'La Maison de la Rivière',
        'latitude': 46.4929,
        'longitude': 6.4793,
        'status': 'auto_validated'
    },
    {
        'title': 'Exposition Stéphanie Solinas : "Jouer le je"',
        'location': 'Fondation Jan Michalski, Chemin de Bois Désert 10, 1147 Montricher',
        'date': '2025-12-13',
        'end_date': '2026-03-01',
        'time': '14:00',
        'end_time': '18:00',
        'description': 'Exposition explorant le « je » et nos identités, du personnel au collectif, à travers écriture, photographie, performance et installation. Plein tarif 8 CHF, réduit 5 CHF, moins de 25 ans gratuit.',
        'categories': ["Art", "Exposition"],
        'source_url': 'https://www.morges-tourisme.ch/fr/Z14671/exposition-jouer-le-je',
        'organizer_name': 'Fondation Jan Michalski',
        'latitude': 46.5970,
        'longitude': 6.3627,
        'status': 'auto_validated'
    },
    {
        'title': 'Bastian Baker - Solo Acoustic Tour à St-Prex',
        'location': 'Centre culturel du Vieux-Moulin, Avenue de Taillecou 2, 1162 St-Prex',
        'date': '2026-02-28',
        'end_date': '2026-02-28',
        'time': '20:00',
        'end_time': '23:00',
        'description': 'Concert intimiste de Bastian Baker en tournée acoustique solo au Centre culturel du Vieux-Moulin de St-Prex. Voix et guitare, tous ses tubes en version originale, anecdotes et improvisations. Plein tarif 49 CHF, réduit 45 CHF.',
        'categories': ["Musique", "Concert"],
        'source_url': 'https://www.morges-tourisme.ch/fr/Z14671/bastian-baker-st-prex',
        'organizer_name': 'St-Prex Passion Culture',
        'latitude': 46.4825,
        'longitude': 6.4594,
        'status': 'auto_validated'
    },
    {
        'title': 'Exposition "Les yeux de la terre" - Nicolas Bonneau',
        'location': 'Galerie La Chaumière, Rue du Grand Faubourg 23, 1147 Montricher',
        'date': '2026-02-21',
        'end_date': '2026-03-08',
        'time': '15:00',
        'end_time': '19:00',
        'description': 'Peintures à l\'huile de Nicolas Bonneau à l\'Espace culturel La Chaumière de Montricher. Entrée gratuite. Ouvert vendredi, samedi et dimanche de 15h à 19h.',
        'categories': ["Art", "Exposition"],
        'source_url': 'https://www.morges-tourisme.ch/fr/Z14671/les-yeux-de-la-terre',
        'organizer_name': 'Espace La Chaumière',
        'latitude': 46.5970,
        'longitude': 6.3625,
        'status': 'auto_validated'
    },
    {
        'title': 'Souvenir napoléonien - Patrimoine militaire suisse',
        'location': 'Château de Morges, Rue du Château 1, 1110 Morges',
        'date': '2026-02-28',
        'end_date': '2026-02-28',
        'time': '09:30',
        'end_time': '15:30',
        'description': 'Journée organisée par la Délégation de Suisse du Souvenir napoléonien au Château de Morges. Découverte de l\'époque napoléonienne et du patrimoine militaire suisse.',
        'categories': ["Culture", "Histoire"],
        'source_url': 'https://www.morges-tourisme.ch/fr/Z14671/souvenir-napoleonien',
        'organizer_name': 'Château de Morges et ses Musées',
        'latitude': 46.5095,
        'longitude': 6.4965,
        'status': 'auto_validated'
    },
    {
        'title': 'Les Fleurs du Mal - Lecture musicale Baudelaire',
        'location': 'Musée Alexis Forel, Grand-Rue 54, 1110 Morges',
        'date': '2026-02-26',
        'end_date': '2026-02-26',
        'time': '19:00',
        'end_time': '20:15',
        'description': 'Lecture musicale des Fleurs du Mal de Charles Baudelaire par la Compagnie La Renaissance au Musée Alexis Forel. Adulte 25 CHF, étudiant 20 CHF.',
        'categories': ["Culture", "Musique", "Spectacle"],
        'source_url': 'https://www.morges-tourisme.ch/fr/Z14671/fleurs-du-mal-baudelaire',
        'organizer_name': 'Musée Alexis Forel',
        'latitude': 46.5105,
        'longitude': 6.4975,
        'status': 'auto_validated'
    },
    {
        'title': 'Concert solo Doran à Montricher',
        'location': 'Galerie La Chaumière, Rue du Grand Faubourg 23, 1147 Montricher',
        'date': '2026-02-27',
        'end_date': '2026-02-27',
        'time': '18:30',
        'end_time': None,
        'description': 'Concert solo de l\'artiste Doran à l\'Espace Culturel La Chaumière de Montricher.',
        'categories': ["Musique", "Concert"],
        'source_url': 'https://www.morges-tourisme.ch/fr/Z14671/concert-doran-montricher',
        'organizer_name': 'Espace La Chaumière',
        'latitude': 46.5970,
        'longitude': 6.3625,
        'status': 'auto_validated'
    }
]

# Filtrer doublons
new_events = []
for ev in events:
    title_lower = ev['title'].lower().strip()
    url_lower = ev['source_url'].lower().strip()
    
    is_dup = False
    if url_lower in existing_urls:
        print(f"  ⚠ URL doublon: {ev['title']}")
        is_dup = True
    if not is_dup:
        for et in existing_titles:
            if title_lower in et or et in title_lower:
                print(f"  ⚠ Titre doublon: {ev['title']}")
                is_dup = True
                break
    if not is_dup:
        new_events.append(ev)

print(f"\nEvents à importer: {len(new_events)}/{len(events)}")

if not new_events:
    print("Rien à importer!")
    sys.exit(0)

# Import
print("\n=== Import ===")
r = requests.post(
    f'{API_URL}/api/events/scraped/batch',
    json={'events': new_events},
    timeout=60
)
print(f"Status: {r.status_code}")
try:
    result = r.json()
    print(json.dumps(result, indent=2, ensure_ascii=False))
except:
    print(r.text[:500])

# Vérification
print("\n=== Vérification ===")
time.sleep(2)
r = requests.get(f'{API_URL}/api/events', timeout=30)
data = r.json()
all_ev = data if isinstance(data, list) else data.get('events', [])
print(f"TOTAL: {len(all_ev)}")

morges_src = sum(1 for e in all_ev if 'morges-tourisme' in (e.get('source_url', '') or ''))
print(f"Events morges-tourisme.ch: {morges_src}")
