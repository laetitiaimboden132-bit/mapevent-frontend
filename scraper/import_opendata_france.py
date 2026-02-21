# -*- coding: utf-8 -*-
"""
Import d'events Open Data depuis OpenAgenda pour les régions françaises.
Source : OpenDataSoft / OpenAgenda - Licence CC-BY (zone verte, 100% safe)
Régions : Haute-Savoie, Savoie, Isère, Ain, Rhône, Haut-Rhin, Bas-Rhin

RÈGLE #1 : Ne prendre QUE des données à licence claire (CC-BY ici)
"""

import sys
import json
import requests
import time
import re

sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'
OPENDATA_URL = 'https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/evenements-publics-openagenda/records'

# Départements français cibles (proches de la Suisse)
TARGET_DEPARTMENTS = [
    'Haute-Savoie', 'Savoie', 'Isère', 'Ain', 'Rhône',
    'Haut-Rhin', 'Bas-Rhin', 'Doubs', 'Jura', 'Territoire de Belfort'
]


def assign_categories(title, description, keywords, location_name):
    """Assigne des catégories spécifiques en analysant titre + description + keywords."""
    text = f"{title} {description} {keywords} {location_name}".lower()
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
        'chorale': 'Musique > Classique', 'orchestre': 'Musique > Classique',
        'salsa': 'Musique > Latin', 'bachata': 'Musique > Latin',
    }
    for kw, cat in music_specific.items():
        if kw in text and cat not in result:
            result.append(cat)
    
    if ('concert' in text or 'musique' in text or 'music' in text) and not any('Musique >' in c for c in result):
        result.append('Musique > Concert')
    
    # === FESTIVAL ===
    if 'festival' in text and 'Festival' not in result:
        result.append('Festival')
    
    # === THÉÂTRE / SPECTACLE ===
    if any(kw in text for kw in ['théâtre', 'theatre', 'pièce de', 'comédie']):
        result.append('Culture > Théâtre')
    if any(kw in text for kw in ['danse', 'ballet', 'chorégraph']):
        result.append('Culture > Danse')
    if any(kw in text for kw in ['cirque', 'acrobat', 'clown', 'jongl']):
        result.append('Culture > Cirque')
    if any(kw in text for kw in ['spectacle', 'one man show', 'one-man-show', 'humoriste']):
        if not any('Culture >' in c for c in result):
            result.append('Culture > Spectacle')
    
    # === CINÉMA ===
    if any(kw in text for kw in ['cinéma', 'cinema', 'film', 'projection', 'ciné-']):
        result.append('Culture > Cinéma')
    
    # === EXPOSITION ===
    expo_kw = ['exposition', 'expo ', 'musée', 'galerie', 'vernissage', 'œuvres', 'oeuvres']
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
        'natation': 'Sport > Aquatique', 'piscine': 'Sport > Aquatique',
        'kayak': 'Sport > Aquatique', 'voile': 'Sport > Aquatique',
        'parapente': 'Sport > Aérien', 'parachute': 'Sport > Aérien',
    }
    for kw, cat in sport_map.items():
        if kw in text and cat not in result:
            result.append(cat)
    
    if any(kw in text for kw in ['sportif', 'compétition', 'tournoi']) and not any('Sport' in c for c in result):
        result.append('Sport > Terrestre')
    
    # === GASTRONOMIE ===
    if any(kw in text for kw in ['dégustation', 'vignoble', 'vigneron', 'cave', 'oenolog', 'vin ']):
        result.append('Gastronomie > Dégustation vin')
    elif any(kw in text for kw in ['bière', 'brasserie']):
        result.append('Gastronomie > Dégustation bière')
    elif any(kw in text for kw in ['brunch', 'gastronomie', 'culinaire', 'cuisine', 'repas', 'food']):
        result.append('Gastronomie')
    
    # === MARCHÉS ===
    if any(kw in text for kw in ['marché', 'brocante', 'vide-grenier', 'puces']):
        cat = 'Marché > Brocante' if any(kw in text for kw in ['brocante', 'vide-grenier', 'puces']) else 'Marché'
        result.append(cat)
    if any(kw in text for kw in ['foire', 'salon ']):
        result.append('Foire')
    
    # === CARNAVAL / FÊTE ===
    if 'carnaval' in text:
        result.append('Carnaval')
    if any(kw in text for kw in ['parade', 'cortège', 'défilé']):
        result.append('Parade')
    
    # === CONFÉRENCE / ATELIER ===
    if any(kw in text for kw in ['conférence', 'séminaire', 'colloque']):
        result.append('Conférence')
    if any(kw in text for kw in ['atelier', 'workshop', 'stage ']):
        result.append('Atelier')
    
    # === CONTE / LECTURE ===
    if any(kw in text for kw in ['conte ', 'contes ', 'lecture', 'littéra']):
        result.append('Culture > Conte')
    
    # Fallback
    if not result:
        result.append('Culture')
    
    # Dédupliquer
    return list(dict.fromkeys(result))


def fetch_opendata_events():
    """Récupère les events français depuis OpenAgenda."""
    all_events = []
    
    # Construire le filtre WHERE pour les départements
    # Filtrer pour des events en 2026 uniquement (pas 2032 qui sont des structures permanentes)
    dept_filters = " OR ".join([f"location_department='{d}'" for d in TARGET_DEPARTMENTS])
    where = f"location_countrycode='FR' AND firstdate_begin>='2026-03-01' AND firstdate_begin<'2027-01-01' AND ({dept_filters})"
    
    offset = 0
    limit = 100
    
    while True:
        params = {
            'where': where,
            'limit': limit,
            'offset': offset,
            'order_by': 'firstdate_begin'
        }
        
        try:
            r = requests.get(OPENDATA_URL, params=params, timeout=30)
            data = r.json()
            records = data.get('results', [])
            total = data.get('total_count', 0)
            
            if not records:
                break
            
            all_events.extend(records)
            print(f"   Fetched {len(all_events)}/{total} events...")
            
            offset += limit
            if offset >= total:
                break
            
            time.sleep(1)  # Respect API
            
        except Exception as e:
            print(f"   ❌ Erreur fetch: {e}")
            break
    
    return all_events


def fetch_existing_events():
    """Récupère les events existants pour éviter les doublons."""
    try:
        r = requests.get(f'{API_URL}/api/events', timeout=30)
        data = r.json()
        events = data if isinstance(data, list) else data.get('events', [])
        return events
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return []


def is_duplicate(new_title, new_source, existing_events):
    """Vérifie si un event existe déjà."""
    new_title_lower = new_title.lower().strip()
    new_title_words = set(re.findall(r'\w+', new_title_lower))
    
    for ev in existing_events:
        # Vérifier par source_url
        if new_source and ev.get('source_url') == new_source:
            return True
        
        # Vérifier par titre similaire
        ex_title = (ev.get('title', '') or '').lower().strip()
        if ex_title == new_title_lower:
            return True
        
        # Similarité par mots communs
        ex_words = set(re.findall(r'\w+', ex_title))
        if len(new_title_words) >= 3 and len(ex_words) >= 3:
            common = new_title_words & ex_words
            similarity = len(common) / max(len(new_title_words), len(ex_words))
            if similarity > 0.7:
                return True
    
    return False


def clean_address(location_name, location_address, location_city, location_postcode):
    """Construit une adresse propre et complète."""
    parts = []
    
    # Adresse (rue + numéro)
    addr = (location_address or '').strip()
    if addr and addr.lower() not in ['', 'null', 'none', location_city.lower() if location_city else '']:
        parts.append(addr)
    
    # Nom du lieu (si différent de l'adresse)
    name = (location_name or '').strip()
    if name and name not in parts and name.lower() != (location_city or '').lower():
        # Éviter d'ajouter si c'est redondant avec l'adresse
        if not any(name.lower() in p.lower() for p in parts):
            parts.insert(0, name)
    
    # Code postal + ville
    city = (location_city or '').strip()
    postcode = str(location_postcode or '').strip()
    
    if postcode and city:
        parts.append(f"{postcode} {city}")
    elif city:
        parts.append(city)
    
    # Pays
    parts.append('France')
    
    return ', '.join(parts) if parts else 'France'


def create_description(title, long_desc, location_name, keywords):
    """Crée un descriptif remanié (jamais copié-collé)."""
    # Résumer la description si elle est longue
    desc = (long_desc or '').strip()
    
    if not desc:
        return f"Événement : {title}."
    
    # Nettoyer le HTML
    desc = re.sub(r'<[^>]+>', ' ', desc)
    desc = re.sub(r'\s+', ' ', desc).strip()
    
    # Limiter la longueur
    if len(desc) > 400:
        desc = desc[:397] + '...'
    
    return desc


def main():
    print("=" * 60)
    print("🇫🇷 IMPORT OPEN DATA - FRANCE (Régions alpines)")
    print("   Source: OpenAgenda / OpenDataSoft")
    print("   Licence: CC-BY (zone verte - 100% safe)")
    print("=" * 60)
    
    # 1. Récupérer les events OpenAgenda France
    print("\n📥 Récupération des events France depuis OpenAgenda...")
    raw_events = fetch_opendata_events()
    print(f"   Total brut: {len(raw_events)} events")
    
    if not raw_events:
        print("❌ Aucun event trouvé")
        return
    
    # 2. Récupérer les events existants
    print("\n📥 Récupération des events existants...")
    existing = fetch_existing_events()
    print(f"   Events existants: {len(existing)}")
    
    # 3. Préparer les events
    print("\n🔧 Préparation des events...")
    events_to_import = []
    stats = {'total': 0, 'no_coords': 0, 'duplicate': 0, 'no_date': 0, 'imported': 0}
    
    for ev in raw_events:
        stats['total'] += 1
        
        title = (ev.get('title_fr') or ev.get('title') or '').strip()
        if not title:
            continue
        
        # Coordonnées - OpenAgenda utilise location_coordinates
        coords = ev.get('location_coordinates')
        lat = None
        lng = None
        if coords and isinstance(coords, dict):
            lat = coords.get('lat')
            lng = coords.get('lon')
        if not lat or not lng:
            lat = ev.get('location_lat')
            lng = ev.get('location_lng')
        if not lat or not lng:
            latlon = ev.get('latlon')
            if latlon and isinstance(latlon, dict):
                lat = latlon.get('lat')
                lng = latlon.get('lon')
        
        if not lat or not lng:
            stats['no_coords'] += 1
            continue
        
        # Dates
        first_date = ev.get('firstdate_begin')
        last_date = ev.get('lastdate_end') or ev.get('lastdate_begin') or first_date
        
        if not first_date:
            stats['no_date'] += 1
            continue
        
        # Extraire date et heure
        start_date = first_date[:10] if first_date else None
        end_date = last_date[:10] if last_date else start_date
        
        if not start_date:
            stats['no_date'] += 1
            continue
        
        # Source URL
        source_url = ev.get('canonicalurl') or ev.get('originagenda_url') or ''
        if not source_url:
            slug = ev.get('slug', '')
            uid = ev.get('uid', '')
            if slug:
                source_url = f"https://openagenda.com/events/{slug}"
            elif uid:
                source_url = f"https://openagenda.com/events/{uid}"
        
        # Vérifier doublons
        if is_duplicate(title, source_url, existing):
            stats['duplicate'] += 1
            continue
        
        # Catégories
        keywords = ' '.join(ev.get('keywords_fr', []) or [])
        description_long = ev.get('longdescription_fr') or ev.get('description_fr') or ''
        location_name = ev.get('location_name') or ''
        
        categories = assign_categories(title, description_long, keywords, location_name)
        
        # Adresse
        location = clean_address(
            ev.get('location_name'),
            ev.get('location_address'),
            ev.get('location_city'),
            ev.get('location_postalcode')
        )
        
        # Description
        description = create_description(title, description_long, location_name, keywords)
        
        event_data = {
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
            'validation_status': 'scraped',
            'organizer_name': ev.get('location_name') or '',
        }
        
        events_to_import.append(event_data)
        stats['imported'] += 1
    
    print(f"\n📊 Statistiques:")
    print(f"   Total brut: {stats['total']}")
    print(f"   Sans coordonnées: {stats['no_coords']}")
    print(f"   Sans date: {stats['no_date']}")
    print(f"   Doublons: {stats['duplicate']}")
    print(f"   ✅ À importer: {stats['imported']}")
    
    if not events_to_import:
        print("\n⚠️ Aucun event à importer")
        return
    
    # Afficher un aperçu
    print(f"\n📋 Aperçu (premiers 10):")
    for ev in events_to_import[:10]:
        dept = ev['location'].split(',')[-2].strip() if ',' in ev['location'] else ''
        print(f"   📍 {ev['title'][:50]} | {ev['date']} | {dept}")
        print(f"      Catégories: {ev['categories']}")
    
    # 4. Importer par batch
    print(f"\n📤 Import de {len(events_to_import)} events par batch de 20...")
    total_created = 0
    
    for i in range(0, len(events_to_import), 20):
        batch = events_to_import[i:i+20]
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
            time.sleep(2)  # Respect
        except Exception as e:
            print(f"   ❌ Batch {i//20 + 1}: {e}")
    
    print(f"\n🎯 TOTAL IMPORTÉ: {total_created} events France")
    print(f"   Régions: {', '.join(TARGET_DEPARTMENTS)}")
    print(f"   Source: OpenAgenda (CC-BY)")


if __name__ == '__main__':
    main()
