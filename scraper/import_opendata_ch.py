"""
Import Open Data events from OpenDataSoft / OpenAgenda API
Licence: Licence Ouverte v1.0 (equivalent CC-BY)
Source: https://public.opendatasoft.com/explore/dataset/evenements-publics-openagenda/
"""
import requests, json, time, sys, re
from datetime import datetime

# Force UTF-8
sys.stdout = open(sys.stdout.fileno(), mode='w', encoding='utf-8', buffering=1)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'
OPENDATA_URL = 'https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/evenements-publics-openagenda/records'

# Regions cibles (codes postaux)
GENEVA_POSTCODES = [str(c) for c in range(1200, 1300)]
VAUD_POSTCODES = [str(c) for c in range(1000, 1200)] + [str(c) for c in range(1300, 1600)] + ['1800','1801','1802','1804','1806','1808','1814','1815','1816','1820']
VALAIS_POSTCODES = [str(c) for c in range(1870, 2000)] + [str(c) for c in range(3900, 4000)] + ['1920','1950','1951','1870','1874','1890','1891','1895','1896','1897','1898','1899']

# ================================================================
# CATEGORY MAPPING - Maps keywords to our exact category system
# Priority: most specific first
# ================================================================
def assign_categories(title, description, keywords, location_name):
    """Assign categories based on event content. Returns list of categories."""
    text = f"{title} {description} {keywords or ''} {location_name or ''}".lower()
    cats = []
    
    # --- MUSIQUE ---
    if any(w in text for w in ['jazz', 'blues', 'soul', 'funk', 'swing']):
        cats.extend(['Musique', 'Musique > Jazz'])
    elif any(w in text for w in ['orchestre', 'symphoni', 'classique', 'philharmon', 'chambre', 'quatuor', 'sonate', 'concerto']):
        cats.extend(['Musique', 'Musique > Classique'])
    elif any(w in text for w in ['opera', 'opéra', 'lyrique', 'baryton', 'soprano', 'ténor']):
        cats.extend(['Musique', 'Musique > Classique'])
    elif any(w in text for w in ['rock', 'metal', 'punk', 'grunge']):
        cats.extend(['Musique', 'Concert'])
    elif any(w in text for w in ['rap', 'hip hop', 'hip-hop', 'trap', 'drill']):
        cats.extend(['Musique', 'Concert'])
    elif any(w in text for w in ['techno', 'electro', 'house', 'dj', 'club', 'bass']):
        cats.extend(['Musique', 'Concert'])
    elif any(w in text for w in ['reggae', 'ska', 'dub']):
        cats.extend(['Musique', 'Concert'])
    elif any(w in text for w in ['concert', 'récital', 'recital', 'musique', 'musical', 'musicien', 'chant', 'choeur', 'chorale', 'flûte', 'piano', 'violon', 'guitare', 'trompette', 'orgue']):
        cats.extend(['Musique', 'Concert'])
    
    # --- SPECTACLE / THEATRE ---
    if any(w in text for w in ['théâtre', 'theatre', 'comédie', 'comedie', 'tragédie', 'dramaturgie', 'mise en scène']):
        if 'Spectacle' not in cats:
            cats.append('Spectacle')
        cats.append('Spectacle > Théâtre')
    elif any(w in text for w in ['danse', 'ballet', 'chorégraph', 'choregraph']):
        if 'Spectacle' not in cats:
            cats.append('Spectacle')
        cats.append('Danse')
    elif any(w in text for w in ['cirque', 'acrobat', 'clown', 'jongl']):
        if 'Spectacle' not in cats:
            cats.append('Spectacle')
        cats.append('Cirque')
    elif any(w in text for w in ['spectacle', 'performance', 'scène', 'scene']):
        if 'Spectacle' not in cats:
            cats.append('Spectacle')
    elif any(w in text for w in ['marionnette', 'conte', 'conteur', 'narrat']):
        if 'Spectacle' not in cats:
            cats.append('Spectacle')
    elif any(w in text for w in ['humour', 'humoriste', 'stand-up', 'stand up', 'comedy', 'one man show', 'one-man-show']):
        if 'Spectacle' not in cats:
            cats.append('Spectacle')
    
    # --- EXPOSITION / MUSEE ---
    if any(w in text for w in ['exposition', 'expo ', 'exposé', 'galerie', 'vernissage']):
        cats.extend(['Culture', 'Exposition'])
    elif any(w in text for w in ['musée', 'museum', 'collection', 'conservatoire']):
        if 'Culture' not in cats:
            cats.append('Culture')
        cats.append('Exposition')
    elif any(w in text for w in ['peinture', 'sculpture', 'gravure', 'estampe', 'photographie', 'photo ']):
        cats.extend(['Culture', 'Exposition'])
    
    # --- CINEMA ---
    if any(w in text for w in ['cinéma', 'cinema', 'film', 'projection', 'documentaire', 'court-métrage', 'animation ']):
        if 'Culture' not in cats:
            cats.append('Culture')
        cats.append('Cinéma')
    
    # --- CONFERENCE / DEBAT ---
    if any(w in text for w in ['conférence', 'conference', 'débat', 'debat', 'colloque', 'séminaire', 'table ronde']):
        if 'Culture' not in cats:
            cats.append('Culture')
        cats.append('Conférence')
    
    # --- ATELIER ---
    if any(w in text for w in ['atelier', 'workshop', 'stage ', 'initiation', 'cours ', 'formation']):
        if 'Culture' not in cats:
            cats.append('Culture')
        cats.append('Atelier')
    
    # --- FESTIVAL ---
    if any(w in text for w in ['festival', 'fest ']):
        if 'Festival' not in cats:
            cats.append('Festival')
    
    # --- SPORT ---
    if any(w in text for w in ['natation', 'piscine', 'nage', 'plongeon', 'water-polo', 'aviron', 'voile', 'kayak', 'canoë']):
        cats.extend(['Sport', 'Sport > Aquatique'])
    elif any(w in text for w in ['ski ', 'snowboard', 'patinage', 'patinoire', 'luge', 'curling', 'hockey']):
        cats.extend(['Sport', 'Sport > Glisse'])
    elif any(w in text for w in ['course à pied', 'marathon', 'trail', 'running', 'jogging', 'marche', 'randonnée']):
        cats.extend(['Sport', 'Sport > Terrestre', 'Course à pied'])
    elif any(w in text for w in ['football', 'tennis', 'basketball', 'basket', 'volleyball', 'volley', 'handball', 'rugby', 'badminton', 'ping-pong', 'escrime', 'judo', 'karate', 'boxe', 'lutte', 'escalade', 'vélo', 'cyclisme', 'triathlon']):
        cats.extend(['Sport', 'Sport > Terrestre'])
    elif any(w in text for w in ['gymnastique', 'gym ', 'agrès', 'agres', 'tumbling', 'trampoline']):
        cats.extend(['Sport', 'Sport > Terrestre'])
    elif any(w in text for w in ['sport', 'compétition', 'championnat', 'tournoi', 'match']):
        cats.append('Sport')
    
    # --- GASTRONOMIE ---
    if any(w in text for w in ['dégustation', 'degustation', 'vin ', 'oenolog', 'gastronomie', 'culinaire', 'cuisine']):
        cats.append('Gastronomie')
    
    # --- MARCHE ---
    if any(w in text for w in ['marché', 'marche ', 'brocante', 'vide-grenier', 'artisan']):
        cats.append('Marché')
    if any(w in text for w in ['foire', 'salon']):
        cats.append('Foire')
    
    # --- CARNAVAL ---
    if 'carnaval' in text:
        cats.extend(['Festival', 'Carnaval'])
    
    # --- FAMILLE ---
    if any(w in text for w in ['enfant', 'famille', 'tout public', 'jeune public', 'tout-petit', 'bébé', 'parent']):
        cats.append('Famille > Activités')
    
    # --- LECTURE ---
    if any(w in text for w in ['lecture', 'livre', 'auteur', 'littérair', 'poésie', 'poème']):
        if 'Culture' not in cats:
            cats.append('Culture')
    
    # Default
    if not cats:
        cats = ['Culture']
    
    # Deduplicate while preserving order
    seen = set()
    result = []
    for c in cats:
        if c not in seen:
            seen.add(c)
            result.append(c)
    
    return result


def get_region(postcode, city, lat, lng):
    """Determine region from postcode, city, or coordinates."""
    pc = str(postcode or '').strip()
    city_lower = (city or '').lower()
    
    # By postcode
    if pc:
        pc_int = int(pc) if pc.isdigit() else 0
        if 1200 <= pc_int < 1300 or 'genève' in city_lower or 'geneve' in city_lower:
            return 'Genève'
        if (1000 <= pc_int < 1200 or 1300 <= pc_int < 1600 or 1800 <= pc_int < 1870) and 'valais' not in city_lower:
            return 'Vaud'
        if 1870 <= pc_int < 2000 or 3900 <= pc_int < 4000 or 1920 <= pc_int <= 1969:
            return 'Valais'
    
    # By coordinates
    if lat and lng:
        lat, lng = float(lat), float(lng)
        if 46.15 < lat < 46.28 and 6.05 < lng < 6.32:
            return 'Genève'
        if 46.35 < lat < 46.65 and 6.1 < lng < 7.0:
            return 'Vaud'
        if 46.0 < lat < 46.4 and 6.8 < lng < 8.2:
            return 'Valais'
    
    # By city name
    geneva_cities = ['genève', 'geneve', 'carouge', 'lancy', 'meyrin', 'vernier', 'onex', 'thônex', 'plan-les-ouates', 'bernex', 'veyrier', 'chêne-bougeries', 'chêne-bourg', 'grand-saconnex', 'pregny-chambésy', 'cologny', 'collonge-bellerive']
    if any(c in city_lower for c in geneva_cities):
        return 'Genève'
    
    vaud_cities = ['lausanne', 'morges', 'nyon', 'montreux', 'vevey', 'aigle', 'yverdon', 'renens', 'ecublens', 'pully', 'prilly']
    if any(c in city_lower for c in vaud_cities):
        return 'Vaud'
    
    valais_cities = ['sion', 'sierre', 'martigny', 'monthey', 'visp', 'brig', 'fully', 'saxon', 'riddes', 'verbier']
    if any(c in city_lower for c in valais_cities):
        return 'Valais'
    
    return 'Autre CH'


def fetch_opendata_events():
    """Fetch Swiss events from OpenDataSoft API, March-December 2026."""
    all_events = []
    offset = 0
    limit = 100
    
    while True:
        params = {
            'where': 'location_countrycode="CH" AND firstdate_begin>="2026-02-15" AND firstdate_begin<="2026-12-31"',
            'limit': limit,
            'offset': offset,
            'select': 'uid,title_fr,description_fr,longdescription_fr,location_name,location_address,location_city,location_postalcode,location_coordinates,firstdate_begin,firstdate_end,lastdate_begin,lastdate_end,originagenda_title,canonicalurl,keywords_fr,conditions_fr'
        }
        
        print(f"  Fetching events {offset}-{offset+limit}...")
        r = requests.get(OPENDATA_URL, params=params, timeout=30)
        data = r.json()
        
        results = data.get('results', [])
        total = data.get('total_count', 0)
        
        all_events.extend(results)
        
        if len(results) < limit or offset + limit >= total:
            break
        
        offset += limit
        time.sleep(0.5)  # Respectful delay
    
    print(f"  Total fetched: {len(all_events)} events (total available: {total})")
    return all_events


def fetch_existing_events():
    """Fetch existing events from our API for duplicate detection."""
    r = requests.get(f'{API_URL}/api/events', timeout=30)
    data = r.json()
    events = data if isinstance(data, list) else data.get('events', [])
    return events


def is_duplicate(new_title, new_source, existing_events):
    """Check if event already exists by source URL or title similarity."""
    new_title_lower = new_title.lower().strip()
    new_words = set(re.findall(r'\w{4,}', new_title_lower))
    
    for e in existing_events:
        # Check source URL
        existing_source = (e.get('source_url') or '').strip()
        if new_source and existing_source and new_source.strip() == existing_source:
            return True
        
        # Check title similarity (3+ matching words of 4+ chars)
        existing_title = (e.get('title') or '').lower().strip()
        existing_words = set(re.findall(r'\w{4,}', existing_title))
        common = new_words & existing_words
        if len(common) >= 3:
            return True
    
    return False


def clean_address(location_name, location_address, location_city, location_postcode):
    """Build a clean, complete address."""
    parts = []
    
    if location_name:
        parts.append(location_name.strip())
    
    if location_address:
        addr = location_address.strip()
        # Remove city/postcode from address if already included
        if location_city and location_city.lower() in addr.lower():
            addr = addr[:addr.lower().index(location_city.lower())].strip().rstrip(',')
        if location_postcode and location_postcode in addr:
            addr = addr.replace(location_postcode, '').strip()
        if addr and addr not in (location_name or ''):
            parts.append(addr)
    
    # Add postcode + city
    if location_postcode and location_city:
        parts.append(f"{location_postcode} {location_city}")
    elif location_city:
        parts.append(location_city)
    
    return ', '.join(parts) if parts else location_city or 'Suisse'


def main():
    print("=" * 60)
    print("IMPORT OPEN DATA - EVENEMENTS SUISSES 2026")
    print("Source: OpenDataSoft / OpenAgenda")
    print("Licence: Licence Ouverte v1.0 (CC-BY)")
    print("=" * 60)
    
    # 1. Fetch Open Data events
    print("\n[1/5] Recuperation des evenements Open Data...")
    od_events = fetch_opendata_events()
    
    # 2. Filter by region
    print("\n[2/5] Filtrage par region (Geneve, Vaud, Valais)...")
    regional_events = []
    region_counts = {'Genève': 0, 'Vaud': 0, 'Valais': 0, 'Autre CH': 0}
    
    for e in od_events:
        coords = e.get('location_coordinates') or {}
        lat = coords.get('lat')
        lng = coords.get('lon')
        city = e.get('location_city', '')
        postcode = e.get('location_postalcode', '')
        
        region = get_region(postcode, city, lat, lng)
        region_counts[region] = region_counts.get(region, 0) + 1
        
        if region in ('Genève', 'Vaud', 'Valais'):
            e['_region'] = region
            e['_lat'] = lat
            e['_lng'] = lng
            regional_events.append(e)
    
    print(f"  Regional distribution:")
    for r, c in sorted(region_counts.items(), key=lambda x: -x[1]):
        print(f"    {r}: {c}")
    print(f"  Selected for import: {len(regional_events)}")
    
    # 3. Check duplicates
    print("\n[3/5] Detection des doublons...")
    existing = fetch_existing_events()
    print(f"  Existing events in DB: {len(existing)}")
    
    new_events = []
    duplicates = 0
    skipped_no_title = 0
    skipped_no_coords = 0
    skipped_no_desc = 0
    
    for e in regional_events:
        title = e.get('title_fr') or ''
        if not title.strip():
            skipped_no_title += 1
            continue
        
        if not e.get('_lat') or not e.get('_lng'):
            skipped_no_coords += 1
            continue
        
        source_url = e.get('canonicalurl', '')
        if is_duplicate(title, source_url, existing):
            duplicates += 1
            continue
        
        # Also add to existing for intra-batch duplicate detection
        existing.append({'title': title, 'source_url': source_url})
        new_events.append(e)
    
    print(f"  Duplicates found: {duplicates}")
    print(f"  Skipped (no title): {skipped_no_title}")
    print(f"  Skipped (no coords): {skipped_no_coords}")
    print(f"  New events to import: {len(new_events)}")
    
    if not new_events:
        print("\nAucun nouvel evenement a importer.")
        return
    
    # 4. Prepare events for import
    print(f"\n[4/5] Preparation de {len(new_events)} evenements...")
    batch_events = []
    
    for e in new_events:
        title = e['title_fr'].strip()
        desc = (e.get('description_fr') or e.get('longdescription_fr') or title).strip()
        # Clean HTML from description
        desc = re.sub(r'<[^>]+>', ' ', desc)
        desc = re.sub(r'\s+', ' ', desc).strip()
        if len(desc) > 500:
            desc = desc[:497] + '...'
        if not desc or desc == title:
            desc = f"Evenement a {e.get('location_city', 'Geneve')}"
        
        keywords = e.get('keywords_fr') or ''
        location_name = e.get('location_name', '')
        cats = assign_categories(title, desc, keywords, location_name)
        
        # Parse dates
        first_begin = e.get('firstdate_begin', '')
        last_end = e.get('lastdate_end', '')
        
        date_str = first_begin[:10] if first_begin else '2026-03-01'
        end_date_str = last_end[:10] if last_end else date_str
        
        # Parse time
        time_str = '10:00:00'
        if first_begin and 'T' in first_begin:
            t = first_begin.split('T')[1][:8]
            # Convert from UTC to CET (+1h in winter, +2h in summer)
            try:
                h = int(t[:2]) + 1  # Rough CET offset
                if h >= 24:
                    h -= 24
                time_str = f"{h:02d}{t[2:]}"
            except:
                time_str = t
        
        # Build address
        address = clean_address(
            location_name,
            e.get('location_address', ''),
            e.get('location_city', ''),
            e.get('location_postalcode', '')
        )
        
        source_url = e.get('canonicalurl', '')
        agenda_title = e.get('originagenda_title', 'OpenAgenda')
        
        event = {
            'title': title,
            'description': desc,
            'location': address,
            'latitude': float(e['_lat']),
            'longitude': float(e['_lng']),
            'date': date_str,
            'time': time_str,
            'end_date': end_date_str,
            'categories': cats,
            'source_url': source_url,
            'organizer_name': agenda_title,
            'organizer_email': 'opendata@mapevent.world'
        }
        
        batch_events.append(event)
    
    # Print sample
    print(f"\n  Sample events:")
    for ev in batch_events[:5]:
        print(f"    - {ev['title'][:60]} | {ev['date']} | {ev['location'][:50]} | {ev['categories']}")
    if len(batch_events) > 5:
        print(f"    ... and {len(batch_events) - 5} more")
    
    # Category distribution
    cat_dist = {}
    for ev in batch_events:
        for c in ev['categories']:
            cat_dist[c] = cat_dist.get(c, 0) + 1
    print(f"\n  Category distribution:")
    for c, n in sorted(cat_dist.items(), key=lambda x: -x[1])[:15]:
        print(f"    {c}: {n}")
    
    # Region distribution
    region_dist = {'Genève': 0, 'Vaud': 0, 'Valais': 0}
    for e, od in zip(batch_events, new_events):
        r = od.get('_region', 'Autre')
        region_dist[r] = region_dist.get(r, 0) + 1
    print(f"\n  Region distribution:")
    for r, n in sorted(region_dist.items(), key=lambda x: -x[1]):
        print(f"    {r}: {n}")
    
    # 5. Import in batches
    print(f"\n[5/5] Import de {len(batch_events)} evenements en batches de 50...")
    
    total_created = 0
    total_skipped = 0
    total_failed = 0
    
    for i in range(0, len(batch_events), 50):
        batch = batch_events[i:i+50]
        print(f"\n  Batch {i//50 + 1}: {len(batch)} events...")
        
        payload = {
            'events': batch,
            'send_emails': False
        }
        
        try:
            r = requests.post(
                f'{API_URL}/api/events/scraped/batch',
                json=payload,
                timeout=60
            )
            
            if r.status_code in (200, 201):
                result = r.json()
                created = result.get('created', 0)
                skipped = result.get('skipped', 0)
                failed = result.get('failed', 0)
                total_created += created
                total_skipped += skipped
                total_failed += failed
                print(f"    Created: {created}, Skipped: {skipped}, Failed: {failed}")
            else:
                print(f"    ERROR {r.status_code}: {r.text[:200]}")
                total_failed += len(batch)
        except Exception as ex:
            print(f"    EXCEPTION: {ex}")
            total_failed += len(batch)
        
        time.sleep(2)  # Delay between batches
    
    # Final count
    print("\n" + "=" * 60)
    print("RESULTAT FINAL")
    print("=" * 60)
    print(f"  Created: {total_created}")
    print(f"  Skipped (API duplicates): {total_skipped}")
    print(f"  Failed: {total_failed}")
    
    # Verify
    time.sleep(3)
    r = requests.get(f'{API_URL}/api/events', timeout=30)
    data = r.json()
    events = data if isinstance(data, list) else data.get('events', [])
    print(f"\n  TOTAL EVENTS IN DB: {len(events)}")
    
    # Final region count
    final_regions = {'Genève': 0, 'Vaud': 0, 'Valais': 0, 'Haute-Savoie': 0, 'Autre': 0}
    for e in events:
        loc = (e.get('location','') or '').lower()
        lat = float(e.get('latitude', 0) or 0)
        lng = float(e.get('longitude', 0) or 0)
        if '74000' in loc or '74200' in loc or 'annecy' in loc or 'thonon' in loc or (45.8 < lat < 46.0 and 6.0 < lng < 6.5):
            final_regions['Haute-Savoie'] += 1
        elif 'geneve' in loc or 'genève' in loc or '1200' in loc or '1201' in loc or '1202' in loc or '1203' in loc or '1204' in loc or '1205' in loc or '1206' in loc or (46.15 < lat < 46.28 and 6.05 < lng < 6.2):
            final_regions['Genève'] += 1
        elif any(c in loc for c in ['valais','sion','sierre','martigny','monthey','1920','1950']) or (46.0 < lat < 46.35 and 6.8 < lng < 8.1):
            final_regions['Valais'] += 1
        elif any(c in loc for c in ['vaud','lausanne','morges','nyon','montreux','vevey','1000 ','1003']) or (46.35 < lat < 46.6 and 6.1 < lng < 7.0):
            final_regions['Vaud'] += 1
        else:
            final_regions['Autre'] += 1
    
    print(f"\n  Final regional distribution:")
    for r, n in sorted(final_regions.items(), key=lambda x: -x[1]):
        print(f"    {r}: {n}")


if __name__ == '__main__':
    main()
