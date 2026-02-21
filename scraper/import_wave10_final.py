"""
Import Wave 10 - Berlin pages 81-115 + France regions (OpenAgenda) + More Montreal/Paris
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
    if any(w in c for w in ["konzert", "concert", "music", "musik", "musique"]):
        if "jazz" in c: cats.append("Musique > Jazz")
        elif any(w in c for w in ["klassik", "classical", "classique"]): cats.append("Musique > Classique")
        elif any(w in c for w in ["electro", "techno", "house", "dj"]): cats.append("Musique > Electronic")
        elif any(w in c for w in ["rock", "metal", "punk"]): cats.append("Musique > Rock")
        else: cats.append("Musique > Concert")
    if any(w in c for w in ["theater", "theatre", "théâtre"]): cats.append("Spectacle > Théâtre")
    if any(w in c for w in ["tanz", "dance", "danse", "ballet"]): cats.append("Danse")
    if any(w in c for w in ["ausstellung", "exhibition", "exposition", "galerie"]): cats.append("Culture > Exposition")
    if any(w in c for w in ["kino", "film", "cinema", "cinéma"]): cats.append("Culture > Cinéma")
    if any(w in c for w in ["museum", "musée", "museo"]): cats.append("Culture > Musée")
    if any(w in c for w in ["sport", "marathon", "running", "football"]): cats.append("Sport")
    if "festival" in c and not cats: cats.append("Festival")
    if any(w in c for w in ["markt", "market", "marché", "brocante", "vide"]): cats.append("Marché & Brocante")
    if any(w in c for w in ["conférence", "conference", "seminar"]): cats.append("Conférence")
    if any(w in c for w in ["atelier", "workshop"]): cats.append("Atelier")
    if any(w in c for w in ["enfant", "famille", "kinder", "family"]): cats.append("Famille & Enfants")
    if any(w in c for w in ["humour", "comedy"]): cats.append("Spectacle > Humour")
    if any(w in c for w in ["fête", "soirée", "party"]): cats.append("Fête")
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
# BERLIN PAGES 81-115
# ============================================
BERLIN_BOROUGHS = {
    "Mitte": (52.5200, 13.4050), "Friedrichshain-Kreuzberg": (52.5000, 13.4400),
    "Pankow": (52.5700, 13.4100), "Charlottenburg-Wilmersdorf": (52.5050, 13.2900),
    "Spandau": (52.5340, 13.2000), "Steglitz-Zehlendorf": (52.4340, 13.2400),
    "Tempelhof-Schöneberg": (52.4670, 13.3500), "Neukölln": (52.4400, 13.4400),
    "Treptow-Köpenick": (52.4500, 13.5800), "Marzahn-Hellersdorf": (52.5400, 13.6000),
    "Lichtenberg": (52.5200, 13.5000), "Reinickendorf": (52.5900, 13.3300),
}

def fetch_berlin_batch(start_page, end_page):
    print(f"\n🇩🇪 BERLIN - pages {start_page}-{end_page}")
    base = "https://api-v2.kulturdaten.berlin/api"
    events = []
    seen = set()
    loc_cache = {}

    for page in range(start_page, end_page + 1):
        try:
            r = requests.get(f"{base}/events", params={
                "page": page, "pageSize": 100, "startDate": TODAY
            }, headers=HEADERS, timeout=30)
            if r.status_code != 200: break

            data = r.json()
            items = data.get("data", {}).get("events", [])
            total_available = data.get("data", {}).get("totalCount", 0)
            if not items: break

            for item in items:
                ev = parse_berlin(item, base, loc_cache)
                if ev:
                    key = f"{ev['title'][:40]}|{ev['date']}|{ev['latitude']:.3f}"
                    if key not in seen:
                        seen.add(key)
                        events.append(ev)

            if page % 10 == 0:
                print(f"  Page {page}/{end_page}: {len(events)} events (avail: {total_available})")
            if page * 100 >= total_available:
                print(f"  Reached end at page {page} ({total_available} total)")
                break
            time.sleep(1)
        except Exception as e:
            print(f"  Page {page}: error {str(e)[:60]}")
            time.sleep(2)
            continue

    print(f"  Total Berlin: {len(events)}")
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
        if street and street not in location_str:
            location_str = f"{location_str}, {street}" if location_str else street
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
        "source_url": source_url, "source": "kulturdaten.berlin",
        "validation_status": "auto_validated"
    }


# ============================================
# FRANCE - OpenAgenda by REGION
# ============================================
def fetch_france_regions():
    """Fetch France events by region."""
    print("\n🇫🇷 FRANCE - OpenAgenda by region")
    base = "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/evenements-publics-openagenda/records"
    
    regions = [
        "Normandie", "Bretagne", "Pays de la Loire", "Centre-Val de Loire",
        "Bourgogne-Franche-Comté", "Grand Est", "Hauts-de-France",
        "Nouvelle-Aquitaine", "Auvergne-Rhône-Alpes", "Occitanie",
        "Provence-Alpes-Côte d'Azur", "Corse",
    ]
    
    all_events = []
    seen = set()
    
    for region in regions:
        offset = 0
        region_count = 0
        while offset < 500:  # Max 500 per region
            try:
                r = requests.get(base, params={
                    "where": f"location_region='{region}' AND firstdate_begin >= '{TODAY}'",
                    "limit": 100,
                    "offset": offset,
                    "select": "title,description,longdescription_fr,firstdate_begin,lastdate_end,location_coordinates,location_address,location_city,source_url,keywords_fr"
                }, headers=HEADERS, timeout=15)
                
                if r.status_code != 200: break
                data = r.json()
                records = data.get("results", [])
                total = data.get("total_count", 0)
                if not records: break
                
                for record in records:
                    ev = parse_openagenda(record)
                    if ev:
                        key = f"{ev['title'][:40]}|{ev['date']}|{ev['latitude']:.3f}"
                        if key not in seen:
                            seen.add(key)
                            all_events.append(ev)
                            region_count += 1
                
                offset += 100
                if offset >= total: break
                time.sleep(0.5)
            except:
                break
        
        if region_count > 0:
            print(f"  {region}: {region_count} new events")
    
    print(f"  Total France regions: {len(all_events)}")
    return all_events


def parse_openagenda(record):
    title = record.get("title", "")
    if not title: return None
    
    desc = clean_html(record.get("longdescription_fr") or record.get("description") or "")
    
    first_date = record.get("firstdate_begin", "")
    last_date = record.get("lastdate_end", "")
    event_date = first_date[:10] if first_date else None
    end_date = last_date[:10] if last_date else None
    if not event_date: return None
    if end_date == event_date: end_date = None
    
    ev_time = None
    if first_date and "T" in first_date:
        t = first_date.split("T")[1][:5]
        if t not in ("00:00", "23:59"): ev_time = t
    
    try:
        check = end_date or event_date
        if datetime.strptime(check, "%Y-%m-%d").date() < date.today(): return None
    except: pass
    
    coords = record.get("location_coordinates", {})
    lat = lon = None
    if isinstance(coords, dict):
        lat = coords.get("lat")
        lon = coords.get("lon")
    elif isinstance(coords, list) and len(coords) >= 2:
        lat, lon = coords[0], coords[1]
    
    if not lat or not lon: return None
    if not (41.0 < float(lat) < 51.5 and -5.5 < float(lon) < 10.0): return None
    
    city = record.get("location_city", "")
    address = record.get("location_address", "")
    location_str = f"{address}, {city}" if address else city
    if not location_str: location_str = "France"
    location_str += ", France"
    
    source_url = record.get("source_url") or ""
    if not source_url: return None
    
    kw = " ".join(record.get("keywords_fr", []) or [])
    
    return {
        "title": title[:200], "description": desc[:350],
        "date": event_date, "end_date": end_date,
        "time": ev_time, "end_time": None,
        "location": location_str[:300],
        "latitude": round(float(lat), 6), "longitude": round(float(lon), 6),
        "categories": categorize(title, desc, kw),
        "source_url": source_url, "source": "OpenAgenda",
        "validation_status": "auto_validated"
    }


# ============================================
# MORE PARIS (page 2+)
# ============================================
def fetch_paris_more():
    """Fetch more Paris events from opendata.paris.fr."""
    print("\n🇫🇷 PARIS - More events (offset 100+)")
    base = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/que-faire-a-paris-/records"
    
    events = []
    seen = set()
    
    for offset in range(100, 500, 100):
        try:
            r = requests.get(base, params={
                "where": f"date_start >= '{TODAY}'",
                "limit": 100,
                "offset": offset,
                "order_by": "date_start"
            }, headers=HEADERS, timeout=15)
            
            if r.status_code != 200: break
            data = r.json()
            records = data.get("results", [])
            if not records: break
            
            for rec in records:
                ev = parse_paris(rec)
                if ev:
                    key = f"{ev['title'][:40]}|{ev['date']}"
                    if key not in seen:
                        seen.add(key)
                        events.append(ev)
            
            print(f"  Offset {offset}: {len(records)} records → {len(events)} total")
            time.sleep(0.5)
        except:
            break
    
    print(f"  Total Paris more: {len(events)}")
    return events


def parse_paris(rec):
    title = rec.get("title", "")
    if not title: return None
    
    desc = clean_html(rec.get("description") or rec.get("lead_text") or "")
    
    date_start = rec.get("date_start", "")
    date_end = rec.get("date_end", "")
    event_date = date_start[:10] if date_start else None
    end_date = date_end[:10] if date_end else None
    if not event_date: return None
    if end_date == event_date: end_date = None
    
    try:
        check = end_date or event_date
        if datetime.strptime(check, "%Y-%m-%d").date() < date.today(): return None
    except: pass
    
    # Coordinates
    lat_lon = rec.get("lat_lon") or rec.get("geo_point_2d", {})
    lat = lon = None
    if isinstance(lat_lon, dict):
        lat = lat_lon.get("lat")
        lon = lat_lon.get("lon")
    elif isinstance(lat_lon, list) and len(lat_lon) >= 2:
        lat, lon = lat_lon[0], lat_lon[1]
    
    if not lat or not lon: return None
    if not (48.7 < float(lat) < 49.0 and 2.1 < float(lon) < 2.6): return None
    
    address = rec.get("address_street") or rec.get("address_name") or ""
    city = rec.get("address_city") or "Paris"
    zipcode = rec.get("address_zipcode") or ""
    location_str = f"{address}, {zipcode} {city}".strip(", ")
    
    source_url = rec.get("url") or ""
    if not source_url: return None
    
    return {
        "title": title[:200], "description": desc[:350],
        "date": event_date, "end_date": end_date,
        "time": None, "end_time": None,
        "location": location_str[:300],
        "latitude": round(float(lat), 6), "longitude": round(float(lon), 6),
        "categories": categorize(title, desc),
        "source_url": source_url, "source": "Paris Open Data",
        "validation_status": "auto_validated"
    }


# ============================================
# MAIN
# ============================================
def main():
    print("=" * 60)
    print("IMPORT WAVE 10 - Berlin final + France regions + Paris")
    print("=" * 60)
    
    results = {}
    
    # Berlin pages 81-115
    berlin = fetch_berlin_batch(81, 115)
    if berlin:
        n = send_all(berlin, "Berlin 81-115")
        results["Berlin (pages 81-115)"] = n
        print(f"  ✅ Berlin: {n}")
    
    # France regions via OpenAgenda
    france = fetch_france_regions()
    if france:
        n = send_all(france, "France regions")
        results["France regions"] = n
        print(f"  ✅ France: {n}")
    
    # More Paris
    paris = fetch_paris_more()
    if paris:
        n = send_all(paris, "Paris more")
        results["Paris more"] = n
        print(f"  ✅ Paris: {n}")
    
    # Summary
    print(f"\n{'=' * 60}")
    print("RÉSUMÉ WAVE 10:")
    total = 0
    for source, count in results.items():
        print(f"  {source}: {count}")
        total += count
    print(f"  TOTAL: {total}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
