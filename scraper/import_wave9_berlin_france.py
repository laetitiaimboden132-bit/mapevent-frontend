"""
Import Wave 9 - Berlin pages 41-80 + French city portals (Toulouse, Rennes, Nantes ODS search)
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
        elif any(w in c for w in ["electro", "techno", "house", "dj", "club"]): cats.append("Musique > Electronic")
        elif any(w in c for w in ["rock", "metal", "punk"]): cats.append("Musique > Rock")
        else: cats.append("Musique > Concert")
    if any(w in c for w in ["theater", "theatre", "théâtre", "schauspiel"]): cats.append("Spectacle > Théâtre")
    if any(w in c for w in ["tanz", "dance", "danse", "ballet"]): cats.append("Danse")
    if any(w in c for w in ["ausstellung", "exhibition", "exposition", "galerie", "gallery"]): cats.append("Culture > Exposition")
    if any(w in c for w in ["kino", "film", "cinema", "cinéma"]): cats.append("Culture > Cinéma")
    if any(w in c for w in ["lesung", "literatur", "lecture", "book"]): cats.append("Culture > Littérature")
    if any(w in c for w in ["museum", "musée", "museo"]): cats.append("Culture > Musée")
    if any(w in c for w in ["sport", "lauf", "marathon", "fussball", "football", "running"]): cats.append("Sport")
    if "festival" in c and not cats: cats.append("Festival")
    if any(w in c for w in ["markt", "flohmarkt", "market", "marché", "brocante"]): cats.append("Marché & Brocante")
    if any(w in c for w in ["vortrag", "konferenz", "conference", "conférence", "seminar"]): cats.append("Conférence")
    if any(w in c for w in ["atelier", "workshop", "kurs", "cours"]): cats.append("Atelier")
    if any(w in c for w in ["kinder", "familie", "children", "enfant", "family"]): cats.append("Famille & Enfants")
    if any(w in c for w in ["comedy", "kabarett", "humour"]): cats.append("Spectacle > Humour")
    if any(w in c for w in ["party", "fête", "soirée"]): cats.append("Fête")
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
# BERLIN PAGES 41-80
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
            if r.status_code != 200:
                print(f"  Page {page}: HTTP {r.status_code}, stopping")
                break

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

            if page % 5 == 0 or page == end_page:
                print(f"  Page {page}/{end_page}: {len(events)} events (total available: {total_available})")
            if page * 100 >= total_available: break
            time.sleep(1)
        except Exception as e:
            print(f"  Page {page}: error {str(e)[:60]}")
            time.sleep(2)
            continue

    print(f"  Total Berlin batch: {len(events)}")
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
        "source_url": source_url,
        "source": "kulturdaten.berlin",
        "validation_status": "auto_validated"
    }


# ============================================
# FRENCH ODS PORTALS - Expanded search
# ============================================
def fetch_france_ods_portals():
    """Fetch events from French cities using broader OpenAgenda with cities filter."""
    print("\n🇫🇷 FRANCE - More cities via OpenAgenda")
    base = "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/evenements-publics-openagenda/records"
    
    # Departments we haven't covered well yet
    departments = [
        "Calvados", "Manche", "Orne",  # Normandie
        "Aisne", "Somme", "Oise",  # Hauts-de-France
        "Aube", "Marne", "Haute-Marne",  # Grand Est
        "Meuse", "Vosges", "Moselle",
        "Côte-d'Or", "Saône-et-Loire", "Yonne", "Nièvre",  # Bourgogne
        "Ain", "Ardèche", "Drôme",  # Auvergne-Rhône-Alpes
        "Cantal", "Haute-Loire", "Allier", "Puy-de-Dôme",
        "Landes", "Lot-et-Garonne", "Gers",  # Nouvelle-Aquitaine
        "Creuse", "Corrèze", "Haute-Vienne",
        "Ariège", "Aveyron", "Lot", "Tarn", "Tarn-et-Garonne",  # Occitanie
        "Aude", "Pyrénées-Orientales", "Lozère",
        "Corse-du-Sud", "Haute-Corse",  # Corse
    ]
    
    all_events = []
    seen = set()
    
    for dept in departments:
        try:
            r = requests.get(base, params={
                "where": f"location_department='{dept}' AND firstdate_begin >= '{TODAY}'",
                "limit": 100,
                "select": "title,description,longdescription_fr,firstdate_begin,lastdate_end,location_coordinates,location_address,location_city,source_url,keywords_fr"
            }, headers=HEADERS, timeout=15)
            
            if r.status_code != 200: continue
            data = r.json()
            total = data.get("total_count", 0)
            if total == 0: continue
            
            new_count = 0
            for record in data.get("results", []):
                ev = parse_openagenda(record)
                if ev:
                    key = f"{ev['title'][:40]}|{ev['date']}|{ev['latitude']:.3f}"
                    if key not in seen:
                        seen.add(key)
                        all_events.append(ev)
                        new_count += 1
            
            if new_count > 0:
                print(f"  {dept}: {new_count}/{total}")
            time.sleep(0.5)
        except:
            continue
    
    print(f"  Total France ODS portals: {len(all_events)}")
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
    if not (41.0 < lat < 51.5 and -5.5 < lon < 10.0): return None
    
    city = record.get("location_city", "")
    address = record.get("location_address", "")
    location_str = f"{address}, {city}" if address else city
    if not location_str: location_str = "France"
    location_str += ", France"
    
    source_url = record.get("source_url") or ""
    if not source_url: return None
    
    kw = " ".join(record.get("keywords_fr", []) or [])
    
    return {
        "title": title[:200],
        "description": desc[:350],
        "date": event_date,
        "end_date": end_date,
        "time": ev_time,
        "end_time": None,
        "location": location_str[:300],
        "latitude": round(float(lat), 6),
        "longitude": round(float(lon), 6),
        "categories": categorize(title, desc, kw),
        "source_url": source_url,
        "source": "OpenAgenda",
        "validation_status": "auto_validated"
    }


# ============================================
# MAIN
# ============================================
def main():
    print("=" * 60)
    print("IMPORT WAVE 9 - Berlin 41-80 + France departments")
    print("=" * 60)
    
    results = {}
    
    # Berlin pages 41-80
    berlin = fetch_berlin_batch(41, 80)
    if berlin:
        n = send_all(berlin, "Berlin 41-80")
        results["Berlin (pages 41-80)"] = n
        print(f"  ✅ Berlin: {n}")
    
    # France departments
    france = fetch_france_ods_portals()
    if france:
        n = send_all(france, "France ODS")
        results["France (more departments)"] = n
        print(f"  ✅ France: {n}")
    
    # Summary
    print(f"\n{'=' * 60}")
    print("RÉSUMÉ WAVE 9:")
    total = 0
    for source, count in results.items():
        print(f"  {source}: {count}")
        total += count
    print(f"  TOTAL: {total}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
