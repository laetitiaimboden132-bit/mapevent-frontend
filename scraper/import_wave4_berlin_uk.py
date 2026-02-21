"""
Import Wave 4 - Berlin kulturdaten.berlin API + more sources.
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


def categorize(title, desc, kw=""):
    cats = []
    c = f"{title} {desc} {kw}".lower()
    if any(w in c for w in ["konzert", "concert", "music", "musik", "orchestra", "symphon", "chor"]):
        if "jazz" in c: cats.append("Musique > Jazz")
        elif any(w in c for w in ["klassik", "classical", "classique"]): cats.append("Musique > Classique")
        elif any(w in c for w in ["electro", "techno", "house", "dj", "club"]): cats.append("Musique > Electronic")
        elif any(w in c for w in ["rock", "metal", "punk"]): cats.append("Musique > Rock")
        elif any(w in c for w in ["hip-hop", "rap"]): cats.append("Musique > Hip-Hop")
        elif "folk" in c: cats.append("Musique > Folk")
        else: cats.append("Musique > Concert")
    if any(w in c for w in ["theater", "theatre", "théâtre", "bühne", "schauspiel"]): cats.append("Spectacle > Théâtre")
    if any(w in c for w in ["tanz", "dance", "ballet", "ballett"]): cats.append("Danse")
    if any(w in c for w in ["ausstellung", "exhibition", "exposition", "galerie", "gallery"]): cats.append("Culture > Exposition")
    if any(w in c for w in ["kino", "film", "cinema"]): cats.append("Culture > Cinéma")
    if any(w in c for w in ["lesung", "literatur", "buch", "reading"]): cats.append("Culture > Littérature")
    if any(w in c for w in ["museum"]): cats.append("Culture > Musée")
    if any(w in c for w in ["sport", "lauf", "marathon", "fussball", "basketball"]): cats.append("Sport")
    if "festival" in c and not cats: cats.append("Festival")
    if any(w in c for w in ["markt", "flohmarkt", "market"]): cats.append("Marché & Brocante")
    if any(w in c for w in ["vortrag", "konferenz", "conference"]): cats.append("Conférence")
    if any(w in c for w in ["workshop", "kurs"]): cats.append("Atelier")
    if any(w in c for w in ["kinder", "familie", "children"]): cats.append("Famille & Enfants")
    if any(w in c for w in ["comedy", "kabarett", "komödie"]): cats.append("Spectacle > Humour")
    if any(w in c for w in ["party", "fest ", "feier"]): cats.append("Fête")
    if not cats: cats.append("Événement")
    return cats[:3]


def send_all(events, name):
    total = 0
    for i in range(0, len(events), 10):
        batch = events[i:i+10]
        try:
            r = requests.post(f"{API_BASE}/events/scraped/batch", json={"events": batch}, headers=HEADERS, timeout=60)
            if r.status_code in (200, 201):
                total += r.json().get("inserted", r.json().get("count", len(batch)))
        except:
            pass
        if i + 10 < len(events):
            time.sleep(0.5)
    return total


# Berlin borough approximate centroids
BERLIN_BOROUGHS = {
    "Mitte": (52.5200, 13.4050),
    "Friedrichshain-Kreuzberg": (52.5000, 13.4400),
    "Pankow": (52.5700, 13.4100),
    "Charlottenburg-Wilmersdorf": (52.5050, 13.2900),
    "Spandau": (52.5340, 13.2000),
    "Steglitz-Zehlendorf": (52.4340, 13.2400),
    "Tempelhof-Schöneberg": (52.4670, 13.3500),
    "Neukölln": (52.4400, 13.4400),
    "Treptow-Köpenick": (52.4500, 13.5800),
    "Marzahn-Hellersdorf": (52.5400, 13.6000),
    "Lichtenberg": (52.5200, 13.5000),
    "Reinickendorf": (52.5900, 13.3300),
}


def fetch_berlin_events(max_pages=8):
    """Fetch Berlin cultural events from kulturdaten.berlin API v2."""
    print("\n🇩🇪 BERLIN - kulturdaten.berlin API v2")
    
    base = "https://api-v2.kulturdaten.berlin/api"
    events = []
    seen = set()
    loc_cache = {}  # Cache location details
    
    for page in range(1, max_pages + 1):
        try:
            r = requests.get(f"{base}/events", params={
                "page": page, "pageSize": 100, "startDate": TODAY
            }, headers=HEADERS, timeout=30)
            
            if r.status_code != 200:
                print(f"  Page {page}: HTTP {r.status_code}")
                break
            
            data = r.json()
            items = data.get("data", {}).get("events", [])
            if not items:
                break
            
            for item in items:
                ev = parse_berlin_event(item, base, loc_cache)
                if ev:
                    key = f"{ev['title'][:40]}|{ev['date']}|{ev['latitude']:.3f}"
                    if key not in seen:
                        seen.add(key)
                        events.append(ev)
            
            print(f"  Page {page}: {len(items)} items → {len(events)} total")
            
            total_available = data.get("data", {}).get("totalCount", 0)
            if page * 100 >= total_available:
                break
            time.sleep(1)
            
        except Exception as e:
            print(f"  Page {page} error: {e}")
            break
    
    print(f"  Total Berlin: {len(events)} events")
    return events


def parse_berlin_event(item, api_base, loc_cache):
    """Parse Berlin kulturdaten event."""
    # Title from attraction
    attractions = item.get("attractions", [])
    title = ""
    for attr in attractions:
        label = attr.get("referenceLabel", {})
        title = label.get("de") or label.get("en") or ""
        if title:
            break
    
    if not title:
        return None
    
    # Schedule
    schedule = item.get("schedule", {})
    start_date = schedule.get("startDate", "")
    end_date = schedule.get("endDate", "")
    start_time = schedule.get("startTime", "")
    end_time_str = schedule.get("endTime", "")
    
    if not start_date:
        return None
    
    event_date = start_date[:10]
    event_end = end_date[:10] if end_date else None
    ev_time = None
    
    if event_end == event_date:
        event_end = None
    
    if start_time and start_time != "00:00:00":
        ev_time = start_time[:5]
    
    try:
        check = event_end or event_date
        if datetime.strptime(check, "%Y-%m-%d").date() < date.today():
            return None
    except:
        pass
    
    # Location
    locations = item.get("locations", [])
    location_str = "Berlin, Deutschland"
    lat = 52.5200
    lon = 13.4050
    borough = ""
    
    for loc in locations:
        loc_id = loc.get("referenceId", "")
        label = loc.get("referenceLabel", {})
        loc_name = label.get("de") or label.get("en") or ""
        
        # Try to get location details from cache or API
        if loc_id and loc_id not in loc_cache:
            try:
                r = requests.get(f"{api_base}/locations/{loc_id}", headers=HEADERS, timeout=8)
                if r.status_code == 200:
                    loc_data = r.json().get("data", {}).get("location", {})
                    loc_cache[loc_id] = loc_data
                else:
                    loc_cache[loc_id] = {}
            except:
                loc_cache[loc_id] = {}
        
        loc_detail = loc_cache.get(loc_id, {})
        
        # Get address
        address = loc_detail.get("address", {})
        street = address.get("streetAddress", "")
        postal = address.get("postalCode", "")
        locality = address.get("addressLocality", "Berlin")
        
        borough = loc_detail.get("borough", "")
        
        if loc_name:
            location_str = loc_name
        if street:
            location_str = f"{location_str}, {street}" if location_str and street not in location_str else street
        if borough:
            location_str += f", {borough}"
        location_str += ", Berlin, Deutschland"
        
        # Get coordinates from borough
        if borough and borough in BERLIN_BOROUGHS:
            base_lat, base_lon = BERLIN_BOROUGHS[borough]
        else:
            base_lat, base_lon = 52.5200, 13.4050
        
        # Add offset based on street/location for uniqueness
        h = int(hashlib.md5((street or loc_name or loc_id).encode()).hexdigest()[:8], 16)
        lat = base_lat + ((h % 200) - 100) / 6000.0
        lon = base_lon + ((h // 200 % 200) - 100) / 6000.0
        
        break  # Use first location
    
    # Source URL
    event_id = item.get("identifier", "")
    source_url = f"https://kulturdaten.berlin/events/{event_id}" if event_id else ""
    if not source_url:
        return None
    
    # Admission
    admission = item.get("admission", {})
    ticket_type = admission.get("ticketType", "")
    is_free = "freeOfCharge" in ticket_type
    
    categories = categorize(title, "", borough)
    
    desc = f"Kulturveranstaltung in {borough or 'Berlin'}"
    if is_free:
        desc += " (Eintritt frei)"
    
    return {
        "title": clean_html(title)[:200],
        "description": desc,
        "date": event_date,
        "end_date": event_end,
        "time": ev_time,
        "end_time": None,
        "location": location_str[:300],
        "latitude": round(lat, 6),
        "longitude": round(lon, 6),
        "categories": categories,
        "source_url": source_url,
        "source": "kulturdaten.berlin",
        "validation_status": "auto_validated"
    }


def main():
    print("=" * 60)
    print("IMPORT WAVE 4 - Berlin + more")
    print("=" * 60)
    
    results = {}
    
    # Berlin
    berlin_events = fetch_berlin_events(max_pages=6)
    if berlin_events:
        n = send_all(berlin_events, "Berlin")
        results["Berlin"] = n
        print(f"  ✅ Berlin: {n}")
    
    # Summary
    print(f"\n{'=' * 60}")
    print("RÉSUMÉ WAVE 4:")
    total = 0
    for source, count in results.items():
        print(f"  {source}: {count}")
        total += count
    print(f"  TOTAL: {total}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
