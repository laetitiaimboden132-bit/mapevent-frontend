"""
Import Wave 8 - More Helsinki + More Berlin + Toronto + French city portals
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
    if any(w in c for w in ["konzert", "concert", "music", "musik", "musique", "musiikki", "konsertti"]):
        if "jazz" in c: cats.append("Musique > Jazz")
        elif any(w in c for w in ["klassik", "classical", "classique"]): cats.append("Musique > Classique")
        elif any(w in c for w in ["electro", "techno", "house", "dj", "club"]): cats.append("Musique > Electronic")
        elif any(w in c for w in ["rock", "metal", "punk"]): cats.append("Musique > Rock")
        elif any(w in c for w in ["hip-hop", "rap"]): cats.append("Musique > Hip-Hop")
        else: cats.append("Musique > Concert")
    if any(w in c for w in ["theater", "theatre", "théâtre", "schauspiel", "teatteri"]): cats.append("Spectacle > Théâtre")
    if any(w in c for w in ["tanz", "dance", "danse", "ballet", "tanssi"]): cats.append("Danse")
    if any(w in c for w in ["ausstellung", "exhibition", "exposition", "galerie", "gallery", "näyttely"]): cats.append("Culture > Exposition")
    if any(w in c for w in ["kino", "film", "cinema", "cinéma", "elokuva"]): cats.append("Culture > Cinéma")
    if any(w in c for w in ["lesung", "literatur", "lecture", "book", "kirja"]): cats.append("Culture > Littérature")
    if any(w in c for w in ["museum", "musée", "museo"]): cats.append("Culture > Musée")
    if any(w in c for w in ["sport", "lauf", "marathon", "run", "urheilu", "hockey", "skating"]): cats.append("Sport")
    if "festival" in c and not cats: cats.append("Festival")
    if any(w in c for w in ["markt", "flohmarkt", "market", "marché", "markkinat", "tori"]): cats.append("Marché & Brocante")
    if any(w in c for w in ["vortrag", "konferenz", "conference", "conférence", "seminar", "workshop"]): cats.append("Conférence")
    if any(w in c for w in ["atelier", "kurs", "cours", "pajapäivä"]): cats.append("Atelier")
    if any(w in c for w in ["kinder", "familie", "children", "enfant", "lapsi", "perhe", "family"]): cats.append("Famille & Enfants")
    if any(w in c for w in ["comedy", "kabarett", "komödie", "humour", "komedia"]): cats.append("Spectacle > Humour")
    if any(w in c for w in ["party", "fest ", "feier", "fête", "juhla", "bileet"]): cats.append("Fête")
    if any(w in c for w in ["arts", "exhibit", "art"]): cats.append("Culture > Exposition")
    if not cats: cats.append("Événement")
    return list(dict.fromkeys(cats))[:3]


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


# ============================================
# MORE HELSINKI (pages 26-50)
# ============================================
def fetch_helsinki_more():
    """Fetch more Helsinki events from LinkedEvents."""
    print("\n🇫🇮 HELSINKI MORE - pages 26-50")
    events = []
    seen = set()

    for page in range(26, 51):
        try:
            r = requests.get("https://api.hel.fi/linkedevents/v1/event/",
                params={"page_size": 100, "page": page, "start": TODAY, "format": "json"},
                headers=HEADERS, timeout=30)
            if r.status_code != 200:
                print(f"  Page {page}: HTTP {r.status_code}")
                break

            data = r.json()
            items = data.get("data", [])
            if not items: break

            for item in items:
                ev = parse_helsinki(item)
                if ev:
                    key = f"{ev['title'][:40]}|{ev['date']}|{ev['latitude']:.3f}"
                    if key not in seen:
                        seen.add(key)
                        events.append(ev)

            print(f"  Page {page}: {len(items)} items → {len(events)} total")
            time.sleep(0.5)
        except Exception as e:
            print(f"  Page {page}: error {str(e)[:60]}")
            break

    print(f"  Total Helsinki more: {len(events)}")
    return events


def parse_helsinki(item):
    name = item.get("name", {})
    title = name.get("fi") or name.get("en") or name.get("sv") or ""
    if not title: return None

    desc_obj = item.get("short_description", {}) or item.get("description", {})
    desc = clean_html(desc_obj.get("fi") or desc_obj.get("en") or "")

    start = item.get("start_time", "")
    end = item.get("end_time", "")
    event_date = start[:10] if start else None
    end_date = end[:10] if end else None
    if not event_date: return None
    if end_date == event_date: end_date = None

    ev_time = None
    if start and "T" in start:
        t = start.split("T")[1][:5]
        if t != "00:00": ev_time = t

    try:
        check = end_date or event_date
        if datetime.strptime(check, "%Y-%m-%d").date() < date.today(): return None
    except: pass

    loc = item.get("location", {})
    if not loc: return None
    pos = loc.get("position", {})
    coords = pos.get("coordinates", [])
    if not coords or len(coords) < 2: return None
    lon, lat = coords[0], coords[1]

    if not (59.0 < lat < 70.5 and 19.0 < lon < 32.0): return None

    loc_name_obj = loc.get("name", {})
    loc_name = loc_name_obj.get("fi") or loc_name_obj.get("en") or ""
    street_obj = loc.get("street_address", {})
    street = street_obj.get("fi") or street_obj.get("en") or ""
    location_str = f"{loc_name}, {street}".strip(", ") if street else loc_name
    if location_str:
        location_str += ", Finland"
    else:
        location_str = "Finland"

    info_url = item.get("info_url", {})
    source_url = ""
    if isinstance(info_url, dict):
        source_url = info_url.get("fi") or info_url.get("en") or ""
    elif isinstance(info_url, str):
        source_url = info_url

    if not source_url:
        event_id = item.get("id", "")
        source_url = f"https://tapahtumat.hel.fi/en/events/{event_id}" if event_id else ""

    if not source_url: return None

    return {
        "title": title[:200], "description": desc[:350],
        "date": event_date, "end_date": end_date,
        "time": ev_time, "end_time": None,
        "location": location_str[:300],
        "latitude": round(lat, 6), "longitude": round(lon, 6),
        "categories": categorize(title, desc),
        "source_url": source_url,
        "source": "Helsinki LinkedEvents",
        "validation_status": "auto_validated"
    }


# ============================================
# MORE BERLIN (pages 21-40)
# ============================================
BERLIN_BOROUGHS = {
    "Mitte": (52.5200, 13.4050), "Friedrichshain-Kreuzberg": (52.5000, 13.4400),
    "Pankow": (52.5700, 13.4100), "Charlottenburg-Wilmersdorf": (52.5050, 13.2900),
    "Spandau": (52.5340, 13.2000), "Steglitz-Zehlendorf": (52.4340, 13.2400),
    "Tempelhof-Schöneberg": (52.4670, 13.3500), "Neukölln": (52.4400, 13.4400),
    "Treptow-Köpenick": (52.4500, 13.5800), "Marzahn-Hellersdorf": (52.5400, 13.6000),
    "Lichtenberg": (52.5200, 13.5000), "Reinickendorf": (52.5900, 13.3300),
}

def fetch_berlin_more():
    """Fetch Berlin events pages 21-40."""
    print("\n🇩🇪 BERLIN MORE - pages 21-40")
    base = "https://api-v2.kulturdaten.berlin/api"
    events = []
    seen = set()
    loc_cache = {}

    for page in range(21, 41):
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
            print(f"  Page {page}: error {str(e)[:60]}")
            break

    print(f"  Total Berlin more: {len(events)}")
    return events


def parse_berlin(item, api_base, loc_cache):
    attractions = item.get("attractions", [])
    title = ""
    for attr in attractions:
        label = attr.get("referenceLabel", {})
        title = label.get("de") or label.get("en") or ""
        if title: break
    if not title: return None

    schedule = item.get("schedule", {})
    start_date = schedule.get("startDate", "")
    end_date_raw = schedule.get("endDate", "")
    start_time = schedule.get("startTime", "")

    if not start_date: return None
    event_date = start_date[:10]
    event_end = end_date_raw[:10] if end_date_raw else None
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
        location_str += ", Berlin"

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
# TORONTO FESTIVALS & EVENTS
# ============================================
TORONTO_NEIGHBORHOODS = {
    "Toronto": (43.6532, -79.3832),
    "North York": (43.7615, -79.4111),
    "Scarborough": (43.7731, -79.2574),
    "Etobicoke": (43.6205, -79.5132),
    "East York": (43.6911, -79.3280),
    "York": (43.6897, -79.4908),
    "Downtown": (43.6510, -79.3470),
}

def fetch_toronto():
    """Fetch Toronto Festivals & Events."""
    print("\n🇨🇦 TORONTO - Festivals & Events")
    
    try:
        r = requests.get(
            "https://ckan0.cf.opendata.inter.prod-toronto.ca/dataset/9201059e-43ed-4369-885e-0b867652feac/resource/8900fdb2-7f6c-4f50-8581-b463311ff05d/download/file.json",
            headers=HEADERS, timeout=30)
        if r.status_code != 200:
            print(f"  HTTP {r.status_code}")
            return []
        data = r.json()
    except Exception as e:
        print(f"  Error: {e}")
        return []
    
    items = data.get("value", data) if isinstance(data, dict) else data
    if not isinstance(items, list):
        print(f"  Unexpected data format")
        return []
    
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
    
    event_date = cal_date[:10]
    try:
        if datetime.strptime(event_date, "%Y-%m-%d").date() < date.today():
            return None
    except:
        return None
    
    # Get location from event_dates array or direct field
    location_str = "Toronto, ON, Canada"
    lat, lon = 43.6532, -79.3832
    
    event_dates = item.get("event_dates", [])
    if event_dates:
        first_loc = None
        for ed in event_dates:
            locs = ed.get("locations", [])
            if locs:
                first_loc = locs[0]
                break
        if first_loc:
            location_str = first_loc
            # Extract neighborhood for geocoding
            for hood, coords in TORONTO_NEIGHBORHOODS.items():
                if hood.lower() in first_loc.lower():
                    lat, lon = coords
                    break
            # Add variance based on location name
            h = int(hashlib.md5(first_loc.encode()).hexdigest()[:8], 16)
            lat += ((h % 200) - 100) / 8000.0
            lon += ((h // 200 % 200) - 100) / 8000.0
    
    # Category
    categories_raw = item.get("event_category", [])
    cat_str = " ".join(categories_raw) if isinstance(categories_raw, list) else str(categories_raw)
    
    # Time
    time_of_day = item.get("calendar_time_of_day", "")
    ev_time = None  # No specific time extraction from this format
    
    # Cost
    cost = item.get("cost_notes") or ""
    accessible = item.get("accessible_event", "")
    
    desc = f"Event in Toronto. {cat_str}."
    if "free" in str(cost).lower() or "free" in title.lower():
        desc += " Free admission."
    if accessible == "Yes":
        desc += " Accessible."
    
    source_url = "https://www.toronto.ca/explore-enjoy/festivals-events/"
    
    return {
        "title": title[:200],
        "description": clean_html(desc)[:350],
        "date": event_date,
        "end_date": None,
        "time": ev_time,
        "end_time": None,
        "location": location_str[:300],
        "latitude": round(lat, 6),
        "longitude": round(lon, 6),
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
    print("IMPORT WAVE 8 - Helsinki + Berlin + Toronto")
    print("=" * 60)
    
    results = {}
    
    # Helsinki more
    hel = fetch_helsinki_more()
    if hel:
        n = send_all(hel, "Helsinki")
        results["Helsinki (pages 26-50)"] = n
        print(f"  ✅ Helsinki: {n}")
    
    # Berlin more
    ber = fetch_berlin_more()
    if ber:
        n = send_all(ber, "Berlin")
        results["Berlin (pages 21-40)"] = n
        print(f"  ✅ Berlin: {n}")
    
    # Toronto
    tor = fetch_toronto()
    if tor:
        n = send_all(tor, "Toronto")
        results["Toronto"] = n
        print(f"  ✅ Toronto: {n}")
    
    # Summary
    print(f"\n{'=' * 60}")
    print("RÉSUMÉ WAVE 8:")
    total = 0
    for source, count in results.items():
        print(f"  {source}: {count}")
        total += count
    print(f"  TOTAL: {total}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
