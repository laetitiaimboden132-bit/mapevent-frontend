# -*- coding: utf-8 -*-
"""
Import multi-sources open data pour enrichir MapEvent.
Sources :
  - Helsinki LinkedEvents (CC BY 4.0)
  - data.stad.gent (Open Data)
  - opendata.swiss (Open Data)
  - OpenAgenda avec recherche par nom de ville (Licence Ouverte v1.0)

Usage : python scraper/import_multi_sources.py
"""
import sys, json, requests, time, re, unicodedata, html as html_mod
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'
STATS = {'created': 0, 'skipped_dup': 0, 'skipped_err': 0}


def norm(s):
    s = (s or '').lower().strip()
    s = unicodedata.normalize('NFD', s)
    return ''.join(c for c in s if unicodedata.category(c) != 'Mn')


def strip_html(s):
    s = re.sub(r'<[^>]+>', ' ', s or '')
    s = html_mod.unescape(s)
    return re.sub(r'\s+', ' ', s).strip()


def assign_cats(title, desc, tags=''):
    text = f"{title} {desc} {tags}".lower()
    result = []
    music_map = {
        'jazz': 'Musique > Jazz', 'blues': 'Musique > Blues',
        'rock': 'Musique > Rock', 'metal': 'Musique > Metal',
        'classical': 'Musique > Classique', 'classique': 'Musique > Classique',
        'opera': 'Musique > Classique', 'techno': 'Musique > Techno',
        'electro': 'Musique > Electro', 'hip hop': 'Musique > Hip-Hop',
        'hip-hop': 'Musique > Hip-Hop', 'rap ': 'Musique > Rap',
        'reggae': 'Musique > Reggae', 'pop ': 'Musique > Pop',
        'punk': 'Musique > Punk', 'house': 'Musique > House',
        'salsa': 'Musique > Latin', 'bachata': 'Musique > Latin',
    }
    for kw, cat in music_map.items():
        if kw in text and cat not in result:
            result.append(cat)
    if any(kw in text for kw in ['concert', 'musik', 'musique', 'music', 'gig', 'live band']) and not any('Musique' in c for c in result):
        result.append('Musique > Concert')
    if 'festival' in text:
        result.append('Festival')
    if any(kw in text for kw in ['theatre', 'theater', 'toneel', 'comedie']):
        result.append('Culture > Theatre')
    if any(kw in text for kw in ['dance', 'danse', 'ballet', 'dans ']):
        result.append('Culture > Danse')
    if any(kw in text for kw in ['circus', 'cirque', 'cirk']):
        result.append('Culture > Cirque')
    if any(kw in text for kw in ['cinema', 'film', 'movie', 'screening']):
        result.append('Culture > Cinema')
    if any(kw in text for kw in ['exhibition', 'exposition', 'expo ', 'museum', 'musee', 'gallery', 'galerie', 'tentoonstelling']):
        result.append('Culture > Exposition')
    if any(kw in text for kw in ['sport', 'running', 'marathon', 'football', 'tennis', 'rugby', 'basket', 'hockey', 'cycling']):
        result.append('Sport > Terrestre')
    if any(kw in text for kw in ['swimming', 'sailing', 'kayak', 'natation']):
        result.append('Sport > Aquatique')
    if any(kw in text for kw in ['ski', 'snowboard', 'luge']):
        result.append('Sport > Glisse')
    if any(kw in text for kw in ['food', 'gastronom', 'culinair', 'cuisine', 'tasting', 'degustation']):
        result.append('Gastronomie')
    if any(kw in text for kw in ['wine', 'vin ', 'wijn']):
        result.append('Gastronomie > Degustation vin')
    if any(kw in text for kw in ['market', 'marche', 'markt', 'brocante', 'flea']):
        result.append('Marche')
    if any(kw in text for kw in ['conference', 'seminar', 'talk', 'lecture']):
        result.append('Conference')
    if any(kw in text for kw in ['workshop', 'atelier']):
        result.append('Atelier')
    if any(kw in text for kw in ['children', 'kids', 'enfant', 'famille', 'family', 'kinderen']):
        result.append('Famille')
    if any(kw in text for kw in ['carnival', 'carnaval']):
        result.append('Carnaval')
    if any(kw in text for kw in ['fair', 'foire', 'salon', 'beurs']):
        result.append('Foire')
    if not result:
        result.append('Culture')
    return list(dict.fromkeys(result))[:3]


# ============ DEDUP ============

def fetch_existing():
    print("[DEDUP] Fetching existing events...")
    r = requests.get(f'{API_URL}/api/events?limit=80000', timeout=120)
    data = r.json()
    keys = data.get('k', [])
    rows = data.get('d', [])
    i_src = keys.index('source_url') if 'source_url' in keys else -1
    i_title = keys.index('title') if 'title' in keys else 1
    i_date = keys.index('date') if 'date' in keys else -1

    source_urls = set()
    title_date = set()
    for row in rows:
        src = (row[i_src] or '').strip().lower() if i_src >= 0 else ''
        if src:
            source_urls.add(src)
        t = norm(row[i_title] or '')
        d = (row[i_date] or '')[:10] if i_date >= 0 else ''
        if t and d:
            title_date.add(f"{t}|{d}")
    print(f"  {len(rows)} events, {len(source_urls)} source_urls")
    return source_urls, title_date


def is_dup(source_url, title, date, source_urls, title_date):
    src = (source_url or '').strip().lower()
    if src and src in source_urls:
        return True
    t = norm(title)
    d = (date or '')[:10]
    if t and d and f"{t}|{d}" in title_date:
        return True
    return False


def send_batch(events, label=''):
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
            STATS['created'] += c
            STATS['skipped_dup'] += s
            print(f"    [{label}] Batch {i//50+1}: {c} created, {s} skipped")
            time.sleep(1)
        except Exception as e:
            print(f"    [{label}] ERR batch: {e}")
    return created


# ============ HELSINKI LinkedEvents (CC BY 4.0) ============

def import_helsinki(source_urls, title_date):
    print("\n" + "="*60)
    print("[HELSINKI] LinkedEvents API - CC BY 4.0")
    print("="*60)
    base = 'https://api.hel.fi/linkedevents/v1/event/'
    events = []
    url = f'{base}?start=2026-02-20&end=2026-12-31&page_size=100&include=location'
    pages = 0
    while url and pages < 20:
        try:
            r = requests.get(url, timeout=30)
            data = r.json()
            for ev in data.get('data', []):
                parsed = parse_helsinki_event(ev, source_urls, title_date)
                if parsed:
                    events.append(parsed)
                    source_urls.add(parsed['source_url'].lower())
                    title_date.add(f"{norm(parsed['title'])}|{parsed['date'][:10]}")
            url = data.get('meta', {}).get('next')
            pages += 1
            time.sleep(1)
        except Exception as e:
            print(f"  ERR: {e}")
            break
    print(f"  {len(events)} new events prepared")
    if events:
        send_batch(events, 'Helsinki')
    return len(events)


def parse_helsinki_event(ev, source_urls, title_date):
    name_obj = ev.get('name', {})
    title = name_obj.get('fi') or name_obj.get('en') or name_obj.get('sv') or ''
    title = title.strip()
    if not title:
        return None

    start = ev.get('start_time', '')
    if not start:
        return None
    date = start[:10]
    end = ev.get('end_time') or start
    end_date = end[:10] if end else date
    start_time = start[11:16] if len(start) > 16 else None
    end_time = end[11:16] if end and len(end) > 16 else None

    source_url = ev.get('info_url', {}).get('fi') or ev.get('info_url', {}).get('en') or ''
    if not source_url:
        eid = ev.get('id', '')
        source_url = f"https://tapahtumat.hel.fi/fi/events/{eid}" if eid else ''
    if not source_url:
        return None

    if is_dup(source_url, title, date, source_urls, title_date):
        return None

    loc = ev.get('location', {})
    pos = loc.get('position', {})
    coords = pos.get('coordinates', [])
    if not coords or len(coords) < 2:
        return None
    lng, lat = coords[0], coords[1]
    if not (59.5 <= lat <= 60.8 and 24.0 <= lng <= 25.5):
        return None

    loc_name = (loc.get('name', {}).get('fi') or loc.get('name', {}).get('en') or '').strip()
    addr = (loc.get('street_address', {}).get('fi') or loc.get('street_address', {}).get('en') or '').strip()
    location = ', '.join(filter(None, [loc_name, addr, 'Helsinki', 'Finland']))

    desc_obj = ev.get('short_description') or ev.get('description') or {}
    desc = strip_html(desc_obj.get('fi') or desc_obj.get('en') or '')
    if len(desc) > 400:
        desc = desc[:397] + '...'
    if not desc:
        desc = f"Event in Helsinki: {title}"

    tags = ' '.join([kw.get('name', {}).get('fi', '') for kw in ev.get('keywords', [])])
    categories = assign_cats(title, desc, tags)

    return {
        'title': title,
        'description': desc,
        'date': date,
        'time': start_time,
        'end_date': end_date,
        'end_time': end_time,
        'location': location,
        'latitude': float(lat),
        'longitude': float(lng),
        'categories': categories,
        'source_url': source_url,
        'type': 'event',
        'validation_status': 'auto_validated',
        'organizer_name': loc_name,
    }


# ============ GENT Open Data (data.stad.gent) ============

def import_gent(source_urls, title_date):
    print("\n" + "="*60)
    print("[GENT] data.stad.gent - Open Data")
    print("="*60)
    base = 'https://data.stad.gent/api/explore/v2.1/catalog/datasets/evenementen-gent/records'
    events = []
    offset = 0
    while offset < 1000:
        params = {
            'where': "startdate >= '2026-02-20'",
            'limit': 100,
            'offset': offset,
            'order_by': 'startdate',
        }
        try:
            r = requests.get(base, params=params, timeout=30)
            if r.status_code != 200:
                print(f"  HTTP {r.status_code}")
                break
            data = r.json()
            records = data.get('results', [])
            if not records:
                break
            for rec in records:
                parsed = parse_gent_event(rec, source_urls, title_date)
                if parsed:
                    events.append(parsed)
                    source_urls.add(parsed['source_url'].lower())
                    title_date.add(f"{norm(parsed['title'])}|{parsed['date'][:10]}")
            offset += 100
            total = data.get('total_count', 0)
            if offset >= total:
                break
            time.sleep(1)
        except Exception as e:
            print(f"  ERR: {e}")
            break
    print(f"  {len(events)} new events prepared")
    if events:
        send_batch(events, 'Gent')
    return len(events)


def parse_gent_event(rec, source_urls, title_date):
    title = (rec.get('title') or rec.get('naam') or '').strip()
    if not title:
        return None

    start = rec.get('startdate') or rec.get('start') or ''
    if not start:
        return None
    date = start[:10]
    end = rec.get('enddate') or rec.get('end') or start
    end_date = end[:10] if end else date

    source_url = rec.get('url') or rec.get('source_url') or ''
    if not source_url:
        return None

    if is_dup(source_url, title, date, source_urls, title_date):
        return None

    geo = rec.get('geometry') or rec.get('geo_point_2d') or {}
    lat, lng = None, None
    if isinstance(geo, dict):
        lat = geo.get('lat') or geo.get('latitude')
        lng = geo.get('lon') or geo.get('lng') or geo.get('longitude')
        if not lat and 'coordinates' in geo:
            coords = geo['coordinates']
            if isinstance(coords, list) and len(coords) >= 2:
                lng, lat = coords[0], coords[1]
    if not lat or not lng:
        lat, lng = 51.05, 3.72

    if not (50.5 <= float(lat) <= 51.5 and 3.0 <= float(lng) <= 4.5):
        return None

    addr = rec.get('address') or rec.get('adres') or rec.get('location') or ''
    location = ', '.join(filter(None, [addr, 'Gent', 'Belgium'])) if addr else 'Gent, Belgium'

    desc = strip_html(rec.get('description') or rec.get('omschrijving') or '')
    if len(desc) > 400:
        desc = desc[:397] + '...'
    if not desc:
        desc = f"Evenement a Gand : {title}"

    categories = assign_cats(title, desc, rec.get('category', ''))

    return {
        'title': title,
        'description': desc,
        'date': date,
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
        'organizer_name': '',
    }


# ============ OPENDATA.SWISS ============

def import_swiss(source_urls, title_date):
    print("\n" + "="*60)
    print("[SWISS] opendata.swiss - Open Data")
    print("="*60)

    cities_ch = [
        ("Winterthur", 47.50, 8.72), ("Thun", 46.76, 7.63),
        ("Aarau", 47.39, 8.04), ("Biel", 47.14, 7.25),
        ("Schaffhausen", 47.70, 8.63), ("Lugano", 46.00, 8.95),
        ("Luzern", 47.05, 8.31), ("St. Gallen", 47.42, 9.37),
        ("Interlaken", 46.69, 7.85), ("Solothurn", 47.21, 7.54),
        ("Zug", 47.17, 8.52), ("Basel", 47.56, 7.59),
        ("Davos", 46.80, 9.84), ("Fribourg", 46.81, 7.15),
    ]

    total = 0
    for city, lat, lng in cities_ch:
        count = import_oa_city_by_name(city, 'CH', lat, lng, source_urls, title_date)
        total += count
    return total


def import_oa_city_by_name(city_name, country_code, lat, lng, source_urls, title_date):
    """Search OpenAgenda by city name in location fields."""
    OA_URL = 'https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/evenements-publics-openagenda/records'
    cn = city_name.lower().replace(' ', '').replace('.', '').replace('-', '')
    where = f"location_countrycode='{country_code}' AND firstdate_begin>='2026-02-01' AND firstdate_begin<'2027-01-01' AND search(location_city, '{city_name}')"

    events = []
    offset = 0
    while offset < 500:
        params = {'where': where, 'limit': 100, 'offset': offset, 'order_by': 'firstdate_begin'}
        try:
            r = requests.get(OA_URL, params=params, timeout=30)
            if r.status_code != 200:
                break
            data = r.json()
            records = data.get('results', [])
            if not records:
                break
            for ev in records:
                parsed = parse_oa_event(ev, country_code, source_urls, title_date)
                if parsed:
                    events.append(parsed)
                    source_urls.add(parsed['source_url'].lower())
                    title_date.add(f"{norm(parsed['title'])}|{parsed['date'][:10]}")
            offset += 100
            total_count = data.get('total_count', 0)
            if offset >= total_count:
                break
            time.sleep(0.8)
        except Exception as e:
            print(f"  ERR {city_name}: {e}")
            break

    print(f"  [{country_code}] {city_name}: {len(events)} new events")
    if events:
        send_batch(events, city_name)
    return len(events)


def parse_oa_event(ev, country_code, source_urls, title_date):
    title = (ev.get('title_fr') or ev.get('title') or '').strip()
    if not title:
        return None

    coords = ev.get('location_coordinates')
    lat, lng = None, None
    if coords and isinstance(coords, dict):
        lat, lng = coords.get('lat'), coords.get('lon')
    if not lat or not lng:
        return None

    first_date = ev.get('firstdate_begin')
    if not first_date:
        return None
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
        return None

    if is_dup(source_url, title, start_date, source_urls, title_date):
        return None

    if country_code == 'CH' and not (45.7 <= lat <= 48.0 and 5.8 <= lng <= 10.6):
        return None
    if country_code == 'FR' and not (41.0 <= lat <= 51.5 and -5.5 <= lng <= 10.0):
        return None

    keywords = ' '.join(ev.get('keywords_fr', []) or [])
    desc_long = ev.get('longdescription_fr') or ev.get('description_fr') or ''
    loc_name = ev.get('location_name') or ''
    categories = assign_cats(title, desc_long, keywords)

    loc_addr = ev.get('location_address') or ''
    loc_city = ev.get('location_city') or ''
    loc_pc = ev.get('location_postalcode') or ''
    parts = list(filter(None, [loc_name if loc_name.lower() != loc_city.lower() else '', loc_addr, f"{loc_pc} {loc_city}".strip()]))
    country_name = {'CH': 'Suisse', 'FR': 'France', 'BE': 'Belgique'}.get(country_code, '')
    if country_name:
        parts.append(country_name)
    location = ', '.join(parts) if parts else loc_city

    desc = strip_html(desc_long)
    if len(desc) > 400:
        desc = desc[:397] + '...'
    if not desc:
        desc = f"Evenement : {title}"

    return {
        'title': title,
        'description': desc,
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
        'organizer_name': loc_name,
    }


# ============ FR cities - deeper search by name ============

def import_fr_by_name(source_urls, title_date):
    print("\n" + "="*60)
    print("[FR] OpenAgenda search by city name")
    print("="*60)
    cities_fr = [
        ("Toulon", "FR", 43.12, 5.93), ("Troyes", "FR", 48.30, 4.07),
        ("Colmar", "FR", 48.08, 7.36), ("Cannes", "FR", 43.55, 7.01),
        ("Auxerre", "FR", 47.80, 3.57), ("Ajaccio", "FR", 41.93, 8.74),
        ("Cherbourg", "FR", 49.64, -1.62), ("Macon", "FR", 46.31, 4.83),
        ("Niort", "FR", 46.32, -0.46), ("Grasse", "FR", 43.66, 6.92),
        ("Beziers", "FR", 43.34, 3.21), ("Vannes", "FR", 47.66, -2.76),
        ("Lorient", "FR", 47.75, -3.37), ("Bayonne", "FR", 43.49, -1.47),
        ("Biarritz", "FR", 43.48, -1.56), ("Reims", "FR", 49.25, 3.88),
        ("Dunkerque", "FR", 51.03, 2.38), ("Senlis", "FR", 49.21, 2.59),
        ("Hyeres", "FR", 43.12, 6.13), ("Chalon-sur-Saone", "FR", 46.78, 4.85),
    ]
    total = 0
    for city, cc, lat, lng in cities_fr:
        count = import_oa_city_by_name(city, cc, lat, lng, source_urls, title_date)
        total += count
    return total


# ============ MAIN ============

def main():
    print("=" * 60)
    print("IMPORT MULTI-SOURCES OPEN DATA")
    print("=" * 60)

    source_urls, title_date = fetch_existing()

    n_helsinki = import_helsinki(source_urls, title_date)
    n_gent = import_gent(source_urls, title_date)
    n_swiss = import_swiss(source_urls, title_date)
    n_fr = import_fr_by_name(source_urls, title_date)

    print("\n" + "=" * 60)
    print("RESUME FINAL")
    print("=" * 60)
    print(f"  Helsinki LinkedEvents : {n_helsinki} events")
    print(f"  Gent Open Data        : {n_gent} events")
    print(f"  Swiss (OA by name)    : {n_swiss} events")
    print(f"  France (OA by name)   : {n_fr} events")
    print(f"  ---")
    print(f"  TOTAL API created     : {STATS['created']}")
    print(f"  TOTAL API skipped     : {STATS['skipped_dup']}")
    print("=" * 60)

    with open('import_multi_sources_log.json', 'w', encoding='utf-8') as f:
        json.dump({
            'helsinki': n_helsinki, 'gent': n_gent,
            'swiss': n_swiss, 'france': n_fr,
            'total_created': STATS['created'],
            'total_skipped': STATS['skipped_dup'],
        }, f, indent=2)


if __name__ == '__main__':
    main()
