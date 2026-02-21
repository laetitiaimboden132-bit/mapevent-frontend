"""Import Wave 12 - PACA (escaped apostrophe) + Centre-Val de Loire (more pages) + Berlin final."""
import requests, json, time, re, hashlib
from datetime import datetime, date

API_BASE = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api"
HEADERS = {"User-Agent": "MapEventAI-Bot/1.0"}
TODAY = date.today().strftime("%Y-%m-%d")
OA_BASE = "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/evenements-publics-openagenda/records"


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
    if any(w in c for w in ["concert", "music", "musique", "orchestre"]): 
        if "jazz" in c: cats.append("Musique > Jazz")
        elif any(w in c for w in ["classique", "symphoni"]): cats.append("Musique > Classique")
        elif any(w in c for w in ["electro", "techno", "dj"]): cats.append("Musique > Electronic")
        elif any(w in c for w in ["rock", "metal"]): cats.append("Musique > Rock")
        else: cats.append("Musique > Concert")
    if any(w in c for w in ["théâtre", "comédie", "spectacle"]): cats.append("Spectacle > Théâtre")
    if any(w in c for w in ["danse", "ballet"]): cats.append("Danse")
    if any(w in c for w in ["exposition", "galerie"]): cats.append("Culture > Exposition")
    if any(w in c for w in ["cinéma", "film"]): cats.append("Culture > Cinéma")
    if any(w in c for w in ["musée", "museum"]): cats.append("Culture > Musée")
    if any(w in c for w in ["sport", "marathon", "trail", "cyclisme"]): cats.append("Sport")
    if "festival" in c and not cats: cats.append("Festival")
    if any(w in c for w in ["marché", "brocante", "vide"]): cats.append("Marché & Brocante")
    if any(w in c for w in ["conférence", "débat"]): cats.append("Conférence")
    if any(w in c for w in ["atelier", "workshop"]): cats.append("Atelier")
    if any(w in c for w in ["enfant", "famille"]): cats.append("Famille & Enfants")
    if any(w in c for w in ["humour", "comedy"]): cats.append("Spectacle > Humour")
    if any(w in c for w in ["fête", "soirée", "carnaval"]): cats.append("Fête")
    if any(w in c for w in ["randonnée", "balade", "nature"]): cats.append("Nature & Plein Air")
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
        except: pass
        if i + 10 < len(events): time.sleep(0.5)
    return total


def parse_oa(record):
    title = record.get("title_fr") or ""
    if not title: return None
    desc = clean_html(record.get("longdescription_fr") or record.get("description_fr") or "")
    
    first_date = record.get("firstdate_begin", "")
    last_date = record.get("lastdate_end", "")
    event_date = first_date[:10] if first_date else None
    end_date = last_date[:10] if last_date else None
    if not event_date: return None
    if end_date == event_date: end_date = None
    
    ev_time = None
    if first_date and "T" in first_date:
        t = first_date.split("T")[1][:5]
        if t not in ("00:00", "23:59", "01:00"): ev_time = t
    
    try:
        d = datetime.strptime(event_date, "%Y-%m-%d").date()
        if d < date.today() or d.year > 2027: return None
    except: pass
    
    coords = record.get("location_coordinates", {})
    lat = lon = None
    if isinstance(coords, dict): lat, lon = coords.get("lat"), coords.get("lon")
    elif isinstance(coords, list) and len(coords) >= 2: lat, lon = coords[0], coords[1]
    if not lat or not lon: return None
    try: lat, lon = float(lat), float(lon)
    except: return None
    if not (41.0 < lat < 51.5 and -5.5 < lon < 10.0): return None
    
    city = record.get("location_city", "")
    address = record.get("location_address", "")
    location_str = f"{address}, {city}" if address else city
    if not location_str: location_str = "France"
    if "France" not in location_str: location_str += ", France"
    
    source_url = record.get("canonicalurl") or ""
    if not source_url: return None
    
    kw_list = record.get("keywords_fr") or []
    kw = " ".join(kw_list) if isinstance(kw_list, list) else ""
    
    return {
        "title": title[:200], "description": desc[:350],
        "date": event_date, "end_date": end_date,
        "time": ev_time, "end_time": None,
        "location": location_str[:300],
        "latitude": round(lat, 6), "longitude": round(lon, 6),
        "categories": categorize(title, desc, kw),
        "source_url": source_url, "source": "OpenAgenda",
        "validation_status": "auto_validated"
    }


def fetch_oa_events(where_clause, label, max_events=500):
    """Fetch events from OpenAgenda with custom where clause."""
    events = []
    seen = set()
    offset = 0
    
    while offset < max_events:
        try:
            r = requests.get(OA_BASE, params={
                "where": where_clause,
                "limit": 100,
                "offset": offset,
            }, headers=HEADERS, timeout=20)
            
            if r.status_code != 200:
                print(f"  {label}: HTTP {r.status_code} at offset {offset}")
                break
            data = r.json()
            records = data.get("results", [])
            total = data.get("total_count", 0)
            if not records: break
            
            for rec in records:
                ev = parse_oa(rec)
                if ev:
                    key = f"{ev['title'][:40]}|{ev['date']}|{ev['latitude']:.3f}"
                    if key not in seen:
                        seen.add(key)
                        events.append(ev)
            
            offset += 100
            if offset >= total: break
            time.sleep(0.5)
        except Exception as e:
            print(f"  {label}: Error {str(e)[:60]}")
            break
    
    print(f"  {label}: {len(events)} events")
    return events


# Berlin final pages
BERLIN_BOROUGHS = {
    "Mitte": (52.5200, 13.4050), "Friedrichshain-Kreuzberg": (52.5000, 13.4400),
    "Pankow": (52.5700, 13.4100), "Charlottenburg-Wilmersdorf": (52.5050, 13.2900),
    "Spandau": (52.5340, 13.2000), "Steglitz-Zehlendorf": (52.4340, 13.2400),
    "Tempelhof-Schöneberg": (52.4670, 13.3500), "Neukölln": (52.4400, 13.4400),
    "Treptow-Köpenick": (52.4500, 13.5800), "Marzahn-Hellersdorf": (52.5400, 13.6000),
    "Lichtenberg": (52.5200, 13.5000), "Reinickendorf": (52.5900, 13.3300),
}

def fetch_berlin_final():
    """Fetch remaining Berlin events."""
    print("\n🇩🇪 BERLIN FINAL - pages 116+")
    base_url = "https://api-v2.kulturdaten.berlin/api"
    events = []
    seen = set()
    loc_cache = {}
    
    page = 116
    while True:
        try:
            r = requests.get(f"{base_url}/events", params={
                "page": page, "pageSize": 100, "startDate": TODAY
            }, headers=HEADERS, timeout=30)
            if r.status_code != 200: break
            
            data = r.json()
            items = data.get("data", {}).get("events", [])
            total = data.get("data", {}).get("totalCount", 0)
            if not items: break
            
            for item in items:
                attractions = item.get("attractions", [])
                title = ""
                for attr in attractions:
                    label = attr.get("referenceLabel", {})
                    title = label.get("de") or label.get("en") or ""
                    if title: break
                if not title: continue
                
                schedule = item.get("schedule", {})
                sd = schedule.get("startDate", "")
                if not sd: continue
                ed = schedule.get("endDate", "")
                st = schedule.get("startTime", "")
                
                event_date = sd[:10]
                event_end = ed[:10] if ed else None
                if event_end == event_date: event_end = None
                ev_time = st[:5] if st and st != "00:00:00" else None
                
                try:
                    check = event_end or event_date
                    if datetime.strptime(check, "%Y-%m-%d").date() < date.today(): continue
                except: pass
                
                borough = ""
                location_str = "Berlin"
                lat, lon = 52.5200, 13.4050
                
                for loc in item.get("locations", []):
                    loc_id = loc.get("referenceId", "")
                    loc_label = loc.get("referenceLabel", {})
                    loc_name = loc_label.get("de") or loc_label.get("en") or ""
                    
                    if loc_id and loc_id not in loc_cache:
                        try:
                            lr = requests.get(f"{base_url}/locations/{loc_id}", headers=HEADERS, timeout=5)
                            loc_cache[loc_id] = lr.json().get("data", {}).get("location", {}) if lr.status_code == 200 else {}
                        except:
                            loc_cache[loc_id] = {}
                    
                    ld = loc_cache.get(loc_id, {})
                    street = ld.get("address", {}).get("streetAddress", "")
                    borough = ld.get("borough", "")
                    
                    if loc_name: location_str = loc_name
                    if street: location_str += f", {street}"
                    if borough: location_str += f", {borough}"
                    location_str += ", Berlin"
                    
                    bl, blo = BERLIN_BOROUGHS.get(borough, (52.5200, 13.4050))
                    h = int(hashlib.md5((street or loc_name or loc_id).encode()).hexdigest()[:8], 16)
                    lat = bl + ((h % 200) - 100) / 6000.0
                    lon = blo + ((h // 200 % 200) - 100) / 6000.0
                    break
                
                eid = item.get("identifier", "")
                if not eid: continue
                
                admission = item.get("admission", {})
                is_free = "freeOfCharge" in admission.get("ticketType", "")
                desc = f"Kulturveranstaltung in {borough or 'Berlin'}"
                if is_free: desc += " (Eintritt frei)"
                
                key = f"{clean_html(title)[:40]}|{event_date}|{lat:.3f}"
                if key in seen: continue
                seen.add(key)
                
                events.append({
                    "title": clean_html(title)[:200], "description": desc,
                    "date": event_date, "end_date": event_end,
                    "time": ev_time, "end_time": None,
                    "location": location_str[:300],
                    "latitude": round(lat, 6), "longitude": round(lon, 6),
                    "categories": categorize(title, "", borough),
                    "source_url": f"https://kulturdaten.berlin/events/{eid}",
                    "source": "kulturdaten.berlin",
                    "validation_status": "auto_validated"
                })
            
            if page % 10 == 0:
                print(f"  Page {page}: {len(events)} events (total: {total})")
            if page * 100 >= total: break
            page += 1
            time.sleep(1)
        except Exception as e:
            print(f"  Page {page}: error {str(e)[:60]}")
            time.sleep(2)
            page += 1
            continue
    
    print(f"  Total Berlin final: {len(events)}")
    return events


def main():
    print("=" * 60)
    print("IMPORT WAVE 12 - PACA + Centre-Val de Loire + Berlin final")
    print("=" * 60)
    
    results = {}
    all_events = []
    seen = set()
    
    # PACA - use search() to avoid apostrophe issue
    print("\n🇫🇷 PACA & more France...")
    paca = fetch_oa_events(
        f"search(location_region, 'Provence') AND firstdate_begin >= '{TODAY}'",
        "PACA"
    )
    for ev in paca:
        key = f"{ev['title'][:40]}|{ev['date']}|{ev['latitude']:.3f}"
        if key not in seen:
            seen.add(key)
            all_events.append(ev)
    
    # Centre-Val de Loire - get all pages (we only got 77 last time due to possible dedup)
    cvl = fetch_oa_events(
        f"location_region='Centre-Val de Loire' AND firstdate_begin >= '{TODAY}'",
        "Centre-Val de Loire", max_events=2000
    )
    for ev in cvl:
        key = f"{ev['title'][:40]}|{ev['date']}|{ev['latitude']:.3f}"
        if key not in seen:
            seen.add(key)
            all_events.append(ev)
    
    if all_events:
        n = send_all(all_events, "France extra")
        results["France (PACA + Centre)"] = n
        print(f"  ✅ France extra: {n}")
    
    # Berlin final
    berlin = fetch_berlin_final()
    if berlin:
        n = send_all(berlin, "Berlin final")
        results["Berlin (pages 116+)"] = n
        print(f"  ✅ Berlin final: {n}")
    
    # Summary
    print(f"\n{'=' * 60}")
    print("RÉSUMÉ WAVE 12:")
    total = 0
    for source, count in results.items():
        print(f"  {source}: {count}")
        total += count
    print(f"  TOTAL: {total}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
