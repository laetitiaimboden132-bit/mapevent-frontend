# -*- coding: utf-8 -*-
"""
Import Helsinki LinkedEvents - CC BY 4.0
Corrige le bug location (string vs objet) et pagine 17K events.
Usage : python scraper/import_helsinki_full.py
"""
import sys, json, requests, time, re, unicodedata, html as html_mod
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'
HEL_BASE = 'https://api.hel.fi/linkedevents/v1'
CREATED = 0
SKIPPED = 0


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
        'classical': 'Musique > Classique', 'klassinen': 'Musique > Classique',
        'opera': 'Musique > Classique', 'ooppera': 'Musique > Classique',
        'techno': 'Musique > Techno', 'electro': 'Musique > Electro',
        'hip hop': 'Musique > Hip-Hop', 'hiphop': 'Musique > Hip-Hop',
        'reggae': 'Musique > Reggae', 'pop ': 'Musique > Pop',
        'punk': 'Musique > Punk', 'folk': 'Musique > Folk',
        'indie': 'Musique > Indie', 'soul': 'Musique > Soul',
    }
    for kw, cat in mm.items():
        if kw in text and cat not in result:
            result.append(cat)
    if any(kw in text for kw in ['concert', 'konsertti', 'keikka', 'music', 'musiik']) and not any('Musique' in c for c in result):
        result.append('Musique > Concert')
    if 'festival' in text:
        result.append('Festival')
    if any(kw in text for kw in ['theatre', 'theater', 'teatteri', 'nayttelija', 'draama']):
        result.append('Culture > Theatre')
    if any(kw in text for kw in ['dance', 'tanssi', 'ballet', 'baletti']):
        result.append('Culture > Danse')
    if any(kw in text for kw in ['circus', 'sirkus']):
        result.append('Culture > Cirque')
    if any(kw in text for kw in ['cinema', 'film', 'elokuva', 'movie']):
        result.append('Culture > Cinema')
    if any(kw in text for kw in ['exhibition', 'nayttely', 'museum', 'museo', 'gallery', 'galleria', 'taide']):
        result.append('Culture > Exposition')
    if any(kw in text for kw in ['sport', 'urheilu', 'running', 'marathon', 'football', 'jalkapallo', 'hockey', 'jaakiekko', 'tennis']):
        result.append('Sport > Terrestre')
    if any(kw in text for kw in ['swimming', 'sailing', 'uinti', 'purjehdus']):
        result.append('Sport > Aquatique')
    if any(kw in text for kw in ['ski', 'hiihto', 'laskettelu', 'snowboard']):
        result.append('Sport > Glisse')
    if any(kw in text for kw in ['food', 'ruoka', 'gastro', 'tasting', 'ravintola']):
        result.append('Gastronomie')
    if any(kw in text for kw in ['market', 'markkinat', 'tori', 'kirppu']):
        result.append('Marche')
    if any(kw in text for kw in ['conference', 'seminaari', 'seminar', 'luento']):
        result.append('Conference')
    if any(kw in text for kw in ['workshop', 'tyopaja', 'atelier']):
        result.append('Atelier')
    if any(kw in text for kw in ['children', 'kids', 'lapsi', 'perhe', 'family', 'lapsille']):
        result.append('Famille')
    if any(kw in text for kw in ['show', 'esitys', 'stand-up', 'komedia', 'spectacle']):
        result.append('Culture > Spectacle')
    if any(kw in text for kw in ['kirja', 'book', 'reading', 'lukeminen', 'kirjallisuus']):
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
    su = set()
    td = set()
    for row in rows:
        src = (row[i_src] or '').strip().lower() if i_src >= 0 else ''
        if src:
            su.add(src)
        t = norm(row[i_title] or '')
        d = (row[i_date] or '')[:10] if i_date >= 0 else ''
        if t and d:
            td.add(f"{t}|{d}")
    print(f"  {len(rows)} events, {len(su)} source_urls")
    return su, td


def resolve_location(loc):
    """Resolve location - handle both embedded objects and URL references."""
    if isinstance(loc, str):
        try:
            r = requests.get(loc, timeout=10)
            if r.status_code == 200:
                return r.json()
        except:
            pass
        return None
    return loc


location_cache = {}

def get_location(loc_data):
    """Get location info, with caching for URL references."""
    if isinstance(loc_data, str):
        if loc_data in location_cache:
            return location_cache[loc_data]
        resolved = resolve_location(loc_data)
        location_cache[loc_data] = resolved
        return resolved
    elif isinstance(loc_data, dict):
        loc_id = loc_data.get('@id', '')
        if loc_id and not loc_data.get('position'):
            if loc_id in location_cache:
                return location_cache[loc_id]
            resolved = resolve_location(loc_id)
            if resolved:
                location_cache[loc_id] = resolved
                return resolved
        return loc_data
    return None


def parse_event(ev, su, td):
    nm = ev.get('name', {})
    if not isinstance(nm, dict):
        return None
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
    if not isinstance(info, dict):
        info = {}
    src = info.get('fi') or info.get('en') or ''
    if not src:
        src = f"https://tapahtumat.hel.fi/fi/events/{eid}" if eid else ''
    if not src:
        return None

    s = src.strip().lower()
    if s in su:
        return None
    t = norm(title)
    d = date[:10]
    if t and d and f"{t}|{d}" in td:
        return None

    loc_data = ev.get('location')
    loc = get_location(loc_data)
    if not loc or not isinstance(loc, dict):
        return None

    pos = loc.get('position') or {}
    coords = pos.get('coordinates', [])
    if not coords or len(coords) < 2:
        return None
    lng_v, lat_v = float(coords[0]), float(coords[1])
    if not (59.0 <= lat_v <= 61.5 and 23.0 <= lng_v <= 26.5):
        return None

    ln = loc.get('name', {})
    if not isinstance(ln, dict):
        ln = {}
    loc_name = (ln.get('fi') or ln.get('en') or '').strip()
    sa = loc.get('street_address', {})
    if not isinstance(sa, dict):
        sa = {}
    addr = (sa.get('fi') or sa.get('en') or '').strip()
    location = ', '.join(filter(None, [loc_name, addr, 'Helsinki', 'Finland']))

    sd = ev.get('short_description') or ev.get('description') or {}
    if not isinstance(sd, dict):
        sd = {}
    desc = strip_html(sd.get('fi') or sd.get('en') or '')
    if len(desc) > 400:
        desc = desc[:397] + '...'
    if not desc:
        desc = f"Event in Helsinki: {title}"

    kws = ev.get('keywords', [])
    tag_parts = []
    for k in (kws or []):
        if isinstance(k, dict):
            n = k.get('name', {})
            if isinstance(n, dict):
                tag_parts.append(n.get('fi', ''))
    cats = assign_cats(title, desc, ' '.join(tag_parts))

    return {
        'title': title, 'description': desc,
        'date': date, 'time': st, 'end_date': end_date, 'end_time': et,
        'location': location, 'latitude': lat_v, 'longitude': lng_v,
        'categories': cats, 'source_url': src,
        'type': 'event', 'validation_status': 'auto_validated',
        'organizer_name': loc_name,
    }


def send_batch(events):
    global CREATED, SKIPPED
    for i in range(0, len(events), 50):
        batch = events[i:i+50]
        try:
            r = requests.post(f'{API_URL}/api/events/scraped/batch',
                              json={'events': batch, 'send_emails': False}, timeout=60)
            res = r.json()
            c = res.get('results', {}).get('created', 0)
            s = res.get('results', {}).get('skipped', 0)
            CREATED += c
            SKIPPED += s
            print(f"  Batch {i//50+1}: {c} crees, {s} skip")
            time.sleep(1)
        except Exception as e:
            print(f"  ERR batch: {e}")


def main():
    print("=" * 60)
    print("HELSINKI LINKEDEVENTS - IMPORT COMPLET")
    print("Licence: CC BY 4.0")
    print("=" * 60)

    su, td = fetch_existing()

    events = []
    url = f'{HEL_BASE}/event/?start=today&end=2026-12-31&page_size=100&include=location&sort=start_time'
    pages = 0
    max_pages = 80
    errors = 0
    no_loc = 0

    while url and pages < max_pages:
        try:
            r = requests.get(url, timeout=30)
            if r.status_code != 200:
                print(f"  HTTP {r.status_code} page {pages}")
                break
            data = r.json()
            total = data.get('meta', {}).get('count', 0)
            if pages == 0:
                print(f"  Total API: {total} events")
            for ev in data.get('data', []):
                try:
                    parsed = parse_event(ev, su, td)
                    if parsed:
                        events.append(parsed)
                        su.add(parsed['source_url'].lower())
                        td.add(f"{norm(parsed['title'])}|{parsed['date'][:10]}")
                except Exception:
                    errors += 1
            url = data.get('meta', {}).get('next')
            pages += 1
            if pages % 10 == 0:
                print(f"  Page {pages}/{max_pages}: {len(events)} new, {errors} errors, cache={len(location_cache)}")
            time.sleep(0.3)
        except Exception as e:
            print(f"  ERR page {pages}: {e}")
            errors += 1
            if errors > 10:
                break
            time.sleep(2)
            continue

    print(f"\n  Pages: {pages}")
    print(f"  New events: {len(events)}")
    print(f"  Errors: {errors}")
    print(f"  Location cache: {len(location_cache)}")

    if events:
        print(f"\n  Sending {len(events)} events...")
        send_batch(events)

    print(f"\n{'='*60}")
    print(f"RESULTAT HELSINKI")
    print(f"  API created: {CREATED}")
    print(f"  API skipped: {SKIPPED}")
    print(f"{'='*60}")

    with open('import_helsinki_log.json', 'w', encoding='utf-8') as f:
        json.dump({'pages': pages, 'new': len(events), 'created': CREATED, 'skipped': SKIPPED, 'errors': errors}, f, indent=2)


if __name__ == '__main__':
    main()
