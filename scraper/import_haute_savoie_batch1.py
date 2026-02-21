"""
Import Haute-Savoie (France) and Martigny (Switzerland) events batch 1
- Geocodes addresses using Nominatim
- Checks for duplicates before importing
- Sends batch import via API
"""
import requests
import sys
import io
import json
import time
import re

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'

# Events to import
EVENTS_DATA = [
    {
        "title": "Bombino - Blues Touareg au Brise Glace",
        "description": "Figure majeure du blues touareg, le musicien nigérien Bombino revient au Brise Glace d'Annecy. Sa musique mêle traditions sahariennes, rythmes africains et influences rock, racontant la vie du désert et les luttes du peuple touareg.",
        "location": "Le Brise Glace, 54 bis Rue des Marquisats, 74000 Annecy",
        "date": "2026-03-31",
        "time": "20:30:00",
        "end_date": "2026-03-31",
        "categories": ["Musique", "Concert", "Festival"],
        "source_url": "https://www.lac-in-blue.com/",
        "organizer_name": "Lac in Blue",
        "organizer_email": "contact@lac-in-blue.com",
        "country": "fr"
    },
    {
        "title": "Nicolas Folmer Sextet - Hommage à Miles Davis",
        "description": "Un hommage vibrant au Prince des ténèbres par le trompettiste Nicolas Folmer, figure incontournable du jazz français. Concert au Château d'Annecy dans le cadre du festival Lac in Blue.",
        "location": "Château d'Annecy, Place du Château, 74000 Annecy",
        "date": "2026-04-01",
        "time": "20:30:00",
        "end_date": "2026-04-01",
        "categories": ["Musique", "Concert", "Musique > Jazz", "Festival"],
        "source_url": "https://www.lac-in-blue.com/",
        "organizer_name": "Lac in Blue",
        "organizer_email": "contact@lac-in-blue.com",
        "country": "fr"
    },
    {
        "title": "La Nuit du Jazz - Congo Square",
        "description": "Voyage à travers 100 ans d'histoire du jazz au travers d'arrangements d'œuvres emblématiques. Jean Gobinet accompagné par le Large Ensemble de la HEMU de Lausanne. Première partie par les élèves du pôle jazz du conservatoire d'Annecy.",
        "location": "Salle Pierre Lamy, 12 Rue de la République, 74000 Annecy",
        "date": "2026-04-02",
        "time": "19:00:00",
        "end_date": "2026-04-02",
        "categories": ["Musique", "Concert", "Musique > Jazz", "Festival"],
        "source_url": "https://www.lac-in-blue.com/",
        "organizer_name": "Lac in Blue",
        "organizer_email": "contact@lac-in-blue.com",
        "country": "fr"
    },
    {
        "title": "Joran Cariou Trio - Lac in Blue",
        "description": "Entre écriture raffinée et spontanéité créative, le Joran Cariou Trio dévoile un répertoire mêlant nouvelles créations et pièces de l'album The Path Up. Un métissage de rythmes d'Afrique, d'Andalousie et de jazz traditionnel.",
        "location": "Conservatoire à Rayonnement Régional, 10 Rue Jean-Jacques Rousseau, 74000 Annecy",
        "date": "2026-04-03",
        "time": "12:30:00",
        "end_date": "2026-04-03",
        "categories": ["Musique", "Concert", "Musique > Jazz", "Festival"],
        "source_url": "https://www.lac-in-blue.com/",
        "organizer_name": "Lac in Blue",
        "organizer_email": "contact@lac-in-blue.com",
        "country": "fr"
    },
    {
        "title": "Jermaine Landsberger Trio feat. Stéphane Belmondo",
        "description": "Pianiste d'exception à l'avant-garde de la scène manouche européenne, Jermaine Landsberger s'associe au trompettiste Stéphane Belmondo pour un concert au Château d'Annecy. Un dialogue entre jazz manouche et trompette moderne.",
        "location": "Château d'Annecy, Place du Château, 74000 Annecy",
        "date": "2026-04-03",
        "time": "20:30:00",
        "end_date": "2026-04-03",
        "categories": ["Musique", "Concert", "Musique > Jazz", "Festival"],
        "source_url": "https://www.lac-in-blue.com/",
        "organizer_name": "Lac in Blue",
        "organizer_email": "contact@lac-in-blue.com",
        "country": "fr"
    },
    {
        "title": "Mohs - Apéro-Concert Jazz aux Carrés",
        "description": "Le talentueux quartet suisse Mohs présente son troisième opus Baïne, mêlant instruments acoustiques et effets électroniques. Des paysages sonores finement ciselés aux multiples références stylistiques, au pied des Alpes.",
        "location": "Les Carrés, Avenue des Carrés, 74940 Annecy-le-Vieux",
        "date": "2026-04-04",
        "time": "19:00:00",
        "end_date": "2026-04-04",
        "categories": ["Musique", "Concert", "Musique > Jazz", "Festival"],
        "source_url": "https://www.lac-in-blue.com/",
        "organizer_name": "Lac in Blue",
        "organizer_email": "contact@lac-in-blue.com",
        "country": "fr"
    },
    {
        "title": "May B - Maguy Marin à Bonlieu Annecy",
        "description": "Pièce emblématique de Maguy Marin, May B est un spectacle de danse contemporaine devenu un classique incontournable. Créé en 1981, il continue de fasciner par sa puissance et son universalité. Au Bonlieu Scène nationale d'Annecy.",
        "location": "Bonlieu Scène nationale, 1 Rue Jean Jaurès, 74000 Annecy",
        "date": "2026-03-05",
        "time": "20:00:00",
        "end_date": "2026-03-07",
        "categories": ["Spectacle", "Danse", "Culture"],
        "source_url": "https://bonlieu-annecy.com/la-saison",
        "organizer_name": "Bonlieu Scène nationale",
        "organizer_email": "contact@bonlieu-annecy.com",
        "country": "fr"
    },
    {
        "title": "Le Pas du monde - Collectif XY au Bonlieu",
        "description": "Spectacle de cirque acrobatique par le Collectif XY, compagnie emblématique du cirque contemporain français. Un spectacle à voir en famille, mêlant acrobatie, portés et émotion. Au Bonlieu Scène nationale d'Annecy.",
        "location": "Bonlieu Scène nationale, 1 Rue Jean Jaurès, 74000 Annecy",
        "date": "2026-03-10",
        "time": "20:00:00",
        "end_date": "2026-03-14",
        "categories": ["Spectacle", "Cirque", "Culture", "Famille > Activités"],
        "source_url": "https://bonlieu-annecy.com/la-saison",
        "organizer_name": "Bonlieu Scène nationale",
        "organizer_email": "contact@bonlieu-annecy.com",
        "country": "fr"
    },
    {
        "title": "Les Médiévales de Ripaille - Thonon-les-Bains",
        "description": "Le château de Ripaille remonte le temps au Moyen Âge avec trois campements authentiques, un marché artisanal de quarante artisans, des spectacles de combat, fauconnerie, jonglerie et acrobatie. Première édition de cet événement médiéval au bord du lac Léman.",
        "location": "Château de Ripaille, 83 Avenue de Ripaille, 74200 Thonon-les-Bains",
        "date": "2026-05-16",
        "time": "08:00:00",
        "end_date": "2026-05-17",
        "categories": ["Festival", "Culture", "Marché", "Spectacle", "Famille > Activités"],
        "source_url": "https://www.thononlesbains.com/fete-et-manifestation/les-medievales-de-ripaille-thonon-les-bains/",
        "organizer_name": "Château de Ripaille",
        "organizer_email": "info@ripaille.fr",
        "country": "fr"
    },
    {
        "title": "Festival International du Film d'Animation d'Annecy 2026",
        "description": "Le plus grand festival mondial dédié au cinéma d'animation revient pour sa nouvelle édition avec le thème Les Grands Frissons. Ouverture de la Cité internationale du cinéma d'animation, un équipement unique en France. Projections, compétitions, masterclasses et marché du film.",
        "location": "Centre de Congrès Impérial, 1 Avenue d'Albigny, 74000 Annecy",
        "date": "2026-06-21",
        "time": "09:00:00",
        "end_date": "2026-06-27",
        "categories": ["Festival", "Culture", "Cinéma"],
        "source_url": "https://www.annecyfestival.com/",
        "organizer_name": "CITIA",
        "organizer_email": "info@annecy.org",
        "country": "fr"
    },
    {
        "title": "De Manet à Kelly - L'art de l'empreinte à la Fondation Gianadda",
        "description": "Exposition rassemblant 178 chefs-d'œuvre de la gravure des XIXe et XXe siècles provenant de la Bibliothèque de l'INHA de Paris. Des œuvres de Manet, Kelly, Goya, Munch et Kollwitz présentées en séquences thématiques à la Fondation Pierre Gianadda de Martigny.",
        "location": "Fondation Pierre Gianadda, Rue du Forum 59, 1920 Martigny",
        "date": "2025-12-12",
        "time": "10:00:00",
        "end_date": "2026-06-14",
        "categories": ["Culture", "Exposition", "Art"],
        "source_url": "https://www.gianadda.ch/expositions/expositions_actuelles/",
        "organizer_name": "Fondation Pierre Gianadda",
        "organizer_email": "info@gianadda.ch",
        "country": "ch"
    }
]

geocode_cache = {}


def geocode(address, country_code=None):
    """Geocode address using Nominatim API with fallback strategies."""
    if address in geocode_cache:
        return geocode_cache[address]
    
    # Try multiple address formats
    address_variants = [address]
    
    # Extract street number and name if present
    street_match = re.search(r'(\d+(?:\s+bis)?)\s+([^,]+),\s*(\d{5})\s+([^,]+)', address)
    if street_match:
        num, street, postal, city = street_match.groups()
        # Try: "Street Name, Postal Code City"
        address_variants.append(f"{street.strip()}, {postal} {city.strip()}")
        # Try: "Street Name Number, Postal Code City"
        address_variants.append(f"{street.strip()} {num}, {postal} {city.strip()}")
    
    # Try without venue name (just street address)
    venue_match = re.match(r'^[^,]+,\s*(.+)', address)
    if venue_match:
        address_variants.append(venue_match.group(1))
    
    for variant in address_variants:
        time.sleep(1.5)  # Respect Nominatim rate limit
        
        params = {
            'q': variant,
            'format': 'json',
            'limit': 1,
        }
        
        if country_code:
            params['countrycodes'] = country_code
        
        try:
            r = requests.get('https://nominatim.openstreetmap.org/search',
                            params=params,
                            headers={'User-Agent': 'MapEventAI-Bot/1.0'},
                            timeout=10)
            
            data = r.json()
            if data:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                result = (lat, lon)
                geocode_cache[address] = result
                geocode_cache[variant] = result  # Cache variant too
                print(f"  ✓ Geocoded: {address[:60]} → ({lat:.6f}, {lon:.6f})")
                return result
        except Exception as e:
            continue  # Try next variant
    
    print(f"  ✗ No results for: {address[:60]}")
    geocode_cache[address] = (None, None)
    return (None, None)


def check_duplicates(existing_events, new_event):
    """Check if event is a duplicate based on title and source_url."""
    title_key = new_event['title'].lower().strip()[:50]
    source_url = new_event.get('source_url', '')
    
    for existing in existing_events:
        existing_title = existing.get('title', '').lower().strip()[:50]
        existing_url = existing.get('source_url', '')
        
        # Check title match
        if title_key == existing_title:
            return True, "title"
        
        # Check URL match
        if source_url and existing_url and source_url == existing_url:
            return True, "url"
    
    return False, None


def main():
    print("=" * 70)
    print("Import Haute-Savoie & Martigny Events - Batch 1")
    print("=" * 70)
    print(f"\nTotal events to process: {len(EVENTS_DATA)}\n")
    
    # Step 1: Geocode all addresses
    print("Step 1: Geocoding addresses...")
    print("-" * 70)
    events_with_coords = []
    
    for i, event in enumerate(EVENTS_DATA, 1):
        print(f"\n[{i}/{len(EVENTS_DATA)}] {event['title'][:50]}")
        location = event['location']
        country = event.get('country', 'fr')
        
        lat, lon = geocode(location, country_code=country)
        
        if lat is None or lon is None:
            print(f"  ⚠️ WARNING: Could not geocode address, skipping event")
            continue
        
        event['latitude'] = lat
        event['longitude'] = lon
        events_with_coords.append(event)
    
    print(f"\n✓ Successfully geocoded {len(events_with_coords)}/{len(EVENTS_DATA)} events\n")
    
    if not events_with_coords:
        print("ERROR: No events could be geocoded. Aborting.")
        sys.exit(1)
    
    # Step 2: Check for duplicates
    print("Step 2: Checking for duplicates...")
    print("-" * 70)
    
    try:
        r = requests.get(f'{API_URL}/api/events', timeout=30)
        data = r.json()
        existing_events = data if isinstance(data, list) else data.get('events', [])
        print(f"Found {len(existing_events)} existing events in database\n")
    except Exception as e:
        print(f"ERROR: Could not fetch existing events: {e}")
        sys.exit(1)
    
    events_to_import = []
    duplicates_found = []
    
    for event in events_with_coords:
        is_dup, reason = check_duplicates(existing_events, event)
        if is_dup:
            duplicates_found.append((event['title'], reason))
            print(f"  ✗ DUPLICATE ({reason}): {event['title'][:60]}")
        else:
            events_to_import.append(event)
    
    print(f"\n✓ Found {len(duplicates_found)} duplicates")
    print(f"✓ {len(events_to_import)} unique events ready to import\n")
    
    if not events_to_import:
        print("No new events to import. All events are duplicates.")
        sys.exit(0)
    
    # Step 3: Format events for API
    print("Step 3: Formatting events for API...")
    print("-" * 70)
    
    formatted_events = []
    for event in events_to_import:
        formatted_event = {
            'title': event['title'],
            'description': event['description'],
            'location': event['location'],
            'latitude': event['latitude'],
            'longitude': event['longitude'],
            'date': event['date'],
            'time': event['time'],
            'end_date': event['end_date'],
            'categories': event['categories'],
            'source_url': event['source_url'],
            'organizer_email': event['organizer_email'],
            'organizer_name': event['organizer_name'],
            'validation_status': 'auto_validated'
        }
        formatted_events.append(formatted_event)
        print(f"  ✓ Formatted: {event['title'][:50]}")
    
    # Step 4: Send batch import
    print(f"\nStep 4: Sending batch import ({len(formatted_events)} events)...")
    print("-" * 70)
    
    try:
        payload = {
            'events': formatted_events,
            'send_emails': False
        }
        
        r = requests.post(f'{API_URL}/api/events/scraped/batch',
                         json=payload,
                         headers={'Content-Type': 'application/json'},
                         timeout=120)
        
        if r.status_code != 200:
            print(f"ERROR: HTTP {r.status_code}")
            print(f"Response: {r.text[:200]}")
            sys.exit(1)
        
        result = r.json()
        created = result.get('results', result).get('created', result.get('created', 0))
        skipped = result.get('results', result).get('skipped', result.get('skipped', 0))
        failed = result.get('results', result).get('failed', result.get('failed', 0))
        
        print(f"\n✓ Batch import completed:")
        print(f"  - Created: {created}")
        print(f"  - Skipped: {skipped}")
        print(f"  - Failed: {failed}")
        
    except Exception as e:
        print(f"ERROR during batch import: {e}")
        sys.exit(1)
    
    # Step 5: Final statistics
    print("\n" + "=" * 70)
    print("Final Statistics")
    print("=" * 70)
    
    try:
        r = requests.get(f'{API_URL}/api/events', timeout=30)
        data = r.json()
        final_events = data if isinstance(data, list) else data.get('events', [])
        
        print(f"\nTotal events in database: {len(final_events)}")
        print(f"Events imported in this batch: {len(events_to_import)}")
        
        # Count by region
        haute_savoie_count = 0
        swiss_count = 0
        
        for event in final_events:
            location = event.get('location', '').lower()
            if 'annecy' in location or 'thonon' in location or 'haute-savoie' in location:
                haute_savoie_count += 1
            elif 'martigny' in location or 'suisse' in location or 'switzerland' in location:
                swiss_count += 1
        
        print(f"\nDistribution by region:")
        print(f"  - Haute-Savoie (France): {haute_savoie_count}")
        print(f"  - Switzerland: {swiss_count}")
        print(f"  - Other: {len(final_events) - haute_savoie_count - swiss_count}")
        
    except Exception as e:
        print(f"Warning: Could not fetch final statistics: {e}")


if __name__ == '__main__':
    main()
