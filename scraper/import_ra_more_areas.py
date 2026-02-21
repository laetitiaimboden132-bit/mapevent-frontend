"""
Scan RA areas 300-800 for more CH/FR cities + fetch events.
Looking for: Zurich, Basel, Lausanne, Bern, Lyon, Marseille, Bordeaux, 
Toulouse, Grenoble, Nice, Montpellier, etc.
"""
import requests, json, time, sys, re
from datetime import date
sys.stdout.reconfigure(line_buffering=True)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Content-Type": "application/json",
    "Referer": "https://ra.co/",
}
TODAY = date.today().isoformat()
API_BACKEND = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"


def normalize_title(title):
    t = title.lower().strip()
    t = re.sub(r'[^a-z0-9\s]', '', t)
    t = re.sub(r'\s+', ' ', t)
    return t


def classify_electro(title, artists=""):
    text = f"{title} {artists}".lower()
    subgenre_map = {
        "Techno": ["techno", "rave", "warehouse", "industrial"],
        "House": ["house music", "deep house", "funky house", "afro house"],
        "Trance": ["trance", "psytrance", "goa"],
        "Deep House": ["deep house"],
        "Minimal Techno": ["minimal techno", "minimal"],
        "Drum and Bass": ["drum and bass", "dnb", "jungle"],
        "Dubstep": ["dubstep", "bass music"],
        "Ambient": ["ambient", "downtempo"],
        "Disco": ["disco", "nu disco"],
        "Hardstyle": ["hardstyle", "hardcore", "gabber", "hard techno"],
    }
    for subgenre, keywords in subgenre_map.items():
        for kw in keywords:
            if kw in text:
                return [f"Musique > Musique electronique > {subgenre}"]
    return ["Musique > Musique electronique"]


# Load existing
print("Chargement events existants...")
try:
    r = requests.get(f"{API_BACKEND}/api/events", timeout=30)
    existing = r.json() if r.status_code == 200 else []
except:
    existing = []

existing_titles = set()
existing_sources = set()
for e in existing:
    existing_titles.add(normalize_title(e.get("title", "")))
    if e.get("source_url"):
        existing_sources.add(e["source_url"].lower().strip("/"))

print(f"  {len(existing)} events existants")


# ==========================================================================
# Scan areas 300-800
# ==========================================================================
print("\n" + "=" * 70)
print("Scan RA areas 300-800")
print("=" * 70)

ch_keywords = ["zurich", "zürich", "bern", "basel", "bâle", "lausanne", "lucerne", "luzern", 
               "switzerland", "winterthur", "lugano", "biel", "fribourg", "st. gallen", "st gallen"]
fr_keywords = ["lyon", "marseille", "bordeaux", "toulouse", "grenoble", "nice", "montpellier",
               "annecy", "france", "rennes", "rouen", "dijon", "clermont"]

# Also scan area IDs that RA commonly uses for bigger cities
known_city_ids = {
    # These are from public knowledge about RA area IDs
    13: "Zurich",
    34: "Lyon",
    55: "Marseille",
    90: "Toulouse",
    113: "Bordeaux",
}

new_areas = []

# First check known city IDs
for aid, expected_name in known_city_ids.items():
    try:
        r = requests.post("https://ra.co/graphql", json={
            "query": """{ eventListings(filters: { areas: {eq: %d} listingDate: {gte: "%s"} } pageSize: 1 page: 1) { totalResults data { event { venue { area { name } } } } } }""" % (aid, TODAY)
        }, headers=HEADERS, timeout=8)
        if r.status_code == 200:
            data = r.json()
            if not data.get("errors"):
                listings = data.get("data", {}).get("eventListings", {})
                total = listings.get("totalResults", 0)
                events = listings.get("data", [])
                if events and total > 0:
                    area_name = events[0].get("event", {}).get("venue", {}).get("area", {}).get("name", "?")
                    print(f"  ID {aid} (expected {expected_name}): {area_name} - {total} events")
                    area_lower = area_name.lower()
                    is_ch = any(kw in area_lower for kw in ch_keywords)
                    is_fr = any(kw in area_lower for kw in fr_keywords)
                    if is_ch or is_fr:
                        new_areas.append({"id": aid, "name": area_name, "country": "CH" if is_ch else "FR"})
    except:
        pass
    time.sleep(0.3)


# Scan 300-800
for area_id in range(300, 800):
    try:
        r = requests.post("https://ra.co/graphql", json={
            "query": """{ eventListings(filters: { areas: {eq: %d} listingDate: {gte: "%s"} } pageSize: 1 page: 1) { totalResults data { event { venue { area { name } } } } } }""" % (area_id, TODAY)
        }, headers=HEADERS, timeout=6)
        
        if r.status_code == 200:
            data = r.json()
            if data.get("errors"):
                continue
            listings = data.get("data", {}).get("eventListings", {})
            total = listings.get("totalResults", 0)
            events = listings.get("data", [])
            
            if events and total > 3:
                area_name = events[0].get("event", {}).get("venue", {}).get("area", {}).get("name", "?")
                area_lower = area_name.lower()
                
                is_ch = any(kw in area_lower for kw in ch_keywords)
                is_fr = any(kw in area_lower for kw in fr_keywords)
                
                if is_ch or is_fr:
                    country = "CH" if is_ch else "FR"
                    new_areas.append({"id": area_id, "name": area_name, "country": country})
                    print(f"  Area {area_id}: {area_name} ({country}) - {total} events")
    except:
        pass
    
    if area_id % 100 == 0:
        print(f"  ... scanned up to area {area_id}")
    time.sleep(0.15)

# Dedup areas
seen_ids = set()
unique_areas = []
for a in new_areas:
    if a["id"] not in seen_ids:
        seen_ids.add(a["id"])
        unique_areas.append(a)

print(f"\nNouvelles areas: {len(unique_areas)}")
for a in unique_areas:
    print(f"  {a['country']} | {a['name']} (ID={a['id']})")


# ==========================================================================
# Fetch events
# ==========================================================================
if unique_areas:
    print("\n" + "=" * 70)
    print("FETCH EVENTS")
    print("=" * 70)

    ra_events = []

    for area in unique_areas:
        area_id = area["id"]
        area_name = area["name"]
        country = area["country"]
        
        print(f"\n  --- {area_name} ({country}) ---")
        
        page = 1
        area_count = 0
        
        while page <= 6:
            try:
                r = requests.post("https://ra.co/graphql", json={
                    "query": """
                    {
                        eventListings(
                            filters: {
                                areas: {eq: %d}
                                listingDate: {gte: "%s", lte: "2026-12-31"}
                            }
                            pageSize: 50
                            page: %d
                        ) {
                            totalResults
                            data {
                                event {
                                    id
                                    title
                                    date
                                    startTime
                                    endTime
                                    contentUrl
                                    venue {
                                        name
                                        address
                                        location {
                                            latitude
                                            longitude
                                        }
                                    }
                                    artists {
                                        name
                                    }
                                }
                            }
                        }
                    }
                    """ % (area_id, TODAY, page)
                }, headers=HEADERS, timeout=15)
                
                if r.status_code != 200:
                    break
                
                data = r.json()
                if data.get("errors"):
                    break
                
                listings = data.get("data", {}).get("eventListings", {})
                total = listings.get("totalResults", 0)
                events = listings.get("data", [])
                
                if not events:
                    break
                
                for item in events:
                    evt = item.get("event", {})
                    title = evt.get("title", "").strip()
                    
                    if "CANCELLED" in title.upper() or "ANNUL" in title.upper():
                        continue
                    
                    event_date = evt.get("date", "")[:10]
                    if not event_date or event_date < TODAY:
                        continue
                    
                    venue = evt.get("venue", {}) or {}
                    venue_name = venue.get("name", "")
                    venue_addr = venue.get("address", "")
                    loc = venue.get("location", {}) or {}
                    lat = loc.get("latitude")
                    lon = loc.get("longitude")
                    
                    if not lat or not lon or lat == 0 or lon == 0:
                        continue
                    
                    lat = float(lat)
                    lon = float(lon)
                    
                    if country == "CH" and not (45.5 <= lat <= 48.0 and 5.5 <= lon <= 11.0):
                        continue
                    if country == "FR" and not (41.0 <= lat <= 51.5 and -5.5 <= lon <= 10.0):
                        continue
                    
                    content_url = evt.get("contentUrl", "")
                    source_url = f"https://ra.co{content_url}" if content_url else ""
                    
                    ntitle = normalize_title(title)
                    if ntitle in existing_titles:
                        continue
                    if source_url and source_url.lower().strip("/") in existing_sources:
                        continue
                    
                    artists = [a.get("name", "") for a in evt.get("artists", []) if a.get("name")]
                    artists_str = ", ".join(artists[:5])
                    
                    cats = classify_electro(title, artists_str)
                    location_str = f"{venue_name}, {venue_addr}".strip(", ") if venue_addr else venue_name
                    
                    desc_parts = []
                    if artists_str:
                        desc_parts.append(f"Avec {artists_str}")
                    desc_parts.append(f"a {venue_name}" if venue_name else "")
                    desc_parts.append(area_name)
                    description = "Soiree electronique. " + ". ".join([p for p in desc_parts if p]) + "."
                    
                    event_obj = {
                        "title": title,
                        "description": description[:500],
                        "location": location_str,
                        "latitude": lat,
                        "longitude": lon,
                        "date": event_date,
                        "time": evt.get("startTime", "")[:5] if evt.get("startTime") else None,
                        "end_time": evt.get("endTime", "")[:5] if evt.get("endTime") else None,
                        "source_url": source_url,
                        "categories": cats,
                        "event_type": "scraped",
                        "validation_status": "auto_validated",
                        "organizer": venue_name or "Resident Advisor",
                    }
                    
                    ra_events.append(event_obj)
                    existing_titles.add(ntitle)
                    if source_url:
                        existing_sources.add(source_url.lower().strip("/"))
                    area_count += 1
                
                print(f"    Page {page}: {area_count} nouveaux")
                
                page += 1
                if page * 50 > total:
                    break
                    
            except Exception as e:
                print(f"    Page {page}: Error: {e}")
                break
            
            time.sleep(1)

    print(f"\nTotal nouveaux events RA: {len(ra_events)}")

    # Import
    if ra_events:
        print("\n" + "=" * 70)
        print("IMPORT")
        print("=" * 70)
        
        imported = 0
        failed = 0
        
        for i in range(0, len(ra_events), 10):
            batch = ra_events[i:i+10]
            try:
                r = requests.post(
                    f"{API_BACKEND}/api/events/scraped/batch",
                    json={"events": batch},
                    headers={"Content-Type": "application/json"},
                    timeout=30
                )
                if r.status_code in (200, 201):
                    imp = r.json().get("imported", len(batch))
                    imported += imp
                    if (i // 10) % 10 == 0:
                        print(f"  [{i}/{len(ra_events)}] importes={imported}")
                else:
                    failed += len(batch)
                    print(f"  [{i}] ERREUR: {r.status_code}")
            except Exception as e:
                failed += len(batch)
            time.sleep(0.3)
        
        print(f"\n  RESULTAT: {imported} importes, {failed} echoues")
else:
    print("\nAucune nouvelle area trouvee.")

print("\nDONE!")
