"""
Import events from morges-tourisme.ch
CGU: "MANIFESTATIONS (STNET): Reproduction libre" ✅
Source: PDF agenda guidle.com + pages événements morges-tourisme.ch
On prend 80% max des events disponibles (autorisé par reproduction libre)
"""
import requests, sys, io, json, time
from urllib.parse import urlparse

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'
NOMINATIM_URL = 'https://nominatim.openstreetmap.org/search'
HEADERS = {'User-Agent': 'MapEventAI/1.0 (contact@mapevent.ai)'}

def geocode(address, fallback_lat=None, fallback_lon=None):
    """Géocode une adresse via Nominatim"""
    try:
        time.sleep(1.5)
        params = {'q': address, 'format': 'json', 'limit': 1, 'countrycodes': 'ch'}
        r = requests.get(NOMINATIM_URL, params=params, headers=HEADERS, timeout=10)
        results = r.json()
        if results:
            return float(results[0]['lat']), float(results[0]['lon'])
    except Exception as e:
        print(f"  ⚠ Geocoding error for '{address}': {e}")
    
    if fallback_lat and fallback_lon:
        return fallback_lat, fallback_lon
    return None, None

# === EVENTS CONFIRMÉS DE MORGES-TOURISME.CH ===
# Source: PDF guidle.com février 2026 + pages web morges-tourisme.ch
# Toutes les infos viennent directement du site source
events = []

# 1. Exposition "Top Secret" - Château de Morges
# Source PDF: "Exposition temporaire Top Secret - Espionnage et résistance en Suisse et en Europe 1939-1945"
# Dates confirmées: jusqu'au 20/12/2026
events.append({
    'title': 'Exposition "Top Secret" - Espionnage et résistance 1939-1945',
    'location': 'Château de Morges, Rue du Château 1, 1110 Morges',
    'date': '2025-11-14',
    'end_date': '2026-12-20',
    'time': None,
    'end_time': None,
    'description': 'Exposition temporaire au Château de Morges explorant l\'espionnage et la résistance en Suisse et en Europe pendant la Seconde Guerre mondiale (1939-1945). Plus de 500 documents et objets inédits. Parcours immersif à travers les transmissions chiffrées, filières d\'évasion et opérations clandestines. Adultes 10 CHF, moins de 18 ans gratuit.',
    'categories': ["Culture", "Exposition"],
    'source_url': 'https://www.morges-tourisme.ch/fr/Z14671/agenda',
    'organizer_name': 'Château de Morges et ses Musées',
    'fallback_lat': 46.5095,
    'fallback_lon': 6.4965
})

# 2. "Un poisson comment ça marche?" - Maison de la Rivière
# Source PDF: "Poissons d'eau douce, des athlètes méconnus"
events.append({
    'title': 'Exposition "Un poisson comment ça marche?"',
    'location': 'La Maison de la Rivière, Chemin du Boiron 2, 1131 Tolochenaz',
    'date': '2025-10-01',
    'end_date': '2026-03-15',
    'time': '10:00',
    'end_time': '17:00',
    'description': 'Exposition interactive sur les poissons d\'eau douce à La Maison de la Rivière de Tolochenaz. Découvrez ces athlètes méconnus. Adultes 12 CHF, réduit 9 CHF, enfants dès 6 ans 6 CHF. Ouvert du mercredi au dimanche.',
    'categories': ["Nature", "Exposition"],
    'source_url': 'https://www.morges-tourisme.ch/fr/Z14671/agenda',
    'organizer_name': 'La Maison de la Rivière',
    'fallback_lat': 46.4738,
    'fallback_lon': 6.4590
})

# 3. Exposition Stéphanie Solinas "Jouer le je"
# Source PDF: Fondation Jan Michalski
events.append({
    'title': 'Exposition Stéphanie Solinas : "Jouer le je"',
    'location': 'Fondation Jan Michalski, Chemin de Bois Désert 10, 1147 Montricher',
    'date': '2025-12-13',
    'end_date': '2026-03-01',
    'time': '14:00',
    'end_time': '18:00',
    'description': 'L\'exposition interroge le « je » et nos identités, du personnel au collectif, à travers l\'écriture, la photographie, la performance et l\'installation. Plein tarif 8 CHF, réduit 5 CHF, moins de 25 ans gratuit. Ouvert ma-ve 14h-18h, sa-di 11h-18h.',
    'categories': ["Art", "Exposition"],
    'source_url': 'https://www.morges-tourisme.ch/fr/Z14671/agenda',
    'organizer_name': 'Fondation Jan Michalski',
    'fallback_lat': 46.5970,
    'fallback_lon': 6.3627
})

# 4. Bastian Baker - Solo Acoustic Tour
# Source PDF: Concert intimiste dans le cadre de St-Prex Passion Culture
events.append({
    'title': 'Bastian Baker - Solo Acoustic Tour',
    'location': 'Centre culturel et sportif du Vieux-Moulin, Avenue de Taillecou 2, 1162 St-Prex',
    'date': '2026-02-28',
    'end_date': '2026-02-28',
    'time': '20:00',
    'end_time': '23:00',
    'description': 'Concert intimiste de Bastian Baker en tournée acoustique solo. L\'artiste vaudois se produit voix et guitare avec tous ses tubes en version originale, anecdotes de tournées, interactions et improvisations. Plein tarif 49 CHF, réduit 45 CHF.',
    'categories': ["Musique", "Concert"],
    'source_url': 'https://www.morges-tourisme.ch/fr/Z14671/agenda',
    'organizer_name': 'St-Prex Passion Culture',
    'fallback_lat': 46.4825,
    'fallback_lon': 6.4594
})

# 5. Exposition "Les yeux de la terre"
# Source PDF: Peintures à l'huile de Nicolas Bonneau
events.append({
    'title': 'Exposition "Les yeux de la terre" - Nicolas Bonneau',
    'location': 'Galerie La Chaumière, Rue du Grand Faubourg 23, 1147 Montricher',
    'date': '2026-02-21',
    'end_date': '2026-03-08',
    'time': '15:00',
    'end_time': '19:00',
    'description': 'Exposition de peintures à l\'huile de Nicolas Bonneau à l\'Espace culturel La Chaumière de Montricher. Entrée gratuite. Ouvert vendredi, samedi et dimanche de 15h à 19h.',
    'categories': ["Art", "Exposition"],
    'source_url': 'https://www.morges-tourisme.ch/fr/Z14671/agenda',
    'organizer_name': 'Espace La Chaumière',
    'fallback_lat': 46.5970,
    'fallback_lon': 6.3625
})

# 6. Festival Morges-sous-Rire 2026
# Source: morges-sous-rire.ch confirmé via morges-tourisme.ch/festivals
events.append({
    'title': 'Festival Morges-sous-Rire 2026',
    'location': 'Théâtre de Beausobre, Avenue de Vertou 2, 1110 Morges',
    'date': '2026-06-06',
    'end_date': '2026-06-12',
    'time': None,
    'end_time': None,
    'description': 'Festival d\'humour majeur de Morges. 8 jours de programmation avec 45 humoristes sur 3 scènes (Le Théâtre, Le CUBE, La Paille). Stand-up, improvisation et performances hybrides. Avec David Castello-Lopes, Nora Hamzawi, Alex Lutz, Laurent Gerra, Chantal Ladesou, Booder et bien d\'autres.',
    'categories': ["Festival", "Humour", "Spectacle"],
    'source_url': 'https://www.morges-tourisme.ch/fr/G4569/festivals',
    'organizer_name': 'Morges-sous-Rire',
    'fallback_lat': 46.5120,
    'fallback_lon': 6.4990
})

# 7. Festival International Classique & Lyrique de Morges 2026
# Source: morges.festivalclassiquelyrique.art, promu sur morges-tourisme.ch
events.append({
    'title': 'Festival International Classique & Lyrique de Morges 2026',
    'location': 'Temple de Morges, Grand-Rue, 1110 Morges',
    'date': '2026-04-25',
    'end_date': '2026-04-30',
    'time': None,
    'end_time': None,
    'description': 'Festival de musique classique et lyrique au Temple et au Cube de Morges. Concert d\'ouverture "Rachmaninov" avec Alexey Botvinov (piano), Anna Orlik (violon) et Constantin Macherel (violoncelle). Concerts gratuits "Interstice", Opera Night Club et concert de clôture vintage.',
    'categories': ["Musique", "Festival", "Culture"],
    'source_url': 'https://www.morges-tourisme.ch/fr/G4569/festivals',
    'organizer_name': 'Festival Classique & Lyrique de Morges',
    'fallback_lat': 46.5100,
    'fallback_lon': 6.4978
})

# 8. Délégation de Suisse du Souvenir napoléonien
# Source PDF: Château de Morges
events.append({
    'title': 'Souvenir napoléonien - Patrimoine militaire suisse',
    'location': 'Château de Morges, Rue du Château 1, 1110 Morges',
    'date': '2026-02-28',
    'end_date': '2026-02-28',
    'time': '09:30',
    'end_time': '15:30',
    'description': 'Journée organisée par la Délégation de Suisse du Souvenir napoléonien au Château de Morges. Découvrez des aspects fascinants de l\'époque napoléonienne et du patrimoine militaire suisse.',
    'categories': ["Culture", "Histoire"],
    'source_url': 'https://www.morges-tourisme.ch/fr/Z14671/agenda',
    'organizer_name': 'Château de Morges et ses Musées',
    'fallback_lat': 46.5095,
    'fallback_lon': 6.4965
})

# 9. Programme musical "Les Fleurs du Mal"
# Source PDF: Lecture musicale Baudelaire, Musée Alexis Forel
events.append({
    'title': 'Les Fleurs du Mal - Lecture musicale Baudelaire',
    'location': 'Musée Alexis Forel, Grand-Rue 54, 1110 Morges',
    'date': '2026-02-26',
    'end_date': '2026-02-26',
    'time': '19:00',
    'end_time': '20:15',
    'description': 'Lecture musicale des Fleurs du Mal de Charles Baudelaire par la Compagnie La Renaissance au Musée Alexis Forel de Morges. Tarif adulte 25 CHF, étudiant 20 CHF.',
    'categories': ["Culture", "Musique", "Spectacle"],
    'source_url': 'https://www.morges-tourisme.ch/fr/Z14671/agenda',
    'organizer_name': 'Musée Alexis Forel',
    'fallback_lat': 46.5105,
    'fallback_lon': 6.4975
})

# 10. Concert solo Doran - Montricher
# Source PDF: Concert solo de Doran à l'Espace Culturel La Chaumière
events.append({
    'title': 'Concert solo Doran',
    'location': 'Galerie La Chaumière, Rue du Grand Faubourg 23, 1147 Montricher',
    'date': '2026-02-27',
    'end_date': '2026-02-27',
    'time': '18:30',
    'end_time': None,
    'description': 'Concert solo de l\'artiste Doran à l\'Espace Culturel La Chaumière de Montricher.',
    'categories': ["Musique", "Concert"],
    'source_url': 'https://www.morges-tourisme.ch/fr/Z14671/agenda',
    'organizer_name': 'Espace La Chaumière',
    'fallback_lat': 46.5970,
    'fallback_lon': 6.3625
})

# === VÉRIFICATION DOUBLONS ===
print("=== Vérification doublons ===")
r = requests.get(f'{API_URL}/api/events', timeout=30)
data = r.json()
existing = data if isinstance(data, list) else data.get('events', [])
existing_titles = [e.get('title', '').lower().strip() for e in existing]
existing_urls = [e.get('source_url', '').lower().strip() for e in existing]
print(f"Events existants: {len(existing)}")

new_events = []
for ev in events:
    title_lower = ev['title'].lower().strip()
    # Check duplicates
    is_dup = False
    for et in existing_titles:
        if title_lower in et or et in title_lower:
            print(f"  ⚠ DOUBLON: '{ev['title']}' ≈ existant")
            is_dup = True
            break
    if not is_dup:
        new_events.append(ev)

print(f"\nEvents à importer: {len(new_events)}/{len(events)}")

if not new_events:
    print("Rien à importer!")
    sys.exit(0)

# === GÉOCODAGE ===
print("\n=== Géocodage ===")
api_events = []
for ev in new_events:
    loc = ev['location']
    fb_lat = ev.pop('fallback_lat', None)
    fb_lon = ev.pop('fallback_lon', None)
    
    lat, lon = geocode(loc, fb_lat, fb_lon)
    if lat is None:
        # Essai avec juste la ville
        city = loc.split(',')[-1].strip()
        lat, lon = geocode(city, fb_lat, fb_lon)
    
    if lat and lon:
        print(f"  ✓ {ev['title'][:50]}: {lat:.4f}, {lon:.4f}")
        api_events.append({
            'title': ev['title'],
            'location': ev['location'],
            'date': ev['date'],
            'end_date': ev.get('end_date'),
            'time': ev.get('time'),
            'end_time': ev.get('end_time'),
            'description': ev['description'],
            'categories': ev['categories'],
            'source_url': ev['source_url'],
            'organizer_name': ev.get('organizer_name'),
            'latitude': lat,
            'longitude': lon,
            'status': 'auto_validated'
        })
    else:
        print(f"  ✗ ÉCHEC géocodage: {ev['title']}")

print(f"\nEvents géocodés: {len(api_events)}/{len(new_events)}")

# === IMPORT ===
if api_events:
    print("\n=== Import via API ===")
    r = requests.post(
        f'{API_URL}/api/events/scraped/batch',
        json={'events': api_events},
        timeout=60
    )
    print(f"Status: {r.status_code}")
    try:
        result = r.json()
        print(f"Résultat: {json.dumps(result, indent=2, ensure_ascii=False)[:500]}")
    except:
        print(f"Response: {r.text[:300]}")

# === VÉRIFICATION FINALE ===
print("\n=== Vérification finale ===")
time.sleep(2)
r = requests.get(f'{API_URL}/api/events', timeout=30)
data = r.json()
all_events = data if isinstance(data, list) else data.get('events', [])
print(f"TOTAL EVENTS: {len(all_events)}")

# Morges region
morges_count = sum(1 for e in all_events if 'morges' in (e.get('location', '') or '').lower() 
                   or 'tolochenaz' in (e.get('location', '') or '').lower()
                   or 'montricher' in (e.get('location', '') or '').lower()
                   or 'st-prex' in (e.get('location', '') or '').lower()
                   or 'eclépens' in (e.get('location', '') or '').lower())
print(f"Events région Morges: {morges_count}")

# Par source morges-tourisme
mt_count = sum(1 for e in all_events if 'morges-tourisme' in (e.get('source_url', '') or ''))
print(f"Events source morges-tourisme.ch: {mt_count}")
