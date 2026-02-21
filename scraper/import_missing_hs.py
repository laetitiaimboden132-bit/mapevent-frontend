"""
Import missing Haute-Savoie events with duplicate detection
"""
import requests
import sys
import io
import re
from datetime import datetime

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace', line_buffering=True)

API_URL = 'https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws'

# Events to import
EVENTS_TO_IMPORT = [
    {
        "title": "Bombino - Blues Touareg au Brise Glace",
        "description": "Figure majeure du blues touareg, le musicien nigerien Bombino revient au Brise Glace d'Annecy. Sa musique mele traditions sahariennes, rythmes africains et influences rock.",
        "location": "Le Brise Glace, 54 bis Rue des Marquisats, 74000 Annecy",
        "latitude": 45.8917,
        "longitude": 6.1335,
        "date": "2026-03-31",
        "end_date": "2026-03-31",
        "time": "20:30:00",
        "categories": ["Musique", "Concert", "Festival"],
        "source_url": "https://www.lac-in-blue.com/",
        "organizer_name": "Lac in Blue",
        "organizer_email": "contact@lac-in-blue.com"
    },
    {
        "title": "La Nuit du Jazz - Congo Square",
        "description": "Voyage a travers 100 ans d'histoire du jazz avec Jean Gobinet et le Large Ensemble de la HEMU de Lausanne. Premiere partie par les eleves du pole jazz du conservatoire d'Annecy.",
        "location": "Salle Pierre Lamy, 12 Rue de la Republique, 74000 Annecy",
        "latitude": 45.8989,
        "longitude": 6.1271,
        "date": "2026-04-02",
        "end_date": "2026-04-02",
        "time": "19:00:00",
        "categories": ["Musique", "Concert", "Musique > Jazz", "Festival"],
        "source_url": "https://www.lac-in-blue.com/",
        "organizer_name": "Lac in Blue",
        "organizer_email": "contact@lac-in-blue.com"
    },
    {
        "title": "Joran Cariou Trio - Lac in Blue",
        "description": "Entre ecriture raffinee et spontaneite creative, le Joran Cariou Trio devoile un repertoire melant nouvelles creations et rythmes d'Afrique, d'Andalousie et de jazz traditionnel.",
        "location": "Conservatoire, 10 Rue Jean-Jacques Rousseau, 74000 Annecy",
        "latitude": 45.9020,
        "longitude": 6.1240,
        "date": "2026-04-03",
        "end_date": "2026-04-03",
        "time": "12:30:00",
        "categories": ["Musique", "Concert", "Musique > Jazz", "Festival"],
        "source_url": "https://www.lac-in-blue.com/",
        "organizer_name": "Lac in Blue",
        "organizer_email": "contact@lac-in-blue.com"
    },
    {
        "title": "Jermaine Landsberger Trio feat. Stephane Belmondo",
        "description": "Pianiste d'exception a l'avant-garde de la scene manouche europeenne, Jermaine Landsberger s'associe au trompettiste Stephane Belmondo pour un concert au Chateau d'Annecy.",
        "location": "Chateau d'Annecy, Place du Chateau, 74000 Annecy",
        "latitude": 45.8988,
        "longitude": 6.1242,
        "date": "2026-04-03",
        "end_date": "2026-04-03",
        "time": "20:30:00",
        "categories": ["Musique", "Concert", "Musique > Jazz", "Festival"],
        "source_url": "https://www.lac-in-blue.com/",
        "organizer_name": "Lac in Blue",
        "organizer_email": "contact@lac-in-blue.com"
    },
    {
        "title": "Mohs - Apero-Concert Jazz aux Carres",
        "description": "Le talentueux quartet suisse Mohs presente son troisieme opus Baine, melant instruments acoustiques et effets electroniques. Des paysages sonores aux multiples references stylistiques.",
        "location": "Les Carres, Avenue des Carres, 74940 Annecy-le-Vieux",
        "latitude": 45.9233,
        "longitude": 6.1403,
        "date": "2026-04-04",
        "end_date": "2026-04-04",
        "time": "19:00:00",
        "categories": ["Musique", "Concert", "Musique > Jazz", "Festival"],
        "source_url": "https://www.lac-in-blue.com/",
        "organizer_name": "Lac in Blue",
        "organizer_email": "contact@lac-in-blue.com"
    },
    {
        "title": "Le Pas du monde - Collectif XY au Bonlieu",
        "description": "Spectacle de cirque acrobatique par le Collectif XY, compagnie emblematique du cirque contemporain francais. Un spectacle a voir en famille, melant acrobatie, portes et emotion.",
        "location": "Bonlieu Scene nationale, 1 Rue Jean Jaures, 74000 Annecy",
        "latitude": 45.8995,
        "longitude": 6.1299,
        "date": "2026-03-10",
        "end_date": "2026-03-14",
        "time": "20:00:00",
        "categories": ["Spectacle", "Cirque", "Culture", "Famille > Activites"],
        "source_url": "https://bonlieu-annecy.com/la-saison",
        "organizer_name": "Bonlieu Scene nationale",
        "organizer_email": "contact@bonlieu-annecy.com"
    },
    {
        "title": "De Manet a Kelly - L'art de l'empreinte a la Fondation Gianadda",
        "description": "Exposition rassemblant 178 chefs-d'oeuvre de la gravure des XIXe et XXe siecles provenant de la Bibliotheque de l'INHA de Paris. Oeuvres de Manet, Kelly, Goya, Munch et Kollwitz.",
        "location": "Fondation Pierre Gianadda, Rue du Forum 59, 1920 Martigny",
        "latitude": 46.0988,
        "longitude": 7.0729,
        "date": "2025-12-12",
        "end_date": "2026-06-14",
        "time": "10:00:00",
        "categories": ["Culture", "Exposition"],
        "source_url": "https://www.gianadda.ch/expositions/expositions_actuelles/",
        "organizer_name": "Fondation Pierre Gianadda",
        "organizer_email": "info@gianadda.ch"
    }
]


def extract_keywords(title):
    """Extract first 3 significant words from title (ignoring articles, prepositions)"""
    # Remove special characters and split
    words = re.sub(r'[^\w\s]', ' ', title.lower())
    words = words.split()
    
    # Filter out common stop words
    stop_words = {'le', 'la', 'les', 'un', 'une', 'des', 'de', 'du', 'et', 'ou', 'au', 'aux', 'a', 'en', 'pour', 'avec', 'sur', 'dans', 'par'}
    significant_words = [w for w in words if w not in stop_words and len(w) > 2]
    
    # Return first 3 significant words
    return tuple(significant_words[:3])


def main():
    print("=" * 60)
    print("Import missing Haute-Savoie events")
    print("=" * 60)
    
    # 1. Fetch all existing events
    print("\n1. Fetching existing events from API...")
    try:
        response = requests.get(f'{API_URL}/api/events', timeout=30)
        if response.status_code != 200:
            print(f"ERROR: Failed to fetch events (HTTP {response.status_code})")
            sys.exit(1)
        
        data = response.json()
        existing_events = data if isinstance(data, list) else data.get('events', [])
        print(f"   Found {len(existing_events)} existing events")
    except Exception as e:
        print(f"ERROR: Failed to fetch events: {e}")
        sys.exit(1)
    
    # 2. Build keyword index from existing events
    print("\n2. Building duplicate detection index...")
    existing_keywords = set()
    for event in existing_events:
        title = event.get('title', '')
        if title:
            keywords = extract_keywords(title)
            if keywords:
                existing_keywords.add(keywords)
    print(f"   Indexed {len(existing_keywords)} unique keyword sets")
    
    # 3. Check for duplicates
    print("\n3. Checking for duplicates...")
    events_to_import = []
    skipped_duplicates = []
    
    for event in EVENTS_TO_IMPORT:
        title = event['title']
        keywords = extract_keywords(title)
        
        if keywords in existing_keywords:
            print(f"   SKIP (duplicate): {title[:50]}...")
            skipped_duplicates.append(event)
        else:
            print(f"   OK: {title[:50]}...")
            events_to_import.append(event)
    
    print(f"\n   Summary: {len(events_to_import)} to import, {len(skipped_duplicates)} duplicates skipped")
    
    if not events_to_import:
        print("\nNo new events to import!")
        sys.exit(0)
    
    # 4. Prepare batch payload
    print("\n4. Preparing batch payload...")
    batch_payload = []
    for event in events_to_import:
        batch_payload.append({
            'title': event['title'],
            'description': event['description'],
            'date': event['date'],
            'end_date': event.get('end_date', event['date']),
            'location': event['location'],
            'latitude': event['latitude'],
            'longitude': event['longitude'],
            'time': event.get('time', '00:00:00'),
            'categories': event['categories'],
            'source_url': event['source_url'],
            'organizer_name': event.get('organizer_name', ''),
            'organizer_email': event.get('organizer_email', ''),
            'validation_status': 'auto_validated'
        })
    
    # 5. Send batch request
    print(f"\n5. Sending batch request ({len(batch_payload)} events)...")
    try:
        response = requests.post(
            f'{API_URL}/api/events/scraped/batch',
            json={'events': batch_payload, 'send_emails': False},
            headers={'Content-Type': 'application/json'},
            timeout=120
        )
        
        if response.status_code != 200:
            print(f"ERROR: HTTP {response.status_code}")
            print(f"Response: {response.text[:500]}")
            sys.exit(1)
        
        result = response.json()
        
        # Handle different response formats
        created = result.get('created', 0)
        skipped = result.get('skipped', 0)
        failed = result.get('failed', 0)
        
        # Check nested results if present
        if 'results' in result:
            created = result['results'].get('created', created)
            skipped = result['results'].get('skipped', skipped)
            failed = result['results'].get('failed', failed)
        
        print(f"\n{'=' * 60}")
        print("RESULTS")
        print(f"{'=' * 60}")
        print(f"Created: {created}")
        print(f"Skipped (duplicates): {skipped}")
        print(f"Failed: {failed}")
        
    except Exception as e:
        print(f"ERROR: Failed to send batch request: {e}")
        sys.exit(1)
    
    # 6. Get final count
    print("\n6. Fetching final event count...")
    try:
        response = requests.get(f'{API_URL}/api/events', timeout=30)
        if response.status_code == 200:
            data = response.json()
            final_events = data if isinstance(data, list) else data.get('events', [])
            print(f"New total count: {len(final_events)} events")
        else:
            print(f"Warning: Could not fetch final count (HTTP {response.status_code})")
    except Exception as e:
        print(f"Warning: Could not fetch final count: {e}")
    
    print(f"\n{'=' * 60}")
    print("Import completed!")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    main()
