# -*- coding: utf-8 -*-
"""
Import de musiciens Audius dans la section Booking de MapEventAI.
Source : Audius API (100% gratuit, zero rate limit)
Audio : Streaming MP3 direct depuis Audius

Les artistes sont géolocalisés via leur profil Audius + geocoding Nominatim.
Seuls les artistes avec une localisation en France/Suisse/Belgique sont importés.
"""

import sys
import json
import requests
import time
import re

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'
AUDIUS_BASE = 'https://api.audius.co/v1'
AUDIUS_FULL = 'https://api.audius.co/v1/full'
APP_NAME = 'MapEvent'

# ============================================================
# VILLES ET PAYS CIBLES pour géolocalisation
# ============================================================

# Mots-clés de localisation MONDE ENTIER (case-insensitive)
WORLD_KEYWORDS = {
    # Europe
    # France - villes
    'paris': (48.8566, 2.3522, 'Paris, France'),
    'lyon': (45.7640, 4.8357, 'Lyon, France'),
    'marseille': (43.2965, 5.3698, 'Marseille, France'),
    'toulouse': (43.6047, 1.4442, 'Toulouse, France'),
    'lille': (50.6292, 3.0573, 'Lille, France'),
    'bordeaux': (44.8378, -0.5792, 'Bordeaux, France'),
    'nantes': (47.2184, -1.5536, 'Nantes, France'),
    'strasbourg': (48.5734, 7.7521, 'Strasbourg, France'),
    'montpellier': (43.6108, 3.8767, 'Montpellier, France'),
    'nice': (43.7102, 7.2620, 'Nice, France'),
    'rennes': (48.1173, -1.6778, 'Rennes, France'),
    'grenoble': (45.1885, 5.7245, 'Grenoble, France'),
    'dijon': (47.3220, 5.0415, 'Dijon, France'),
    'annecy': (45.8992, 6.1294, 'Annecy, France'),
    'avignon': (43.9493, 4.8055, 'Avignon, France'),
    'rouen': (49.4432, 1.0993, 'Rouen, France'),
    'clermont': (45.7772, 3.0870, 'Clermont-Ferrand, France'),
    'nancy': (48.6921, 6.1844, 'Nancy, France'),
    'metz': (49.1193, 6.1757, 'Metz, France'),
    'reims': (49.2583, 4.0317, 'Reims, France'),
    'tours': (47.3941, 0.6848, 'Tours, France'),
    'caen': (49.1829, -0.3707, 'Caen, France'),
    'orléans': (47.9029, 1.9039, 'Orléans, France'),
    'orleans': (47.9029, 1.9039, 'Orléans, France'),
    'perpignan': (42.6887, 2.8948, 'Perpignan, France'),
    'brest': (48.3904, -4.4861, 'Brest, France'),
    'toulon': (43.1242, 5.9280, 'Toulon, France'),
    # France - régions
    'occitanie': (43.6047, 1.4442, 'Toulouse, Occitanie, France'),
    'île-de-france': (48.8566, 2.3522, 'Paris, Île-de-France, France'),
    'ile-de-france': (48.8566, 2.3522, 'Paris, Île-de-France, France'),
    'bretagne': (48.1173, -1.6778, 'Rennes, Bretagne, France'),
    'provence': (43.2965, 5.3698, 'Marseille, Provence, France'),
    'normandie': (49.1829, -0.3707, 'Caen, Normandie, France'),
    'alsace': (48.5734, 7.7521, 'Strasbourg, Alsace, France'),
    # France - pays
    'france': (48.8566, 2.3522, 'France'),
    'french': (48.8566, 2.3522, 'France'),
    # Suisse
    'genève': (46.2044, 6.1432, 'Genève, Suisse'),
    'geneve': (46.2044, 6.1432, 'Genève, Suisse'),
    'geneva': (46.2044, 6.1432, 'Genève, Suisse'),
    'lausanne': (46.5197, 6.6323, 'Lausanne, Suisse'),
    'zurich': (47.3769, 8.5417, 'Zurich, Suisse'),
    'zürich': (47.3769, 8.5417, 'Zurich, Suisse'),
    'berne': (46.9480, 7.4474, 'Berne, Suisse'),
    'bern': (46.9480, 7.4474, 'Berne, Suisse'),
    'basel': (47.5596, 7.5886, 'Bâle, Suisse'),
    'bâle': (47.5596, 7.5886, 'Bâle, Suisse'),
    'sion': (46.2298, 7.3607, 'Sion, Suisse'),
    'montreux': (46.4312, 6.9107, 'Montreux, Suisse'),
    'fribourg': (46.8065, 7.1620, 'Fribourg, Suisse'),
    'neuchâtel': (46.9900, 6.9293, 'Neuchâtel, Suisse'),
    'neuchatel': (46.9900, 6.9293, 'Neuchâtel, Suisse'),
    'lucerne': (47.0502, 8.3093, 'Lucerne, Suisse'),
    'luzern': (47.0502, 8.3093, 'Lucerne, Suisse'),
    'nyon': (46.3833, 6.2396, 'Nyon, Suisse'),
    'vevey': (46.4603, 6.8428, 'Vevey, Suisse'),
    'switzerland': (46.8182, 8.2275, 'Suisse'),
    'suisse': (46.8182, 8.2275, 'Suisse'),
    'swiss': (46.8182, 8.2275, 'Suisse'),
    'helvétique': (46.8182, 8.2275, 'Suisse'),
    'helvetique': (46.8182, 8.2275, 'Suisse'),
    # Belgique
    'bruxelles': (50.8503, 4.3517, 'Bruxelles, Belgique'),
    'brussels': (50.8503, 4.3517, 'Bruxelles, Belgique'),
    'liège': (50.6326, 5.5797, 'Liège, Belgique'),
    'liege': (50.6326, 5.5797, 'Liège, Belgique'),
    'anvers': (51.2194, 4.4025, 'Anvers, Belgique'),
    'antwerp': (51.2194, 4.4025, 'Anvers, Belgique'),
    'gand': (51.0543, 3.7174, 'Gand, Belgique'),
    'ghent': (51.0543, 3.7174, 'Gand, Belgique'),
    'namur': (50.4669, 4.8675, 'Namur, Belgique'),
    'charleroi': (50.4108, 4.4446, 'Charleroi, Belgique'),
    'mons': (50.4542, 3.9563, 'Mons, Belgique'),
    'bruges': (51.2093, 3.2247, 'Bruges, Belgique'),
    'belgium': (50.8503, 4.3517, 'Belgique'),
    'belgique': (50.8503, 4.3517, 'Belgique'),
    'belgian': (50.8503, 4.3517, 'Belgique'),
    # Pays voisins intéressants
    'london': (51.5074, -0.1278, 'London, UK'),
    'berlin': (52.5200, 13.4050, 'Berlin, Germany'),
    'amsterdam': (52.3676, 4.9041, 'Amsterdam, Netherlands'),
    'luxembourg': (49.6117, 6.1300, 'Luxembourg'),
    # Monde entier
    'new york': (40.7128, -74.0060, 'New York, USA'),
    'nyc': (40.7128, -74.0060, 'New York, USA'),
    'los angeles': (34.0522, -118.2437, 'Los Angeles, USA'),
    'la': (34.0522, -118.2437, 'Los Angeles, USA'),
    'chicago': (41.8781, -87.6298, 'Chicago, USA'),
    'miami': (25.7617, -80.1918, 'Miami, USA'),
    'san francisco': (37.7749, -122.4194, 'San Francisco, USA'),
    'tokyo': (35.6762, 139.6503, 'Tokyo, Japan'),
    'osaka': (34.6937, 135.5023, 'Osaka, Japan'),
    'sydney': (-33.8688, 151.2093, 'Sydney, Australia'),
    'melbourne': (-37.8136, 144.9631, 'Melbourne, Australia'),
    'singapore': (1.3521, 103.8198, 'Singapore'),
    'hong kong': (22.3193, 114.1694, 'Hong Kong'),
    'seoul': (37.5665, 126.9780, 'Seoul, South Korea'),
    'bangkok': (13.7563, 100.5018, 'Bangkok, Thailand'),
    'mumbai': (19.0760, 72.8777, 'Mumbai, India'),
    'delhi': (28.7041, 77.1025, 'Delhi, India'),
    'dubai': (25.2048, 55.2708, 'Dubai, UAE'),
    'istanbul': (41.0082, 28.9784, 'Istanbul, Turkey'),
    'moscow': (55.7558, 37.6173, 'Moscow, Russia'),
    'madrid': (40.4168, -3.7038, 'Madrid, Spain'),
    'barcelona': (41.3851, 2.1734, 'Barcelona, Spain'),
    'lisbon': (38.7223, -9.1393, 'Lisbon, Portugal'),
    'rome': (41.9028, 12.4964, 'Rome, Italy'),
    'milan': (45.4642, 9.1900, 'Milan, Italy'),
    'vienna': (48.2082, 16.3738, 'Vienna, Austria'),
    'prague': (50.0755, 14.4378, 'Prague, Czech Republic'),
    'warsaw': (52.2297, 21.0122, 'Warsaw, Poland'),
    'budapest': (47.4979, 19.0402, 'Budapest, Hungary'),
    'bucharest': (44.4268, 26.1025, 'Bucharest, Romania'),
    'athens': (37.9838, 23.7275, 'Athens, Greece'),
    'copenhagen': (55.6761, 12.5683, 'Copenhagen, Denmark'),
    'stockholm': (59.3293, 18.0686, 'Stockholm, Sweden'),
    'oslo': (59.9139, 10.7522, 'Oslo, Norway'),
    'helsinki': (60.1695, 24.9354, 'Helsinki, Finland'),
    'dublin': (53.3498, -6.2603, 'Dublin, Ireland'),
    'london': (51.5074, -0.1278, 'London, UK'),
    'edinburgh': (55.9533, -3.1883, 'Edinburgh, UK'),
    'manchester': (53.4808, -2.2426, 'Manchester, UK'),
    'birmingham': (52.4862, -1.8904, 'Birmingham, UK'),
    'toronto': (43.6532, -79.3832, 'Toronto, Canada'),
    'montreal': (45.5017, -73.5673, 'Montreal, Canada'),
    'vancouver': (49.2827, -123.1207, 'Vancouver, Canada'),
    'mexico city': (19.4326, -99.1332, 'Mexico City, Mexico'),
    'buenos aires': (-34.6037, -58.3816, 'Buenos Aires, Argentina'),
    'sao paulo': (-23.5505, -46.6333, 'São Paulo, Brazil'),
    'rio de janeiro': (-22.9068, -43.1729, 'Rio de Janeiro, Brazil'),
    'lima': (-12.0464, -77.0428, 'Lima, Peru'),
    'bogota': (4.7110, -74.0721, 'Bogotá, Colombia'),
    'santiago': (-33.4489, -70.6693, 'Santiago, Chile'),
    'johannesburg': (-26.2041, 28.0473, 'Johannesburg, South Africa'),
    'cape town': (-33.9249, 18.4241, 'Cape Town, South Africa'),
    'lagos': (6.5244, 3.3792, 'Lagos, Nigeria'),
    'nairobi': (-1.2921, 36.8219, 'Nairobi, Kenya'),
    'cairo': (30.0444, 31.2357, 'Cairo, Egypt'),
    'tel aviv': (32.0853, 34.7818, 'Tel Aviv, Israel'),
}

# Rétrocompatibilité
EUROPEAN_KEYWORDS = {k: v for k, v in WORLD_KEYWORDS.items() if k in [
   'paris','lyon','marseille','toulouse','lille','bordeaux','nantes','strasbourg',
   'montpellier','nice','rennes','grenoble','dijon','annecy','avignon','rouen',
   'clermont','nancy','metz','reims','tours','caen','perpignan','brest','toulon',
   'genève','geneve','geneva','lausanne','zurich','berne','bern','basel','bâle',
   'sion','montreux','fribourg','neuchâtel','neuchatel','lucerne','luzern','nyon',
   'vevey','switzerland','suisse','swiss','bruxelles','brussels','liège','liege',
   'anvers','antwerp','gand','ghent','namur','charleroi','mons','bruges',
   'belgium','belgique','belgian','london','berlin','amsterdam','luxembourg'
]}

# ============================================================
# CATÉGORIES PAR GENRE AUDIUS
# ============================================================

GENRE_TO_CATEGORIES = {
    'Electronic': ['Musique > Electro'],
    'Tech House': ['Musique > Electro', 'Musique > House'],
    'House': ['Musique > House'],
    'Deep House': ['Musique > House'],
    'Techno': ['Musique > Techno'],
    'Trance': ['Musique > Trance'],
    'Drum & Bass': ['Musique > Electro'],
    'Dubstep': ['Musique > Electro'],
    'Trap': ['Musique > Electro'],
    'Future Bass': ['Musique > Electro'],
    'Ambient': ['Musique > Electro', 'Musique > Ambient'],
    'Experimental': ['Musique > Expérimental'],
    'Rock': ['Musique > Rock'],
    'Alternative': ['Musique > Rock'],
    'Punk': ['Musique > Punk'],
    'Metal': ['Musique > Metal'],
    'Indie': ['Musique > Indie'],
    'Jazz': ['Musique > Jazz'],
    'Hip-Hop/Rap': ['Musique > Hip-Hop'],
    'R&B/Soul': ['Musique > R&B'],
    'Pop': ['Musique > Pop'],
    'Classical': ['Musique > Classique'],
    'Reggae': ['Musique > Reggae'],
    'Folk': ['Musique > Folk'],
    'Country': ['Musique > Country'],
    'World': ['Musique > World'],
    'Latin': ['Musique > Latin'],
    'Soundtrack': ['Musique > Soundtrack'],
    'Lo-Fi': ['Musique > Lo-Fi'],
    'Disco': ['Musique > Disco'],
    'Funk': ['Musique > Funk'],
    'Soul': ['Musique > Soul'],
    'Blues': ['Musique > Blues'],
    'Downtempo': ['Musique > Electro'],
    'Dancehall': ['Musique > Dancehall'],
    'Afrobeats': ['Musique > Afrobeat'],
    'Hardstyle': ['Musique > Hardstyle'],
    'Glitch Hop': ['Musique > Electro'],
    'Moombahton': ['Musique > Electro'],
    'Devotional': ['Musique'],
    'Comedy': ['Culture > Humour'],
    'Spoken Word': ['Culture > Littérature'],
    'Audiobooks': ['Culture > Littérature'],
    'Podcasts': ['Culture'],
}


def match_world_location(location_str):
    """Cherche si la localisation correspond à un lieu connu (monde entier).
    Retourne (lat, lng, clean_location) ou None."""
    if not location_str:
        return None
    loc_lower = location_str.lower().strip()
    
    # Chercher chaque mot-clé
    for keyword, (lat, lng, clean_loc) in WORLD_KEYWORDS.items():
        if keyword in loc_lower:
            return (lat, lng, clean_loc)
    
    return None


def geocode_nominatim(location_str):
    """Géocode avec Nominatim (OpenStreetMap, gratuit).
    Retourne (lat, lng, display_name) ou None."""
    if not location_str:
        return None
    try:
        r = requests.get('https://nominatim.openstreetmap.org/search', params={
            'q': location_str,
            'format': 'json',
            'limit': 1,
            # Pas de restriction pays - monde entier
        }, headers={'User-Agent': 'MapEventAI/1.0'}, timeout=10)
        results = r.json()
        if results:
            lat = float(results[0]['lat'])
            lng = float(results[0]['lon'])
            name = results[0].get('display_name', location_str)
            return (lat, lng, name)
    except Exception:
        pass
    return None


def get_categories(genre, mood=None):
    """Convertit un genre Audius en catégories MapEvent."""
    cats = GENRE_TO_CATEGORIES.get(genre, ['Musique'])
    # Toujours ajouter la catégorie parente si c'est un sous-genre
    if cats and 'Musique' not in cats:
        cats = ['Musique'] + cats
    return cats


def build_description(artist, track, genre):
    """Construit une description professionnelle pour le booking."""
    parts = []
    
    name = artist.get('name', '')
    bio = (artist.get('bio') or '').strip()
    location = artist.get('location', '')
    
    # Première ligne : présentation
    parts.append(f"🎵 {name}")
    if genre:
        parts.append(f"Genre : {genre}")
    if location:
        parts.append(f"📍 {location}")
    
    # Bio (tronquée) - jamais de numéro de téléphone
    if bio:
        # Nettoyer : emails, URLs, numéros de téléphone
        bio_clean = re.sub(r'\S+@\S+\.\S+', '', bio)  # emails
        bio_clean = re.sub(r'https?://\S+', '', bio_clean)  # URLs
        bio_clean = re.sub(r'(?:Tel|Tél|Téléphone|Phone|Tel\.|Tél\.)\s*[:.]?\s*[\+]?[\d\s\.\-\(\)]{7,}', '', bio_clean, flags=re.I)
        bio_clean = re.sub(r'[\+]?\d{1,3}[\s\.\-]?\(?\d{2,4}\)?[\s\.\-]?\d{2,4}[\s\.\-]?\d{2,4}[\s\.\-]?\d{0,4}', '', bio_clean)
        bio_clean = re.sub(r'\s+', ' ', bio_clean).strip()
        if bio_clean and len(bio_clean) > 10:
            if len(bio_clean) > 150:
                bio_clean = bio_clean[:147] + '...'
            parts.append(bio_clean)
    
    # Track info
    if track:
        duration = track.get('duration', 0)
        mins = duration // 60
        secs = duration % 60
        parts.append(f"🎧 Extrait : \"{track.get('title', '')}\" ({mins}:{secs:02d})")
    
    # Liens
    website = artist.get('website', '')
    if website:
        parts.append(f"🌐 {website}")
    
    # Social
    socials = []
    if artist.get('instagram_handle'):
        socials.append(f"IG: @{artist['instagram_handle']}")
    if artist.get('twitter_handle'):
        socials.append(f"X: @{artist['twitter_handle']}")
    if socials:
        parts.append(' | '.join(socials))
    
    return ' | '.join(parts)


# ============================================================
# FETCH ARTISTES AUDIUS
# ============================================================

def search_audius_artists_worldwide():
    """Cherche des artistes Audius localisés dans le monde entier."""
    all_artists = {}  # user_id -> {artist_data, track_data}
    
    # Stratégie 1: Trending par genre
    genres = [
        'Electronic', 'Rock', 'Jazz', 'Hip-Hop/Rap', 'Pop', 'R&B/Soul',
        'Classical', 'Reggae', 'Folk', 'Metal', 'World', 'House',
        'Tech House', 'Techno', 'Ambient', 'Indie', 'Funk', 'Soul',
        'Disco', 'Latin', 'Lo-Fi', 'Trance', 'Drum & Bass', 'Dubstep',
        'Alternative', 'Blues', 'Country', 'Soundtrack', 'Dancehall',
    ]
    
    print("\n📥 Récupération des artistes Audius par genre...")
    for genre in genres:
        try:
            r = requests.get(f'{AUDIUS_BASE}/tracks/trending', params={
                'app_name': APP_NAME,
                'genre': genre,
                'limit': 50,
            }, timeout=30)
            data = r.json()
            tracks = data.get('data', [])
            
            for track in tracks:
                user = track.get('user', {})
                user_id = user.get('id', '')
                if not user_id or user_id in all_artists:
                    continue
                
                location = user.get('location', '')
                geo = match_world_location(location)
                
                if geo:
                    all_artists[user_id] = {
                        'artist': user,
                        'track': track,
                        'tracks': [track],
                        'genre': genre,
                        'geo': geo,
                    }
            
            genre_count = sum(1 for a in all_artists.values() if a['genre'] == genre)
            if genre_count > 0:
                print(f"   {genre:20s}: +{genre_count} artistes EU")
            
            time.sleep(0.3)
            
        except Exception as e:
            print(f"   {genre}: erreur - {e}")
    
    # Stratégie 2: Recherche par nom de ville
    print("\n📥 Recherche directe par ville...")
    search_terms = [
        'Paris', 'France', 'Lyon', 'Marseille', 'Toulouse', 'Geneva', 'Lausanne', 'Zurich', 'Swiss', 'Suisse',
        'Brussels', 'Bruxelles', 'Belgium', 'Bordeaux', 'Nantes', 'Lille', 'Strasbourg', 'Nice',
        'Berlin', 'London', 'Amsterdam', 'New York', 'Tokyo', 'Sydney', 'Toronto', 'Madrid',
        'Barcelona', 'Mexico City', 'São Paulo', 'Dubai', 'Singapore', 'Seoul', 'Bangkok', 'Mumbai',
        'Istanbul', 'Cairo', 'Lagos', 'Nairobi', 'Buenos Aires', 'Rio', 'Lima', 'Johannesburg',
    ]
    
    for term in search_terms:
        try:
            r = requests.get(f'{AUDIUS_BASE}/users/search', params={
                'app_name': APP_NAME,
                'query': term,
                'limit': 30,
            }, timeout=30)
            data = r.json()
            users = data.get('data', [])
            
            found = 0
            for user in users:
                user_id = user.get('id', '')
                if not user_id or user_id in all_artists:
                    continue
                
                location = user.get('location', '')
                geo = match_world_location(location)
                
                if geo and user.get('track_count', 0) > 0:
                    # Récupérer les 5 meilleurs tracks (pour 5 sons par artiste)
                    try:
                        tr = requests.get(f'{AUDIUS_BASE}/users/{user_id}/tracks', params={
                            'app_name': APP_NAME,
                            'limit': 5,
                            'sort': 'plays',
                        }, timeout=15)
                        tracks_data = tr.json().get('data', [])
                        if tracks_data:
                            track = tracks_data[0]  # Meilleur pour la description
                            genre = track.get('genre', 'Electronic')
                            all_artists[user_id] = {
                                'artist': user,
                                'track': track,
                                'tracks': tracks_data[:5],  # Jusqu'à 5 pistes
                                'genre': genre,
                                'geo': geo,
                            }
                            found += 1
                    except:
                        pass
                    
                    time.sleep(0.3)
            
            if found > 0:
                print(f"   Search '{term}': +{found} artistes")
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"   Search '{term}': erreur - {e}")
    
    return all_artists


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 65)
    print("  IMPORT MUSICIENS AUDIUS → BOOKING")
    print("  Source: Audius API (gratuit, zero rate limit)")
    print("  Audio: Streaming MP3 direct depuis Audius")
    print("  Zone: France + Suisse + Belgique + voisins")
    print("=" * 65)
    
    # 1. Récupérer les artistes européens
    artists = search_audius_artists_worldwide()
    print(f"\n📊 Total artistes européens trouvés: {len(artists)}")
    
    if not artists:
        print("⚠️ Aucun artiste trouvé")
        return
    
    # 2. Récupérer les bookings existants
    print("\n📥 Récupération des bookings existants...")
    try:
        r = requests.get(f'{API_URL}/api/bookings', timeout=30)
        existing = r.json() if r.status_code == 200 else []
        print(f"   Bookings existants: {len(existing)}")
    except:
        existing = []
    
    existing_names = set((b.get('name', '') or '').lower() for b in existing)
    
    # 3. Préparer les bookings
    print("\n🔧 Préparation des bookings...")
    bookings_to_import = []
    stats = {'total': 0, 'duplicate': 0, 'imported': 0}
    
    for user_id, data in artists.items():
        stats['total'] += 1
        artist = data['artist']
        track = data['track']
        genre = data['genre']
        lat, lng, clean_location = data['geo']
        
        name = artist.get('name', '').strip()
        if not name:
            continue
        
        # Vérifier doublon
        if name.lower() in existing_names:
            stats['duplicate'] += 1
            continue
        existing_names.add(name.lower())
        
        # Catégories
        categories = get_categories(genre)
        
        # Jusqu'à 5 stream URLs (5 sons par artiste)
        tracks_list = data.get('tracks') or [track]
        stream_urls = []
        TRUSTED_AUDIO_DOMAINS = ('audius.co', 'soundcloud.com', 'spotify.com', 'mixcloud.com', 'youtube.com', 'youtu.be')
        for t in tracks_list[:5]:
            tid = t.get('id', '')
            if tid:
                url = f'https://api.audius.co/v1/tracks/{tid}/stream?app_name=MapEvent'
                if any(d in url for d in TRUSTED_AUDIO_DOMAINS) or 'audius.co' in url:
                    stream_urls.append(url)
        stream_url = stream_urls[0] if stream_urls else ''
        
        # Lien publication originale (profil Audius)
        handle = artist.get('handle', '')
        source_url = f'https://audius.co/{handle}' if handle else ''
        
        # Artwork
        artwork = track.get('artwork', {})
        artwork_url = ''
        if isinstance(artwork, dict):
            artwork_url = artwork.get('480x480') or artwork.get('150x150') or artwork.get('1000x1000') or ''
        
        # Profile pic
        profile_pic = artist.get('profile_picture', {})
        profile_url = ''
        if isinstance(profile_pic, dict):
            profile_url = profile_pic.get('150x150') or profile_pic.get('480x480') or ''
        
        # Description
        description = build_description(artist, track, genre)
        
        # Ajouter jusqu'à 3 URLs audio dans la description
        for u in stream_urls:
            description += f' | 🔊 Audio: {u}'
        if artwork_url:
            description += f' | 🖼️ Cover: {artwork_url}'
        if source_url:
            description += f' | 🔗 Source: {source_url}'
        
        # Légère variation de position pour éviter la superposition
        import random
        lat_offset = random.uniform(-0.005, 0.005)
        lng_offset = random.uniform(-0.005, 0.005)
        
        # Ne pas importer si pas d'audio (le frontend filtre les bookings sans son)
        if not stream_urls:
            continue

        booking = {
            'name': f"🎵 {name}",
            'description': description[:2000],  # Plus large pour 3 audios + source
            'location': clean_location,
            'latitude': round(lat + lat_offset, 6),
            'longitude': round(lng + lng_offset, 6),
            'categories': categories,
        }
        bookings_to_import.append(booking)
        stats['imported'] += 1
    
    print(f"\n📊 Statistiques:")
    print(f"   Total artistes EU: {stats['total']}")
    print(f"   Doublons: {stats['duplicate']}")
    print(f"   ✅ À importer: {stats['imported']}")
    
    if not bookings_to_import:
        print("\n⚠️ Aucun booking à importer")
        return
    
    # Stats par pays
    country_stats = {}
    for b in bookings_to_import:
        loc = b['location']
        if 'France' in loc:
            country_stats['France'] = country_stats.get('France', 0) + 1
        elif 'Suisse' in loc:
            country_stats['Suisse'] = country_stats.get('Suisse', 0) + 1
        elif 'Belgique' in loc:
            country_stats['Belgique'] = country_stats.get('Belgique', 0) + 1
        else:
            country_stats['Autre'] = country_stats.get('Autre', 0) + 1
    
    print(f"\n   Par pays:")
    for country, count in sorted(country_stats.items(), key=lambda x: -x[1]):
        print(f"     {country}: {count}")
    
    # Stats par genre
    genre_stats = {}
    for b in bookings_to_import:
        for cat in b['categories']:
            genre_stats[cat] = genre_stats.get(cat, 0) + 1
    
    print(f"\n   Par catégorie:")
    for cat, count in sorted(genre_stats.items(), key=lambda x: -x[1])[:10]:
        print(f"     {cat}: {count}")
    
    # Aperçu
    print(f"\n📋 Aperçu (premiers 10):")
    for b in bookings_to_import[:10]:
        cats = ', '.join(b['categories'][:2])
        print(f"   {b['name'][:35]:35s} | {b['location'][:25]:25s} | {cats}")
    
    # 4. Importer
    print(f"\n📤 Import de {len(bookings_to_import)} bookings...")
    total_created = 0
    
    for i, booking in enumerate(bookings_to_import):
        try:
            r = requests.post(
                f'{API_URL}/api/bookings/publish',
                json=booking,
                timeout=15
            )
            if r.status_code in (200, 201):
                total_created += 1
                if (i + 1) % 10 == 0:
                    print(f"   {i + 1}/{len(bookings_to_import)} créés...")
            else:
                print(f"   ❌ {booking['name'][:30]}: {r.status_code} - {r.text[:100]}")
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"   ❌ {booking['name'][:30]}: {e}")
    
    print(f"\n{'=' * 65}")
    print(f"  🎯 TOTAL IMPORTÉ: {total_created} musiciens dans Booking")
    print(f"  Source: Audius API (gratuit)")
    print(f"  Audio: Streaming MP3 direct via Audius")
    print(f"  Zone: France + Suisse + Belgique")
    print(f"{'=' * 65}")


if __name__ == '__main__':
    main()
