"""
Import d'événements de Lisbonne depuis agendalx.pt (Open Data).
Source: dados.cm-lisboa.pt -> Agenda Cultural de Lisboa -> agendalx.pt
Licence: CC-BY (via dados.cm-lisboa.pt)
"""

import requests
import json
import time
import re
from datetime import datetime, date

API_BASE = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api"
HEADERS = {"User-Agent": "MapEventAI-Bot/1.0 (open data consumer)"}

# Cache de géocodage par venue
VENUE_COORDS = {}

# Coordonnées connues de lieux à Lisbonne
KNOWN_VENUES = {
    "teatro nacional d. maria ii": (38.7139, -9.1377),
    "teatro nacional de são carlos": (38.7097, -9.1425),
    "coliseu dos recreios": (38.7170, -9.1387),
    "fundação calouste gulbenkian": (38.7357, -9.1537),
    "centro cultural de belém": (38.6942, -9.2069),
    "ccb": (38.6942, -9.2069),
    "museu nacional de arte antiga": (38.7035, -9.1614),
    "museu berardo": (38.6940, -9.2070),
    "casa da imprensa": (38.7205, -9.1488),
    "maat": (38.6964, -9.1907),
    "oceanário de lisboa": (38.7636, -9.0938),
    "pavilhão do conhecimento": (38.7629, -9.0949),
    "campo pequeno": (38.7421, -9.1475),
    "altice arena": (38.7682, -9.0940),
    "meo arena": (38.7682, -9.0940),
    "capitólio": (38.7197, -9.1400),
    "lux frágil": (38.7145, -9.1210),
    "village underground": (38.7071, -9.1460),
    "culturgest": (38.7276, -9.1459),
    "museu do oriente": (38.6998, -9.1818),
    "lx factory": (38.7035, -9.1749),
    "museu nacional do azulejo": (38.7240, -9.1139),
    "cinemateca portuguesa": (38.7315, -9.1490),
    "galeria 111": (38.7370, -9.1515),
    "eritage art projects": (38.7130, -9.1390),
    "comunidade hindu de portugal": (38.7570, -9.1450),
    "topo chiado": (38.7112, -9.1400),
    "casa fernando pessoa": (38.7173, -9.1574),
    "jardim botânico de lisboa": (38.7177, -9.1496),
    "teatro da trindade": (38.7140, -9.1425),
    "cinema são jorge": (38.7194, -9.1429),
    "teatro do bairro alto": (38.7127, -9.1438),
    "musicbox": (38.7078, -9.1452),
    "galeria filomena soares": (38.7243, -9.1252),
    "zdb": (38.7140, -9.1478),
}


def geocode_venue(venue_name):
    """Géocode un lieu à Lisbonne."""
    if not venue_name:
        return None, None
    
    key = venue_name.lower().strip()
    
    # Cache
    if key in VENUE_COORDS:
        return VENUE_COORDS[key]
    
    # Known venues
    for known_key, coords in KNOWN_VENUES.items():
        if known_key in key or key in known_key:
            VENUE_COORDS[key] = coords
            return coords
    
    # Fallback: centre de Lisbonne avec léger offset basé sur le nom
    # (évite les appels Nominatim lents)
    import hashlib
    h = int(hashlib.md5(key.encode()).hexdigest()[:8], 16)
    lat = 38.7223 + ((h % 200) - 100) / 10000.0
    lon = -9.1393 + ((h // 200 % 200) - 100) / 10000.0
    VENUE_COORDS[key] = (lat, lon)
    return lat, lon


def clean_html(text, max_len=300):
    if not text:
        return ""
    if isinstance(text, list):
        text = " ".join(text)
    text = re.sub(r'<[^>]+>', ' ', str(text))
    text = re.sub(r'&[a-z]+;', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) > max_len:
        text = text[:max_len].rsplit(' ', 1)[0] + "..."
    return text


def categorize_lisbon(categories, tags, subject, title):
    """Catégorise un événement de Lisbonne."""
    cat_keys = list(categories.keys()) if isinstance(categories, dict) else categories if isinstance(categories, list) else []
    tag_keys = list(tags.keys()) if isinstance(tags, dict) else tags if isinstance(tags, list) else []
    combined = " ".join(cat_keys + tag_keys + [subject or "", title or ""]).lower()
    cats = []
    
    if any(w in combined for w in ["concerto", "musica", "música", "jazz", "fado"]):
        if "jazz" in combined: cats.append("Musique > Jazz")
        elif "fado" in combined: cats.append("Musique > Fado")
        elif "clássic" in combined: cats.append("Musique > Classique")
        else: cats.append("Musique > Concert")
    
    if any(w in combined for w in ["exposição", "exposicao", "artes", "arte", "pintura", "fotografia"]):
        cats.append("Culture > Exposition")
    
    if any(w in combined for w in ["teatro", "comédia"]):
        cats.append("Spectacle > Théâtre")
    
    if any(w in combined for w in ["dança", "ballet"]):
        cats.append("Danse")
    
    if any(w in combined for w in ["festival", "festa", "carnaval"]):
        cats.append("Festival")
    
    if any(w in combined for w in ["cinema", "filme"]):
        cats.append("Culture > Cinéma")
    
    if any(w in combined for w in ["conferência", "workshop", "oficina"]):
        cats.append("Culture > Conférence")
    
    if any(w in combined for w in ["visita", "passeio", "ruta"]):
        cats.append("Culture > Visite guidée")
    
    if any(w in combined for w in ["infantil", "crianças", "família"]):
        cats.append("Famille")
    
    if not cats:
        cats = ["Divertissement"]
    
    return cats[:3]


def fetch_lisbon_events():
    """Fetch tous les événements de agendalx.pt."""
    print("📥 Téléchargement données Lisbonne (CC-BY)...")
    
    all_events_raw = []
    for page in range(1, 30):
        try:
            r = requests.get(
                f"https://www.agendalx.pt/wp-json/agendalx/v1/events?page={page}",
                headers=HEADERS, timeout=30
            )
            if r.status_code != 200:
                break
            events = r.json()
            if not events:
                break
            all_events_raw.extend(events)
            print(f"  Page {page}: {len(events)} events")
        except Exception as e:
            print(f"  Page {page}: erreur {e}")
            break
    
    print(f"  📊 {len(all_events_raw)} events bruts")
    
    today = date.today()
    events = []
    
    for raw in all_events_raw:
        title_data = raw.get("title", {})
        title = title_data.get("rendered", "") if isinstance(title_data, dict) else str(title_data)
        if not title:
            continue
        
        # Dates
        start_date = raw.get("StartDate")
        last_date = raw.get("LastDate")
        
        if not start_date:
            continue
        
        # Vérifier futur
        try:
            check_d = last_date or start_date
            if datetime.strptime(check_d, "%Y-%m-%d").date() < today:
                continue
        except:
            pass
        
        # URL source
        link = raw.get("link", "")
        if not link or not link.startswith("http"):
            continue
        
        # Venue -> Geocode
        venue_data = raw.get("venue", {})
        if isinstance(venue_data, dict):
            venue_names = [v.get("name", "") for v in venue_data.values() if isinstance(v, dict)]
        else:
            venue_names = []
        venue_name = venue_names[0] if venue_names else ""
        
        lat, lon = geocode_venue(venue_name)
        if not lat:
            continue
        
        # Description
        description = clean_html(raw.get("description", ""))
        
        # Categories
        cats_data = raw.get("categories_name_list", {})
        tags_data = raw.get("tags_name_list", {})
        subject = raw.get("subject", "")
        categories = categorize_lisbon(cats_data, tags_data, subject, title)
        
        # Time
        time_str = raw.get("string_times", "")
        start_time = None
        if time_str and re.match(r'\d{1,2}h\d{2}', time_str):
            start_time = time_str.replace("h", ":")
        elif time_str and re.match(r'\d{1,2}:\d{2}', time_str):
            start_time = time_str[:5]
        
        location = f"{venue_name}, Lisboa, Portugal" if venue_name else "Lisboa, Portugal"
        
        events.append({
            "title": title.strip(),
            "description": description,
            "location": location,
            "latitude": round(lat, 6),
            "longitude": round(lon, 6),
            "date": start_date,
            "time": start_time,
            "end_date": last_date if last_date != start_date else None,
            "end_time": None,
            "categories": categories,
            "source_url": link,
            "validation_status": "auto_validated",
            "status": "active",
        })
    
    print(f"  ✅ {len(events)} événements futurs Lisbonne")
    return events


def deduplicate_with_existing(new_events):
    print("\n🔍 Vérification des doublons...")
    r = requests.get(f"{API_BASE}/events", timeout=30)
    if r.status_code != 200:
        return new_events
    
    existing = r.json()
    existing_titles = set((e.get("title") or "").lower().strip() for e in existing)
    existing_urls = set(e.get("source_url") or "" for e in existing)
    
    unique = [ev for ev in new_events 
              if ev["title"].lower().strip() not in existing_titles 
              and ev["source_url"] not in existing_urls]
    
    dupes = len(new_events) - len(unique)
    print(f"  📊 {dupes} doublons, {len(unique)} uniques")
    return unique


def import_events(events, batch_size=30):
    if not events:
        print("  Aucun événement à importer.")
        return 0
    
    print(f"\n📤 Import {len(events)} événements Lisbonne...")
    total = 0
    for i in range(0, len(events), batch_size):
        batch = events[i:i+batch_size]
        try:
            r = requests.post(f"{API_BASE}/events/scraped/batch", json={"events": batch},
                            headers={"Content-Type": "application/json"}, timeout=30)
            if r.status_code in (200, 201):
                count = r.json().get("imported", len(batch))
                total += count
                print(f"  ✅ Batch {i//batch_size + 1}: {count}")
            else:
                print(f"  ❌ Batch {i//batch_size + 1}: {r.status_code}")
        except Exception as e:
            print(f"  ❌ Batch {i//batch_size + 1}: {e}")
        time.sleep(1)
    
    print(f"🎉 Total importé Lisbonne: {total}")
    return total


if __name__ == "__main__":
    print("=" * 60)
    print("🇵🇹 IMPORT ÉVÉNEMENTS LISBONNE - OPEN DATA")
    print("   Source: agendalx.pt via dados.cm-lisboa.pt")
    print("   Licence: CC-BY")
    print("=" * 60)
    
    events = fetch_lisbon_events()
    
    if events:
        print(f"\nAperçu (5 premiers):")
        for e in events[:5]:
            print(f"  {e['date']} | {e['title'][:50]}")
            print(f"    📍 {e['latitude']:.4f}, {e['longitude']:.4f} | {e['location'][:50]}")
            print(f"    🔗 {e['source_url'][:70]}")
        
        unique = deduplicate_with_existing(events)
        if unique:
            import_events(unique)
    
    print("\n✅ Terminé!")
