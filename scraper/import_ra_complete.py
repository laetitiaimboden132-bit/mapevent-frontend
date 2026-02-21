"""
Import electronic music events from Resident Advisor (GraphQL API)
+ Paris OpenData electro events.

Searches for CH + FR areas, fetches events, dedup, import.
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


# ==========================================================================
# 1. Load existing events for dedup
# ==========================================================================
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

print(f"  {len(existing)} events, {len(existing_titles)} titres uniques")


# ==========================================================================
# 2. RA - Find ALL CH/FR areas (scan 1-250)
# ==========================================================================
print("\n" + "=" * 70)
print("RESIDENT ADVISOR - Recherche des areas CH/FR")
print("=" * 70)

ch_keywords = ["zurich", "zürich", "geneva", "geneve", "genève", "bern", "basel", 
               "lausanne", "lucerne", "luzern", "switzerland", "winterthur",
               "lugano", "biel", "fribourg", "st. gallen"]
fr_keywords = ["paris", "lyon", "marseille", "bordeaux", "nantes", "strasbourg",
               "grenoble", "toulouse", "lille", "montpellier", "france",
               "nice", "annecy"]

target_areas = []

for area_id in range(1, 250):
    try:
        r = requests.post("https://ra.co/graphql", json={
            "query": """
            {
                eventListings(
                    filters: {
                        areas: {eq: %d}
                        listingDate: {gte: "%s"}
                    }
                    pageSize: 1
                ) {
                    totalResults
                    data {
                        event {
                            venue {
                                area { id name }
                            }
                        }
                    }
                }
            }
            """ % (area_id, TODAY)
        }, headers=HEADERS, timeout=8)
        
        if r.status_code == 200:
            data = r.json()
            listings = data.get("data", {}).get("eventListings", {})
            total = listings.get("totalResults", 0)
            events = listings.get("data", [])
            
            if events and total > 0:
                area_name = events[0].get("event", {}).get("venue", {}).get("area", {}).get("name", "?")
                area_lower = area_name.lower()
                
                is_ch = any(kw in area_lower for kw in ch_keywords)
                is_fr = any(kw in area_lower for kw in fr_keywords)
                
                if is_ch or is_fr:
                    country = "CH" if is_ch else "FR"
                    target_areas.append({"id": area_id, "name": area_name, "total": total, "country": country})
                    print(f"  Area {area_id}: {area_name} ({country}) - {total} events")
    except:
        pass
    
    if area_id % 50 == 0:
        print(f"  ... scanne area {area_id}/250")
    time.sleep(0.3)

print(f"\nAreas trouvees: {len(target_areas)}")
for a in target_areas:
    print(f"  {a['country']} | {a['name']} (ID={a['id']}, {a['total']} events)")


# ==========================================================================
# 3. RA - Fetch events from all areas
# ==========================================================================
print("\n" + "=" * 70)
print("RESIDENT ADVISOR - Fetch events")
print("=" * 70)

ra_events = []

for area in target_areas:
    area_id = area["id"]
    area_name = area["name"]
    country = area["country"]
    
    print(f"\n  --- {area_name} ({country}, ID={area_id}) ---")
    
    # Paginate
    page = 0
    page_size = 50
    
    while True:
        try:
            r = requests.post("https://ra.co/graphql", json={
                "query": """
                {
                    eventListings(
                        filters: {
                            areas: {eq: %d}
                            listingDate: {gte: "%s", lte: "2026-12-31"}
                        }
                        pageSize: %d
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
                                    area { name }
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
                """ % (area_id, TODAY, page_size, page)
            }, headers=HEADERS, timeout=15)
            
            if r.status_code != 200:
                print(f"    Page {page}: Error {r.status_code}")
                break
            
            data = r.json()
            
            # Check for errors
            if data.get("errors"):
                print(f"    Page {page}: GraphQL error: {data['errors'][0].get('message', '')[:100]}")
                break
            
            listings = data.get("data", {}).get("eventListings", {})
            total = listings.get("totalResults", 0)
            events = listings.get("data", [])
            
            if not events:
                break
            
            for item in events:
                evt = item.get("event", {})
                title = evt.get("title", "").strip()
                
                # Skip cancelled events
                if title.upper().startswith("CANCELLED") or "CANCELLED" in title.upper():
                    continue
                
                event_date = evt.get("date", "")[:10]
                if event_date < TODAY:
                    continue
                
                venue = evt.get("venue", {}) or {}
                venue_name = venue.get("name", "")
                venue_addr = venue.get("address", "")
                loc = venue.get("location", {}) or {}
                lat = loc.get("latitude")
                lon = loc.get("longitude")
                
                # Need coordinates
                if not lat or not lon:
                    continue
                
                lat = float(lat)
                lon = float(lon)
                
                # Verify coordinates are in CH or FR
                if country == "CH" and not (45.8 <= lat <= 47.9 and 5.8 <= lon <= 10.6):
                    continue
                if country == "FR" and not (41.0 <= lat <= 51.5 and -5.5 <= lon <= 10.0):
                    continue
                
                content_url = evt.get("contentUrl", "")
                source_url = f"https://ra.co{content_url}" if content_url else ""
                
                # Dedup
                ntitle = normalize_title(title)
                if ntitle in existing_titles:
                    continue
                if source_url and source_url.lower().strip("/") in existing_sources:
                    continue
                
                # Artists
                artists = [a.get("name", "") for a in evt.get("artists", []) if a.get("name")]
                artists_str = ", ".join(artists[:5])
                
                # Classification
                cats = classify_electro(title, artists_str)
                
                # Location string
                loc_parts = [venue_name]
                if venue_addr:
                    loc_parts.append(venue_addr)
                location_str = ", ".join(loc_parts)
                
                # Description
                desc_parts = [f"Soiree electronique a {venue_name}"]
                if artists_str:
                    desc_parts.append(f"Avec: {artists_str}")
                if area_name:
                    desc_parts.append(f"Region: {area_name}")
                description = ". ".join(desc_parts) + "."
                
                start_time = evt.get("startTime", "")
                end_time_val = evt.get("endTime", "")
                
                event_obj = {
                    "title": title,
                    "description": description[:500],
                    "location": location_str,
                    "latitude": lat,
                    "longitude": lon,
                    "date": event_date,
                    "time": start_time[:5] if start_time else None,
                    "end_time": end_time_val[:5] if end_time_val else None,
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
            
            fetched = len(events)
            print(f"    Page {page}: +{fetched} events (total RA: {len(ra_events)})")
            
            page += 1
            if page * page_size >= total or page >= 5:  # Max 5 pages per area (250 events)
                break
                
        except Exception as e:
            print(f"    Page {page}: Error: {e}")
            break
        
        time.sleep(1)

print(f"\nTotal RA events (dedup): {len(ra_events)}")


# ==========================================================================
# 4. PARIS OPENDATA - Electro events
# ==========================================================================
print("\n" + "=" * 70)
print("PARIS OPENDATA - Events electro")
print("=" * 70)

paris_events = []
base_url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/que-faire-a-paris-/records"

search_terms = ["electro", "techno", "dj set", "dj", "house music", "rave", "clubbing", "electronic"]

for term in search_terms:
    try:
        params = {
            "where": f"(title like '%{term}%' OR lead_text like '%{term}%') AND date_start >= '{TODAY}'",
            "limit": 50,
        }
        r = requests.get(base_url, params=params, timeout=15)
        if r.status_code != 200:
            continue
        
        data = r.json()
        total = data.get("total_count", 0)
        results = data.get("results", [])
        
        if not results:
            continue
        
        new_count = 0
        for evt in results:
            title = evt.get("title", "").strip()
            date_start = evt.get("date_start", "")[:10]
            date_end = evt.get("date_end", "")[:10] if evt.get("date_end") else None
            
            if date_start < TODAY:
                continue
            
            # Skip non-electro results
            title_lower = title.lower()
            lead = (evt.get("lead_text", "") or "").lower()
            combined = f"{title_lower} {lead}"
            
            electro_keywords = ["electro", "techno", "house", "dj", "rave", "club", "electronic", "mix"]
            if not any(kw in combined for kw in electro_keywords):
                continue
            
            # Get coordinates
            lat_lon = evt.get("lat_lon", {})
            if isinstance(lat_lon, dict):
                lat = lat_lon.get("lat")
                lon = lat_lon.get("lon")
            elif isinstance(lat_lon, str) and "," in lat_lon:
                parts = lat_lon.split(",")
                lat, lon = float(parts[0]), float(parts[1])
            else:
                continue
            
            if not lat or not lon:
                continue
            
            lat = float(lat)
            lon = float(lon)
            
            # Dedup
            ntitle = normalize_title(title)
            if ntitle in existing_titles:
                continue
            
            source_url = evt.get("url", "")
            if source_url and source_url.lower().strip("/") in existing_sources:
                continue
            
            # Location
            address_name = evt.get("address_name", "")
            address_street = evt.get("address_street", "")
            address_zip = evt.get("address_zipcode", "")
            address_city = evt.get("address_city", "") or "Paris"
            
            loc_parts = [address_name, address_street, f"{address_zip} {address_city}".strip()]
            location_str = ", ".join([p for p in loc_parts if p])
            
            # Description
            lead_text = evt.get("lead_text", "") or ""
            description = lead_text[:400] if lead_text else f"Evenement electro a {address_name}, Paris."
            
            cats = classify_electro(title, description)
            
            event_obj = {
                "title": title,
                "description": description,
                "location": location_str,
                "latitude": lat,
                "longitude": lon,
                "date": date_start,
                "end_date": date_end,
                "source_url": source_url,
                "categories": cats,
                "event_type": "scraped",
                "validation_status": "auto_validated",
                "organizer": address_name or "Paris.fr",
            }
            
            paris_events.append(event_obj)
            existing_titles.add(ntitle)
            if source_url:
                existing_sources.add(source_url.lower().strip("/"))
            new_count += 1
        
        if new_count > 0:
            print(f"  '{term}': {total} total, +{new_count} nouveaux")
    except Exception as e:
        print(f"  '{term}': {e}")
    time.sleep(0.5)

print(f"\nParis OpenData electro events: {len(paris_events)}")


# ==========================================================================
# 5. IMPORT
# ==========================================================================
print("\n" + "=" * 70)
print("IMPORT")
print("=" * 70)

all_to_import = ra_events + paris_events
print(f"Total a importer: {len(all_to_import)} (RA: {len(ra_events)}, Paris: {len(paris_events)})")

if not all_to_import:
    print("Rien a importer!")
    sys.exit(0)

imported = 0
failed = 0

for i in range(0, len(all_to_import), 10):
    batch = all_to_import[i:i+10]
    try:
        r = requests.post(
            f"{API_BACKEND}/api/events/scraped/batch",
            json={"events": batch},
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        if r.status_code in (200, 201):
            data = r.json()
            imp = data.get("imported", len(batch))
            imported += imp
            if (i // 10) % 5 == 0:
                print(f"  [{i}/{len(all_to_import)}] importes={imported} echoues={failed}")
        else:
            failed += len(batch)
            print(f"  [{i}/{len(all_to_import)}] ERREUR {r.status_code}: {r.text[:150]}")
    except Exception as e:
        failed += len(batch)
        print(f"  [{i}/{len(all_to_import)}] ERREUR: {e}")
    time.sleep(0.3)

print(f"\n  RESULTAT: {imported} importes, {failed} echoues")

# Stats par source
print("\n" + "=" * 70)
print("RECAP")
print("=" * 70)
print(f"  RA: {len(ra_events)} events electro")
print(f"  Paris OpenData: {len(paris_events)} events electro")
print(f"  Total importes: {imported}")
print(f"  Echecs: {failed}")

# Stats par area RA
if ra_events:
    by_area = {}
    for e in ra_events:
        area = "RA"
        if "Region:" in e.get("description", ""):
            area = e["description"].split("Region:")[1].split(".")[0].strip()
        by_area[area] = by_area.get(area, 0) + 1
    print(f"\n  RA events par region:")
    for area, cnt in sorted(by_area.items(), key=lambda x: -x[1]):
        print(f"    {area}: {cnt}")
