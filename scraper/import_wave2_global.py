"""
Import Wave 2 - More countries via OpenAgenda + NYC Open Data.
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
ODS_BASE = "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/evenements-publics-openagenda/records"


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
    cats = []
    combined = f"{title} {description} {keywords_str}".lower()
    
    if any(w in combined for w in ["concert", "music", "musiikki", "musique", "orchestra", "symphon", "choir", "gig", "live band"]):
        if "jazz" in combined: cats.append("Musique > Jazz")
        elif any(w in combined for w in ["classical", "classique", "klassik"]): cats.append("Musique > Classique")
        elif any(w in combined for w in ["electro", "techno", "house", "dj"]): cats.append("Musique > Electronic")
        elif any(w in combined for w in ["rock", "metal", "punk"]): cats.append("Musique > Rock")
        elif any(w in combined for w in ["hip-hop", "hip hop", "rap"]): cats.append("Musique > Hip-Hop")
        elif "folk" in combined: cats.append("Musique > Folk")
        elif "blues" in combined: cats.append("Musique > Blues")
        else: cats.append("Musique > Concert")
    if any(w in combined for w in ["theatre", "theater", "théâtre", "play ", "drama"]):
        cats.append("Spectacle > Théâtre")
    if any(w in combined for w in ["dance", "danse", "ballet"]):
        cats.append("Danse")
    if any(w in combined for w in ["comedy", "comédie", "humour", "stand-up"]):
        cats.append("Spectacle > Humour")
    if any(w in combined for w in ["exhibition", "exposition", "exhibit", "gallery", "galerie"]):
        cats.append("Culture > Exposition")
    if any(w in combined for w in ["museum", "musée", "museo"]):
        cats.append("Culture > Musée")
    if any(w in combined for w in ["cinema", "cinéma", "film ", "movie", "screening"]):
        cats.append("Culture > Cinéma")
    if any(w in combined for w in ["marathon", "running", "course ", "trail"]):
        cats.append("Sport > Course à pied")
    if any(w in combined for w in ["football", "soccer"]):
        cats.append("Sport > Football")
    if any(w in combined for w in ["baseball"]):
        cats.append("Sport > Baseball")
    if any(w in combined for w in ["basketball", "basket"]):
        cats.append("Sport > Basketball")
    if any(w in combined for w in ["yoga", "pilates"]):
        cats.append("Sport > Yoga & Bien-être")
    if any(w in combined for w in ["sport", "athletic"]):
        if not any("Sport" in c for c in cats): cats.append("Sport")
    if "festival" in combined:
        if not cats: cats.append("Festival")
    if any(w in combined for w in ["food", "gastro", "wine", "beer", "tasting", "dégustation"]):
        cats.append("Gastronomie > Dégustation")
    if any(w in combined for w in ["market", "marché", "brocante", "flea"]):
        cats.append("Marché & Brocante")
    if any(w in combined for w in ["conference", "conférence", "seminar"]):
        cats.append("Conférence")
    if any(w in combined for w in ["workshop", "atelier"]):
        cats.append("Atelier")
    if any(w in combined for w in ["children", "kids", "family", "enfant", "famille"]):
        cats.append("Famille & Enfants")
    if any(w in combined for w in ["party", "fête", "carnival", "carnaval"]):
        if not any("Fête" in c for c in cats): cats.append("Fête")
    if not cats:
        cats.append("Événement")
    return cats[:3]


def send_batch(events, label=""):
    if not events:
        return 0
    try:
        r = requests.post(f"{API_BASE}/events/scraped/batch", json={"events": events}, headers=HEADERS, timeout=60)
        if r.status_code in (200, 201):
            return r.json().get("inserted", r.json().get("count", len(events)))
        else:
            print(f"  ⚠ Batch error {label}: HTTP {r.status_code}")
            return 0
    except Exception as e:
        print(f"  ❌ Batch error {label}: {e}")
        return 0


def send_all(events, source_name):
    total = 0
    for i in range(0, len(events), 10):
        batch = events[i:i+10]
        n = send_batch(batch, source_name)
        total += n
        if i + 10 < len(events):
            time.sleep(0.5)
    return total


# ============================================
# OpenAgenda - Various countries
# ============================================
def fetch_openagenda_country(country_code, country_name, max_events=100):
    """Fetch events for a country from OpenAgenda."""
    events = []
    seen = set()
    offset = 0
    
    while len(events) < max_events:
        try:
            params = {
                "where": f'location_countrycode="{country_code}" AND firstdate_begin >= "{TODAY}"',
                "limit": min(100, max_events - len(events)),
                "offset": offset,
                "order_by": "firstdate_begin"
            }
            r = requests.get(ODS_BASE, params=params, headers=HEADERS, timeout=20)
            if r.status_code != 200:
                break
            
            data = r.json()
            results = data.get("results", [])
            if not results:
                break
            
            for record in results:
                ev = parse_oa_generic(record, country_name)
                if ev:
                    key = f"{ev['title'][:40]}|{ev['date']}|{ev['latitude']:.3f}"
                    if key not in seen:
                        seen.add(key)
                        events.append(ev)
            
            offset += len(results)
            if len(results) < 50:
                break
            time.sleep(0.5)
            
        except Exception as e:
            print(f"  Error {country_name}: {e}")
            break
    
    return events


def parse_oa_generic(record, country_name):
    """Parse OpenAgenda record for any country."""
    title = record.get("title_fr") or record.get("title") or ""
    if not title:
        return None
    
    desc = record.get("description_fr") or record.get("description") or ""
    description = clean_html(desc)
    
    loc_name = record.get("location_name") or ""
    loc_addr = record.get("location_address") or ""
    loc_city = record.get("location_city") or ""
    
    location_str = loc_name
    if loc_addr:
        location_str += f", {loc_addr}" if location_str else loc_addr
    if loc_city and loc_city not in location_str:
        location_str += f", {loc_city}"
    if country_name and country_name not in location_str:
        location_str += f", {country_name}"
    
    coords = record.get("location_coordinates")
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
    
    if lat == 0 and lon == 0:
        return None
    
    # Dates
    fb = record.get("firstdate_begin") or ""
    le = record.get("lastdate_end") or ""
    
    event_date = fb[:10] if fb else None
    end_date = le[:10] if le else None
    event_time = None
    
    if not event_date:
        return None
    if end_date == event_date:
        end_date = None
    
    if fb and len(fb) >= 16 and "T" in fb:
        h = fb[11:16]
        if h != "00:00":
            event_time = h
    
    try:
        check = end_date or event_date
        if datetime.strptime(check, "%Y-%m-%d").date() < date.today():
            return None
    except:
        pass
    
    source_url = record.get("canonicalurl") or ""
    if not source_url:
        return None
    
    keywords = []
    kw = record.get("keywords_fr")
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
        "time": event_time,
        "end_time": None,
        "location": location_str[:300],
        "latitude": round(lat, 6),
        "longitude": round(lon, 6),
        "categories": categories,
        "source_url": source_url,
        "source": f"OpenAgenda - {loc_city or country_name}",
        "validation_status": "auto_validated"
    }


# ============================================
# NYC Open Data Events
# ============================================
NYC_BOROUGH_COORDS = {
    "Manhattan": (40.7831, -73.9712),
    "Brooklyn": (40.6782, -73.9442),
    "Queens": (40.7282, -73.7949),
    "Bronx": (40.8448, -73.8648),
    "Staten Island": (40.5795, -74.1502),
}

def fetch_nyc_events(max_events=400):
    """Fetch NYC events from open data."""
    events = []
    seen = set()
    offset = 0
    
    while len(events) < max_events:
        try:
            params = {
                "$limit": 200,
                "$offset": offset,
                "$where": f"start_date_time > '{TODAY}'",
                "$order": "start_date_time"
            }
            r = requests.get("https://data.cityofnewyork.us/resource/tvpp-9vvx.json",
                             params=params, headers=HEADERS, timeout=30)
            if r.status_code != 200:
                break
            
            items = r.json()
            if not items:
                break
            
            for item in items:
                ev = parse_nyc_event(item)
                if ev:
                    key = f"{ev['title'][:40]}|{ev['date']}"
                    if key not in seen:
                        seen.add(key)
                        events.append(ev)
            
            offset += len(items)
            if len(items) < 200:
                break
            time.sleep(1)
            
        except Exception as e:
            print(f"  NYC error: {e}")
            break
    
    return events


def parse_nyc_event(item):
    """Parse NYC open data event."""
    title = item.get("event_name", "")
    if not title:
        return None
    
    # Skip very generic sport events (too many similar)
    event_type = item.get("event_type", "")
    if "Non Regulation" in title:
        return None
    
    borough = item.get("event_borough", "Manhattan")
    location_str = item.get("event_location", "")
    
    if borough:
        if borough not in location_str:
            location_str = f"{location_str}, {borough}" if location_str else borough
        location_str += ", New York, USA"
    
    # Get approximate coordinates from borough
    base_lat, base_lon = NYC_BOROUGH_COORDS.get(borough, (40.7128, -74.0060))
    
    # Add small offset based on location string for uniqueness
    h = int(hashlib.md5((location_str or title).encode()).hexdigest()[:8], 16)
    lat = base_lat + ((h % 200) - 100) / 8000.0
    lon = base_lon + ((h // 200 % 200) - 100) / 8000.0
    
    # Dates
    start = item.get("start_date_time", "")
    end = item.get("end_date_time", "")
    
    event_date = start[:10] if start else None
    end_date = end[:10] if end else None
    event_time = None
    end_time = None
    
    if not event_date:
        return None
    
    if start and len(start) >= 16 and "T" in start:
        h_str = start[11:16]
        if h_str != "00:00":
            event_time = h_str
    
    if end and len(end) >= 16 and "T" in end:
        h_str = end[11:16]
        if h_str != "00:00":
            end_time = h_str
    
    if end_date == event_date:
        end_date = None
    
    try:
        check = end_date or event_date
        if datetime.strptime(check, "%Y-%m-%d").date() < date.today():
            return None
    except:
        pass
    
    # Source URL - NYC open data event page
    event_id = item.get("event_id", "")
    source_url = f"https://data.cityofnewyork.us/City-Government/NYC-Permitted-Event-Information/tvpp-9vvx"
    
    categories = categorize_generic(title, event_type)
    
    return {
        "title": f"{title} ({event_type})" if event_type and event_type not in title else title,
        "description": f"Event in {borough}, New York. Type: {event_type}." if event_type else f"Event in {borough}, New York.",
        "date": event_date,
        "end_date": end_date,
        "time": event_time,
        "end_time": end_time,
        "location": location_str[:300],
        "latitude": round(lat, 6),
        "longitude": round(lon, 6),
        "categories": categories,
        "source_url": source_url,
        "source": "NYC Open Data",
        "validation_status": "auto_validated"
    }


# ============================================
# MAIN
# ============================================
def main():
    print("=" * 60)
    print("IMPORT WAVE 2 - OpenAgenda countries + NYC")
    print("=" * 60)
    
    all_results = {}
    
    # OpenAgenda countries
    oa_countries = [
        ("DE", "Deutschland", 50),
        ("ES", "España", 50),
        ("CH", "Suisse", 100),
        ("MQ", "Martinique", 30),
        ("GP", "Guadeloupe", 10),
        ("CA", "Canada", 15),
        ("RE", "La Réunion", 5),
    ]
    
    for cc, name, limit in oa_countries:
        print(f"\n🌍 {name} (OpenAgenda {cc})")
        events = fetch_openagenda_country(cc, name, limit)
        if events:
            n = send_all(events, name)
            all_results[name] = n
            print(f"  ✅ {name}: {n} events importés")
        else:
            print(f"  ⚠ {name}: 0 events")
        time.sleep(1)
    
    # NYC
    print(f"\n🗽 NEW YORK CITY (NYC Open Data)")
    nyc_events = fetch_nyc_events(max_events=300)
    if nyc_events:
        n = send_all(nyc_events, "NYC")
        all_results["NYC"] = n
        print(f"  ✅ NYC: {n} events importés")
    
    # Summary
    print(f"\n{'=' * 60}")
    print("RÉSUMÉ WAVE 2:")
    total = 0
    for source, count in all_results.items():
        print(f"  {source}: {count} events")
        total += count
    print(f"  TOTAL: {total} events importés")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
