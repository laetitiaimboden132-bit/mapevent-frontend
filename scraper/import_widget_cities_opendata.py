# -*- coding: utf-8 -*-
"""
Import Open Data events for widget target cities with < 20 events.
Source: OpenAgenda via OpenDataSoft - Licence Ouverte v1.0 (CC-BY equivalent)
Deduplication: source_url + title+city+date + title similarity
"""
import sys, json, requests, time, re, unicodedata
from datetime import datetime, date

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'
ODS_URL = 'https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/evenements-publics-openagenda/records'
HEADERS = {"User-Agent": "MapEventAI-Bot/1.0 (open data consumer)"}
TODAY = date.today().strftime("%Y-%m-%d")

CITIES_FR = [
    ("Troyes", "FR"), ("Auxerre", "FR"), ("Chalon-sur-Saône", "FR"),
    ("Mâcon", "FR"), ("Colmar", "FR"), ("Lorient", "FR"), ("Vannes", "FR"),
    ("Biarritz", "FR"), ("Béziers", "FR"), ("Hyères", "FR"), ("Antibes", "FR"),
    ("Grasse", "FR"), ("Toulon", "FR"), ("Ajaccio", "FR"), ("Cherbourg", "FR"),
    ("Niort", "FR"), ("Nevers", "FR"), ("Senlis", "FR"), ("Bayonne", "FR"),
    ("Reims", "FR"), ("Cannes", "FR"),
]

CITIES_CH = [
    ("Lugano", "CH"), ("Lucerne", "CH"), ("Interlaken", "CH"), ("Soleure", "CH"),
    ("Zoug", "CH"), ("Davos", "CH"), ("Fribourg", "CH"), ("Montreux", "CH"),
    ("Bâle", "CH"), ("Bienne", "CH"), ("Vevey", "CH"), ("Monthey", "CH"),
    ("Yverdon-les-Bains", "CH"), ("Neuchâtel", "CH"), ("Aarau", "CH"),
    ("Winterthour", "CH"), ("Thoune", "CH"), ("Morges", "CH"), ("Nyon", "CH"),
    ("Bulle", "CH"), ("Martigny", "CH"), ("Zurich", "CH"), ("Saint-Gall", "CH"),
    ("Schaffhouse", "CH"),
]

# Alternate city names for OpenAgenda search (some cities indexed differently)
CITY_ALIASES = {
    "Chalon-sur-Saône": ["Chalon-sur-Saone", "Chalon sur Saône"],
    "Mâcon": ["Macon"],
    "Béziers": ["Beziers"],
    "Hyères": ["Hyeres"],
    "Cherbourg": ["Cherbourg-en-Cotentin", "Cherbourg-Octeville"],
    "Yverdon-les-Bains": ["Yverdon"],
    "Neuchâtel": ["Neuchatel"],
    "Bâle": ["Basel", "Bale", "Basle"],
    "Winterthour": ["Winterthur"],
    "Thoune": ["Thun"],
    "Zoug": ["Zug"],
    "Lucerne": ["Luzern"],
    "Saint-Gall": ["St. Gallen", "Sankt Gallen"],
    "Schaffhouse": ["Schaffhausen"],
    "Zurich": ["Zürich"],
    "Soleure": ["Solothurn"],
    "Fribourg": ["Freiburg"],
    "Bienne": ["Biel"],
}

# =========================================================================
# CATEGORY MAPPING
# =========================================================================
def assign_categories(title, description, keywords, location_name):
    text = f"{title} {description} {keywords or ''} {location_name or ''}".lower()
    cats = []

    # Musique (specifique d'abord)
    music_kw = {
        'jazz': 'Musique > Jazz', 'blues': 'Musique > Blues',
        'rock': 'Musique > Rock', 'metal': 'Musique > Metal',
        'punk': 'Musique > Punk', 'reggae': 'Musique > Reggae',
        'techno': 'Musique > Techno', 'electro': 'Musique > Electro',
        'house': 'Musique > House', 'trance': 'Musique > Trance',
        'hip hop': 'Musique > Hip-Hop', 'hip-hop': 'Musique > Hip-Hop',
        'rap ': 'Musique > Hip-Hop',
        'classique': 'Musique > Classique', 'orchestre': 'Musique > Classique',
        'opéra': 'Musique > Classique', 'symphoni': 'Musique > Classique',
        'chorale': 'Musique > Classique',
        'salsa': 'Musique > Latin', 'bachata': 'Musique > Latin',
        'folk': 'Musique > Folk', 'chanson': 'Musique > Chanson française',
    }
    for kw, cat in music_kw.items():
        if kw in text and cat not in cats:
            cats.append(cat)
    if any(w in text for w in ['concert', 'musique', 'musical', 'récital']) and not any('Musique' in c for c in cats):
        cats.append('Musique > Concert')

    # Theatre / Spectacle
    if any(w in text for w in ['théâtre', 'theatre', 'comédie', 'tragédie']):
        cats.append('Spectacle > Théâtre')
    if any(w in text for w in ['danse', 'ballet', 'chorégraph']):
        cats.append('Danse')
    if any(w in text for w in ['cirque', 'acrobat', 'clown']):
        cats.append('Spectacle > Cirque')
    if any(w in text for w in ['humour', 'stand-up', 'one man show', 'humoriste']):
        cats.append('Spectacle > Humour')

    # Culture
    if any(w in text for w in ['exposition', 'expo ', 'vernissage', 'galerie']):
        cats.append('Culture > Exposition')
    if any(w in text for w in ['musée', 'museum', 'patrimoine']):
        cats.append('Culture > Musée')
    if any(w in text for w in ['cinéma', 'cinema', 'film', 'projection']):
        cats.append('Culture > Cinéma')
    if any(w in text for w in ['lecture', 'littéra', 'livre', 'poésie']):
        cats.append('Culture > Littérature')
    if any(w in text for w in ['photo', 'photographi']):
        cats.append('Culture > Photographie')

    # Sport
    sport_map = {
        'randonnée': 'Sport > Randonnée', 'marche': 'Sport > Randonnée',
        'trail': 'Sport > Course à pied', 'marathon': 'Sport > Course à pied',
        'course à pied': 'Sport > Course à pied', 'running': 'Sport > Course à pied',
        'football': 'Sport > Football', 'tennis': 'Sport > Tennis',
        'rugby': 'Sport > Rugby', 'basket': 'Sport > Basketball',
        'vélo': 'Sport > Cyclisme', 'cyclisme': 'Sport > Cyclisme',
        'natation': 'Sport > Natation', 'yoga': 'Sport > Yoga & Bien-être',
        'ski': 'Sport > Glisse', 'snowboard': 'Sport > Glisse',
        'patinage': 'Sport > Glisse', 'hockey': 'Sport > Glisse',
        'escalade': 'Sport > Escalade',
    }
    for kw, cat in sport_map.items():
        if kw in text and cat not in cats:
            cats.append(cat)
    if any(w in text for w in ['sportif', 'compétition', 'tournoi']) and not any('Sport' in c for c in cats):
        cats.append('Sport')

    # Gastro / Marché
    if any(w in text for w in ['dégustation', 'vin ', 'oenolog', 'gastronomie', 'culinaire']):
        cats.append('Gastronomie > Dégustation')
    if any(w in text for w in ['marché', 'brocante', 'vide-grenier', 'puces']):
        cats.append('Marché & Brocante')
    if any(w in text for w in ['foire', 'salon ']):
        cats.append('Foire')

    # Festival / Fête
    if 'festival' in text:
        cats.append('Festival')
    if 'carnaval' in text:
        cats.append('Carnaval')
    if any(w in text for w in ['fête', 'fete', 'feu d\'artifice']):
        cats.append('Fête')

    # Conférence / Atelier
    if any(w in text for w in ['conférence', 'séminaire', 'colloque', 'débat']):
        cats.append('Conférence')
    if any(w in text for w in ['atelier', 'workshop', 'stage ']):
        cats.append('Atelier')

    # Famille
    if any(w in text for w in ['enfant', 'famille', 'jeune public', 'tout public']):
        cats.append('Famille & Enfants')

    if not cats:
        cats.append('Événement')

    seen = set()
    unique = []
    for c in cats:
        if c not in seen:
            seen.add(c)
            unique.append(c)
    return unique[:3]


# =========================================================================
# HELPERS
# =========================================================================
def norm(s):
    s = s.lower().strip()
    s = unicodedata.normalize('NFD', s)
    return ''.join(c for c in s if unicodedata.category(c) != 'Mn')

def clean_html(text, max_len=400):
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', ' ', str(text))
    text = re.sub(r'&[a-z]+;', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) > max_len:
        text = text[:max_len].rsplit(' ', 1)[0] + "..."
    return text


def fetch_existing_events():
    """Fetch existing events for dedup."""
    print("Fetching existing events...")
    r = requests.get(f'{API_URL}/api/events?limit=80000', timeout=120)
    data = r.json()
    keys = data.get('k', [])
    rows = data.get('d', [])
    i_title = keys.index('title') if 'title' in keys else -1
    i_loc = keys.index('location') if 'location' in keys else -1
    i_date = keys.index('date') if 'date' in keys else -1
    i_source = keys.index('source_url') if 'source_url' in keys else -1

    existing = []
    source_urls = set()
    for row in rows:
        title = str(row[i_title] or '') if i_title >= 0 else ''
        loc = str(row[i_loc] or '') if i_loc >= 0 else ''
        dt = str(row[i_date] or '') if i_date >= 0 else ''
        src = str(row[i_source] or '') if i_source >= 0 else ''
        existing.append({'title': title, 'location': loc, 'date': dt, 'source_url': src})
        if src:
            source_urls.add(src.strip())
    print(f"  {len(existing)} events existants charges ({len(source_urls)} source_urls)")
    return existing, source_urls


def is_duplicate(title, source_url, event_date, existing, source_urls, seen_local):
    if source_url and source_url.strip() in source_urls:
        return True

    title_norm = norm(title)[:60]
    local_key = f"{title_norm}|{event_date}"
    if local_key in seen_local:
        return True

    title_words = set(re.findall(r'\w{4,}', title_norm))
    if len(title_words) >= 3:
        for e in existing:
            e_words = set(re.findall(r'\w{4,}', norm(e['title'])[:60]))
            common = title_words & e_words
            if len(common) >= 3 and len(common) / max(len(title_words), len(e_words)) > 0.6:
                if e['date'][:10] == event_date[:10] if event_date and e['date'] else True:
                    return True

    return False


def fetch_openagenda_city(city_name, country_code, limit=60):
    """Fetch events for a city from OpenAgenda/OpenDataSoft."""
    names_to_try = [city_name] + CITY_ALIASES.get(city_name, [])
    all_results = []

    for name in names_to_try:
        if country_code == "CH":
            where = f'location_countrycode="CH" AND location_city="{name}" AND firstdate_begin>="{TODAY}"'
        else:
            where = f'location_countrycode="FR" AND location_city="{name}" AND firstdate_begin>="{TODAY}"'

        params = {
            'where': where,
            'limit': limit,
            'offset': 0,
            'order_by': 'firstdate_begin',
        }

        try:
            r = requests.get(ODS_URL, params=params, headers=HEADERS, timeout=30)
            if r.status_code != 200:
                continue
            data = r.json()
            results = data.get('results', [])
            total = data.get('total_count', 0)
            if results:
                all_results.extend(results)
                print(f"    {name}: {len(results)} events (total dispo: {total})")
                if total > limit:
                    # Fetch remaining pages
                    for off in range(limit, min(total, limit * 3), limit):
                        params['offset'] = off
                        r2 = requests.get(ODS_URL, params=params, headers=HEADERS, timeout=30)
                        if r2.status_code == 200:
                            more = r2.json().get('results', [])
                            all_results.extend(more)
                        time.sleep(0.5)
        except Exception as e:
            print(f"    {name}: erreur {e}")
        time.sleep(0.5)

    return all_results


def parse_event(record, city_name, country_code):
    """Parse an OpenAgenda record into a MapEvent event dict."""
    title = record.get('title_fr') or record.get('title') or ''
    title = title.strip()
    if not title:
        return None

    desc_raw = record.get('longdescription_fr') or record.get('description_fr') or record.get('description') or ''
    description = clean_html(desc_raw)

    coords = record.get('location_coordinates')
    lat, lon = None, None
    if isinstance(coords, dict):
        lat, lon = coords.get('lat'), coords.get('lon')
    elif isinstance(coords, list) and len(coords) >= 2:
        lat, lon = coords[0], coords[1]
    if lat is None or lon is None:
        return None
    try:
        lat, lon = float(lat), float(lon)
    except (ValueError, TypeError):
        return None

    if country_code == "FR" and not (41.0 <= lat <= 51.5 and -5.5 <= lon <= 10.0):
        return None
    if country_code == "CH" and not (45.7 <= lat <= 47.9 and 5.8 <= lon <= 10.6):
        return None

    # Dates
    first_begin = record.get('firstdate_begin') or ''
    last_end = record.get('lastdate_end') or record.get('lastdate_begin') or first_begin
    if not first_begin:
        return None

    event_date = first_begin[:10]
    end_date = last_end[:10] if last_end else None
    event_time = None
    end_time = None

    if len(first_begin) >= 16 and 'T' in first_begin:
        h = first_begin[11:16]
        if h != '00:00':
            event_time = h
    if last_end and len(last_end) >= 16 and 'T' in last_end:
        h = last_end[11:16]
        if h != '00:00':
            end_time = h

    if end_date == event_date:
        end_date = None

    # Skip past events
    try:
        check = end_date or event_date
        if datetime.strptime(check, "%Y-%m-%d").date() < date.today():
            return None
    except:
        pass

    # Source URL
    source_url = record.get('canonicalurl') or record.get('originagenda_url') or ''
    if not source_url:
        uid = record.get('uid')
        slug = record.get('slug')
        if slug:
            source_url = f"https://openagenda.com/events/{slug}"
        elif uid:
            source_url = f"https://openagenda.com/events/{uid}"
    if not source_url:
        return None

    # Location
    loc_name = record.get('location_name') or ''
    loc_addr = record.get('location_address') or ''
    loc_city = record.get('location_city') or city_name
    loc_pc = record.get('location_postalcode') or ''

    parts = []
    if loc_name:
        parts.append(loc_name.strip())
    if loc_addr and loc_addr.strip() not in (loc_name or ''):
        parts.append(loc_addr.strip())
    if loc_pc and loc_city:
        parts.append(f"{loc_pc} {loc_city}")
    elif loc_city:
        parts.append(loc_city)
    parts.append("Suisse" if country_code == "CH" else "France")
    location = ', '.join(parts)

    # Keywords
    kw_raw = record.get('keywords_fr')
    keywords = ''
    if isinstance(kw_raw, str):
        keywords = kw_raw
    elif isinstance(kw_raw, list):
        keywords = ' '.join(kw_raw)

    categories = assign_categories(title, description, keywords, loc_name)

    return {
        'title': title[:200],
        'description': description,
        'date': event_date,
        'end_date': end_date,
        'time': event_time,
        'end_time': end_time,
        'location': location[:300],
        'latitude': round(lat, 6),
        'longitude': round(lon, 6),
        'categories': categories,
        'source_url': source_url,
        'source': f"OpenAgenda - {loc_city}",
        'validation_status': 'auto_validated',
    }


def send_batch(events):
    if not events:
        return 0
    try:
        r = requests.post(
            f'{API_URL}/api/events/scraped/batch',
            json={'events': events},
            headers=HEADERS,
            timeout=60,
        )
        if r.status_code in (200, 201):
            result = r.json()
            inserted = result.get('inserted', result.get('created', result.get('count', len(events))))
            return inserted
        else:
            print(f"    Batch erreur HTTP {r.status_code}: {r.text[:200]}")
            return 0
    except Exception as e:
        print(f"    Batch erreur: {e}")
        return 0


def main():
    print("=" * 70)
    print("IMPORT OPEN DATA - VILLES WIDGET (< 20 events)")
    print("Source: OpenAgenda / OpenDataSoft - Licence Ouverte v1.0")
    print("=" * 70)

    existing, source_urls = fetch_existing_events()
    seen_local = set()

    all_cities = CITIES_FR + CITIES_CH
    total_imported = 0
    city_stats = {}

    for city_name, country_code in all_cities:
        print(f"\n{'─'*50}")
        print(f"  {city_name} ({country_code})")
        print(f"{'─'*50}")

        records = fetch_openagenda_city(city_name, country_code)
        if not records:
            print(f"    Aucun event trouve")
            city_stats[city_name] = 0
            continue

        events_for_city = []
        skipped_dup = 0
        skipped_parse = 0

        for rec in records:
            event = parse_event(rec, city_name, country_code)
            if not event:
                skipped_parse += 1
                continue

            if is_duplicate(event['title'], event['source_url'], event['date'], existing, source_urls, seen_local):
                skipped_dup += 1
                continue

            local_key = f"{norm(event['title'])[:60]}|{event['date']}"
            seen_local.add(local_key)
            if event['source_url']:
                source_urls.add(event['source_url'].strip())

            events_for_city.append(event)

        print(f"    Records: {len(records)} | Parse OK: {len(records)-skipped_parse} | Doublons: {skipped_dup} | A importer: {len(events_for_city)}")

        if events_for_city:
            for ev in events_for_city[:3]:
                print(f"      -> {ev['title'][:50]} | {ev['date']} | {ev['categories']}")

            inserted = 0
            for i in range(0, len(events_for_city), 15):
                batch = events_for_city[i:i+15]
                n = send_batch(batch)
                inserted += n
                time.sleep(1)

            print(f"    INSERE: {inserted}")
            total_imported += inserted
            city_stats[city_name] = inserted
        else:
            city_stats[city_name] = 0

        time.sleep(1)

    print(f"\n{'='*70}")
    print(f"RESULTAT FINAL: {total_imported} events importes")
    print(f"{'='*70}")

    print(f"\nDetail par ville:")
    for city, count in sorted(city_stats.items(), key=lambda x: -x[1]):
        marker = "OK" if count > 0 else "---"
        print(f"  {city:<30} {count:>5}  {marker}")

    with open('import_widget_cities_result.json', 'w', encoding='utf-8') as f:
        json.dump({
            'total_imported': total_imported,
            'by_city': city_stats,
            'timestamp': datetime.now().isoformat(),
        }, f, indent=2, ensure_ascii=False)


if __name__ == '__main__':
    main()
