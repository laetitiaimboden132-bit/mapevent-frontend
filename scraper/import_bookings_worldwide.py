# -*- coding: utf-8 -*-
"""
Import de musiciens Audius dans la section Booking - MONDE ENTIER
Source : Audius API (100% gratuit)
Audio : Jusqu'à 5 sons par artiste (pas 1 seul)
Sans numéros de téléphone dans les descriptions
"""

import sys
import re
import requests
import time

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'
AUDIUS_BASE = 'https://api.audius.co/v1'
APP_NAME = 'MapEvent'

# Villes mondiales (lat, lng, display)
WORLD_CITIES = {
    'paris': (48.8566, 2.3522, 'Paris, France'),
    'lyon': (45.7640, 4.8357, 'Lyon, France'),
    'marseille': (43.2965, 5.3698, 'Marseille, France'),
    'geneva': (46.2044, 6.1432, 'Genève, Suisse'),
    'geneve': (46.2044, 6.1432, 'Genève, Suisse'),
    'lausanne': (46.5197, 6.6323, 'Lausanne, Suisse'),
    'zurich': (47.3769, 8.5417, 'Zurich, Suisse'),
    'london': (51.5074, -0.1278, 'London, UK'),
    'berlin': (52.5200, 13.4050, 'Berlin, Germany'),
    'amsterdam': (52.3676, 4.9041, 'Amsterdam, Netherlands'),
    'madrid': (40.4168, -3.7038, 'Madrid, Spain'),
    'barcelona': (41.3851, 2.1734, 'Barcelona, Spain'),
    'rome': (41.9028, 12.4964, 'Rome, Italy'),
    'milan': (45.4642, 9.1900, 'Milan, Italy'),
    'brussels': (50.8503, 4.3517, 'Brussels, Belgium'),
    'bruxelles': (50.8503, 4.3517, 'Brussels, Belgium'),
    'new york': (40.7128, -74.0060, 'New York, USA'),
    'los angeles': (34.0522, -118.2437, 'Los Angeles, USA'),
    'chicago': (41.8781, -87.6298, 'Chicago, USA'),
    'san francisco': (37.7749, -122.4194, 'San Francisco, USA'),
    'miami': (25.7617, -80.1918, 'Miami, USA'),
    'austin': (30.2672, -97.7431, 'Austin, USA'),
    'seattle': (47.6062, -122.3321, 'Seattle, USA'),
    'denver': (39.7392, -104.9903, 'Denver, USA'),
    'toronto': (43.6532, -79.3832, 'Toronto, Canada'),
    'montreal': (45.5017, -73.5673, 'Montreal, Canada'),
    'vancouver': (49.2827, -123.1207, 'Vancouver, Canada'),
    'tokyo': (35.6762, 139.6503, 'Tokyo, Japan'),
    'osaka': (34.6937, 135.5023, 'Osaka, Japan'),
    'sydney': (-33.8688, 151.2093, 'Sydney, Australia'),
    'melbourne': (-37.8136, 144.9631, 'Melbourne, Australia'),
    'rio de janeiro': (-22.9068, -43.1729, 'Rio de Janeiro, Brazil'),
    'sao paulo': (-23.5505, -46.6333, 'São Paulo, Brazil'),
    'buenos aires': (-34.6037, -58.3816, 'Buenos Aires, Argentina'),
    'mexico city': (19.4326, -99.1332, 'Mexico City, Mexico'),
    'bogota': (4.7110, -74.0721, 'Bogotá, Colombia'),
    'lima': (-12.0464, -77.0428, 'Lima, Peru'),
    'santiago': (-33.4489, -70.6693, 'Santiago, Chile'),
    'lisbon': (38.7223, -9.1393, 'Lisbon, Portugal'),
    'lisboa': (38.7223, -9.1393, 'Lisbon, Portugal'),
    'dublin': (53.3498, -6.2603, 'Dublin, Ireland'),
    'copenhagen': (55.6761, 12.5683, 'Copenhagen, Denmark'),
    'stockholm': (59.3293, 18.0686, 'Stockholm, Sweden'),
    'oslo': (59.9139, 10.7522, 'Oslo, Norway'),
    'helsinki': (60.1695, 24.9354, 'Helsinki, Finland'),
    'warsaw': (52.2297, 21.0122, 'Warsaw, Poland'),
    'prague': (50.0755, 14.4378, 'Prague, Czech Republic'),
    'budapest': (47.4979, 19.0402, 'Budapest, Hungary'),
    'athens': (37.9838, 23.7275, 'Athens, Greece'),
    'istanbul': (41.0082, 28.9784, 'Istanbul, Turkey'),
    'moscow': (55.7558, 37.6173, 'Moscow, Russia'),
    'dubai': (25.2048, 55.2708, 'Dubai, UAE'),
    'tel aviv': (32.0853, 34.7818, 'Tel Aviv, Israel'),
    'delhi': (28.6139, 77.2090, 'Delhi, India'),
    'mumbai': (19.0760, 72.8777, 'Mumbai, India'),
    'bangalore': (12.9716, 77.5946, 'Bangalore, India'),
    'singapore': (1.3521, 103.8198, 'Singapore'),
    'hong kong': (22.3193, 114.1694, 'Hong Kong'),
    'seoul': (37.5665, 126.9780, 'Seoul, South Korea'),
    'taipei': (25.0330, 121.5654, 'Taipei, Taiwan'),
    'bangkok': (13.7563, 100.5018, 'Bangkok, Thailand'),
    'johannesburg': (-26.2041, 28.0473, 'Johannesburg, South Africa'),
    'cape town': (-33.9249, 18.4241, 'Cape Town, South Africa'),
    'lagos': (6.5244, 3.3792, 'Lagos, Nigeria'),
    'nairobi': (-1.2921, 36.8219, 'Nairobi, Kenya'),
    'cairo': (30.0444, 31.2357, 'Cairo, Egypt'),
}

GENRE_TO_CATEGORIES = {
    'Electronic': ['Musique > Electro'],
    'House': ['Musique > House'],
    'Techno': ['Musique > Techno'],
    'Rock': ['Musique > Rock'],
    'Jazz': ['Musique > Jazz'],
    'Hip-Hop/Rap': ['Musique > Hip-Hop'],
    'Pop': ['Musique > Pop'],
    'Reggae': ['Musique > Reggae'],
    'Folk': ['Musique > Folk'],
    'Metal': ['Musique > Metal'],
    'Indie': ['Musique > Indie'],
    'Funk': ['Musique > Funk'],
    'Soul': ['Musique > Soul'],
    'Blues': ['Musique > Blues'],
    'Latin': ['Musique > Latin'],
    'World': ['Musique > World'],
    'Classical': ['Musique > Classique'],
    'Ambient': ['Musique > Ambient'],
    'Lo-Fi': ['Musique > Lo-Fi'],
    'Trance': ['Musique > Trance'],
    'Drum & Bass': ['Musique > Electro'],
    'Dubstep': ['Musique > Electro'],
    'Tech House': ['Musique > House'],
    'R&B/Soul': ['Musique > R&B'],
    'Alternative': ['Musique > Rock'],
    'Dancehall': ['Musique > Dancehall'],
    'Afrobeats': ['Musique > Afrobeat'],
}


def strip_phone_from_text(text):
    """Retire tous les numéros de téléphone du texte."""
    if not text:
        return ''
    s = str(text)
    s = re.sub(r'📞\s*[^\n|]*', '', s)
    s = re.sub(r'☎\s*[^\n|]*', '', s)
    s = re.sub(r'(?:Tel|Tél|Téléphone|Phone|Tel\.|Tél\.)\s*[:.]?\s*[\+]?[\d\s\.\-\(\)]{7,}', '', s, flags=re.I)
    s = re.sub(r'(?:\+\d{1,3}[\s\.\-]?)?\(?\d{2,4}\)?[\s\.\-]?\d{2,4}[\s\.\-]?\d{2,4}[\s\.\-]?\d{0,4}', lambda m: '' if len(re.sub(r'\D', '', m.group())) >= 10 else m.group(), s)
    s = re.sub(r'\s{2,}', ' ', s).strip()
    return s


def match_world_location(location_str):
    if not location_str:
        return None
    loc_lower = location_str.lower().strip()
    for keyword, (lat, lng, clean_loc) in WORLD_CITIES.items():
        if keyword in loc_lower:
            return (lat, lng, clean_loc)
    return None


def get_categories(genre):
    return GENRE_TO_CATEGORIES.get(genre, ['Musique'])


def build_description_no_phone(artist, track, genre):
    """Description sans aucun numéro de téléphone."""
    parts = []
    name = artist.get('name', '')
    bio = (artist.get('bio') or '').strip()
    location = artist.get('location', '')
    parts.append(f"🎵 {name}")
    if genre:
        parts.append(f"Genre : {genre}")
    if location:
        parts.append(f"📍 {location}")
    if bio:
        bio_clean = re.sub(r'\S+@\S+\.\S+', '', bio)
        bio_clean = re.sub(r'https?://\S+', '', bio_clean)
        bio_clean = strip_phone_from_text(bio_clean)
        bio_clean = re.sub(r'\s+', ' ', bio_clean).strip()
        if bio_clean and len(bio_clean) > 10:
            if len(bio_clean) > 150:
                bio_clean = bio_clean[:147] + '...'
            parts.append(bio_clean)
    if track:
        duration = track.get('duration', 0)
        mins = duration // 60
        secs = duration % 60
        parts.append(f"🎧 Extrait : \"{track.get('title', '')}\" ({mins}:{secs:02d})")
    website = artist.get('website', '')
    if website:
        parts.append(f"🌐 {website}")
    socials = []
    if artist.get('instagram_handle'):
        socials.append(f"IG: @{artist['instagram_handle']}")
    if artist.get('twitter_handle'):
        socials.append(f"X: @{artist['twitter_handle']}")
    if socials:
        parts.append(' | '.join(socials))
    return strip_phone_from_text(' | '.join(parts))


def search_audius_artists_worldwide():
    all_artists = {}
    genres = [
        'Electronic', 'Rock', 'Jazz', 'Hip-Hop/Rap', 'Pop', 'R&B/Soul',
        'House', 'Techno', 'Ambient', 'Indie', 'Funk', 'Soul',
        'Reggae', 'Folk', 'Metal', 'World', 'Latin', 'Lo-Fi',
        'Trance', 'Drum & Bass', 'Dubstep', 'Alternative', 'Blues',
    ]
    print("\n📥 Récupération des artistes Audius (monde entier)...")
    for genre in genres:
        try:
            r = requests.get(f'{AUDIUS_BASE}/tracks/trending', params={
                'app_name': APP_NAME,
                'genre': genre,
                'limit': 60,
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
                    try:
                        tr = requests.get(f'{AUDIUS_BASE}/users/{user_id}/tracks', params={
                            'app_name': APP_NAME,
                            'limit': 5,
                            'sort': 'plays',
                        }, timeout=15)
                        tracks_data = tr.json().get('data', [])
                        if not tracks_data:
                            tracks_data = [track]
                        all_artists[user_id] = {
                            'artist': user,
                            'track': track,
                            'tracks': tracks_data[:5],
                            'genre': genre,
                            'geo': geo,
                        }
                    except:
                        all_artists[user_id] = {
                            'artist': user,
                            'track': track,
                            'tracks': [track],
                            'genre': genre,
                            'geo': geo,
                        }
            time.sleep(0.3)
        except Exception as e:
            print(f"   {genre}: erreur - {e}")
    search_terms = [
        'Tokyo', 'New York', 'London', 'Berlin', 'Paris', 'Sydney',
        'Los Angeles', 'Toronto', 'Miami', 'Amsterdam', 'Barcelona',
        'Mexico City', 'Rio', 'São Paulo', 'Singapore', 'Dubai',
    ]
    print("\n📥 Recherche par ville...")
    for term in search_terms:
        try:
            r = requests.get(f'{AUDIUS_BASE}/users/search', params={
                'app_name': APP_NAME,
                'query': term,
                'limit': 40,
            }, timeout=30)
            users = r.json().get('data', [])
            for user in users:
                user_id = user.get('id', '')
                if not user_id or user_id in all_artists:
                    continue
                location = user.get('location', '')
                geo = match_world_location(location)
                if geo and user.get('track_count', 0) > 0:
                    try:
                        tr = requests.get(f'{AUDIUS_BASE}/users/{user_id}/tracks', params={
                            'app_name': APP_NAME,
                            'limit': 5,
                            'sort': 'plays',
                        }, timeout=15)
                        tracks_data = tr.json().get('data', [])
                        if tracks_data:
                            all_artists[user_id] = {
                                'artist': user,
                                'track': tracks_data[0],
                                'tracks': tracks_data[:5],
                                'genre': tracks_data[0].get('genre', 'Electronic'),
                                'geo': geo,
                            }
                    except:
                        pass
                    time.sleep(0.2)
            time.sleep(0.5)
        except Exception as e:
            print(f"   {term}: {e}")
    return all_artists


def main():
    print("=" * 65)
    print("  IMPORT BOOKINGS MONDE ENTIER")
    print("  • Plusieurs sons par artiste (2-5)")
    print("  • Aucun numéro de téléphone")
    print("  • Villes : Europe, USA, Japon, Australie, Amérique du Sud...")
    print("=" * 65)
    artists = search_audius_artists_worldwide()
    print(f"\n📊 Total artistes trouvés: {len(artists)}")
    if not artists:
        print("⚠️ Aucun artiste")
        return
    try:
        r = requests.get(f'{API_URL}/api/bookings', timeout=30)
        existing = r.json() if r.status_code == 200 else []
    except:
        existing = []
    existing_names = set((b.get('name', '') or '').lower() for b in existing)
    bookings_to_import = []
    for user_id, data in artists.items():
        artist = data['artist']
        track = data['track']
        genre = data['genre']
        lat, lng, clean_location = data['geo']
        name = artist.get('name', '').strip()
        if not name or name.lower() in existing_names:
            continue
        existing_names.add(name.lower())
        categories = get_categories(genre)
        tracks_list = data.get('tracks') or [track]
        stream_urls = []
        for t in tracks_list[:5]:
            tid = t.get('id', '')
            if tid:
                url = f'https://api.audius.co/v1/tracks/{tid}/stream?app_name=MapEvent'
                stream_urls.append(url)
        if not stream_urls:
            continue
        handle = artist.get('handle', '')
        source_url = f'https://audius.co/{handle}' if handle else ''
        artwork = track.get('artwork', {})
        artwork_url = artwork.get('480x480', '') if isinstance(artwork, dict) else ''
        description = build_description_no_phone(artist, track, genre)
        for u in stream_urls:
            description += f' | 🔊 Audio: {u}'
        if artwork_url:
            description += f' | 🖼️ Cover: {artwork_url}'
        if source_url:
            description += f' | 🔗 Source: {source_url}'
        import random
        lat_offset = random.uniform(-0.008, 0.008)
        lng_offset = random.uniform(-0.008, 0.008)
        booking = {
            'name': f"🎵 {name}",
            'description': description[:2500],
            'location': clean_location,
            'latitude': round(lat + lat_offset, 6),
            'longitude': round(lng + lng_offset, 6),
            'categories': categories,
        }
        bookings_to_import.append(booking)
    songs_per = max(len(b.get('description', '').split('🔊 Audio:')) - 1 for b in bookings_to_import) if bookings_to_import else 0
    print(f"\n✅ À importer: {len(bookings_to_import)} (jusqu'à 5 sons par artiste)")
    if not bookings_to_import:
        return
    total_created = 0
    for i, booking in enumerate(bookings_to_import):
        try:
            r = requests.post(f'{API_URL}/api/bookings/publish', json=booking, timeout=15)
            if r.status_code in (200, 201):
                total_created += 1
                if (i + 1) % 15 == 0:
                    print(f"   {i + 1}/{len(bookings_to_import)} créés...")
            time.sleep(0.4)
        except Exception as e:
            print(f"   ❌ {booking['name'][:30]}: {e}")
    print(f"\n{'=' * 65}")
    print(f"  🎯 IMPORTÉ: {total_created} bookings (monde entier, plusieurs sons, sans tel)")
    print(f"{'=' * 65}")


if __name__ == '__main__':
    main()
