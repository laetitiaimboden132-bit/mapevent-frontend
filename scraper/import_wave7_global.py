"""
Import Wave 7 - More Berlin + OSM Calendar worldwide + More NYC.
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
    if not text: return ""
    text = re.sub(r'<[^>]+>', ' ', str(text))
    text = re.sub(r'&[a-z]+;', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) > max_len: text = text[:max_len].rsplit(' ', 1)[0] + "..."
    return text


def categorize(title, desc, kw=""):
    cats = []
    c = f"{title} {desc} {kw}".lower()
    if any(w in c for w in ["konzert", "concert", "music", "musik", "musique"]): 
        if "jazz" in c: cats.append("Musique > Jazz")
        elif any(w in c for w in ["klassik", "classical", "classique"]): cats.append("Musique > Classique")
        elif any(w in c for w in ["electro", "techno", "house", "dj", "club"]): cats.append("Musique > Electronic")
        elif any(w in c for w in ["rock", "metal", "punk"]): cats.append("Musique > Rock")
        elif any(w in c for w in ["hip-hop", "rap"]): cats.append("Musique > Hip-Hop")
        else: cats.append("Musique > Concert")
    if any(w in c for w in ["theater", "theatre", "théâtre", "schauspiel"]): cats.append("Spectacle > Théâtre")
    if any(w in c for w in ["tanz", "dance", "danse", "ballet"]): cats.append("Danse")
    if any(w in c for w in ["ausstellung", "exhibition", "exposition", "galerie", "gallery"]): cats.append("Culture > Exposition")
    if any(w in c for w in ["kino", "film", "cinema", "cinéma"]): cats.append("Culture > Cinéma")
    if any(w in c for w in ["lesung", "literatur", "buch", "lecture", "book"]): cats.append("Culture > Littérature")
    if any(w in c for w in ["museum", "musée"]): cats.append("Culture > Musée")
    if any(w in c for w in ["sport", "lauf", "marathon", "fussball", "football", "basketball", "running"]): cats.append("Sport")
    if "festival" in c and not cats: cats.append("Festival")
    if any(w in c for w in ["markt", "flohmarkt", "market", "marché"]): cats.append("Marché & Brocante")
    if any(w in c for w in ["vortrag", "konferenz", "conference", "conférence", "meetup", "mapping party"]): cats.append("Conférence")
    if any(w in c for w in ["workshop", "kurs", "atelier"]): cats.append("Atelier")
    if any(w in c for w in ["kinder", "familie", "children", "enfant"]): cats.append("Famille & Enfants")
    if any(w in c for w in ["comedy", "kabarett", "komödie", "humour"]): cats.append("Spectacle > Humour")
    if any(w in c for w in ["party", "fest ", "feier", "fête"]): cats.append("Fête")
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


# Berlin borough coords
BERLIN_BOROUGHS = {
    "Mitte": (52.5200, 13.4050), "Friedrichshain-Kreuzberg": (52.5000, 13.4400),
    "Pankow": (52.5700, 13.4100), "Charlottenburg-Wilmersdorf": (52.5050, 13.2900),
    "Spandau": (52.5340, 13.2000), "Steglitz-Zehlendorf": (52.4340, 13.2400),
    "Tempelhof-Schöneberg": (52.4670, 13.3500), "Neukölln": (52.4400, 13.4400),
    "Treptow-Köpenick": (52.4500, 13.5800), "Marzahn-Hellersdorf": (52.5400, 13.6000),
    "Lichtenberg": (52.5200, 13.5000), "Reinickendorf": (52.5900, 13.3300),
}


# ============================================
# MORE BERLIN (pages 7-20)
# ============================================
def fetch_berlin_more():
    """Fetch more Berlin events from pages 7-20."""
    print("\n🇩🇪 BERLIN MORE - kulturdaten.berlin pages 7-20")
    base = "https://api-v2.kulturdaten.berlin/api"
    events = []
    seen = set()
    loc_cache = {}
    
    for page in range(7, 21):
        try:
            r = requests.get(f"{base}/events", params={
                "page": page, "pageSize": 100, "startDate": TODAY
            }, headers=HEADERS, timeout=30)
            if r.status_code != 200: break
            
            data = r.json()
            items = data.get("data", {}).get("events", [])
            if not items: break
            
            for item in items:
                ev = parse_berlin(item, base, loc_cache)
                if ev:
                    key = f"{ev['title'][:40]}|{ev['date']}|{ev['latitude']:.3f}"
                    if key not in seen:
                        seen.add(key)
                        events.append(ev)
            
            print(f"  Page {page}: {len(items)} → {len(events)} total")
            if page * 100 >= data.get("data", {}).get("totalCount", 0): break
            time.sleep(1)
        except Exception as e:
            print(f"  Page {page} error: {e}")
            break
    
    print(f"  Total Berlin more: {len(events)}")
    return events


def parse_berlin(item, api_base, loc_cache):
    """Parse Berlin kulturdaten event."""
    attractions = item.get("attractions", [])
    title = ""
    for attr in attractions:
        label = attr.get("referenceLabel", {})
        title = label.get("de") or label.get("en") or ""
        if title: break
    if not title: return None
    
    schedule = item.get("schedule", {})
    start_date = schedule.get("startDate", "")
    end_date = schedule.get("endDate", "")
    start_time = schedule.get("startTime", "")
    
    if not start_date: return None
    event_date = start_date[:10]
    event_end = end_date[:10] if end_date else None
    ev_time = None
    if event_end == event_date: event_end = None
    if start_time and start_time != "00:00:00": ev_time = start_time[:5]
    
    try:
        check = event_end or event_date
        if datetime.strptime(check, "%Y-%m-%d").date() < date.today(): return None
    except: pass
    
    locations = item.get("locations", [])
    location_str = "Berlin, Deutschland"
    lat, lon = 52.5200, 13.4050
    borough = ""
    
    for loc in locations:
        loc_id = loc.get("referenceId", "")
        label = loc.get("referenceLabel", {})
        loc_name = label.get("de") or label.get("en") or ""
        
        if loc_id and loc_id not in loc_cache:
            try:
                r = requests.get(f"{api_base}/locations/{loc_id}", headers=HEADERS, timeout=5)
                loc_cache[loc_id] = r.json().get("data", {}).get("location", {}) if r.status_code == 200 else {}
            except:
                loc_cache[loc_id] = {}
        
        loc_detail = loc_cache.get(loc_id, {})
        address = loc_detail.get("address", {})
        street = address.get("streetAddress", "")
        borough = loc_detail.get("borough", "")
        
        if loc_name: location_str = loc_name
        if street and street not in location_str: location_str = f"{location_str}, {street}" if location_str else street
        if borough: location_str += f", {borough}"
        location_str += ", Berlin, Deutschland"
        
        base_lat, base_lon = BERLIN_BOROUGHS.get(borough, (52.5200, 13.4050))
        h = int(hashlib.md5((street or loc_name or loc_id).encode()).hexdigest()[:8], 16)
        lat = base_lat + ((h % 200) - 100) / 6000.0
        lon = base_lon + ((h // 200 % 200) - 100) / 6000.0
        break
    
    event_id = item.get("identifier", "")
    source_url = f"https://kulturdaten.berlin/events/{event_id}" if event_id else ""
    if not source_url: return None
    
    admission = item.get("admission", {})
    is_free = "freeOfCharge" in admission.get("ticketType", "")
    desc = f"Kulturveranstaltung in {borough or 'Berlin'}"
    if is_free: desc += " (Eintritt frei)"
    
    return {
        "title": clean_html(title)[:200], "description": desc,
        "date": event_date, "end_date": event_end,
        "time": ev_time, "end_time": None,
        "location": location_str[:300],
        "latitude": round(lat, 6), "longitude": round(lon, 6),
        "categories": categorize(title, "", borough),
        "source_url": source_url,
        "source": "kulturdaten.berlin",
        "validation_status": "auto_validated"
    }


# ============================================
# OSM Calendar - Worldwide events
# ============================================
def fetch_osm_calendar():
    """Fetch worldwide events from OpenStreetMap Calendar."""
    print("\n🌍 OSM CALENDAR - Worldwide events")
    
    try:
        r = requests.get("https://osmcal.org/api/v2/events/",
            headers={**HEADERS, "Accept": "application/json"}, timeout=15)
        if r.status_code != 200:
            print(f"  HTTP {r.status_code}")
            return []
        
        data = r.json()
    except Exception as e:
        print(f"  Error: {e}")
        return []
    
    events = []
    seen = set()
    
    for item in data:
        ev = parse_osm_event(item)
        if ev:
            key = f"{ev['title'][:40]}|{ev['date']}|{ev['latitude']:.3f}"
            if key not in seen:
                seen.add(key)
                events.append(ev)
    
    print(f"  Total OSM Calendar: {len(events)} events")
    return events


def parse_osm_event(item):
    """Parse OSM Calendar event."""
    title = item.get("name", "")
    if not title: return None
    
    # Date
    date_info = item.get("date", {})
    start = date_info.get("start", "")
    end = date_info.get("end", "")
    
    event_date = start[:10] if start else None
    event_end = end[:10] if end else None
    if not event_date: return None
    if event_end == event_date: event_end = None
    
    try:
        if datetime.strptime(event_date, "%Y-%m-%d").date() < date.today(): return None
    except: pass
    
    # Location
    location = item.get("location", {})
    coords_str = location.get("coords", "")
    if not coords_str: return None
    
    # coords format: "lon,lat" or array
    try:
        if isinstance(coords_str, str):
            parts = coords_str.split(",")
            if len(parts) >= 2:
                # Could be "lat,lon" or "lon,lat" - OSM typically uses lon,lat
                # But osmcal uses lat,lon based on the sample
                lat = float(parts[0].strip())
                lon = float(parts[1].strip())
                # If lat is clearly a longitude (>90 or <-90), swap
                if abs(lat) > 90:
                    lat, lon = lon, lat
        elif isinstance(coords_str, list) and len(coords_str) >= 2:
            lon = float(coords_str[0])
            lat = float(coords_str[1])
        else:
            return None
    except:
        return None
    
    if lat == 0 and lon == 0: return None
    
    location_str = location.get("detailed") or location.get("short") or ""
    
    source_url = item.get("url", "")
    if not source_url: return None
    
    description = f"OpenStreetMap community event. {date_info.get('human', '')}"
    
    return {
        "title": title[:200],
        "description": description[:350],
        "date": event_date,
        "end_date": event_end,
        "time": None,
        "end_time": None,
        "location": location_str[:300],
        "latitude": round(lat, 6),
        "longitude": round(lon, 6),
        "categories": categorize(title, description, "community meetup mapping"),
        "source_url": source_url,
        "source": "OSM Calendar",
        "validation_status": "auto_validated"
    }


# ============================================
# MORE NYC (better import)
# ============================================
NYC_BOROUGH_COORDS = {
    "Manhattan": (40.7831, -73.9712), "Brooklyn": (40.6782, -73.9442),
    "Queens": (40.7282, -73.7949), "Bronx": (40.8448, -73.8648),
    "Staten Island": (40.5795, -74.1502),
}

def fetch_nyc_more():
    """Fetch more diverse NYC events."""
    print("\n🗽 NYC - More events")
    events = []
    seen = set()
    
    # Get diverse event types (skip sport duplicates)
    for event_type in ["Theater", "Concert", "Festival", "Cultural", "Community", "Parade", 
                        "Rally", "Street Fair", "Farmers Market", "Film", "Dance"]:
        try:
            r = requests.get("https://data.cityofnewyork.us/resource/tvpp-9vvx.json",
                params={
                    "$limit": 50,
                    "$where": f"start_date_time > '{TODAY}' AND event_type LIKE '%{event_type}%'",
                    "$order": "start_date_time"
                }, headers=HEADERS, timeout=15)
            if r.status_code != 200: continue
            
            items = r.json()
            for item in items:
                ev = parse_nyc(item)
                if ev:
                    key = f"{ev['title'][:40]}|{ev['date']}"
                    if key not in seen:
                        seen.add(key)
                        events.append(ev)
            
            if items:
                print(f"  {event_type}: {len(items)} items")
            time.sleep(0.5)
        except:
            continue
    
    # Also get general events (non-sport)
    try:
        r = requests.get("https://data.cityofnewyork.us/resource/tvpp-9vvx.json",
            params={
                "$limit": 200,
                "$where": f"start_date_time > '{TODAY}' AND event_type NOT LIKE '%Sport%' AND event_type NOT LIKE '%Non Regulation%'",
                "$order": "start_date_time"
            }, headers=HEADERS, timeout=30)
        if r.status_code == 200:
            items = r.json()
            for item in items:
                ev = parse_nyc(item)
                if ev:
                    key = f"{ev['title'][:40]}|{ev['date']}"
                    if key not in seen:
                        seen.add(key)
                        events.append(ev)
            print(f"  General non-sport: {len(items)} items")
    except:
        pass
    
    print(f"  Total NYC more: {len(events)}")
    return events


def parse_nyc(item):
    title = item.get("event_name", "")
    if not title or "Non Regulation" in title: return None
    
    event_type = item.get("event_type", "")
    borough = item.get("event_borough", "Manhattan")
    location = item.get("event_location", "")
    
    location_str = location
    if borough and borough not in location_str:
        location_str = f"{location_str}, {borough}" if location_str else borough
    location_str += ", New York, USA"
    
    base_lat, base_lon = NYC_BOROUGH_COORDS.get(borough, (40.7128, -74.0060))
    h = int(hashlib.md5((location or title).encode()).hexdigest()[:8], 16)
    lat = base_lat + ((h % 200) - 100) / 8000.0
    lon = base_lon + ((h // 200 % 200) - 100) / 8000.0
    
    start = item.get("start_date_time", "")
    end = item.get("end_date_time", "")
    event_date = start[:10] if start else None
    end_date = end[:10] if end else None
    ev_time = None
    end_time = None
    
    if not event_date: return None
    if start and "T" in start: 
        h_str = start[11:16]
        if h_str != "00:00": ev_time = h_str
    if end and "T" in end:
        h_str = end[11:16]
        if h_str != "00:00": end_time = h_str
    if end_date == event_date: end_date = None
    
    try:
        check = end_date or event_date
        if datetime.strptime(check, "%Y-%m-%d").date() < date.today(): return None
    except: pass
    
    source_url = "https://data.cityofnewyork.us/City-Government/NYC-Permitted-Event-Information/tvpp-9vvx"
    
    full_title = f"{title} ({event_type})" if event_type and event_type not in title else title
    desc = f"Event in {borough}, New York. Type: {event_type}." if event_type else f"Event in {borough}, New York."
    
    return {
        "title": full_title[:200], "description": desc,
        "date": event_date, "end_date": end_date,
        "time": ev_time, "end_time": end_time,
        "location": location_str[:300],
        "latitude": round(lat, 6), "longitude": round(lon, 6),
        "categories": categorize(full_title, desc, event_type),
        "source_url": source_url,
        "source": "NYC Open Data",
        "validation_status": "auto_validated"
    }


# ============================================
# MAIN
# ============================================
def main():
    print("=" * 60)
    print("IMPORT WAVE 7 - More Berlin + OSM + More NYC")
    print("=" * 60)
    
    results = {}
    
    # More Berlin
    berlin_events = fetch_berlin_more()
    if berlin_events:
        n = send_all(berlin_events, "Berlin more")
        results["Berlin (pages 7-20)"] = n
        print(f"  ✅ Berlin: {n}")
    
    # OSM Calendar
    osm_events = fetch_osm_calendar()
    if osm_events:
        n = send_all(osm_events, "OSM Calendar")
        results["OSM Calendar worldwide"] = n
        print(f"  ✅ OSM Calendar: {n}")
    
    # More NYC
    nyc_events = fetch_nyc_more()
    if nyc_events:
        n = send_all(nyc_events, "NYC more")
        results["NYC (diverse types)"] = n
        print(f"  ✅ NYC: {n}")
    
    # Summary
    print(f"\n{'=' * 60}")
    print("RÉSUMÉ WAVE 7:")
    total = 0
    for source, count in results.items():
        print(f"  {source}: {count}")
        total += count
    print(f"  TOTAL: {total}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
