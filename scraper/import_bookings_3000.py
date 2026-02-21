# -*- coding: utf-8 -*-
"""
Import massif de 3000+ bookings mondiaux.
Chaque artiste Audius est placé dans plusieurs villes du monde (même audio, plusieurs points sur la carte).
"""

import sys
import random
import requests
import time

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'
AUDIUS_BASE = 'https://api.audius.co/v1'
APP_NAME = 'MapEvent'

# Villes pour placer les bookings (lat, lng, nom)
CITIES = [
    (48.8566, 2.3522, 'Paris, France'), (45.7640, 4.8357, 'Lyon, France'),
    (43.2965, 5.3698, 'Marseille, France'), (43.6047, 1.4442, 'Toulouse, France'),
    (50.6292, 3.0573, 'Lille, France'), (44.8378, -0.5792, 'Bordeaux, France'),
    (47.2184, -1.5536, 'Nantes, France'), (48.5734, 7.7521, 'Strasbourg, France'),
    (43.6108, 3.8767, 'Montpellier, France'), (43.7102, 7.2620, 'Nice, France'),
    (48.1173, -1.6778, 'Rennes, France'), (45.1885, 5.7245, 'Grenoble, France'),
    (46.2044, 6.1432, 'Genève, Suisse'), (46.5197, 6.6323, 'Lausanne, Suisse'),
    (47.3769, 8.5417, 'Zurich, Suisse'), (50.8503, 4.3517, 'Bruxelles, Belgique'),
    (51.5074, -0.1278, 'London, UK'), (52.5200, 13.4050, 'Berlin, Germany'),
    (52.3676, 4.9041, 'Amsterdam, Netherlands'), (40.7128, -74.0060, 'New York, USA'),
    (34.0522, -118.2437, 'Los Angeles, USA'), (41.8781, -87.6298, 'Chicago, USA'),
    (25.7617, -80.1918, 'Miami, USA'), (37.7749, -122.4194, 'San Francisco, USA'),
    (35.6762, 139.6503, 'Tokyo, Japan'), (34.6937, 135.5023, 'Osaka, Japan'),
    (-33.8688, 151.2093, 'Sydney, Australia'), (-37.8136, 144.9631, 'Melbourne, Australia'),
    (1.3521, 103.8198, 'Singapore'), (22.3193, 114.1694, 'Hong Kong'),
    (37.5665, 126.9780, 'Seoul, South Korea'), (13.7563, 100.5018, 'Bangkok, Thailand'),
    (19.0760, 72.8777, 'Mumbai, India'), (28.7041, 77.1025, 'Delhi, India'),
    (25.2048, 55.2708, 'Dubai, UAE'), (41.0082, 28.9784, 'Istanbul, Turkey'),
    (55.7558, 37.6173, 'Moscow, Russia'), (40.4168, -3.7038, 'Madrid, Spain'),
    (41.3851, 2.1734, 'Barcelona, Spain'), (38.7223, -9.1393, 'Lisbon, Portugal'),
    (41.9028, 12.4964, 'Rome, Italy'), (45.4642, 9.1900, 'Milan, Italy'),
    (48.2082, 16.3738, 'Vienna, Austria'), (50.0755, 14.4378, 'Prague, Czech Republic'),
    (52.2297, 21.0122, 'Warsaw, Poland'), (47.4979, 19.0402, 'Budapest, Hungary'),
    (44.4268, 26.1025, 'Bucharest, Romania'), (37.9838, 23.7275, 'Athens, Greece'),
    (55.6761, 12.5683, 'Copenhagen, Denmark'), (59.3293, 18.0686, 'Stockholm, Sweden'),
    (59.9139, 10.7522, 'Oslo, Norway'), (60.1695, 24.9354, 'Helsinki, Finland'),
    (53.3498, -6.2603, 'Dublin, Ireland'), (55.9533, -3.1883, 'Edinburgh, UK'),
    (53.4808, -2.2426, 'Manchester, UK'), (43.6532, -79.3832, 'Toronto, Canada'),
    (45.5017, -73.5673, 'Montreal, Canada'), (49.2827, -123.1207, 'Vancouver, Canada'),
    (19.4326, -99.1332, 'Mexico City, Mexico'), (-34.6037, -58.3816, 'Buenos Aires, Argentina'),
    (-23.5505, -46.6333, 'São Paulo, Brazil'), (-22.9068, -43.1729, 'Rio de Janeiro, Brazil'),
    (-12.0464, -77.0428, 'Lima, Peru'), (4.7110, -74.0721, 'Bogotá, Colombia'),
    (-33.4489, -70.6693, 'Santiago, Chile'), (-26.2041, 28.0473, 'Johannesburg, South Africa'),
    (-33.9249, 18.4241, 'Cape Town, South Africa'), (6.5244, 3.3792, 'Lagos, Nigeria'),
    (-1.2921, 36.8219, 'Nairobi, Kenya'), (30.0444, 31.2357, 'Cairo, Egypt'),
    (32.0853, 34.7818, 'Tel Aviv, Israel'), (46.9480, 7.4474, 'Berne, Suisse'),
    (47.5596, 7.5886, 'Bâle, Suisse'), (49.4432, 1.0993, 'Rouen, France'),
    (49.2583, 4.0317, 'Reims, France'), (47.3941, 0.6848, 'Tours, France'),
]

GENRE_TO_CATEGORIES = {
    'Electronic': ['Musique > Electro'], 'Tech House': ['Musique > Electro', 'Musique > House'],
    'House': ['Musique > House'], 'Techno': ['Musique > Techno'],
    'Rock': ['Musique > Rock'], 'Jazz': ['Musique > Jazz'],
    'Hip-Hop/Rap': ['Musique > Hip-Hop'], 'Pop': ['Musique > Pop'],
    'R&B/Soul': ['Musique > R&B'], 'Reggae': ['Musique > Reggae'],
    'Folk': ['Musique > Folk'], 'Metal': ['Musique > Metal'],
    'Classical': ['Musique > Classique'], 'Latin': ['Musique > Latin'],
    'Ambient': ['Musique > Ambient'], 'Lo-Fi': ['Musique > Lo-Fi'],
    'Disco': ['Musique > Disco'], 'Funk': ['Musique > Funk'],
    'Blues': ['Musique > Blues'], 'World': ['Musique > World'],
    'Country': ['Musique > Country'], 'Indie': ['Musique > Indie'],
}

def fetch_audius_artists(limit_artists=350):
    """Récupère des artistes Audius avec leurs tracks."""
    all_artists = {}
    genres = ['Electronic', 'Rock', 'Jazz', 'Hip-Hop/Rap', 'Pop', 'House', 'Techno',
              'R&B/Soul', 'Reggae', 'Folk', 'Metal', 'Classical', 'Latin', 'Ambient',
              'Lo-Fi', 'Disco', 'Funk', 'Blues', 'World', 'Country', 'Indie']
    
    print("📥 Récupération des artistes Audius...")
    for genre in genres:
        if len(all_artists) >= limit_artists:
            break
        try:
            r = requests.get(f'{AUDIUS_BASE}/tracks/trending', params={
                'app_name': APP_NAME, 'genre': genre, 'limit': 80
            }, timeout=30)
            data = r.json()
            for track in data.get('data', []):
                user = track.get('user', {})
                uid = user.get('id', '')
                if not uid or uid in all_artists:
                    continue
                if user.get('track_count', 0) < 1:
                    continue
                try:
                    tr = requests.get(f'{AUDIUS_BASE}/users/{uid}/tracks', params={
                        'app_name': APP_NAME, 'limit': 5, 'sort': 'plays'
                    }, timeout=15)
                    tracks_data = tr.json().get('data', [])
                    if tracks_data:
                        stream_urls = []
                        for t in tracks_data[:5]:
                            tid = t.get('id', '')
                            if tid:
                                stream_urls.append(f'https://api.audius.co/v1/tracks/{tid}/stream?app_name=MapEvent')
                        if stream_urls:
                            all_artists[uid] = {
                                'name': user.get('name', 'Artist').strip(),
                                'genre': track.get('genre', 'Electronic'),
                                'handle': user.get('handle', ''),
                                'tracks': stream_urls,
                            }
                            if len(all_artists) % 50 == 0 and len(all_artists) > 0:
                                print(f"   {len(all_artists)} artistes...")
                except:
                    pass
                time.sleep(0.1)
            time.sleep(0.2)
        except Exception as e:
            print(f"   {genre}: {e}")
    return list(all_artists.values())

def main():
    TARGET = 3000
    print("=" * 60)
    print("  IMPORT 3000+ BOOKINGS MONDAUX")
    print("  Source: Audius | Objectif: 3000+ points sur la carte")
    print("=" * 60)
    
    artists = fetch_audius_artists(600)
    print(f"\n📊 {len(artists)} artistes avec audio récupérés")
    
    if not artists:
        print("❌ Aucun artiste trouvé")
        return
    
    # Répartir: chaque artiste dans ~5-6 villes pour atteindre 3000
    bookings_per_artist = max(5, (TARGET + len(artists) - 1) // len(artists))
    random.shuffle(CITIES)
    
    bookings = []
    for i, artist in enumerate(artists):
        cities_sample = random.sample(CITIES, min(bookings_per_artist, len(CITIES)))
        for lat, lng, loc in cities_sample:
            offset_lat = random.uniform(-0.008, 0.008)
            offset_lng = random.uniform(-0.008, 0.008)
            desc = f"🎵 {artist['name']} | Genre: {artist['genre']} | 📍 {loc}"
            for u in artist['tracks']:
                desc += f" | 🔊 Audio: {u}"
            if artist.get('handle'):
                desc += f" | 🔗 Source: https://audius.co/{artist['handle']}"
            
            cats = GENRE_TO_CATEGORIES.get(artist['genre'], ['Musique'])
            if 'Musique' not in cats:
                cats = ['Musique'] + cats
            
            bookings.append({
                'name': f"🎵 {artist['name']}",
                'description': desc[:2000],
                'location': loc,
                'latitude': round(lat + offset_lat, 6),
                'longitude': round(lng + offset_lng, 6),
                'categories': cats,
            })
    
    print(f"📋 {len(bookings)} bookings préparés")
    
    # Récupérer les existants
    try:
        r = requests.get(f'{API_URL}/api/bookings', timeout=30)
        existing = r.json() if r.status_code == 200 else []
        existing_names = set((b.get('name', '') or '').lower() for b in existing)
        print(f"   Déjà en base: {len(existing)}")
    except:
        existing_names = set()
    
    # Filtrer doublons potentiels (même nom+ville)
    seen = set()
    to_import = []
    for b in bookings:
        key = (b['name'].lower(), b['location'])
        if key not in seen:
            seen.add(key)
            to_import.append(b)
    
    print(f"   À importer: {len(to_import)}")
    
    # Envoyer
    print(f"\n📤 Import vers l'API...")
    created = 0
    for i, b in enumerate(to_import):
        try:
            r = requests.post(f'{API_URL}/api/bookings/publish', json=b, timeout=15)
            if r.status_code in (200, 201):
                created += 1
                if created % 100 == 0:
                    print(f"   {created}/{len(to_import)} créés...")
        except Exception as e:
            pass
        time.sleep(0.05)
    
    print(f"\n{'=' * 60}")
    print(f"  ✅ {created} bookings importés (visibles sur la carte)")
    print(f"{'=' * 60}")

if __name__ == '__main__':
    main()
