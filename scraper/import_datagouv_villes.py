# -*- coding: utf-8 -*-
"""
Import d'events Open Data depuis data.gouv.fr - Grandes villes françaises
Sources :
  - Paris "Que faire à Paris" (ODbL) - opendata.paris.fr
  - Nantes Métropole agenda (Licence Ouverte v2.0) - data.nantesmetropole.fr
  - Bordeaux Métropole agenda (CC-BY / OpenAgenda) - opendata.bordeaux-metropole.fr

RÈGLE #1 : Ne prendre QUE des données à licence claire
  ✅ ODbL (Paris) - Usage commercial OK, attribution requise
  ✅ Licence Ouverte v2.0 (Nantes) - 100% safe
  ✅ CC-BY (Bordeaux via OpenAgenda) - Usage commercial OK
"""

import sys
import json
import requests
import time
import re

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'

# ============================================================
# SOURCES DE DONNÉES
# ============================================================

SOURCES = {
    'paris': {
        'name': 'Paris - Que faire à Paris',
        'license': 'ODbL (Open Database License)',
        'url': 'https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/que-faire-a-paris-/records',
        'format': 'paris',
    },
    'nantes': {
        'name': 'Nantes Métropole - Agenda',
        'license': 'Licence Ouverte v2.0 (Etalab)',
        'url': 'https://data.nantesmetropole.fr/api/explore/v2.1/catalog/datasets/244400404_agenda-evenements-nantes-metropole_v2/records',
        'format': 'nantes',
    },
    'bordeaux': {
        'name': 'Bordeaux Métropole - Agenda',
        'license': 'CC-BY (OpenAgenda)',
        'url': 'https://opendata.bordeaux-metropole.fr/api/explore/v2.1/catalog/datasets/met_agenda/records',
        'format': 'openagenda',
    },
}


# ============================================================
# CATÉGORIES INTELLIGENTES
# ============================================================

def assign_categories(title, description, tags='', location_name=''):
    """Assigne des catégories spécifiques en analysant titre + description + tags."""
    text = f"{title} {description} {tags} {location_name}".lower()
    result = []

    # === MUSIQUE ===
    music_specific = {
        'jazz': 'Musique > Jazz', 'blues': 'Musique > Blues',
        'rock': 'Musique > Rock', 'metal': 'Musique > Metal',
        'punk': 'Musique > Punk', 'pop ': 'Musique > Pop',
        'rap ': 'Musique > Rap', 'hip hop': 'Musique > Hip-Hop',
        'hip-hop': 'Musique > Hip-Hop', 'techno': 'Musique > Techno',
        'electro': 'Musique > Electro', 'house ': 'Musique > House',
        'trance': 'Musique > Trance', 'reggae': 'Musique > Reggae',
        'classique': 'Musique > Classique', 'opéra': 'Musique > Opéra',
        'opera': 'Musique > Opéra', 'chorale': 'Musique > Classique',
        'orchestre': 'Musique > Classique', 'symphoni': 'Musique > Classique',
        'salsa': 'Musique > Latin', 'bachata': 'Musique > Latin',
        'chanson': 'Musique > Chanson', 'folk': 'Musique > Folk',
        'country': 'Musique > Country', 'soul': 'Musique > Soul',
        'funk': 'Musique > Funk', 'r&b': 'Musique > R&B',
        'gospel': 'Musique > Gospel', 'world music': 'Musique > World',
        'musiques du monde': 'Musique > World',
        'musique bretonne': 'Musique > Folk', 'celtique': 'Musique > Folk',
    }
    for kw, cat in music_specific.items():
        if kw in text and cat not in result:
            result.append(cat)

    if ('concert' in text or 'musique' in text or 'music' in text or 'spectacle musical' in text) and not any('Musique >' in c for c in result):
        result.append('Musique > Concert')

    # === FESTIVAL ===
    if 'festival' in text and 'Festival' not in result:
        result.append('Festival')

    # === THÉÂTRE / SPECTACLE ===
    if any(kw in text for kw in ['théâtre', 'theatre', 'pièce de', 'comédie', 'tragédie']):
        result.append('Culture > Théâtre')
    if any(kw in text for kw in ['danse', 'ballet', 'chorégraph']):
        result.append('Culture > Danse')
    if any(kw in text for kw in ['cirque', 'acrobat', 'clown', 'jongl']):
        result.append('Culture > Cirque')
    if any(kw in text for kw in ['marionnette', 'puppet']):
        result.append('Culture > Marionnettes')
    if any(kw in text for kw in ['humour', 'humoriste', 'one man show', 'one-man-show', 'stand-up', 'stand up', 'sketch']):
        result.append('Culture > Humour')
    if any(kw in text for kw in ['spectacle', 'cabaret', 'revue']) and not any('Culture >' in c for c in result):
        if not any('Musique >' in c for c in result):
            result.append('Culture > Spectacle')

    # === CINÉMA ===
    if any(kw in text for kw in ['cinéma', 'cinema', 'film', 'projection', 'ciné-', 'ciné ']):
        result.append('Culture > Cinéma')

    # === EXPOSITION ===
    expo_kw = ['exposition', 'expo ', "l'expo", 'musée', 'galerie', 'vernissage', 'œuvres', 'oeuvres', 'art contemporain']
    if any(kw in text for kw in expo_kw):
        result.append('Culture > Exposition')

    # === PHOTOGRAPHIE ===
    if any(kw in text for kw in ['photo', 'photographi']):
        result.append('Culture > Photographie')

    # === SPORTS ===
    sport_map = {
        'ski': 'Sport > Glisse', 'snowboard': 'Sport > Glisse',
        'patinage': 'Sport > Glisse', 'luge': 'Sport > Glisse',
        'hockey': 'Sport > Terrestre', 'football': 'Sport > Terrestre',
        'tennis': 'Sport > Terrestre', 'basket': 'Sport > Terrestre',
        'rugby': 'Sport > Terrestre', 'volley': 'Sport > Terrestre',
        'golf': 'Sport > Terrestre', 'randonnée': 'Sport > Terrestre',
        'trail': 'Sport > Terrestre', 'course à pied': 'Sport > Terrestre',
        'marathon': 'Sport > Terrestre', 'triathlon': 'Sport > Terrestre',
        'cyclisme': 'Sport > Terrestre', 'vélo': 'Sport > Terrestre',
        'vtt': 'Sport > Terrestre', 'escalade': 'Sport > Terrestre',
        'yoga': 'Sport > Terrestre', 'gym': 'Sport > Terrestre',
        'boxe': 'Sport > Terrestre', 'judo': 'Sport > Terrestre',
        'karaté': 'Sport > Terrestre', 'escrime': 'Sport > Terrestre',
        'athlétisme': 'Sport > Terrestre',
        'natation': 'Sport > Aquatique', 'piscine': 'Sport > Aquatique',
        'kayak': 'Sport > Aquatique', 'voile': 'Sport > Aquatique',
        'aviron': 'Sport > Aquatique', 'nautique': 'Sport > Aquatique',
        'parapente': 'Sport > Aérien', 'parachute': 'Sport > Aérien',
    }
    for kw, cat in sport_map.items():
        if kw in text and cat not in result:
            result.append(cat)

    if any(kw in text for kw in ['sportif', 'compétition', 'tournoi', 'multisports']) and not any('Sport' in c for c in result):
        result.append('Sport > Terrestre')

    # === GASTRONOMIE ===
    if any(kw in text for kw in ['dégustation', 'vignoble', 'vigneron', 'cave', 'oenolog', 'vin ', 'viticole']):
        result.append('Gastronomie > Dégustation vin')
    elif any(kw in text for kw in ['bière', 'brasserie', 'beer']):
        result.append('Gastronomie > Dégustation bière')
    elif any(kw in text for kw in ['brunch', 'gastronomie', 'culinaire', 'cuisine', 'food', 'gourmand']):
        result.append('Gastronomie')

    # === MARCHÉS ===
    if any(kw in text for kw in ['marché', 'brocante', 'vide-grenier', 'puces', 'grenier']):
        cat = 'Marché > Brocante' if any(kw in text for kw in ['brocante', 'vide-grenier', 'puces', 'grenier']) else 'Marché'
        result.append(cat)
    if any(kw in text for kw in ['foire', 'salon ']):
        result.append('Foire')

    # === CARNAVAL / FÊTE ===
    if 'carnaval' in text:
        result.append('Carnaval')
    if any(kw in text for kw in ['parade', 'cortège', 'défilé']):
        result.append('Parade')

    # === CONFÉRENCE / ATELIER ===
    if any(kw in text for kw in ['conférence', 'séminaire', 'colloque', 'débat']):
        result.append('Conférence')
    if any(kw in text for kw in ['atelier', 'workshop', 'stage ']):
        result.append('Atelier')

    # === CONTE / LECTURE ===
    if any(kw in text for kw in ['conte ', 'contes ', 'conteur']):
        result.append('Culture > Conte')
    if any(kw in text for kw in ['lecture', 'littéra', 'poésie', 'slam']):
        result.append('Culture > Littérature')

    # === VISITE / PATRIMOINE ===
    if any(kw in text for kw in ['visite guidée', 'visite commentée', 'patrimoine', 'balade']):
        result.append('Culture > Visite')

    # === ENFANTS ===
    if any(kw in text for kw in ['enfant', 'jeune public', 'familial', 'famille', 'kids']):
        if not result or all('Culture' not in c and 'Musique' not in c for c in result):
            result.append('Famille')

    # Fallback
    if not result:
        result.append('Culture')

    # Dédupliquer
    return list(dict.fromkeys(result))


# ============================================================
# HELPERS
# ============================================================

def clean_html(text):
    """Nettoie le HTML d'un texte."""
    if not text:
        return ''
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'&nbsp;', ' ', text)
    text = re.sub(r'&amp;', '&', text)
    text = re.sub(r'&lt;', '<', text)
    text = re.sub(r'&gt;', '>', text)
    text = re.sub(r'&[a-z]+;', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def truncate_desc(desc, max_len=400):
    """Tronque une description à max_len caractères."""
    if not desc:
        return ''
    desc = clean_html(desc)
    if len(desc) > max_len:
        desc = desc[:max_len - 3] + '...'
    return desc


def parse_time(time_str):
    """Parse un horaire en format HH:MM ou retourne None."""
    if not time_str:
        return None
    time_str = str(time_str).strip()
    if time_str in ['--:--', '', 'None', 'null']:
        return None
    # Essayer d'extraire HH:MM
    match = re.match(r'(\d{1,2}):(\d{2})', time_str)
    if match:
        h, m = int(match.group(1)), int(match.group(2))
        if 0 <= h <= 23 and 0 <= m <= 59:
            return f"{h:02d}:{m:02d}"
    return None


def fetch_existing_events():
    """Récupère les events existants pour éviter les doublons."""
    try:
        r = requests.get(f'{API_URL}/api/events', timeout=30)
        data = r.json()
        events = data if isinstance(data, list) else data.get('events', [])
        return events
    except Exception as e:
        print(f"   Erreur: {e}")
        return []


def is_duplicate(new_title, new_source, existing_events):
    """Vérifie si un event existe déjà."""
    new_title_lower = new_title.lower().strip()
    new_title_words = set(re.findall(r'\w+', new_title_lower))

    for ev in existing_events:
        # Vérifier par source_url
        if new_source and ev.get('source_url') == new_source:
            return True

        # Vérifier par titre exact
        ex_title = (ev.get('title', '') or '').lower().strip()
        if ex_title == new_title_lower:
            return True

        # Similarité par mots communs (seulement si titres assez longs)
        ex_words = set(re.findall(r'\w+', ex_title))
        if len(new_title_words) >= 4 and len(ex_words) >= 4:
            common = new_title_words & ex_words
            similarity = len(common) / max(len(new_title_words), len(ex_words))
            if similarity > 0.75:
                return True

    return False


# ============================================================
# PARIS - "Que faire à Paris"
# ============================================================

def fetch_paris_events():
    """Récupère les events de Paris (Que faire à Paris)."""
    print("\n   [PARIS] Récupération des events...")
    all_events = []
    url = SOURCES['paris']['url']

    # Filtrer: events avec date_start en 2026
    where = "date_start >= '2026-02-01' AND date_start < '2027-01-01'"

    offset = 0
    limit = 100

    while True:
        params = {
            'where': where,
            'limit': limit,
            'offset': offset,
            'order_by': 'date_start',
        }

        try:
            r = requests.get(url, params=params, timeout=30)
            data = r.json()
            records = data.get('results', [])
            total = data.get('total_count', 0)

            if not records:
                break

            all_events.extend(records)
            print(f"   [PARIS] {len(all_events)}/{total} events...")

            offset += limit
            if offset >= total:
                break

            time.sleep(0.5)

        except Exception as e:
            print(f"   [PARIS] Erreur: {e}")
            break

    return all_events


def parse_paris_event(ev):
    """Transforme un event Paris en format MapEventAI."""
    title = (ev.get('title') or '').strip()
    if not title:
        return None

    # Coordonnées
    lat_lon = ev.get('lat_lon')
    if not lat_lon or not isinstance(lat_lon, dict):
        return None
    lat = lat_lon.get('lat')
    lng = lat_lon.get('lon')
    if not lat or not lng:
        return None

    # Dates
    date_start = ev.get('date_start', '')
    date_end = ev.get('date_end', '')
    start_date = date_start[:10] if date_start else None
    end_date = date_end[:10] if date_end else start_date

    if not start_date:
        return None

    # Horaires
    start_time = None
    end_time = None
    if date_start and 'T' in date_start:
        t = date_start.split('T')[1][:5]
        if t != '00:00':
            start_time = t
    if date_end and 'T' in date_end:
        t = date_end.split('T')[1][:5]
        if t != '00:00':
            end_time = t

    # Source URL
    source_url = ev.get('url', '')

    # Description
    lead = clean_html(ev.get('lead_text', ''))
    desc = clean_html(ev.get('description', ''))
    description = lead if lead else truncate_desc(desc)
    if not description:
        description = f"Événement à Paris : {title}"

    # Tags et catégories
    tags = ev.get('qfap_tags', '') or ''
    address_name = ev.get('address_name', '') or ''
    categories = assign_categories(title, description, tags, address_name)

    # Adresse
    parts = []
    addr_name = (ev.get('address_name') or '').strip()
    addr_street = (ev.get('address_street') or '').strip()
    addr_zip = (ev.get('address_zipcode') or '').strip()
    addr_city = (ev.get('address_city') or 'Paris').strip()

    if addr_name:
        parts.append(addr_name)
    if addr_street and addr_street.lower() != addr_name.lower():
        parts.append(addr_street)
    if addr_zip:
        parts.append(f"{addr_zip} {addr_city}")
    else:
        parts.append(addr_city)
    parts.append('France')
    location = ', '.join(parts)

    # Prix
    price = ev.get('price_type', '')
    price_detail = clean_html(ev.get('price_detail', '') or '')
    if price == 'gratuit':
        price_info = 'Gratuit'
    elif price_detail:
        price_info = truncate_desc(price_detail, 100)
    else:
        price_info = ''

    return {
        'title': title,
        'description': truncate_desc(description, 400),
        'date': start_date,
        'time': parse_time(start_time),
        'end_date': end_date,
        'end_time': parse_time(end_time),
        'location': location,
        'latitude': float(lat),
        'longitude': float(lng),
        'categories': categories,
        'source_url': source_url,
        'type': 'event',
        'validation_status': 'scraped',
        'organizer_name': addr_name or 'Paris.fr',
    }


# ============================================================
# NANTES MÉTROPOLE
# ============================================================

def fetch_nantes_events():
    """Récupère les events de Nantes Métropole."""
    print("\n   [NANTES] Récupération des events...")
    all_events = []
    url = SOURCES['nantes']['url']

    # Filtrer: events en 2026
    where = "date >= '2026-02-01' AND date < '2027-01-01' AND annule='non'"

    offset = 0
    limit = 100

    # Titres déjà vus (Nantes a des doublons d'occurrences du même event)
    seen_titles = set()

    while True:
        params = {
            'where': where,
            'limit': limit,
            'offset': offset,
            'order_by': 'date',
        }

        try:
            r = requests.get(url, params=params, timeout=30)
            data = r.json()
            records = data.get('results', [])
            total = data.get('total_count', 0)

            if not records:
                break

            # Dédupliquer par id_manif (même événement, dates différentes)
            for rec in records:
                manif_id = rec.get('id_manif', '')
                if manif_id and manif_id not in seen_titles:
                    seen_titles.add(manif_id)
                    all_events.append(rec)

            print(f"   [NANTES] {offset + len(records)}/{total} fetched, {len(all_events)} uniques...")

            offset += limit
            if offset >= total or offset >= 2000:  # Cap à 2000 pour ne pas être trop gourmand
                break

            time.sleep(0.5)

        except Exception as e:
            print(f"   [NANTES] Erreur: {e}")
            break

    return all_events


def parse_nantes_event(ev):
    """Transforme un event Nantes en format MapEventAI."""
    title = (ev.get('nom') or '').strip()
    if not title:
        return None

    # Coordonnées
    lat = ev.get('latitude')
    lng = ev.get('longitude')
    if not lat or not lng:
        latlon = ev.get('location_latlong')
        if latlon and isinstance(latlon, dict):
            lat = latlon.get('lat')
            lng = latlon.get('lon')
    if not lat or not lng:
        return None

    # Dates
    date_str = ev.get('date', '')
    if not date_str:
        return None
    start_date = str(date_str)[:10]

    # Trouver la dernière date pour cet événement (on prend la date fournie)
    end_date = start_date

    # Horaires
    start_time = parse_time(ev.get('heure_debut'))
    end_time = parse_time(ev.get('heure_fin'))

    # Source URL
    source_url = ev.get('lien_agenda', '') or ev.get('url_site', '') or ''

    # Description
    desc_evt = clean_html(ev.get('description_evt', ''))
    desc = clean_html(ev.get('description', ''))
    description = desc_evt if desc_evt else desc
    if not description:
        description = f"Événement à Nantes : {title}"

    # Tags et catégories
    themes = ev.get('themes_libelles', []) or []
    types = ev.get('types_libelles', []) or []
    tags = ' '.join(themes + types)
    lieu = ev.get('lieu', '') or ''

    categories = assign_categories(title, description, tags, lieu)

    # Adresse
    parts = []
    lieu_name = (ev.get('lieu') or '').strip()
    adresse = (ev.get('adresse') or '').strip()
    cp = str(ev.get('code_postal', '') or '').strip()
    ville = (ev.get('ville') or 'Nantes').strip()

    if lieu_name:
        parts.append(lieu_name)
    if adresse and adresse.lower() != lieu_name.lower():
        parts.append(adresse)
    if cp:
        parts.append(f"{cp} {ville}")
    else:
        parts.append(ville)
    parts.append('France')
    location = ', '.join(parts)

    return {
        'title': title,
        'description': truncate_desc(description, 400),
        'date': start_date,
        'time': start_time,
        'end_date': end_date,
        'end_time': end_time,
        'location': location,
        'latitude': float(lat),
        'longitude': float(lng),
        'categories': categories,
        'source_url': source_url,
        'type': 'event',
        'validation_status': 'scraped',
        'organizer_name': ev.get('emetteur') or lieu_name or '',
    }


# ============================================================
# BORDEAUX MÉTROPOLE (format OpenAgenda)
# ============================================================

def fetch_bordeaux_events():
    """Récupère les events de Bordeaux Métropole."""
    print("\n   [BORDEAUX] Récupération des events...")
    all_events = []
    url = SOURCES['bordeaux']['url']

    # Filtrer: events 2026
    where = "firstdate_begin >= '2026-02-01' AND firstdate_begin < '2027-01-01'"

    offset = 0
    limit = 100

    # Déduplications par uid
    seen_uids = set()

    while True:
        params = {
            'where': where,
            'limit': limit,
            'offset': offset,
            'order_by': 'firstdate_begin',
        }

        try:
            r = requests.get(url, params=params, timeout=30)
            data = r.json()
            records = data.get('results', [])
            total = data.get('total_count', 0)

            if not records:
                break

            for rec in records:
                uid = rec.get('uid', '')
                if uid and uid not in seen_uids:
                    seen_uids.add(uid)
                    all_events.append(rec)

            print(f"   [BORDEAUX] {offset + len(records)}/{total} fetched, {len(all_events)} uniques...")

            offset += limit
            if offset >= total or offset >= 2000:
                break

            time.sleep(0.5)

        except Exception as e:
            print(f"   [BORDEAUX] Erreur: {e}")
            break

    return all_events


def parse_bordeaux_event(ev):
    """Transforme un event Bordeaux (OpenAgenda) en format MapEventAI."""
    title = (ev.get('title_fr') or ev.get('title') or '').strip()
    if not title:
        return None

    # Coordonnées
    coords = ev.get('location_coordinates')
    lat = None
    lng = None
    if coords and isinstance(coords, dict):
        lat = coords.get('lat')
        lng = coords.get('lon')
    if not lat or not lng:
        return None

    # Dates
    first_date = ev.get('firstdate_begin', '')
    last_date = ev.get('lastdate_end') or ev.get('lastdate_begin') or first_date

    start_date = first_date[:10] if first_date else None
    end_date = last_date[:10] if last_date else start_date

    if not start_date:
        return None

    # Horaires
    start_time = None
    end_time = None
    if first_date and 'T' in first_date:
        t = first_date.split('T')[1][:5]
        if t != '00:00':
            start_time = t
    if last_date and 'T' in str(last_date):
        fe = ev.get('firstdate_end', '')
        if fe and 'T' in fe:
            t = fe.split('T')[1][:5]
            if t != '00:00':
                end_time = t

    # Source URL
    slug = ev.get('slug', '')
    source_url = f"https://openagenda.com/events/{slug}" if slug else ''

    # Description
    desc = clean_html(ev.get('longdescription_fr') or ev.get('description_fr') or '')
    description = truncate_desc(desc) if desc else f"Événement à Bordeaux : {title}"

    # Tags et catégories
    keywords = ' '.join(ev.get('keywords_fr', []) or [])
    location_name = ev.get('location_name', '') or ''

    categories = assign_categories(title, description, keywords, location_name)

    # Adresse
    parts = []
    loc_name = (ev.get('location_name') or '').strip()
    loc_address = (ev.get('location_address') or '').strip()
    loc_city = (ev.get('location_city') or 'Bordeaux').strip()
    loc_postal = (ev.get('location_postalcode') or '').strip()

    if loc_name:
        parts.append(loc_name)
    if loc_address and loc_name.lower() not in loc_address.lower():
        parts.append(loc_address)
    if loc_postal:
        parts.append(f"{loc_postal} {loc_city}")
    else:
        parts.append(loc_city)
    parts.append('France')
    location = ', '.join(parts)

    return {
        'title': title,
        'description': truncate_desc(description, 400),
        'date': start_date,
        'time': parse_time(start_time),
        'end_date': end_date,
        'end_time': parse_time(end_time),
        'location': location,
        'latitude': float(lat),
        'longitude': float(lng),
        'categories': categories,
        'source_url': source_url,
        'type': 'event',
        'validation_status': 'scraped',
        'organizer_name': loc_name or '',
    }


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 60)
    print("  IMPORT OPEN DATA - GRANDES VILLES FRANCAISES")
    print("  Sources: data.gouv.fr / portails OpenData municipaux")
    print("  Licences: ODbL + Licence Ouverte v2.0 + CC-BY")
    print("=" * 60)

    # 1. Récupérer les events existants
    print("\n  Récupération des events existants...")
    existing = fetch_existing_events()
    print(f"   Events existants: {len(existing)}")

    all_events_to_import = []
    city_stats = {}

    # 2. Récupérer et parser chaque source
    fetchers = {
        'paris': (fetch_paris_events, parse_paris_event),
        'nantes': (fetch_nantes_events, parse_nantes_event),
        'bordeaux': (fetch_bordeaux_events, parse_bordeaux_event),
    }

    for city, (fetcher, parser) in fetchers.items():
        source = SOURCES[city]
        print(f"\n{'='*40}")
        print(f"  {source['name']}")
        print(f"  Licence: {source['license']}")
        print(f"{'='*40}")

        stats = {'total': 0, 'no_coords': 0, 'duplicate': 0, 'no_date': 0, 'parsed': 0}

        raw_events = fetcher()
        print(f"   Total brut: {len(raw_events)} events")

        for ev in raw_events:
            stats['total'] += 1
            parsed = parser(ev)

            if not parsed:
                stats['no_coords'] += 1
                continue

            # Vérifier doublons
            if is_duplicate(parsed['title'], parsed['source_url'], existing):
                stats['duplicate'] += 1
                continue

            # Ajouter aux events existants pour éviter doublons inter-sources
            existing.append({'title': parsed['title'], 'source_url': parsed['source_url']})

            all_events_to_import.append(parsed)
            stats['parsed'] += 1

        city_stats[city] = stats

        print(f"\n   Statistiques {city.upper()}:")
        print(f"   Total brut: {stats['total']}")
        print(f"   Sans coords/date: {stats['no_coords']}")
        print(f"   Doublons: {stats['duplicate']}")
        print(f"   A importer: {stats['parsed']}")

    # 3. Résumé global
    total_to_import = len(all_events_to_import)
    print(f"\n{'='*60}")
    print(f"  RÉSUMÉ GLOBAL")
    print(f"{'='*60}")
    for city, stats in city_stats.items():
        print(f"   {city.upper():12s}: {stats['parsed']:4d} events")
    print(f"   {'TOTAL':12s}: {total_to_import:4d} events")

    if not all_events_to_import:
        print("\n  Aucun event à importer")
        return

    # 4. Aperçu
    print(f"\n  Aperçu (premiers 15):")
    for ev in all_events_to_import[:15]:
        city_name = ''
        if 'Paris' in ev['location']:
            city_name = 'Paris'
        elif 'Nantes' in ev['location']:
            city_name = 'Nantes'
        elif 'Bordeaux' in ev['location'] or 'Gironde' in ev['location']:
            city_name = 'Bordeaux'
        print(f"   [{city_name:10s}] {ev['title'][:45]:45s} | {ev['date']} | {ev['categories'][:2]}")

    # 5. Importer par batch
    print(f"\n  Import de {total_to_import} events par batch de 20...")
    total_created = 0

    for i in range(0, total_to_import, 20):
        batch = all_events_to_import[i:i+20]
        try:
            r = requests.post(
                f'{API_URL}/api/events/scraped/batch',
                json={'events': batch},
                timeout=30
            )
            result = r.json()
            created = result.get('created', len(batch))
            total_created += created
            print(f"   Batch {i//20 + 1}: {created} créés")
            time.sleep(2)
        except Exception as e:
            print(f"   Batch {i//20 + 1}: erreur - {e}")

    print(f"\n{'='*60}")
    print(f"  TOTAL IMPORTE: {total_created} events")
    print(f"  Sources:")
    print(f"    - Paris (ODbL)")
    print(f"    - Nantes (Licence Ouverte v2.0)")
    print(f"    - Bordeaux (CC-BY)")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
