# -*- coding: utf-8 -*-
"""
Import d'events Open Data depuis OpenAgenda pour la Belgique.
Source : OpenDataSoft / OpenAgenda - Licence CC-BY (zone verte)
"""
import sys, json, requests, time, re
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'
OPENDATA_URL = 'https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/evenements-publics-openagenda/records'

print('=' * 60)
print('  IMPORT OPEN DATA - BELGIQUE (OpenAgenda CC-BY)')
print('=' * 60)

# Fetch existing events
print('\n  Recuperation events existants...')
r = requests.get(f'{API_URL}/api/events', timeout=30)
data = r.json()
existing = data if isinstance(data, list) else data.get('events', [])
print(f'  Events existants: {len(existing)}')

# Fetch Belgian events from OpenAgenda
print('\n  Recuperation events belges...')
where = "location_countrycode='BE' AND firstdate_begin>='2026-02-01' AND firstdate_begin<'2027-01-01'"
params = {'where': where, 'limit': 100, 'offset': 0, 'order_by': 'firstdate_begin'}
r = requests.get(OPENDATA_URL, params=params, timeout=30)
data = r.json()
raw_events = data.get('results', [])
total = data.get('total_count', 0)
print(f'  Total: {total} events belges')

music_map = {
    'jazz': 'Musique > Jazz', 'blues': 'Musique > Blues',
    'rock': 'Musique > Rock', 'classique': 'Musique > Classique',
    'electro': 'Musique > Electro', 'chorale': 'Musique > Classique',
    'orchestre': 'Musique > Classique',
}

def assign_cats(title, desc, kw):
    text = f'{title} {desc} {kw}'.lower()
    cats = []
    for k, v in music_map.items():
        if k in text and v not in cats:
            cats.append(v)
    if ('concert' in text or 'musique' in text) and not any('Musique' in c for c in cats):
        cats.append('Musique > Concert')
    if 'festival' in text:
        cats.append('Festival')
    if any(k in text for k in ['theatre', 'comedie', 'tragedie']):
        cats.append('Culture > Theatre')
    if any(k in text for k in ['danse', 'ballet', 'choregraph']):
        cats.append('Culture > Danse')
    if any(k in text for k in ['exposition', 'expo ', 'musee', 'galerie', 'vernissage']):
        cats.append('Culture > Exposition')
    if any(k in text for k in ['cinema', 'film', 'projection']):
        cats.append('Culture > Cinema')
    if any(k in text for k in ['conference', 'seminaire']):
        cats.append('Conference')
    if any(k in text for k in ['atelier', 'workshop']):
        cats.append('Atelier')
    if any(k in text for k in ['marche', 'brocante']):
        cats.append('Marche')
    if any(k in text for k in ['spectacle']) and not any('Culture' in c for c in cats):
        cats.append('Culture > Spectacle')
    if not cats:
        cats.append('Culture')
    return list(dict.fromkeys(cats))

def clean(t):
    if not t:
        return ''
    t = re.sub(r'<[^>]+>', ' ', t)
    return re.sub(r'\s+', ' ', t).strip()

def is_dup(title, src, existing):
    tl = title.lower().strip()
    tw = set(re.findall(r'\w+', tl))
    for ev in existing:
        if src and ev.get('source_url') == src:
            return True
        et = (ev.get('title', '') or '').lower().strip()
        if et == tl:
            return True
        ew = set(re.findall(r'\w+', et))
        if len(tw) >= 4 and len(ew) >= 4:
            common = tw & ew
            if len(common) / max(len(tw), len(ew)) > 0.75:
                return True
    return False

events_to_import = []
stats = {'total': 0, 'no_coords': 0, 'dup': 0, 'ok': 0}

for ev in raw_events:
    stats['total'] += 1
    title = (ev.get('title_fr') or '').strip()
    if not title:
        continue

    coords = ev.get('location_coordinates')
    lat = lng = None
    if coords and isinstance(coords, dict):
        lat = coords.get('lat')
        lng = coords.get('lon')
    if not lat or not lng:
        stats['no_coords'] += 1
        continue

    fd = ev.get('firstdate_begin', '')
    ld = ev.get('lastdate_end') or ev.get('lastdate_begin') or fd
    sd = fd[:10] if fd else None
    ed = ld[:10] if ld else sd
    if not sd:
        stats['no_coords'] += 1
        continue

    slug = ev.get('slug', '')
    src = ev.get('canonicalurl') or (f'https://openagenda.com/events/{slug}' if slug else '')

    if is_dup(title, src, existing):
        stats['dup'] += 1
        continue

    existing.append({'title': title, 'source_url': src})

    kw = ' '.join(ev.get('keywords_fr', []) or [])
    desc = clean(ev.get('longdescription_fr') or ev.get('description_fr') or '')
    if len(desc) > 400:
        desc = desc[:397] + '...'
    if not desc:
        desc = f'Evenement en Belgique : {title}'

    cats = assign_cats(title, desc, kw)

    parts = []
    ln = (ev.get('location_name') or '').strip()
    la = (ev.get('location_address') or '').strip()
    lc = (ev.get('location_city') or '').strip()
    lp = (ev.get('location_postalcode') or '').strip()

    if ln:
        parts.append(ln)
    if la and ln.lower() not in la.lower():
        parts.append(la)
    if lp and lc:
        parts.append(f'{lp} {lc}')
    elif lc:
        parts.append(lc)
    parts.append('Belgique')

    events_to_import.append({
        'title': title,
        'description': desc,
        'date': sd,
        'time': None,
        'end_date': ed,
        'end_time': None,
        'location': ', '.join(parts),
        'latitude': float(lat),
        'longitude': float(lng),
        'categories': cats,
        'source_url': src,
        'type': 'event',
        'validation_status': 'scraped',
        'organizer_name': ln or '',
    })
    stats['ok'] += 1

print(f'\n  Stats:')
print(f'  Total brut: {stats["total"]}')
print(f'  Sans coords: {stats["no_coords"]}')
print(f'  Doublons: {stats["dup"]}')
print(f'  A importer: {stats["ok"]}')

if events_to_import:
    print(f'\n  Apercu:')
    for ev in events_to_import[:15]:
        print(f'    {ev["title"][:50]:50s} | {ev["location"][:40]}')
        print(f'      Categories: {ev["categories"]}')

    print(f'\n  Import de {len(events_to_import)} events...')
    total_created = 0
    for i in range(0, len(events_to_import), 20):
        batch = events_to_import[i:i + 20]
        r = requests.post(f'{API_URL}/api/events/scraped/batch', json={'events': batch}, timeout=30)
        res = r.json()
        created = res.get('created', len(batch))
        total_created += created
        print(f'  Batch {i // 20 + 1}: {created} crees')
        time.sleep(2)

    print(f'\n  TOTAL IMPORTE: {total_created} events Belgique')
    print(f'  Source: OpenAgenda (CC-BY)')
else:
    print('\n  Aucun event a importer')
