# -*- coding: utf-8 -*-
"""
Import d'events Open Data - Nouvelles villes France + Suisse + Belgique
Source : OpenAgenda via OpenDataSoft (public.opendatasoft.com)
Licence : CC-BY / Licence Ouverte (100% safe, usage commercial OK)

Villes France : Lyon, Marseille, Toulouse, Lille, Strasbourg, Montpellier,
                Nice, Rennes, Grenoble, Dijon
Suisse : Genève (+ toute la Suisse romande)
Belgique : Bruxelles, Liège, Tournai, etc.

RÈGLE #1 : Ne prendre QUE des données à licence claire
"""

import sys
import json
import requests
import time
import re

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'
OPENDATA_URL = 'https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/evenements-publics-openagenda/records'

# ============================================================
# CONFIGURATION DES VILLES / PAYS À IMPORTER
# ============================================================

IMPORT_GROUPS = {
    'france_villes': {
        'name': 'France - Nouvelles villes',
        'license': 'CC-BY / Licence Ouverte (OpenAgenda)',
        'country': 'FR',
        'cities': [
            'Lyon', 'Marseille', 'Toulouse', 'Lille', 'Strasbourg',
            'Montpellier', 'Nice', 'Rennes', 'Grenoble', 'Dijon',
            'Rouen', 'Metz', 'Reims', 'Saint-Étienne', 'Toulon',
            'Le Mans', 'Aix-en-Provence', 'Clermont-Ferrand', 'Tours',
            'Limoges', 'Amiens', 'Perpignan', 'Besançon', 'Orléans',
            'Caen', 'Mulhouse', 'Boulogne-Billancourt', 'Nancy',
            'Avignon', 'Cannes', 'Annecy', 'Chambéry',
        ],
        'country_name': 'France',
    },
    'suisse': {
        'name': 'Suisse (toutes villes)',
        'license': 'CC-BY (OpenAgenda)',
        'country': 'CH',
        'cities': None,  # None = tout le pays
        'country_name': 'Suisse',
    },
    'belgique': {
        'name': 'Belgique (toutes villes)',
        'license': 'CC-BY (OpenAgenda)',
        'country': 'BE',
        'cities': None,  # None = tout le pays
        'country_name': 'Belgique',
    },
}


# ============================================================
# CATÉGORIES INTELLIGENTES
# ============================================================

def assign_categories(title, description='', keywords='', location_name=''):
    """
    Assigne des categories - utilise le module partage category_utils.
    Import local pour compatibilite avec les anciens scripts.
    """
    try:
        from category_utils import assign_categories as _assign
        return _assign(title, description, keywords, location_name)
    except ImportError:
        # Fallback si le module n'est pas trouvable
        import sys, os
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from category_utils import assign_categories as _assign
        return _assign(title, description, keywords, location_name)


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
    """Tronque une description."""
    if not desc:
        return ''
    desc = clean_html(desc)
    if len(desc) > max_len:
        desc = desc[:max_len - 3] + '...'
    return desc


def parse_time_str(dt_str):
    """Extrait HH:MM d'un datetime string."""
    if not dt_str or 'T' not in str(dt_str):
        return None
    try:
        t = str(dt_str).split('T')[1][:5]
        if t and t != '00:00':
            h, m = int(t[:2]), int(t[3:5])
            if 0 <= h <= 23 and 0 <= m <= 59:
                return t
    except:
        pass
    return None


def is_junk_event(title, start_date):
    """Filtre les events poubelle (tests, dates trop lointaines, etc.)."""
    title_lower = title.lower().strip()
    
    # Titres trop courts ou tests
    if len(title_lower) < 3:
        return True
    if title_lower in ['test', 'test event', 'essai', 'titre', 'test2', 'toto']:
        return True
    
    # Dates trop lointaines (structures permanentes codées en 2030+)
    if start_date and start_date > '2027-06-01':
        return True
    
    # Titres qui sont juste des noms de lieux (auberge, hôtel, etc.)
    junk_patterns = [
        r'^auberge de jeunesse',
        r'^hôtel ',
        r'^hotel ',
        r'^camping ',
        r'^gîte ',
    ]
    for pattern in junk_patterns:
        if re.match(pattern, title_lower):
            return True
    
    return False


def fetch_existing_events():
    """Récupère les events existants pour éviter les doublons."""
    try:
        r = requests.get(f'{API_URL}/api/events', timeout=60)
        data = r.json()
        events = data if isinstance(data, list) else data.get('events', [])
        return events
    except Exception as e:
        print(f"   Erreur récup existants: {e}")
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
# FETCH & PARSE OPENAGENDA
# ============================================================

def fetch_openagenda_events(country_code, cities=None, max_per_city=500):
    """Récupère les events depuis OpenAgenda pour un pays/villes."""
    all_events = []
    
    if cities:
        # Fetch par ville
        for city in cities:
            where = f'location_countrycode="{country_code}" AND location_city="{city}" AND firstdate_begin>="2026-02-01" AND firstdate_begin<"2027-06-01"'
            city_events = _fetch_paginated(where, max_records=max_per_city)
            print(f"   {city}: {len(city_events)} events")
            all_events.extend(city_events)
            time.sleep(0.5)
    else:
        # Fetch tout le pays
        where = f'location_countrycode="{country_code}" AND firstdate_begin>="2026-02-01" AND firstdate_begin<"2027-06-01"'
        all_events = _fetch_paginated(where, max_records=2000)
        print(f"   Total: {len(all_events)} events")
    
    return all_events


def _fetch_paginated(where, max_records=2000):
    """Fetch paginé depuis OpenDataSoft."""
    all_records = []
    offset = 0
    limit = 100
    
    while offset < max_records:
        params = {
            'where': where,
            'limit': limit,
            'offset': offset,
            'order_by': 'firstdate_begin',
        }
        
        try:
            r = requests.get(OPENDATA_URL, params=params, timeout=30)
            data = r.json()
            records = data.get('results', [])
            total = data.get('total_count', 0)
            
            if not records:
                break
            
            all_records.extend(records)
            
            offset += limit
            if offset >= total:
                break
            
            time.sleep(0.3)
            
        except Exception as e:
            print(f"      Erreur fetch: {e}")
            break
    
    return all_records


def parse_openagenda_event(ev, country_name='France'):
    """Transforme un event OpenAgenda en format MapEventAI."""
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
    
    # Filtrer les events poubelle
    if is_junk_event(title, start_date):
        return None
    
    # Horaires
    start_time = parse_time_str(first_date)
    end_time = parse_time_str(ev.get('firstdate_end'))
    
    # Source URL
    source_url = ev.get('canonicalurl') or ''
    if not source_url:
        slug = ev.get('slug', '')
        if slug:
            source_url = f"https://openagenda.com/events/{slug}"
    
    # Description
    desc = clean_html(ev.get('longdescription_fr') or ev.get('description_fr') or '')
    description = truncate_desc(desc) if desc else f"Événement : {title}"
    
    # Tags et catégories
    keywords = ' '.join(ev.get('keywords_fr', []) or [])
    location_name = ev.get('location_name', '') or ''
    categories = assign_categories(title, description, keywords, location_name)
    
    # Adresse
    parts = []
    loc_name = (ev.get('location_name') or '').strip()
    loc_address = (ev.get('location_address') or '').strip()
    loc_city = (ev.get('location_city') or '').strip()
    loc_postal = (ev.get('location_postalcode') or '').strip()
    
    if loc_name:
        parts.append(loc_name)
    if loc_address and loc_name.lower() not in loc_address.lower():
        parts.append(loc_address)
    if loc_postal and loc_city:
        parts.append(f"{loc_postal} {loc_city}")
    elif loc_city:
        parts.append(loc_city)
    parts.append(country_name)
    location = ', '.join(parts)
    
    # Organizer email (si dispo dans les données)
    organizer_email = ''
    # OpenAgenda ne fournit généralement pas l'email dans l'API publique
    
    return {
        'title': title,
        'description': description,
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
        'organizer_name': loc_name or '',
    }


# ============================================================
# IMPORT
# ============================================================

def import_batch(events, batch_size=20):
    """Importe des events par batch via l'API."""
    total_created = 0
    
    for i in range(0, len(events), batch_size):
        batch = events[i:i + batch_size]
        try:
            r = requests.post(
                f'{API_URL}/api/events/scraped/batch',
                json={'events': batch},
                timeout=30
            )
            result = r.json()
            created = result.get('created', len(batch))
            total_created += created
            print(f"   Batch {i // batch_size + 1}: {created} créés")
            time.sleep(2)
        except Exception as e:
            print(f"   Batch {i // batch_size + 1}: erreur - {e}")
    
    return total_created


# ============================================================
# MAIN
# ============================================================

def main():
    print("=" * 65)
    print("  IMPORT OPEN DATA - NOUVELLES VILLES (Fév 2026)")
    print("  Source: OpenAgenda via OpenDataSoft")
    print("  Licence: CC-BY / Licence Ouverte (100% safe)")
    print("=" * 65)
    
    # 1. Récupérer les events existants
    print("\n📥 Récupération des events existants...")
    existing = fetch_existing_events()
    print(f"   Events existants: {len(existing)}")
    
    all_events_to_import = []
    group_stats = {}
    
    # 2. Fetch & parse chaque groupe
    for group_key, config in IMPORT_GROUPS.items():
        print(f"\n{'=' * 50}")
        print(f"  {config['name']}")
        print(f"  Licence: {config['license']}")
        print(f"{'=' * 50}")
        
        stats = {'fetched': 0, 'parsed': 0, 'junk': 0, 'no_data': 0, 'duplicate': 0, 'imported': 0}
        
        # Fetch
        raw_events = fetch_openagenda_events(
            config['country'],
            config.get('cities'),
            max_per_city=500
        )
        stats['fetched'] = len(raw_events)
        print(f"\n   Total brut: {stats['fetched']} events")
        
        # Dédupliquer les raw par uid
        seen_uids = set()
        unique_events = []
        for ev in raw_events:
            uid = ev.get('uid', '')
            if uid and uid in seen_uids:
                continue
            if uid:
                seen_uids.add(uid)
            unique_events.append(ev)
        
        print(f"   Uniques (par uid): {len(unique_events)}")
        
        # Parse
        for ev in unique_events:
            parsed = parse_openagenda_event(ev, config['country_name'])
            
            if not parsed:
                stats['no_data'] += 1
                continue
            
            stats['parsed'] += 1
            
            # Vérifier doublons
            if is_duplicate(parsed['title'], parsed['source_url'], existing):
                stats['duplicate'] += 1
                continue
            
            # Ajouter aux existants pour éviter doublons inter-groupes
            existing.append({'title': parsed['title'], 'source_url': parsed['source_url']})
            
            all_events_to_import.append(parsed)
            stats['imported'] += 1
        
        group_stats[group_key] = stats
        
        print(f"\n   📊 Stats {config['name']}:")
        print(f"      Brut: {stats['fetched']}")
        print(f"      Sans données/junk: {stats['no_data']}")
        print(f"      Parsés: {stats['parsed']}")
        print(f"      Doublons: {stats['duplicate']}")
        print(f"      ✅ À importer: {stats['imported']}")
    
    # 3. Résumé global
    total = len(all_events_to_import)
    print(f"\n{'=' * 65}")
    print(f"  RÉSUMÉ GLOBAL")
    print(f"{'=' * 65}")
    for key, stats in group_stats.items():
        name = IMPORT_GROUPS[key]['name']
        print(f"   {name:35s}: {stats['imported']:4d} events")
    print(f"   {'TOTAL':35s}: {total:4d} events")
    
    if not all_events_to_import:
        print("\n⚠️ Aucun event à importer")
        return
    
    # 4. Aperçu par ville
    city_counts = {}
    for ev in all_events_to_import:
        loc = ev['location']
        # Extraire la ville (avant-dernier élément)
        parts = [p.strip() for p in loc.split(',')]
        city = parts[-2] if len(parts) >= 2 else parts[0]
        # Nettoyer (enlever code postal)
        city_clean = re.sub(r'^\d{4,5}\s+', '', city)
        city_counts[city_clean] = city_counts.get(city_clean, 0) + 1
    
    print(f"\n📋 Répartition par ville:")
    for city, count in sorted(city_counts.items(), key=lambda x: -x[1])[:20]:
        print(f"   {city:25s}: {count:4d} events")
    
    # 5. Aperçu des premiers events
    print(f"\n📋 Aperçu (premiers 15):")
    for ev in all_events_to_import[:15]:
        loc_parts = [p.strip() for p in ev['location'].split(',')]
        city = loc_parts[-2] if len(loc_parts) >= 2 else '?'
        city = re.sub(r'^\d{4,5}\s+', '', city)
        cats = ', '.join(ev['categories'][:2])
        print(f"   [{city:15s}] {ev['title'][:40]:40s} | {ev['date']} | {cats}")
    
    # 6. Importer
    print(f"\n📤 Import de {total} events par batch de 20...")
    total_created = import_batch(all_events_to_import)
    
    print(f"\n{'=' * 65}")
    print(f"  🎯 TOTAL IMPORTÉ: {total_created} events")
    print(f"  Sources: OpenAgenda (CC-BY)")
    for key, config in IMPORT_GROUPS.items():
        print(f"    - {config['name']} ({config['license']})")
    print(f"{'=' * 65}")


if __name__ == '__main__':
    main()
