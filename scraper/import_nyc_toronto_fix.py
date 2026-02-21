"""
Re-import NYC and Toronto with UNIQUE source_urls per event.
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


def categorize(title, desc="", kw=""):
    cats = []
    c = f"{title} {desc} {kw}".lower()
    if any(w in c for w in ["concert", "music"]): cats.append("Musique > Concert")
    if any(w in c for w in ["theater", "theatre"]): cats.append("Spectacle > Théâtre")
    if any(w in c for w in ["dance"]): cats.append("Danse")
    if any(w in c for w in ["exhibition", "gallery", "arts"]): cats.append("Culture > Exposition")
    if any(w in c for w in ["film", "cinema"]): cats.append("Culture > Cinéma")
    if any(w in c for w in ["museum"]): cats.append("Culture > Musée")
    if any(w in c for w in ["sport", "marathon", "run"]): cats.append("Sport")
    if "festival" in c and not cats: cats.append("Festival")
    if any(w in c for w in ["market", "farmers"]): cats.append("Marché & Brocante")
    if any(w in c for w in ["parade", "rally"]): cats.append("Fête")
    if any(w in c for w in ["community"]): cats.append("Événement")
    if any(w in c for w in ["family", "children"]): cats.append("Famille & Enfants")
    if not cats: cats.append("Événement")
    return list(dict.fromkeys(cats))[:3]


def send_all(events, name):
    total = 0
    for i in range(0, len(events), 10):
        batch = events[i:i+10]
        try:
            r = requests.post(f"{API_BASE}/events/scraped/batch", json={"events": batch}, headers=HEADERS, timeout=60)
            if r.status_code in (200, 201):
                resp = r.json()
                created = resp.get("results", {}).get("created", 0)
                skipped = resp.get("results", {}).get("skipped", 0)
                total += created
                if i == 0:
                    print(f"  First batch: created={created}, skipped={skipped}")
        except Exception as e:
            if i == 0:
                print(f"  Error: {e}")
        if i + 10 < len(events):
            time.sleep(0.5)
    return total


# ============================================
# NYC EVENTS (with unique source_urls)
# ============================================
NYC_BOROUGH_COORDS = {
    "Manhattan": (40.7831, -73.9712), "Brooklyn": (40.6782, -73.9442),
    "Queens": (40.7282, -73.7949), "Bronx": (40.8448, -73.8648),
    "Staten Island": (40.5795, -74.1502),
}

def fetch_nyc():
    """Fetch NYC events with unique source_urls."""
    print("\n🗽 NYC EVENTS")
    events = []
    seen = set()
    
    try:
        # Get diverse events (non-sport)
        r = requests.get("https://data.cityofnewyork.us/resource/tvpp-9vvx.json",
            params={
                "$limit": 1000,
                "$where": f"start_date_time > '{TODAY}' AND event_type != 'Non Regulation Sports'",
                "$order": "start_date_time"
            }, headers=HEADERS, timeout=30)
        
        if r.status_code != 200:
            print(f"  HTTP {r.status_code}")
            return []
        
        items = r.json()
        print(f"  Raw items: {len(items)}")
        
        for item in items:
            ev = parse_nyc(item)
            if ev:
                key = f"{ev['title'][:40]}|{ev['date']}"
                if key not in seen:
                    seen.add(key)
                    events.append(ev)
    except Exception as e:
        print(f"  Error: {e}")
    
    print(f"  Total NYC: {len(events)}")
    return events


def parse_nyc(item):
    title = item.get("event_name", "")
    if not title: return None
    
    event_type = item.get("event_type", "")
    event_id = item.get("event_id", "")
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
    ev_time = end_time = None
    
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
    
    # CRITICAL: Generate UNIQUE source_url per event using event_id
    if event_id:
        source_url = f"https://data.cityofnewyork.us/City-Government/NYC-Permitted-Event-Information/tvpp-9vvx/data?event_id={event_id}"
    else:
        # Use hash of title+date as unique identifier
        uid = hashlib.md5(f"{title}|{event_date}".encode()).hexdigest()[:12]
        source_url = f"https://data.cityofnewyork.us/City-Government/NYC-Permitted-Event-Information/tvpp-9vvx/data?uid={uid}"
    
    full_title = f"{title} ({event_type})" if event_type and event_type not in title else title
    desc = f"Event in {borough}, New York. Type: {event_type}." if event_type else f"Event in {borough}, New York."
    
    return {
        "title": full_title[:200], "description": desc[:350],
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
# TORONTO (with unique source_urls)
# ============================================
TORONTO_NEIGHBORHOODS = {
    "Toronto": (43.6532, -79.3832), "North York": (43.7615, -79.4111),
    "Scarborough": (43.7731, -79.2574), "Etobicoke": (43.6205, -79.5132),
    "East York": (43.6911, -79.3280), "York": (43.6897, -79.4908),
    "Downtown": (43.6510, -79.3470),
}

def fetch_toronto():
    """Fetch Toronto events with unique source_urls."""
    print("\n🇨🇦 TORONTO EVENTS")
    
    try:
        r = requests.get(
            "https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/9201059e-43ed-4369-885e-0b867652feac/resource/8900fdb2-7f6c-4f50-8581-b463311ff05d/download/file.json",
            headers=HEADERS, timeout=30)
        data = r.json()
    except Exception as e:
        print(f"  Error: {e}")
        return []
    
    items = data.get("value", data) if isinstance(data, dict) else data
    print(f"  Raw items: {len(items)}")
    
    events = []
    seen = set()
    
    for item in items:
        ev = parse_toronto(item)
        if ev:
            key = f"{ev['title'][:40]}|{ev['date']}"
            if key not in seen:
                seen.add(key)
                events.append(ev)
    
    print(f"  Total Toronto: {len(events)}")
    return events


def parse_toronto(item):
    title = item.get("calendar_name") or item.get("event_name") or ""
    if not title: return None
    
    cal_date = item.get("calendar_date", "")
    if not cal_date: return None
    cal_id = item.get("calendar_id", "")
    
    event_date = cal_date[:10]
    try:
        if datetime.strptime(event_date, "%Y-%m-%d").date() < date.today(): return None
    except: return None
    
    location_str = "Toronto, ON, Canada"
    lat, lon = 43.6532, -79.3832
    
    event_dates = item.get("event_dates", [])
    if event_dates:
        for ed in event_dates:
            locs = ed.get("locations", [])
            if locs:
                location_str = locs[0]
                for hood, coords in TORONTO_NEIGHBORHOODS.items():
                    if hood.lower() in location_str.lower():
                        lat, lon = coords
                        break
                h = int(hashlib.md5(location_str.encode()).hexdigest()[:8], 16)
                lat += ((h % 200) - 100) / 8000.0
                lon += ((h // 200 % 200) - 100) / 8000.0
                break
    
    categories_raw = item.get("event_category", [])
    cat_str = " ".join(categories_raw) if isinstance(categories_raw, list) else str(categories_raw)
    
    cost = item.get("cost_notes") or ""
    accessible = item.get("accessible_event", "")
    desc = f"Event in Toronto. {cat_str}."
    if "free" in str(cost).lower(): desc += " Free admission."
    if accessible == "Yes": desc += " Accessible."
    
    # CRITICAL: Unique source_url per event
    if cal_id:
        source_url = f"https://www.toronto.ca/explore-enjoy/festivals-events/?id={cal_id}"
    else:
        uid = hashlib.md5(f"{title}|{event_date}".encode()).hexdigest()[:12]
        source_url = f"https://www.toronto.ca/explore-enjoy/festivals-events/?uid={uid}"
    
    return {
        "title": title[:200], "description": clean_html(desc)[:350],
        "date": event_date, "end_date": None,
        "time": None, "end_time": None,
        "location": location_str[:300],
        "latitude": round(lat, 6), "longitude": round(lon, 6),
        "categories": categorize(title, cat_str),
        "source_url": source_url,
        "source": "Toronto Open Data",
        "validation_status": "auto_validated"
    }


# ============================================
# MAIN
# ============================================
def main():
    print("=" * 60)
    print("RE-IMPORT NYC + TORONTO (unique source_urls)")
    print("=" * 60)
    
    results = {}
    
    # NYC
    nyc = fetch_nyc()
    if nyc:
        n = send_all(nyc, "NYC")
        results["NYC"] = n
        print(f"  ✅ NYC: {n}")
    
    # Toronto
    tor = fetch_toronto()
    if tor:
        n = send_all(tor, "Toronto")
        results["Toronto"] = n
        print(f"  ✅ Toronto: {n}")
    
    # Summary
    print(f"\n{'=' * 60}")
    print("RÉSUMÉ:")
    total = 0
    for source, count in results.items():
        print(f"  {source}: {count}")
        total += count
    print(f"  TOTAL: {total}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
