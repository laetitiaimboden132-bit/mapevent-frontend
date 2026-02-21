"""
Import additional electronic music events from:
1. Eventfrog (JSON-LD from event pages + geocoding)
2. Goabase (city-based searches - dedup against existing)

Strict rules:
- Only CH + FR events
- Future dates only
- Precise addresses required
- Dedup against existing database
"""
import requests, json, time, sys, re
from datetime import date, datetime
sys.stdout.reconfigure(line_buffering=True)

TODAY = date.today().isoformat()
HEADERS = {"User-Agent": "MapEventAI-Bot/1.0 (contact: mapevent777@gmail.com)"}
API_BACKEND = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"
BASE_GOA = "https://www.goabase.net/api/party"

# ==========================================================================
# UTILS
# ==========================================================================

def classify_electro(title, description=""):
    """Classify electronic music events with specific subgenres."""
    text = f"{title} {description}".lower()
    
    subgenre_map = {
        "Techno": ["techno", "rave", "warehouse"],
        "House": ["house music", "deep house", "funky house", "afro house", "jackin house"],
        "Trance": ["trance", "psytrance", "psy trance", "goa trance", "progressive trance", "psychedelic trance", "full on"],
        "Deep House": ["deep house"],
        "Minimal Techno": ["minimal techno", "minimal tech"],
        "Drum and Bass": ["drum and bass", "drum'n'bass", "dnb", "d&b", "jungle", "liquid dnb"],
        "Dubstep": ["dubstep", "bass music", "riddim"],
        "Ambient": ["ambient", "chill out", "chillout", "downtempo"],
        "Acid": ["acid techno", "acid house", "acid"],
        "Progressive": ["progressive house", "progressive"],
        "Disco": ["disco", "nu disco", "nu-disco", "italo disco"],
        "Hardstyle": ["hardstyle", "hardcore", "gabber", "hard techno"],
        "Breakbeat": ["breakbeat", "breaks"],
        "Electro": ["electro", "electronica"],
    }
    
    for subgenre, keywords in subgenre_map.items():
        for kw in keywords:
            if kw in text:
                return [f"Musique > Musique electronique > {subgenre}"]
    
    # Default
    return ["Musique > Musique electronique"]


def geocode_address(address, country="Switzerland"):
    """Geocode address using Nominatim."""
    try:
        query = f"{address}, {country}" if country not in address else address
        r = requests.get("https://nominatim.openstreetmap.org/search", params={
            "q": query,
            "format": "json",
            "limit": 1,
            "addressdetails": 1,
        }, headers={"User-Agent": "MapEventAI-Bot/1.0"}, timeout=10)
        if r.status_code == 200 and r.json():
            result = r.json()[0]
            lat = float(result["lat"])
            lon = float(result["lon"])
            return lat, lon
    except:
        pass
    return None, None


def normalize_title(title):
    """Normalize title for dedup comparison."""
    t = title.lower().strip()
    t = re.sub(r'[^a-z0-9\s]', '', t)
    t = re.sub(r'\s+', ' ', t)
    return t


# ==========================================================================
# 1. Fetch existing events for dedup
# ==========================================================================
print("Chargement events existants pour dedup...")
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

print(f"  {len(existing)} events existants, {len(existing_titles)} titres, {len(existing_sources)} source_urls")


# ==========================================================================
# 2. EVENTFROG - Scrape event pages
# ==========================================================================
print("\n" + "=" * 70)
print("EVENTFROG - Soirees electro suisses")
print("=" * 70)

# Collect event links from category pages
all_links = set()

for cat_url in [
    "https://eventfrog.ch/fr/r/soiree-fete/house-techno-161.html",
]:
    try:
        r = requests.get(cat_url, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            links = re.findall(r'href="(/fr/p/[^"]+\.html)"', r.text)
            all_links.update(links)
            print(f"  {cat_url.split('/')[-1]}: {len(links)} links")
    except Exception as e:
        print(f"  Erreur: {e}")
    time.sleep(1)

# Also add some specific pages we know about
extra_pages = [
    "https://eventfrog.ch/fr/r/soiree-fete/techno-electronica-163.html",
    "https://eventfrog.ch/fr/r/soiree-fete/clubbing-51.html",
]
for url in extra_pages:
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            links = re.findall(r'href="(/fr/p/[^"]+\.html)"', r.text)
            all_links.update(links)
            print(f"  {url.split('/')[-1]}: {len(links)} links")
    except:
        pass
    time.sleep(1)

print(f"\n  Total unique links: {len(all_links)}")

eventfrog_events = []
for i, link in enumerate(sorted(all_links)):
    url = f"https://eventfrog.ch{link}"
    
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            continue
            
        lds = re.findall(r'<script type="application/ld\+json">(.*?)</script>', r.text, re.DOTALL)
        for ld in lds:
            try:
                data = json.loads(ld)
                # Handle list format
                events_list = data if isinstance(data, list) else [data]
                for d in events_list:
                    if d.get("@type") != "Event":
                        continue
                    
                    name = d.get("name", "")
                    start = d.get("startDate", "")
                    end = d.get("endDate", "")
                    loc = d.get("location", {})
                    
                    if not isinstance(loc, dict):
                        continue
                    
                    addr_obj = loc.get("address", {})
                    if isinstance(addr_obj, str):
                        addr_obj = {"streetAddress": addr_obj}
                    
                    street = addr_obj.get("streetAddress", "")
                    city = addr_obj.get("addressLocality", "")
                    zip_code = addr_obj.get("postalCode", "")
                    country = addr_obj.get("addressCountry", "")
                    venue = loc.get("name", "")
                    
                    # Only Swiss events
                    if country and country not in ("Switzerland", "CH", "Suisse"):
                        continue
                    
                    # Parse date
                    event_date = start[:10] if start else ""
                    event_time = start[11:16] if start and "T" in start else None
                    end_date = end[:10] if end else None
                    end_time = end[11:16] if end and "T" in end else None
                    
                    # Must be future
                    if event_date < TODAY:
                        continue
                    
                    # Check dedup
                    ntitle = normalize_title(name)
                    if ntitle in existing_titles:
                        continue
                    if url.lower().strip("/") in existing_sources:
                        continue
                    
                    # Build location string
                    loc_parts = [venue, street, f"{zip_code} {city}".strip()]
                    location_str = ", ".join([p for p in loc_parts if p])
                    
                    # Geocode
                    geocode_query = f"{street}, {zip_code} {city}"
                    lat, lon = geocode_address(geocode_query)
                    
                    if not lat or not lon:
                        # Try with venue name
                        lat, lon = geocode_address(f"{venue}, {city}, Switzerland")
                    
                    if not lat or not lon:
                        print(f"  [{i+1}] SKIP (no coords): {name[:40]} | {city}")
                        continue
                    
                    # Classify
                    desc = d.get("description", "") or ""
                    cats = classify_electro(name, desc)
                    
                    # Rewrite description
                    if desc:
                        desc = desc[:400].strip()
                        if len(desc) > 395:
                            desc = desc[:desc.rfind(' ')] + "..."
                    else:
                        desc = f"Soiree electronique a {venue}, {city}."
                    
                    evt = {
                        "title": name,
                        "description": desc,
                        "location": location_str,
                        "latitude": lat,
                        "longitude": lon,
                        "date": event_date,
                        "time": event_time,
                        "end_date": end_date,
                        "end_time": end_time,
                        "source_url": url,
                        "categories": cats,
                        "event_type": "scraped",
                        "validation_status": "auto_validated",
                        "organizer": venue or "Eventfrog",
                    }
                    eventfrog_events.append(evt)
                    existing_titles.add(ntitle)
                    existing_sources.add(url.lower().strip("/"))
                    print(f"  [{i+1}] OK: {name[:45]} | {event_date} | {city} | {lat:.4f},{lon:.4f}")
                    
            except json.JSONDecodeError:
                pass
    except Exception as e:
        pass
    
    time.sleep(8)  # Respect 8s delay

print(f"\n  Eventfrog events: {len(eventfrog_events)}")


# ==========================================================================
# 3. GOABASE - Events par ville (CH + FR frontalier)
# ==========================================================================
print("\n" + "=" * 70)
print("GOABASE - Events supplementaires par ville")
print("=" * 70)

cities = [
    ("Lausanne", "CH"), ("Bern", "CH"), ("Basel", "CH"), ("Lucerne", "CH"),
    ("Zurich", "CH"), ("Winterthur", "CH"), ("Fribourg", "CH"),
    ("St. Gallen", "CH"), ("Biel", "CH"), ("Thun", "CH"),
    ("Annecy", "FR"), ("Grenoble", "FR"), ("Lyon", "FR"),
    ("Besancon", "FR"), ("Mulhouse", "FR"), ("Strasbourg", "FR"),
    ("Chambery", "FR"),
]

goabase_events = []
goa_seen_ids = set()

for city_name, expected_country in cities:
    try:
        r = requests.get(f"{BASE_GOA}/json/?geoloc={city_name}&georad=40&limit=100", headers=HEADERS, timeout=15)
        if r.status_code != 200:
            continue
            
        parties = r.json().get("partylist", [])
        new_count = 0
        
        for p in parties:
            pid = p.get("id")
            if not pid or pid in goa_seen_ids:
                continue
            goa_seen_ids.add(pid)
            
            name = p.get("nameParty", "").strip()
            date_start = p.get("dateStart", "")[:10]
            iso_country = p.get("isoCountry", "")
            town = p.get("nameTown", "")
            country_name = p.get("nameCountry", "")
            lat = p.get("geoLat")
            lon = p.get("geoLon")
            
            # Only CH + FR
            if iso_country not in ("CH", "FR"):
                continue
            
            # Future only
            if date_start < TODAY:
                continue
            
            # Need coordinates
            if not lat or not lon:
                continue
            
            lat = float(lat)
            lon = float(lon)
            
            # Dedup against existing
            ntitle = normalize_title(name)
            if ntitle in existing_titles:
                continue
            
            # Build event
            name_location = p.get("nameLocation", "")
            location_str = f"{name_location}, {town}" if name_location else town
            if iso_country == "CH":
                location_str += ", Suisse"
            elif iso_country == "FR":
                location_str += ", France"
            
            # Get lineup if available
            lineup = p.get("nameLineUp", "")
            eventtype = p.get("nameType", "")
            
            # Classify
            cats = classify_electro(name, f"{lineup} {eventtype}")
            
            # Build description
            desc_parts = []
            if eventtype:
                desc_parts.append(f"Type: {eventtype}")
            if lineup:
                artists = [a.strip() for a in lineup.split(",")[:5]]
                desc_parts.append(f"Line-up: {', '.join(artists)}")
            desc_parts.append(f"Lieu: {location_str}")
            description = ". ".join(desc_parts)
            
            # Source URL
            source_url = f"https://www.goabase.net/party/{pid}"
            if source_url.lower().strip("/") in existing_sources:
                continue
            
            end_date = p.get("dateEnd", "")[:10] if p.get("dateEnd") else None
            
            evt = {
                "title": name,
                "description": description[:500],
                "location": location_str,
                "latitude": lat,
                "longitude": lon,
                "date": date_start,
                "time": p.get("dateStart", "")[11:16] if len(p.get("dateStart", "")) > 11 else None,
                "end_date": end_date,
                "end_time": p.get("dateEnd", "")[11:16] if p.get("dateEnd") and len(p.get("dateEnd", "")) > 11 else None,
                "source_url": source_url,
                "categories": cats,
                "event_type": "scraped",
                "validation_status": "auto_validated",
                "organizer": p.get("nameOrganizer", "") or "Goabase",
            }
            goabase_events.append(evt)
            existing_titles.add(ntitle)
            existing_sources.add(source_url.lower().strip("/"))
            new_count += 1
        
        if new_count > 0:
            print(f"  {city_name}: +{new_count} nouveaux events")
    except Exception as e:
        print(f"  {city_name}: {e}")
    time.sleep(1)

print(f"\n  Goabase nouveaux events: {len(goabase_events)}")


# ==========================================================================
# 4. IMPORT
# ==========================================================================
print("\n" + "=" * 70)
print("IMPORT DANS MAPEVENTAI")
print("=" * 70)

all_to_import = eventfrog_events + goabase_events
print(f"Total a importer: {len(all_to_import)} (Eventfrog: {len(eventfrog_events)}, Goabase: {len(goabase_events)})")

if not all_to_import:
    print("Rien a importer!")
    sys.exit(0)

# Import par batch de 10
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
            print(f"  [{i}/{len(all_to_import)}] +{imp} importes")
        else:
            failed += len(batch)
            print(f"  [{i}/{len(all_to_import)}] ERREUR {r.status_code}: {r.text[:200]}")
    except Exception as e:
        failed += len(batch)
        print(f"  [{i}/{len(all_to_import)}] ERREUR: {e}")
    time.sleep(0.5)

print(f"\n  RESULTAT: {imported} importes, {failed} echoues")

# Stats
print("\n" + "=" * 70)
print("RECAP")
print("=" * 70)
print(f"  Eventfrog: {len(eventfrog_events)} events electro suisses")
print(f"  Goabase: {len(goabase_events)} events electro CH/FR")
print(f"  Total importes: {imported}")
print(f"  Echecs: {failed}")
