"""
Import d'événements internationaux depuis plusieurs sources Open Data.
Sources:
- Helsinki LinkedEvents API (Finland)
- Turku LinkedEvents API (Finland) 
- Espoo LinkedEvents API (Finland)
- OpenAgenda (Belgium, French-speaking countries)
- Madrid Open Data (Spain - more events)
Licence: Open data, CC-BY ou équivalent
"""

import requests
import json
import time
import re
import hashlib
from datetime import datetime, date

API_BASE = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api"
HEADERS = {"User-Agent": "MapEventAI-Bot/1.0 (open data consumer)"}
TODAY = date.today().strftime("%Y-%m-%d")


def clean_html(text, max_len=350):
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', ' ', str(text))
    text = re.sub(r'&[a-z]+;', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) > max_len:
        text = text[:max_len].rsplit(' ', 1)[0] + "..."
    return text


def categorize_generic(title, description, keywords_str=""):
    """Catégorisation multilingue (FR/EN/FI/DE/ES)."""
    cats = []
    combined = f"{title} {description} {keywords_str}".lower()
    
    # Musique
    if any(w in combined for w in ["concert", "music", "musiikki", "orchestra", "symphon", "choir", "chorus", "gig"]):
        if "jazz" in combined: cats.append("Musique > Jazz")
        elif any(w in combined for w in ["classical", "classique", "klassik", "clásic"]): cats.append("Musique > Classique")
        elif any(w in combined for w in ["electro", "techno", "house", "dj", "club night"]): cats.append("Musique > Electronic")
        elif any(w in combined for w in ["rock", "metal", "punk"]): cats.append("Musique > Rock")
        elif any(w in combined for w in ["hip-hop", "hip hop", "rap"]): cats.append("Musique > Hip-Hop")
        elif "folk" in combined: cats.append("Musique > Folk")
        elif "blues" in combined: cats.append("Musique > Blues")
        elif "pop" in combined: cats.append("Musique > Pop")
        else: cats.append("Musique > Concert")
    
    # Theatre / Performance
    if any(w in combined for w in ["theatre", "theater", "théâtre", "teatteri", "play ", "drama"]):
        cats.append("Spectacle > Théâtre")
    if any(w in combined for w in ["dance", "danse", "tanssi", "ballet", "choreograph"]):
        cats.append("Danse")
    if any(w in combined for w in ["comedy", "comédie", "humour", "stand-up", "komedia"]):
        cats.append("Spectacle > Humour")
    if any(w in combined for w in ["circus", "cirque", "sirkus"]):
        cats.append("Spectacle > Cirque")
    if any(w in combined for w in ["opera", "opéra", "ooppera"]):
        cats.append("Musique > Opéra")
    
    # Culture / Art
    if any(w in combined for w in ["exhibition", "exposition", "näyttely", "ausstellung", "exhibit", "gallery"]):
        cats.append("Culture > Exposition")
    if any(w in combined for w in ["museum", "musée", "museo"]):
        cats.append("Culture > Musée")
    if any(w in combined for w in ["cinema", "cinéma", "film ", "movie", "screening"]):
        cats.append("Culture > Cinéma")
    if any(w in combined for w in ["literature", "littéra", "book", "reading", "poetry", "kirjallisuus"]):
        cats.append("Culture > Littérature")
    
    # Sport
    if any(w in combined for w in ["marathon", "running", "course ", "jogging", "trail"]):
        cats.append("Sport > Course à pied")
    if any(w in combined for w in ["football", "soccer", "jalkapallo"]):
        cats.append("Sport > Football")
    if any(w in combined for w in ["hockey", "jääkiekko"]):
        cats.append("Sport > Hockey")
    if any(w in combined for w in ["yoga", "pilates"]):
        cats.append("Sport > Yoga & Bien-être")
    if any(w in combined for w in ["sport", "urheilu", "athletics", "swim"]):
        if not any("Sport" in c for c in cats):
            cats.append("Sport")
    
    # Festival
    if "festival" in combined:
        if not cats:
            cats.append("Festival")
    
    # Food & Drink
    if any(w in combined for w in ["food", "gastro", "wine", "beer", "tasting", "cuisine", "dégustation", "ruoka"]):
        cats.append("Gastronomie > Dégustation")
    if any(w in combined for w in ["market", "marché", "brocante", "flea", "tori"]):
        cats.append("Marché & Brocante")
    
    # Conference / Workshop
    if any(w in combined for w in ["conference", "conférence", "seminar", "congress", "symposium"]):
        cats.append("Conférence")
    if any(w in combined for w in ["workshop", "atelier", "course", "class ", "training"]):
        cats.append("Atelier")
    
    # Children / Family
    if any(w in combined for w in ["children", "kids", "family", "enfant", "famille", "lapsi", "perhe"]):
        if not any("enfant" in c.lower() or "famille" in c.lower() for c in cats):
            cats.append("Famille & Enfants")
    
    # Fête / Party
    if any(w in combined for w in ["party", "fête", "carnival", "carnaval", "night "]):
        if not any("Fête" in c for c in cats):
            cats.append("Fête")
    
    if not cats:
        cats.append("Événement")
    
    return cats[:3]


def send_batch(events, label=""):
    """Envoie un batch d'events à l'API MapEvent."""
    if not events:
        return 0
    try:
        r = requests.post(
            f"{API_BASE}/events/scraped/batch",
            json={"events": events},
            headers=HEADERS,
            timeout=60
        )
        if r.status_code in (200, 201):
            result = r.json()
            inserted = result.get("inserted", result.get("count", len(events)))
            return inserted
        else:
            print(f"  ⚠ Batch error {label}: HTTP {r.status_code} - {r.text[:200]}")
            return 0
    except Exception as e:
        print(f"  ❌ Batch error {label}: {e}")
        return 0


def send_all_events(events, source_name):
    """Envoie tous les events par batchs de 10."""
    total = 0
    for i in range(0, len(events), 10):
        batch = events[i:i+10]
        n = send_batch(batch, source_name)
        total += n
        if i + 10 < len(events):
            time.sleep(0.5)
    return total


# ============================================
# FINLAND - Helsinki LinkedEvents API
# ============================================
def fetch_helsinki_events(max_pages=8):
    """Fetch events from Helsinki LinkedEvents API."""
    print("\n🇫🇮 FINLAND - Helsinki LinkedEvents API")
    events = []
    seen = set()
    
    base_url = "https://api.hel.fi/linkedevents/v1/event/"
    page = 1
    
    while page <= max_pages:
        try:
            params = {
                "start": TODAY,
                "page_size": 100,
                "page": page,
                "format": "json",
                "include": "location"
            }
            r = requests.get(base_url, params=params, headers=HEADERS, timeout=30)
            if r.status_code != 200:
                print(f"  Page {page}: HTTP {r.status_code}")
                break
            
            data = r.json()
            items = data.get("data", [])
            if not items:
                break
            
            for item in items:
                ev = parse_linkedevents(item)
                if ev:
                    key = f"{ev['title'][:40]}|{ev['date']}|{ev['latitude']:.3f}"
                    if key not in seen:
                        seen.add(key)
                        events.append(ev)
            
            print(f"  Page {page}: {len(items)} items → {len(events)} total")
            
            if not data.get("meta", {}).get("next"):
                break
            page += 1
            time.sleep(1)
            
        except Exception as e:
            print(f"  Page {page} error: {e}")
            break
    
    print(f"  Total Finland: {len(events)} events")
    return events


def parse_linkedevents(item):
    """Parse un event LinkedEvents (Helsinki/Turku/Espoo)."""
    # Title - prefer Finnish, then English
    name = item.get("name", {})
    title = name.get("fi") or name.get("en") or name.get("sv") or ""
    if not title:
        return None
    
    # Description
    desc = item.get("short_description", {}) or item.get("description", {})
    description = clean_html(desc.get("fi") or desc.get("en") or desc.get("sv") or "")
    
    # Location
    location = item.get("location", {})
    if isinstance(location, str):
        # Location is just an ID, not embedded
        return None
    
    if not location or not isinstance(location, dict):
        return None
    
    loc_name = (location.get("name", {}) or {})
    location_str = loc_name.get("fi") or loc_name.get("en") or ""
    
    street = (location.get("street_address", {}) or {})
    street_str = street.get("fi") or street.get("en") or ""
    if street_str:
        location_str = f"{location_str}, {street_str}" if location_str else street_str
    
    # Coordinates - LinkedEvents uses [lon, lat] format (GeoJSON)
    position = location.get("position")
    if not position:
        return None
    
    coords = position.get("coordinates", [])
    if not coords or len(coords) < 2:
        return None
    
    lon = float(coords[0])
    lat = float(coords[1])
    
    # Validate Finland bounds (approximate)
    if not (59.0 <= lat <= 70.5 and 19.0 <= lon <= 32.0):
        return None
    
    # Dates
    start_time = item.get("start_time", "")
    end_time = item.get("end_time", "")
    
    event_date = None
    event_end = None
    event_time_str = None
    event_end_time_str = None
    
    if start_time:
        event_date = start_time[:10]
        if len(start_time) >= 16 and "T" in start_time:
            h = start_time[11:16]
            if h != "00:00":
                event_time_str = h
    
    if end_time:
        event_end = end_time[:10]
        if len(end_time) >= 16 and "T" in end_time:
            h = end_time[11:16]
            if h != "00:00":
                event_end_time_str = h
    
    if not event_date:
        return None
    
    if event_end == event_date:
        event_end = None
    
    # Check future
    try:
        check = event_end or event_date
        if datetime.strptime(check, "%Y-%m-%d").date() < date.today():
            return None
    except:
        pass
    
    # Source URL
    info_url = item.get("info_url", {}) or {}
    source_url = info_url.get("fi") or info_url.get("en") or ""
    if not source_url:
        event_id = item.get("id", "")
        if event_id:
            source_url = f"https://linkedevents.hel.fi/fi/event/{event_id}"
    
    if not source_url:
        return None
    
    # Keywords for categorization
    kw_names = []
    for kw in item.get("keywords", []):
        if isinstance(kw, dict):
            n = kw.get("name", {})
            kw_names.append(n.get("fi") or n.get("en") or "")
    
    categories = categorize_generic(title, description, " ".join(kw_names))
    
    city = "Helsinki"
    # Try to detect city from location
    addr_locality = (location.get("address_locality", {}) or {})
    loc_city = addr_locality.get("fi") or addr_locality.get("en") or ""
    if loc_city:
        city = loc_city
    
    if location_str and city not in location_str:
        location_str += f", {city}"
    if "Finland" not in location_str and "Suomi" not in location_str:
        location_str += ", Finland"
    
    return {
        "title": title[:200],
        "description": description,
        "date": event_date,
        "end_date": event_end,
        "time": event_time_str,
        "end_time": event_end_time_str,
        "location": location_str[:300],
        "latitude": round(lat, 6),
        "longitude": round(lon, 6),
        "categories": categories,
        "source_url": source_url,
        "source": f"LinkedEvents - {city}",
        "validation_status": "auto_validated"
    }


# ============================================
# BELGIUM - OpenAgenda
# ============================================
def fetch_belgium_events():
    """Fetch events from Belgium via OpenAgenda."""
    print("\n🇧🇪 BELGIUM - OpenAgenda")
    ODS_BASE = "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/evenements-publics-openagenda/records"
    
    # Belgian cities (French and Dutch names)
    cities = [
        "Bruxelles", "Brussels", "Liège", "Namur", "Charleroi", "Mons",
        "Gand", "Gent", "Anvers", "Antwerpen", "Bruges", "Brugge",
        "Louvain-la-Neuve", "Waterloo", "Tournai", "Arlon", "Spa",
        "Dinant", "Hasselt", "Leuven", "Mechelen", "Kortrijk", "Ostende"
    ]
    
    events = []
    seen = set()
    
    for city in cities:
        try:
            params = {
                "where": f'location_city="{city}" AND firstdate_begin >= "{TODAY}"',
                "limit": 30,
                "order_by": "firstdate_begin"
            }
            r = requests.get(ODS_BASE, params=params, headers=HEADERS, timeout=20)
            if r.status_code != 200:
                continue
            
            data = r.json()
            results = data.get("results", [])
            
            for record in results:
                ev = parse_openagenda_be(record, city)
                if ev:
                    key = f"{ev['title'][:40]}|{ev['date']}|{ev['latitude']:.3f}"
                    if key not in seen:
                        seen.add(key)
                        events.append(ev)
            
            count = len([r for r in results if r])
            if count > 0:
                print(f"  {city}: {count} fetched")
            time.sleep(0.5)
            
        except Exception as e:
            print(f"  {city}: error {e}")
    
    print(f"  Total Belgium: {len(events)} events")
    return events


def parse_openagenda_be(record, city):
    """Parse OpenAgenda record for Belgium."""
    fields = record
    
    title = fields.get("title_fr") or fields.get("title") or ""
    if not title:
        return None
    
    desc = fields.get("description_fr") or fields.get("description") or ""
    description = clean_html(desc)
    
    # Location
    loc_name = fields.get("location_name") or ""
    loc_addr = fields.get("location_address") or ""
    loc_city = fields.get("location_city") or city
    
    location_str = loc_name
    if loc_addr:
        location_str += f", {loc_addr}" if location_str else loc_addr
    if loc_city and loc_city not in location_str:
        location_str += f", {loc_city}"
    if "Belgique" not in location_str and "Belgium" not in location_str:
        location_str += ", Belgique"
    
    # Coords
    coords = fields.get("location_coordinates")
    if not coords:
        return None
    
    if isinstance(coords, dict):
        lat = coords.get("lat")
        lon = coords.get("lon")
    elif isinstance(coords, list) and len(coords) >= 2:
        lat = coords[0]
        lon = coords[1]
    else:
        return None
    
    try:
        lat = float(lat)
        lon = float(lon)
    except:
        return None
    
    # Belgium bounds
    if not (49.4 <= lat <= 51.6 and 2.5 <= lon <= 6.5):
        return None
    
    # Dates
    first_begin = fields.get("firstdate_begin") or ""
    last_end = fields.get("lastdate_end") or ""
    
    event_date = first_begin[:10] if first_begin else None
    end_date = last_end[:10] if last_end else None
    
    if not event_date:
        return None
    if end_date == event_date:
        end_date = None
    
    try:
        check = end_date or event_date
        if datetime.strptime(check, "%Y-%m-%d").date() < date.today():
            return None
    except:
        pass
    
    # Source
    source_url = fields.get("canonicalurl") or ""
    if not source_url:
        return None
    
    keywords = []
    kw = fields.get("keywords_fr")
    if isinstance(kw, str):
        keywords = [k.strip() for k in kw.split(",")]
    elif isinstance(kw, list):
        keywords = kw
    
    categories = categorize_generic(title, description, " ".join(keywords))
    
    return {
        "title": title[:200],
        "description": description,
        "date": event_date,
        "end_date": end_date,
        "time": None,
        "end_time": None,
        "location": location_str[:300],
        "latitude": round(lat, 6),
        "longitude": round(lon, 6),
        "categories": categories,
        "source_url": source_url,
        "source": f"OpenAgenda - {loc_city}",
        "validation_status": "auto_validated"
    }


# ============================================
# MADRID - More events (datos.madrid.es)
# ============================================
def fetch_madrid_extra():
    """Fetch additional Madrid events from open data."""
    print("\n🇪🇸 MADRID - datos.madrid.es (extra)")
    
    urls = [
        "https://datos.madrid.es/egob/catalogo/300107-0-agenda-actividades-eventos.json"
    ]
    
    events = []
    seen = set()
    
    for url in urls:
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            if r.status_code != 200:
                print(f"  HTTP {r.status_code}")
                continue
            
            data = r.json()
            items = data.get("@graph", [])
            print(f"  Madrid: {len(items)} items")
            
            for item in items:
                ev = parse_madrid(item)
                if ev:
                    key = f"{ev['title'][:40]}|{ev['date']}|{ev['latitude']:.3f}"
                    if key not in seen:
                        seen.add(key)
                        events.append(ev)
            
        except Exception as e:
            print(f"  Error: {e}")
    
    print(f"  Total Madrid extra: {len(events)} events")
    return events


def parse_madrid(item):
    """Parse Madrid open data event."""
    title = item.get("title", "")
    if not title:
        return None
    
    desc = clean_html(item.get("description", ""))
    
    # Dates
    dtstart = item.get("dtstart") or ""
    dtend = item.get("dtend") or ""
    
    event_date = dtstart[:10] if dtstart else None
    end_date = dtend[:10] if dtend else None
    
    if not event_date:
        return None
    if end_date == event_date:
        end_date = None
    
    try:
        check = end_date or event_date
        if datetime.strptime(check, "%Y-%m-%d").date() < date.today():
            return None
    except:
        pass
    
    # Time
    event_time = None
    if "time" in item:
        event_time = item["time"][:5] if item["time"] else None
    elif len(dtstart) >= 16 and "T" in dtstart:
        h = dtstart[11:16]
        if h != "00:00":
            event_time = h
    
    # Location
    location_str = item.get("event-location", "") or item.get("address", {}).get("street-address", "")
    loc_area = item.get("address", {}).get("area", {}).get("@id", "")
    if loc_area:
        loc_area_name = loc_area.split("/")[-1].replace("-", " ").title()
        if loc_area_name and loc_area_name not in location_str:
            location_str += f", {loc_area_name}"
    if "Madrid" not in location_str:
        location_str += ", Madrid, España"
    
    # Coords
    lat = item.get("location", {}).get("latitude")
    lon = item.get("location", {}).get("longitude")
    
    if not lat or not lon:
        return None
    
    try:
        lat = float(lat)
        lon = float(lon)
    except:
        return None
    
    # Madrid bounds
    if not (39.8 <= lat <= 41.0 and -4.5 <= lon <= -3.0):
        return None
    
    # Source URL  
    source_url = item.get("link") or item.get("@id") or ""
    if not source_url:
        return None
    
    categories = categorize_generic(title, desc)
    
    return {
        "title": title[:200],
        "description": desc,
        "date": event_date,
        "end_date": end_date,
        "time": event_time,
        "end_time": None,
        "location": location_str[:300],
        "latitude": round(lat, 6),
        "longitude": round(lon, 6),
        "categories": categories,
        "source_url": source_url,
        "source": "datos.madrid.es",
        "validation_status": "auto_validated"
    }


# ============================================
# MAIN
# ============================================
def main():
    print("=" * 60)
    print("IMPORT EUROPE + GLOBAL - Multi-source Open Data")
    print("=" * 60)
    
    all_results = {}
    
    # 1. Finland (Helsinki)
    finland_events = fetch_helsinki_events(max_pages=6)
    if finland_events:
        n = send_all_events(finland_events, "Finland")
        all_results["Finland"] = n
        print(f"  ✅ Finland: {n} events importés")
    
    # 2. Belgium  
    belgium_events = fetch_belgium_events()
    if belgium_events:
        n = send_all_events(belgium_events, "Belgium")
        all_results["Belgium"] = n
        print(f"  ✅ Belgium: {n} events importés")
    
    # 3. Madrid extra
    madrid_events = fetch_madrid_extra()
    if madrid_events:
        n = send_all_events(madrid_events, "Madrid")
        all_results["Madrid"] = n
        print(f"  ✅ Madrid: {n} events importés")
    
    # Summary
    print(f"\n{'=' * 60}")
    print("RÉSUMÉ FINAL:")
    total = 0
    for source, count in all_results.items():
        print(f"  {source}: {count} events")
        total += count
    print(f"  TOTAL: {total} events importés")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
