# -*- coding: utf-8 -*-
"""
Import d'events OpenAgenda pour les villes contactees par email (widget).
Source : OpenDataSoft / OpenAgenda - Licence Ouverte v1.0
Dedup triple : source_url + titre exact + titre+ville+date
Usage : python scraper/import_widget_cities.py
"""
import sys, json, requests, time, re, unicodedata
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'
OA_URL = 'https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/evenements-publics-openagenda/records'

CITIES = [
    # (nom recherche OpenAgenda, pays code, lat, lng) pour geofilter fallback
    # FR - villes < 20 events
    ("Antibes", "FR", 43.58, 7.12), ("Toulon", "FR", 43.12, 5.93),
    ("Hyeres", "FR", 43.12, 6.13), ("Troyes", "FR", 48.30, 4.07),
    ("Colmar", "FR", 48.08, 7.36), ("Cannes", "FR", 43.55, 7.01),
    ("Auxerre", "FR", 47.80, 3.57), ("Ajaccio", "FR", 41.93, 8.74),
    ("Cherbourg", "FR", 49.64, -1.62), ("Macon", "FR", 46.31, 4.83),
    ("Chalon-sur-Saone", "FR", 46.78, 4.85), ("Niort", "FR", 46.32, -0.46),
    ("Grasse", "FR", 43.66, 6.92), ("Beziers", "FR", 43.34, 3.21),
    ("Vannes", "FR", 47.66, -2.76), ("Lorient", "FR", 47.75, -3.37),
    ("Bayonne", "FR", 43.49, -1.47), ("Biarritz", "FR", 43.48, -1.56),
    ("Reims", "FR", 49.25, 3.88), ("Dunkerque", "FR", 51.03, 2.38),
    ("Senlis", "FR", 49.21, 2.59),
    # CH - villes < 20 events
    ("Montreux", "CH", 46.43, 6.91), ("Vevey", "CH", 46.46, 6.84),
    ("Yverdon", "CH", 46.78, 6.64), ("Monthey", "CH", 46.25, 6.95),
    ("Neuchatel", "CH", 47.00, 6.93), ("Morges", "CH", 46.51, 6.50),
    ("Winterthur", "CH", 47.50, 8.72), ("Thun", "CH", 46.76, 7.63),
    ("Aarau", "CH", 47.39, 8.04), ("Biel", "CH", 47.14, 7.25),
    ("Schaffhausen", "CH", 47.70, 8.63), ("Davos", "CH", 46.80, 9.84),
    ("Lugano", "CH", 46.00, 8.95), ("Luzern", "CH", 47.05, 8.31),
    ("St. Gallen", "CH", 47.42, 9.37), ("Fribourg", "CH", 46.81, 7.15),
    ("Interlaken", "CH", 46.69, 7.85), ("Solothurn", "CH", 47.21, 7.54),
    ("Zug", "CH", 47.17, 8.52), ("Basel", "CH", 47.56, 7.59),
    # BE
    ("Antwerpen", "BE", 51.22, 4.40), ("Gent", "BE", 51.05, 3.72),
]


def norm(s):
    s = (s or '').lower().strip()
    s = unicodedata.normalize('NFD', s)
    return ''.join(c for c in s if unicodedata.category(c) != 'Mn')


def assign_categories(title, description, keywords, location_name):
    text = f"{title} {description} {keywords} {location_name}".lower()
    result = []

    music_map = {
        'jazz': 'Musique > Jazz', 'blues': 'Musique > Blues',
        'rock': 'Musique > Rock', 'metal': 'Musique > Metal',
        'punk': 'Musique > Punk', 'pop ': 'Musique > Pop',
        'rap ': 'Musique > Rap', 'hip hop': 'Musique > Hip-Hop',
        'hip-hop': 'Musique > Hip-Hop', 'techno': 'Musique > Techno',
        'electro': 'Musique > Electro', 'house ': 'Musique > House',
        'trance': 'Musique > Trance', 'reggae': 'Musique > Reggae',
        'classique': 'Musique > Classique', 'opera': 'Musique > Classique',
        'chorale': 'Musique > Classique', 'orchestre': 'Musique > Classique',
        'salsa': 'Musique > Latin', 'bachata': 'Musique > Latin',
    }
    for kw, cat in music_map.items():
        if kw in text and cat not in result:
            result.append(cat)
    if ('concert' in text or 'musique' in text or 'music' in text) and not any('Musique >' in c for c in result):
        result.append('Musique > Concert')

    if 'festival' in text:
        result.append('Festival')
    if any(kw in text for kw in ['theatre', 'piece de', 'comedie']):
        result.append('Culture > Theatre')
    if any(kw in text for kw in ['danse', 'ballet', 'choregraph']):
        result.append('Culture > Danse')
    if any(kw in text for kw in ['cirque', 'acrobat', 'clown']):
        result.append('Culture > Cirque')
    if any(kw in text for kw in ['spectacle', 'one man show', 'humoriste']) and not any('Culture >' in c for c in result):
        result.append('Culture > Spectacle')
    if any(kw in text for kw in ['cinema', 'film', 'projection']):
        result.append('Culture > Cinema')
    if any(kw in text for kw in ['exposition', 'expo ', 'musee', 'galerie', 'vernissage']):
        result.append('Culture > Exposition')
    if any(kw in text for kw in ['photo', 'photographi']):
        result.append('Culture > Photographie')

    sport_map = {
        'ski': 'Sport > Glisse', 'snowboard': 'Sport > Glisse',
        'hockey': 'Sport > Terrestre', 'football': 'Sport > Terrestre',
        'tennis': 'Sport > Terrestre', 'basket': 'Sport > Terrestre',
        'rugby': 'Sport > Terrestre', 'randonnee': 'Sport > Terrestre',
        'trail': 'Sport > Terrestre', 'marathon': 'Sport > Terrestre',
        'cyclisme': 'Sport > Terrestre', 'velo': 'Sport > Terrestre',
        'natation': 'Sport > Aquatique', 'voile': 'Sport > Aquatique',
        'kayak': 'Sport > Aquatique',
    }
    for kw, cat in sport_map.items():
        if kw in text and cat not in result:
            result.append(cat)
    if any(kw in text for kw in ['sportif', 'competition', 'tournoi']) and not any('Sport' in c for c in result):
        result.append('Sport > Terrestre')

    if any(kw in text for kw in ['degustation', 'vignoble', 'oenolog', 'vin ']):
        result.append('Gastronomie > Degustation vin')
    elif any(kw in text for kw in ['biere', 'brasserie']):
        result.append('Gastronomie > Degustation biere')
    elif any(kw in text for kw in ['brunch', 'gastronomie', 'culinaire', 'cuisine', 'food']):
        result.append('Gastronomie')

    if any(kw in text for kw in ['marche', 'brocante', 'vide-grenier', 'puces']):
        result.append('Marche > Brocante' if any(kw in text for kw in ['brocante', 'vide-grenier']) else 'Marche')
    if any(kw in text for kw in ['foire', 'salon ']):
        result.append('Foire')
    if 'carnaval' in text:
        result.append('Carnaval')
    if any(kw in text for kw in ['conference', 'seminaire', 'colloque']):
        result.append('Conference')
    if any(kw in text for kw in ['atelier', 'workshop']):
        result.append('Atelier')
    if any(kw in text for kw in ['conte ', 'lecture', 'littera']):
        result.append('Culture > Conte')
    if any(kw in text for kw in ['enfant', 'famille', 'kid', 'jeune public']):
        result.append('Famille')

    if not result:
        result.append('Culture')
    return list(dict.fromkeys(result))[:3]


def clean_address(loc_name, loc_addr, loc_city, loc_postcode, country_code):
    parts = []
    addr = (loc_addr or '').strip()
    name = (loc_name or '').strip()
    city = (loc_city or '').strip()
    postcode = str(loc_postcode or '').strip()

    if name and name.lower() != city.lower():
        parts.append(name)
    if addr and addr.lower() not in ['', 'null', 'none'] and addr.lower() != city.lower():
        if not any(addr.lower() in p.lower() for p in parts):
            parts.append(addr)
    if postcode and city:
        parts.append(f"{postcode} {city}")
    elif city:
        parts.append(city)

    country = {'FR': 'France', 'CH': 'Suisse', 'BE': 'Belgique'}.get(country_code, '')
    if country:
        parts.append(country)
    return ', '.join(parts) if parts else city or ''


def clean_desc(title, long_desc):
    desc = (long_desc or '').strip()
    if not desc:
        return f"Evenement : {title}."
    desc = re.sub(r'<[^>]+>', ' ', desc)
    desc = re.sub(r'\s+', ' ', desc).strip()
    if len(desc) > 400:
        desc = desc[:397] + '...'
    return desc


def fetch_existing():
    print("Fetching existing events for dedup...")
    r = requests.get(f'{API_URL}/api/events?limit=80000', timeout=120)
    data = r.json()
    keys = data.get('k', [])
    rows = data.get('d', [])
    i_title = keys.index('title') if 'title' in keys else 1
    i_src = keys.index('source_url') if 'source_url' in keys else -1
    i_loc = keys.index('location') if 'location' in keys else -1
    i_date = keys.index('date') if 'date' in keys else -1

    source_urls = set()
    title_keys = set()
    title_city_date = set()

    for row in rows:
        src = (row[i_src] or '').strip().lower() if i_src >= 0 else ''
        if src:
            source_urls.add(src)
        t = norm(row[i_title] or '')
        if t:
            title_keys.add(t)
        loc = norm(row[i_loc] or '') if i_loc >= 0 else ''
        d = (row[i_date] or '') if i_date >= 0 else ''
        if t and d:
            title_city_date.add(f"{t}|{d[:10]}")

    print(f"  {len(rows)} events, {len(source_urls)} source_urls, {len(title_keys)} titles")
    return source_urls, title_keys, title_city_date


def is_dup(source_url, title, date, source_urls, title_keys, title_city_date):
    src = (source_url or '').strip().lower()
    if src and src in source_urls:
        return True
    t = norm(title)
    if t in title_keys:
        return True
    d = (date or '')[:10]
    if t and d and f"{t}|{d}" in title_city_date:
        return True
    return False


def fetch_oa_city(city_name, country_code, lat, lng):
    """Fetch events from OpenAgenda for a specific city."""
    all_ev = []
    where_parts = [
        f"location_countrycode='{country_code}'",
        "firstdate_begin>='2026-02-01'",
        "firstdate_begin<'2027-01-01'",
    ]
    where = ' AND '.join(where_parts)

    offset = 0
    limit = 100
    max_records = 500

    while offset < max_records:
        params = {
            'where': where,
            'limit': limit,
            'offset': offset,
            'order_by': 'firstdate_begin',
            'geofilter.distance': f'{lat},{lng},20000',
        }
        try:
            r = requests.get(OA_URL, params=params, timeout=30)
            if r.status_code != 200:
                break
            data = r.json()
            records = data.get('results', [])
            total = data.get('total_count', 0)
            if not records:
                break
            all_ev.extend(records)
            offset += limit
            if offset >= total or offset >= max_records:
                break
            time.sleep(0.8)
        except Exception as e:
            print(f"    ERR fetch {city_name}: {e}")
            break
    return all_ev


def process_event(ev, country_code, source_urls, title_keys, title_city_date):
    title = (ev.get('title_fr') or ev.get('title') or '').strip()
    if not title:
        return None, 'no_title'

    coords = ev.get('location_coordinates')
    lat, lng = None, None
    if coords and isinstance(coords, dict):
        lat, lng = coords.get('lat'), coords.get('lon')
    if not lat or not lng:
        latlon = ev.get('latlon')
        if latlon and isinstance(latlon, dict):
            lat, lng = latlon.get('lat'), latlon.get('lon')
    if not lat or not lng:
        return None, 'no_coords'

    first_date = ev.get('firstdate_begin')
    if not first_date:
        return None, 'no_date'
    start_date = first_date[:10]
    last_date = ev.get('lastdate_end') or ev.get('lastdate_begin') or first_date
    end_date = last_date[:10] if last_date else start_date

    source_url = ev.get('canonicalurl') or ''
    if not source_url:
        slug = ev.get('slug', '')
        uid = ev.get('uid', '')
        if slug:
            source_url = f"https://openagenda.com/events/{slug}"
        elif uid:
            source_url = f"https://openagenda.com/events/{uid}"
    if not source_url:
        return None, 'no_source_url'

    if is_dup(source_url, title, start_date, source_urls, title_keys, title_city_date):
        return None, 'duplicate'

    # Bounds check
    if country_code == 'FR' and not (41.0 <= lat <= 51.5 and -5.5 <= lng <= 10.0):
        return None, 'bad_coords'
    if country_code == 'CH' and not (45.7 <= lat <= 48.0 and 5.8 <= lng <= 10.6):
        return None, 'bad_coords'
    if country_code == 'BE' and not (49.5 <= lat <= 51.6 and 2.5 <= lng <= 6.5):
        return None, 'bad_coords'

    keywords = ' '.join(ev.get('keywords_fr', []) or [])
    desc_long = ev.get('longdescription_fr') or ev.get('description_fr') or ''
    loc_name = ev.get('location_name') or ''
    categories = assign_categories(title, desc_long, keywords, loc_name)
    location = clean_address(
        ev.get('location_name'), ev.get('location_address'),
        ev.get('location_city'), ev.get('location_postalcode'), country_code
    )
    description = clean_desc(title, desc_long)

    return {
        'title': title,
        'description': description,
        'date': start_date,
        'time': None,
        'end_date': end_date,
        'end_time': None,
        'location': location,
        'latitude': float(lat),
        'longitude': float(lng),
        'categories': categories,
        'source_url': source_url,
        'type': 'event',
        'validation_status': 'auto_validated',
        'organizer_name': ev.get('location_name') or '',
    }, 'ok'


def send_batch(events):
    created = 0
    for i in range(0, len(events), 50):
        batch = events[i:i+50]
        try:
            r = requests.post(
                f'{API_URL}/api/events/scraped/batch',
                json={'events': batch, 'send_emails': False},
                timeout=60
            )
            res = r.json()
            c = res.get('results', {}).get('created', 0)
            s = res.get('results', {}).get('skipped', 0)
            created += c
            print(f"    Batch {i//50+1}: {c} created, {s} skipped")
            time.sleep(1)
        except Exception as e:
            print(f"    ERR batch: {e}")
    return created


def main():
    print("=" * 60)
    print("IMPORT OPEN DATA - VILLES WIDGET")
    print("Source: OpenAgenda / OpenDataSoft")
    print("Licence: Licence Ouverte v1.0")
    print("=" * 60)

    source_urls, title_keys, title_city_date = fetch_existing()

    total_imported = 0
    city_stats = []

    for city_name, cc, lat, lng in CITIES:
        print(f"\n  [{cc}] {city_name} ({lat},{lng})...")
        raw = fetch_oa_city(city_name, cc, lat, lng)
        print(f"    Raw: {len(raw)} events from OpenAgenda")

        if not raw:
            city_stats.append((city_name, cc, 0, 0))
            continue

        events = []
        stats = {'ok': 0, 'duplicate': 0, 'no_coords': 0, 'no_date': 0, 'no_title': 0, 'no_source_url': 0, 'bad_coords': 0}
        for ev in raw:
            event_data, status = process_event(ev, cc, source_urls, title_keys, title_city_date)
            stats[status] = stats.get(status, 0) + 1
            if event_data:
                events.append(event_data)
                source_urls.add(event_data['source_url'].lower())
                title_keys.add(norm(event_data['title']))

        print(f"    OK: {stats['ok']} | Dup: {stats['duplicate']} | NoCoord: {stats['no_coords']} | NoDt: {stats['no_date']} | BadC: {stats['bad_coords']}")

        if events:
            created = send_batch(events)
            total_imported += created
            city_stats.append((city_name, cc, len(events), created))
        else:
            city_stats.append((city_name, cc, 0, 0))

    print(f"\n{'='*60}")
    print(f"RESUME")
    print(f"{'='*60}")
    print(f"{'Ville':<25} {'Pays':>4} {'Prep':>6} {'Import':>7}")
    print(f"{'-'*45}")
    for name, cc, prep, imp in city_stats:
        if prep > 0:
            print(f"  {name:<23} {cc:>4} {prep:>6} {imp:>7}")
    print(f"\nTOTAL IMPORTE: {total_imported} events")
    print(f"{'='*60}")

    with open('import_widget_cities_log.json', 'w', encoding='utf-8') as f:
        json.dump({
            'total_imported': total_imported,
            'cities': [{'city': n, 'country': c, 'prepared': p, 'imported': i} for n, c, p, i in city_stats]
        }, f, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    main()
