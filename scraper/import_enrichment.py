# -*- coding: utf-8 -*-
"""
Enrichissement massif - Sources open data additionnelles.
  1. Helsinki LinkedEvents (CC BY 4.0) - 17K events
  2. OpenAgenda API directe - agendas specifiques par ville
  3. Nantes Metropole Open Data
  4. OpenAgenda FR - recherche elargie departements
Usage : python scraper/import_enrichment.py
"""
import sys, json, requests, time, re, unicodedata, html as html_mod
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'
STATS = {'created': 0, 'skipped': 0}


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
    mm = {
        'jazz': 'Musique > Jazz', 'blues': 'Musique > Blues',
        'rock': 'Musique > Rock', 'metal': 'Musique > Metal',
        'classical': 'Musique > Classique', 'classique': 'Musique > Classique',
        'opera': 'Musique > Classique', 'techno': 'Musique > Techno',
        'electro': 'Musique > Electro', 'hip hop': 'Musique > Hip-Hop',
        'hip-hop': 'Musique > Hip-Hop', 'reggae': 'Musique > Reggae',
        'pop ': 'Musique > Pop', 'punk': 'Musique > Punk',
        'house ': 'Musique > House', 'salsa': 'Musique > Latin',
        'folk': 'Musique > Folk', 'country': 'Musique > Country',
        'soul': 'Musique > Soul', 'r&b': 'Musique > R&B',
        'indie': 'Musique > Indie', 'ambient': 'Musique > Ambient',
    }
    for kw, cat in mm.items():
        if kw in text and cat not in result:
            result.append(cat)
    if any(kw in text for kw in ['concert', 'musik', 'musique', 'music', 'keikka', 'konsertti', 'gig']) and not any('Musique' in c for c in result):
        result.append('Musique > Concert')
    if 'festival' in text:
        result.append('Festival')
    if any(kw in text for kw in ['theatre', 'theater', 'teatteri', 'nayttelija', 'comedie', 'piece']):
        result.append('Culture > Theatre')
    if any(kw in text for kw in ['dance', 'danse', 'ballet', 'tanssi']):
        result.append('Culture > Danse')
    if any(kw in text for kw in ['circus', 'cirque', 'sirkus']):
        result.append('Culture > Cirque')
    if any(kw in text for kw in ['cinema', 'film', 'movie', 'elokuva']):
        result.append('Culture > Cinema')
    if any(kw in text for kw in ['exhibition', 'exposition', 'nayttely', 'museum', 'musee', 'gallery', 'galerie', 'museo']):
        result.append('Culture > Exposition')
    if any(kw in text for kw in ['spectacle', 'show ', 'esitys', 'stand-up', 'humour']):
        result.append('Culture > Spectacle')
    if any(kw in text for kw in ['photo', 'valokuv']):
        result.append('Culture > Photographie')
    if any(kw in text for kw in ['sport', 'urheilu', 'running', 'marathon', 'football', 'tennis', 'rugby', 'basket', 'hockey', 'jalkapallo']):
        result.append('Sport > Terrestre')
    if any(kw in text for kw in ['swimming', 'sailing', 'kayak', 'uinti', 'purjehdus']):
        result.append('Sport > Aquatique')
    if any(kw in text for kw in ['ski', 'snowboard', 'laskettelu', 'hiihto']):
        result.append('Sport > Glisse')
    if any(kw in text for kw in ['food', 'gastronom', 'cuisine', 'tasting', 'degustation', 'ruoka']):
        result.append('Gastronomie')
    if any(kw in text for kw in ['wine', 'vin ', 'viini']):
        result.append('Gastronomie > Degustation vin')
    if any(kw in text for kw in ['beer', 'biere', 'olut', 'brasserie', 'brewery']):
        result.append('Gastronomie > Degustation biere')
    if any(kw in text for kw in ['market', 'marche', 'markkinat', 'tori', 'brocante', 'flea']):
        result.append('Marche')
    if any(kw in text for kw in ['conference', 'seminar', 'seminaari', 'colloque', 'talk']):
        result.append('Conference')
    if any(kw in text for kw in ['workshop', 'atelier', 'tyopaja']):
        result.append('Atelier')
    if any(kw in text for kw in ['children', 'kids', 'enfant', 'famille', 'family', 'lapsi', 'perhe', 'jeune public']):
        result.append('Famille')
    if any(kw in text for kw in ['carnival', 'carnaval', 'karnevaali']):
        result.append('Carnaval')
    if any(kw in text for kw in ['fair', 'foire', 'salon', 'messut']):
        result.append('Foire')
    if any(kw in text for kw in ['conte', 'lecture', 'reading', 'lukeminen', 'litterature', 'book']):
        result.append('Culture > Conte')
    if not result:
        result.append('Culture')
    return list(dict.fromkeys(result))[:3]


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
    print(f"  {len(rows)} events existants, {len(source_urls)} source_urls")
    return source_urls, title_date


def is_dup(src_url, title, date, su, td):
    s = (src_url or '').strip().lower()
    if s and s in su:
        return True
    t = norm(title)
    d = (date or '')[:10]
    if t and d and f"{t}|{d}" in td:
        return True
    return False


def register(ev, su, td):
    su.add(ev['source_url'].lower())
    td.add(f"{norm(ev['title'])}|{ev['date'][:10]}")


def send_batch(events, label=''):
    created = 0
    for i in range(0, len(events), 50):
        batch = events[i:i+50]
        try:
            r = requests.post(f'{API_URL}/api/events/scraped/batch',
                              json={'events': batch, 'send_emails': False}, timeout=60)
            res = r.json()
            c = res.get('results', {}).get('created', 0)
            s = res.get('results', {}).get('skipped', 0)
            created += c
            STATS['created'] += c
            STATS['skipped'] += s
            print(f"    [{label}] Batch {i//50+1}: {c} crees, {s} skip")
            time.sleep(1)
        except Exception as e:
            print(f"    [{label}] ERR: {e}")
    return created


# ===============================================
# 1. HELSINKI - LinkedEvents API (CC BY 4.0)
# ===============================================

def import_helsinki(su, td):
    print("\n" + "="*60)
    print("HELSINKI LinkedEvents - CC BY 4.0")
    print("  17K+ events disponibles")
    print("="*60)
    base = 'https://api.hel.fi/linkedevents/v1/event/'
    events = []
    url = f'{base}?start=today&end=2026-12-31&page_size=100&include=location&sort=start_time'
    pages = 0
    max_pages = 50
    while url and pages < max_pages:
        try:
            r = requests.get(url, timeout=30)
            if r.status_code != 200:
                print(f"  HTTP {r.status_code} at page {pages}")
                break
            data = r.json()
            total = data.get('meta', {}).get('count', 0)
            if pages == 0:
                print(f"  Total disponible: {total} events")
            for ev in data.get('data', []):
                parsed = parse_hel(ev, su, td)
                if parsed:
                    events.append(parsed)
                    register(parsed, su, td)
            url = data.get('meta', {}).get('next')
            pages += 1
            if pages % 10 == 0:
                print(f"  Page {pages}: {len(events)} new events so far...")
            time.sleep(0.5)
        except Exception as e:
            print(f"  ERR page {pages}: {e}")
            break

    print(f"  Total: {len(events)} new events")
    if events:
        send_batch(events, 'Helsinki')
    return len(events)


def parse_hel(ev, su, td):
    nm = ev.get('name', {})
    title = (nm.get('fi') or nm.get('en') or nm.get('sv') or '').strip()
    if not title or len(title) < 3:
        return None

    start = ev.get('start_time', '')
    if not start:
        return None
    date = start[:10]
    end = ev.get('end_time') or start
    end_date = end[:10] if end else date
    st = start[11:16] if len(start) > 16 and 'T' in start else None
    et = end[11:16] if end and len(end) > 16 and 'T' in end else None

    eid = ev.get('id', '')
    info = ev.get('info_url') or {}
    src = info.get('fi') or info.get('en') or ''
    if not src:
        src = f"https://tapahtumat.hel.fi/fi/events/{eid}" if eid else ''
    if not src:
        return None

    if is_dup(src, title, date, su, td):
        return None

    loc = ev.get('location') or {}
    if isinstance(loc, str):
        return None
    pos = loc.get('position') or {}
    coords = pos.get('coordinates', [])
    if not coords or len(coords) < 2:
        return None
    lng, lat = float(coords[0]), float(coords[1])
    if not (59.0 <= lat <= 61.0 and 23.5 <= lng <= 26.0):
        return None

    ln = loc.get('name', {})
    loc_name = (ln.get('fi') or ln.get('en') or '').strip()
    sa = loc.get('street_address', {})
    addr = (sa.get('fi') or sa.get('en') or '').strip()
    location = ', '.join(filter(None, [loc_name, addr, 'Helsinki', 'Finland']))

    sd = ev.get('short_description') or ev.get('description') or {}
    desc = strip_html(sd.get('fi') or sd.get('en') or '')
    if len(desc) > 400:
        desc = desc[:397] + '...'
    if not desc:
        desc = f"Event in Helsinki: {title}"

    kws = ev.get('keywords', [])
    tags = ' '.join([k.get('name', {}).get('fi', '') for k in kws if isinstance(k, dict)])
    cats = assign_cats(title, desc, tags)

    return {
        'title': title, 'description': desc,
        'date': date, 'time': st, 'end_date': end_date, 'end_time': et,
        'location': location, 'latitude': lat, 'longitude': lng,
        'categories': cats, 'source_url': src,
        'type': 'event', 'validation_status': 'auto_validated',
        'organizer_name': loc_name,
    }


# ===============================================
# 2. NANTES METROPOLE OPEN DATA
# ===============================================

def import_nantes(su, td):
    print("\n" + "="*60)
    print("NANTES Metropole Open Data")
    print("="*60)
    base = 'https://data.nantesmetropole.fr/api/explore/v2.1/catalog/datasets/244400404_agenda-evenements-nantes-nantes-metropole/records'
    events = []
    offset = 0
    while offset < 2000:
        params = {
            'where': "date >= '2026-02-20'",
            'limit': 100, 'offset': offset,
            'order_by': 'date',
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
                parsed = parse_nantes(rec, su, td)
                if parsed:
                    events.append(parsed)
                    register(parsed, su, td)
            offset += 100
            tc = data.get('total_count', 0)
            if offset == 100:
                print(f"  Total disponible: {tc}")
            if offset >= tc:
                break
            time.sleep(0.8)
        except Exception as e:
            print(f"  ERR: {e}")
            break
    print(f"  {len(events)} new events")
    if events:
        send_batch(events, 'Nantes')
    return len(events)


def parse_nantes(rec, su, td):
    title = (rec.get('nom') or rec.get('title') or '').strip()
    if not title:
        return None
    date = (rec.get('date') or '')[:10]
    if not date:
        return None
    end_date = (rec.get('date_fin') or date)[:10]

    src = rec.get('url') or rec.get('lien') or ''
    if not src:
        return None
    if is_dup(src, title, date, su, td):
        return None

    geo = rec.get('location') or rec.get('geo') or rec.get('geo_shape') or {}
    lat, lng = None, None
    if isinstance(geo, dict):
        lat = geo.get('lat')
        lng = geo.get('lon') or geo.get('lng')
    if not lat or not lng:
        lat, lng = 47.218, -1.553
    if not (46.5 <= float(lat) <= 48.0 and -2.5 <= float(lng) <= 0.0):
        return None

    addr = rec.get('lieu') or rec.get('adresse') or ''
    location = ', '.join(filter(None, [addr, 'Nantes', 'France'])) if addr else 'Nantes, France'

    desc = strip_html(rec.get('description') or rec.get('resume') or '')
    if len(desc) > 400:
        desc = desc[:397] + '...'
    if not desc:
        desc = f"Evenement a Nantes : {title}"

    cats = assign_cats(title, desc, rec.get('rubrique', ''))

    return {
        'title': title, 'description': desc,
        'date': date, 'time': None, 'end_date': end_date, 'end_time': None,
        'location': location, 'latitude': float(lat), 'longitude': float(lng),
        'categories': cats, 'source_url': src,
        'type': 'event', 'validation_status': 'auto_validated',
        'organizer_name': '',
    }


# ===============================================
# 3. OpenAgenda - Agendas specifiques par ville
# ===============================================

CITY_AGENDAS = [
    # (agenda_uid or slug, city, country_code, lat, lng)
    # FR
    ("toulon-evenements", "Toulon", "FR", 43.12, 5.93),
    ("ville-de-reims", "Reims", "FR", 49.25, 3.88),
    ("colmar-agglomeration", "Colmar", "FR", 48.08, 7.36),
    ("bayonne-evenements", "Bayonne", "FR", 43.49, -1.47),
    ("ville-de-cannes", "Cannes", "FR", 43.55, 7.01),
    ("dunkerque-evenements", "Dunkerque", "FR", 51.03, 2.38),
    ("ajaccio-evenements", "Ajaccio", "FR", 41.93, 8.74),
    ("vannes-evenements", "Vannes", "FR", 47.66, -2.76),
    ("biarritz-tourisme", "Biarritz", "FR", 43.48, -1.56),
    ("lorient-agglo", "Lorient", "FR", 47.75, -3.37),
    ("troyes-champagne-metropole", "Troyes", "FR", 48.30, 4.07),
    ("niort-agglo", "Niort", "FR", 46.32, -0.46),
    ("beziers-evenements", "Beziers", "FR", 43.34, 3.21),
    ("grasse-evenements", "Grasse", "FR", 43.66, 6.92),
    ("hyeres-tourisme", "Hyeres", "FR", 43.12, 6.13),
    # CH
    ("winterthur-events", "Winterthur", "CH", 47.50, 8.72),
    ("basel-tourismus", "Basel", "CH", 47.56, 7.59),
    ("luzern-events", "Luzern", "CH", 47.05, 8.31),
    ("lugano-eventi", "Lugano", "CH", 46.00, 8.95),
]

OA_SEARCH = 'https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/evenements-publics-openagenda/records'


def import_oa_agendas(su, td):
    print("\n" + "="*60)
    print("OpenAgenda - Recherche elargie par region/departement")
    print("="*60)

    FR_DEPTS = [
        ("Var", "FR", 43.46, 6.22, 40000),
        ("Marne", "FR", 49.0, 3.9, 40000),
        ("Haut-Rhin", "FR", 48.0, 7.3, 30000),
        ("Pyrenees-Atlantiques", "FR", 43.3, -0.8, 40000),
        ("Alpes-Maritimes", "FR", 43.7, 7.2, 40000),
        ("Nord", "FR", 50.6, 3.0, 40000),
        ("Morbihan", "FR", 47.7, -2.8, 40000),
        ("Aube", "FR", 48.3, 4.1, 30000),
        ("Deux-Sevres", "FR", 46.3, -0.4, 30000),
        ("Herault", "FR", 43.6, 3.4, 40000),
        ("Corse-du-Sud", "FR", 41.9, 8.9, 30000),
        ("Finistere", "FR", 48.4, -4.0, 40000),
        ("Saone-et-Loire", "FR", 46.6, 4.6, 40000),
    ]

    total = 0
    for dept, cc, lat, lng, radius in FR_DEPTS:
        count = _oa_geo_search(dept, cc, lat, lng, radius, su, td)
        total += count
        time.sleep(1)

    CH_REGIONS = [
        ("Zurich-region", "CH", 47.38, 8.54, 30000),
        ("Basel-region", "CH", 47.56, 7.59, 25000),
        ("Luzern-region", "CH", 47.05, 8.31, 25000),
        ("Bern-Oberland", "CH", 46.69, 7.85, 30000),
        ("Ticino", "CH", 46.00, 8.95, 30000),
        ("Ostschweiz", "CH", 47.42, 9.37, 30000),
        ("Aargau", "CH", 47.39, 8.04, 25000),
        ("Solothurn-region", "CH", 47.21, 7.54, 20000),
        ("Schaffhausen-region", "CH", 47.70, 8.63, 20000),
        ("Zug-region", "CH", 47.17, 8.52, 20000),
    ]

    for reg, cc, lat, lng, radius in CH_REGIONS:
        count = _oa_geo_search(reg, cc, lat, lng, radius, su, td)
        total += count
        time.sleep(1)

    return total


def _oa_geo_search(label, cc, lat, lng, radius, su, td):
    where = f"location_countrycode='{cc}' AND firstdate_begin>='2026-02-20' AND firstdate_begin<'2027-01-01'"
    events = []
    offset = 0
    while offset < 800:
        params = {
            'where': where, 'limit': 100, 'offset': offset,
            'order_by': 'firstdate_begin',
            'geofilter.distance': f'{lat},{lng},{radius}',
        }
        try:
            r = requests.get(OA_SEARCH, params=params, timeout=30)
            if r.status_code != 200:
                break
            data = r.json()
            recs = data.get('results', [])
            if not recs:
                break
            for ev in recs:
                p = _parse_oa(ev, cc, su, td)
                if p:
                    events.append(p)
                    register(p, su, td)
            offset += 100
            tc = data.get('total_count', 0)
            if offset >= tc or offset >= 800:
                break
            time.sleep(0.8)
        except Exception as e:
            print(f"  ERR {label}: {e}")
            break
    if events:
        send_batch(events, label)
    print(f"  [{cc}] {label}: {len(events)} new")
    return len(events)


def _parse_oa(ev, cc, su, td):
    title = (ev.get('title_fr') or ev.get('title') or '').strip()
    if not title:
        return None
    coords = ev.get('location_coordinates')
    lat, lng = None, None
    if coords and isinstance(coords, dict):
        lat, lng = coords.get('lat'), coords.get('lon')
    if not lat or not lng:
        return None
    fd = ev.get('firstdate_begin')
    if not fd:
        return None
    date = fd[:10]
    ld = ev.get('lastdate_end') or ev.get('lastdate_begin') or fd
    end_date = ld[:10] if ld else date

    src = ev.get('canonicalurl') or ''
    if not src:
        slug = ev.get('slug', '')
        uid = ev.get('uid', '')
        src = f"https://openagenda.com/events/{slug}" if slug else (f"https://openagenda.com/events/{uid}" if uid else '')
    if not src:
        return None
    if is_dup(src, title, date, su, td):
        return None

    if cc == 'FR' and not (41.0 <= lat <= 51.5 and -5.5 <= lng <= 10.0):
        return None
    if cc == 'CH' and not (45.7 <= lat <= 48.0 and 5.8 <= lng <= 10.6):
        return None

    kw = ' '.join(ev.get('keywords_fr', []) or [])
    dl = ev.get('longdescription_fr') or ev.get('description_fr') or ''
    ln = ev.get('location_name') or ''
    cats = assign_cats(title, dl, kw)

    la = ev.get('location_address') or ''
    lc = ev.get('location_city') or ''
    lp = ev.get('location_postalcode') or ''
    parts = list(filter(None, [ln if ln.lower() != lc.lower() else '', la, f"{lp} {lc}".strip()]))
    cn = {'CH': 'Suisse', 'FR': 'France'}.get(cc, '')
    if cn:
        parts.append(cn)
    location = ', '.join(parts) if parts else lc

    desc = strip_html(dl)
    if len(desc) > 400:
        desc = desc[:397] + '...'
    if not desc:
        desc = f"Evenement : {title}"

    return {
        'title': title, 'description': desc,
        'date': date, 'time': None, 'end_date': end_date, 'end_time': None,
        'location': location, 'latitude': float(lat), 'longitude': float(lng),
        'categories': cats, 'source_url': src,
        'type': 'event', 'validation_status': 'auto_validated',
        'organizer_name': ln,
    }


# ===============================================
# MAIN
# ===============================================

def main():
    print("=" * 60)
    print("ENRICHISSEMENT OPEN DATA - VILLES CIBLEES")
    print("=" * 60)

    su, td = fetch_existing()

    n1 = import_helsinki(su, td)
    n2 = import_nantes(su, td)
    n3 = import_oa_agendas(su, td)

    print("\n" + "=" * 60)
    print("RESUME FINAL")
    print("=" * 60)
    print(f"  Helsinki LinkedEvents : {n1} events")
    print(f"  Nantes Metropole      : {n2} events")
    print(f"  OA departements FR/CH : {n3} events")
    print(f"  ---")
    print(f"  TOTAL API crees       : {STATS['created']}")
    print(f"  TOTAL API skipped     : {STATS['skipped']}")
    print("=" * 60)

    with open('import_enrichment_log.json', 'w', encoding='utf-8') as f:
        json.dump({
            'helsinki': n1, 'nantes': n2, 'oa_depts': n3,
            'total_created': STATS['created'], 'total_skipped': STATS['skipped'],
        }, f, indent=2)


if __name__ == '__main__':
    main()
