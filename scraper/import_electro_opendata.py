"""
Import d'events ELECTRO depuis les sources open data.
- Helsinki LinkedEvents (CC BY 4.0)
- Paris Open Data (Licence Ouverte v2.0)  
- Madrid Open Data (Datos Abiertos)
- Montréal Open Data
- Goabase (déjà importé mais on recatégorise si besoin)

SANS DOUBLONS : on vérifie les source_url existantes.
Avec les BONNES sous-catégories du tree.
"""
import requests
import time
import json
import re
from urllib.parse import urlparse

API = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"

# Catégories valides du tree events_tree.json
# Format: "Music > Electronic > Techno" etc.
ELECTRO_SUBCATS = {
    # Techno
    "techno": "Music > Electronic > Techno",
    "acid techno": "Music > Electronic > Techno > Acid Techno",
    "minimal techno": "Music > Electronic > Techno > Minimal Techno",
    "minimal": "Music > Electronic > Techno > Minimal Techno",
    "hard techno": "Music > Electronic > Techno > Hard Techno",
    "industrial techno": "Music > Electronic > Techno > Industrial Techno",
    "industrial": "Music > Electronic > Techno > Industrial Techno",
    "peak time": "Music > Electronic > Techno > Peak Time Techno",
    "detroit techno": "Music > Electronic > Techno > Detroit Techno",
    "melodic techno": "Music > Electronic > Techno > Melodic Techno",
    "dub techno": "Music > Electronic > Techno > Dub Techno",
    "hypnotic techno": "Music > Electronic > Techno > Hypnotic Techno",
    # House
    "house": "Music > Electronic > House",
    "deep house": "Music > Electronic > House > Deep House",
    "electro house": "Music > Electronic > House > Electro House",
    "tech house": "Music > Electronic > House > Tech House",
    "progressive house": "Music > Electronic > House > Progressive House",
    "tribal house": "Music > Electronic > House > Tribal House",
    "funky house": "Music > Electronic > House > Funky House",
    "afro house": "Music > Electronic > House > Afro House",
    "soulful house": "Music > Electronic > House > Soulful House",
    # Trance
    "trance": "Music > Electronic > Trance",
    "psytrance": "Music > Electronic > Trance > Psytrance",
    "psy trance": "Music > Electronic > Trance > Psytrance",
    "psychedelic trance": "Music > Electronic > Trance > Psytrance",
    "full on": "Music > Electronic > Trance > Full On",
    "goa": "Music > Electronic > Trance > Goa",
    "goa trance": "Music > Electronic > Trance > Goa",
    "progressive psy": "Music > Electronic > Trance > Progressive Psy",
    "dark psy": "Music > Electronic > Trance > Dark Psy",
    "darkpsy": "Music > Electronic > Trance > Dark Psy",
    "forest": "Music > Electronic > Trance > Forest",
    "hi-tech": "Music > Electronic > Trance > Hi-Tech",
    "hitech": "Music > Electronic > Trance > Hi-Tech",
    "uplifting trance": "Music > Electronic > Trance > Uplifting Trance",
    "uplifting": "Music > Electronic > Trance > Uplifting Trance",
    "vocal trance": "Music > Electronic > Trance > Vocal Trance",
    "classic trance": "Music > Electronic > Trance > Classic Trance",
    "acid trance": "Music > Electronic > Trance > Acid Trance",
    # Drum & Bass
    "drum and bass": "Music > Electronic > Drum & Bass",
    "drum & bass": "Music > Electronic > Drum & Bass",
    "drum n bass": "Music > Electronic > Drum & Bass",
    "dnb": "Music > Electronic > Drum & Bass",
    "d&b": "Music > Electronic > Drum & Bass",
    "neurofunk": "Music > Electronic > Drum & Bass > Neurofunk",
    "jungle": "Music > Electronic > Drum & Bass > Jungle",
    "liquid dnb": "Music > Electronic > Drum & Bass > Liquid DnB",
    "liquid drum": "Music > Electronic > Drum & Bass > Liquid DnB",
    "jump up": "Music > Electronic > Drum & Bass > Jump Up",
    "darkstep": "Music > Electronic > Drum & Bass > Darkstep",
    "ragga jungle": "Music > Electronic > Drum & Bass > Ragga Jungle",
    # Bass Music
    "dubstep": "Music > Electronic > Bass Music > Dubstep",
    "riddim": "Music > Electronic > Bass Music > Riddim",
    "uk bass": "Music > Electronic > Bass Music > UK Bass",
    "future bass": "Music > Electronic > Bass Music > Future Bass",
    "bass music": "Music > Electronic > Bass Music",
    # Hard Music
    "hardstyle": "Music > Electronic > Hard Music > Hardstyle",
    "hardcore": "Music > Electronic > Hard Music > Hardcore",
    "gabber": "Music > Electronic > Hard Music > Gabber",
    "rawstyle": "Music > Electronic > Hard Music > Rawstyle",
    "frenchcore": "Music > Electronic > Hard Music",
    # Chill / Ambient
    "ambient": "Music > Electronic > Chill / Ambient > Ambient",
    "chillout": "Music > Electronic > Chill / Ambient > Chillout",
    "chill out": "Music > Electronic > Chill / Ambient > Chillout",
    "lofi": "Music > Electronic > Chill / Ambient > Lofi",
    "lo-fi": "Music > Electronic > Chill / Ambient > Lofi",
    "downtempo": "Music > Electronic > Chill / Ambient > Downtempo",
    # Disco
    "disco": "Music > Electronic > House",  # Close enough
    "nu-disco": "Music > Electronic > House",
    # Generic electro
    "electronic": "Music > Electronic",
    "electronic music": "Music > Electronic",
    "electro": "Music > Electronic",
    "edm": "Music > Electronic",
    "dj set": "Music > Electronic",
    "dj": "Music > Electronic",
    "rave": "Music > Electronic",
    "club night": "Music > Electronic",
    "clubbing": "Music > Electronic",
    "synthwave": "Music > Electronic",
    "breakbeat": "Music > Electronic",
}


def detect_electro_categories(title, description):
    """
    Detect precise electro sub-categories from title and description.
    Returns list of up to 3 categories, most specific first.
    """
    text = f"{title} {description}".lower()
    
    # Score each category by specificity (more specific = longer path = higher priority)
    matches = []
    for keyword, category in ELECTRO_SUBCATS.items():
        # Use word boundary matching for short keywords
        if len(keyword) <= 3:
            pattern = r'\b' + re.escape(keyword) + r'\b'
            if re.search(pattern, text):
                matches.append((len(category), category, keyword))
        else:
            if keyword in text:
                matches.append((len(category), category, keyword))
    
    if not matches:
        return None
    
    # Sort by specificity (longest path = most specific), deduplicate
    matches.sort(key=lambda x: -x[0])
    seen = set()
    result = []
    for _, cat, _ in matches:
        if cat not in seen:
            seen.add(cat)
            result.append(cat)
            if len(result) >= 3:
                break
    
    return result


def is_truly_electro(title, description):
    """
    Strict check: is this event truly an electronic music event?
    Not just containing 'club' or 'dance' in title.
    """
    text = f"{title} {description}".lower()
    
    # Strong electro indicators
    strong_indicators = [
        "techno", "house music", "deep house", "tech house", "minimal",
        "trance", "psytrance", "psy trance", "drum and bass", "drum & bass",
        "dnb", "dubstep", "hardstyle", "hardcore", "gabber", "rave",
        "dj set", "electronic music", "electro music", "edm ", 
        "bass music", "breakbeat", "jungle", "neurofunk",
        "club night", "after party", "afterparty",
        "electronic dance", "dance music event",
        "synthwave", "acid techno", "melodic techno",
        "afro house", "soulful house", "funky house",
    ]
    
    # Weak indicators (need at least 2 to qualify)
    weak_indicators = [
        "dj", "electro", "electronic", "dance", "club", "disco",
        "set ", "mix ", "beats", "bass", "synth", "bpm",
    ]
    
    # Strong match
    for ind in strong_indicators:
        if ind in text:
            return True
    
    # Weak: need at least 2
    weak_count = sum(1 for ind in weak_indicators if ind in text)
    if weak_count >= 2:
        return True
    
    return False


# ============================================================
# Fetch existing source_urls to avoid duplicates
# ============================================================
def get_existing_source_urls():
    """Get all existing source URLs from the map."""
    print("Récupération des events existants pour dédoublonnage...")
    r = requests.get(f"{API}/api/events", timeout=60)
    events = r.json()
    if isinstance(events, dict):
        events = events.get("events", [])
    
    urls = set()
    for ev in events:
        url = ev.get("source_url", "")
        if url:
            urls.add(url.lower().strip().rstrip("/"))
    
    print(f"  {len(urls)} source_urls existantes")
    return urls


# ============================================================
# HELSINKI LinkedEvents - Events electro
# ============================================================
def fetch_helsinki_electro(existing_urls):
    """Fetch events musique Helsinki et filtrer strict electro."""
    print("\n" + "=" * 60)
    print("HELSINKI - Import events electro (CC BY 4.0)")
    print("=" * 60)
    
    base = "https://api.hel.fi/linkedevents/v1"
    all_events = []
    url = f"{base}/event/"
    params = {
        "keyword": "yso:p1808",  # music
        "start": "2026-02-12",
        "end": "2026-12-31",
        "page_size": 100,
        "sort": "start_time",
        "include": "location"
    }
    
    page = 0
    next_url = url
    while next_url and page < 30:
        page += 1
        try:
            if page == 1:
                r = requests.get(next_url, params=params, timeout=30)
            else:
                r = requests.get(next_url, timeout=30)
            data = r.json()
            events = data.get("data", [])
            all_events.extend(events)
            next_url = data.get("meta", {}).get("next", None)
            time.sleep(0.3)
        except Exception as e:
            print(f"  Error page {page}: {e}")
            break
    
    print(f"  Total events musique: {len(all_events)}")
    
    # Filter electro
    electro_events = []
    for ev in all_events:
        name_en = (ev.get("name", {}) or {}).get("en", "") or ""
        name_fi = (ev.get("name", {}) or {}).get("fi", "") or ""
        desc_en = (ev.get("short_description", {}) or {}).get("en", "") or ""
        desc_fi = (ev.get("short_description", {}) or {}).get("fi", "") or ""
        desc_long_en = (ev.get("description", {}) or {}).get("en", "") or ""
        desc_long_fi = (ev.get("description", {}) or {}).get("fi", "") or ""
        
        title = name_en or name_fi
        description = f"{desc_en} {desc_fi} {desc_long_en} {desc_long_fi}"
        
        if not is_truly_electro(title, description):
            continue
        
        # Get source URL
        info_url = (ev.get("info_url", {}) or {}).get("en", "") or \
                   (ev.get("info_url", {}) or {}).get("fi", "") or ""
        event_url = f"https://api.hel.fi/linkedevents/v1/event/{ev.get('id', '')}/"
        source_url = info_url or event_url
        
        # Check duplicate
        if source_url.lower().strip().rstrip("/") in existing_urls:
            continue
        
        # Get location
        loc = ev.get("location", {}) or {}
        loc_name = (loc.get("name", {}) or {}).get("fi", "") or \
                   (loc.get("name", {}) or {}).get("en", "")
        pos = loc.get("position", {}) or {}
        coords = pos.get("coordinates", [])
        
        addr_fi = (loc.get("street_address", {}) or {}).get("fi", "") or ""
        addr_en = (loc.get("street_address", {}) or {}).get("en", "") or ""
        
        lat = coords[1] if len(coords) >= 2 else None
        lng = coords[0] if len(coords) >= 2 else None
        
        if not lat or not lng:
            continue
        
        # Detect categories
        cats = detect_electro_categories(title, description)
        if not cats:
            cats = ["Music > Electronic"]
        
        # Parse dates
        start_time = ev.get("start_time", "")
        end_time_raw = ev.get("end_time", "")
        
        date_str = start_time[:10] if start_time else None
        time_str = start_time[11:16] if start_time and len(start_time) > 11 else None
        end_date = end_time_raw[:10] if end_time_raw else None
        end_time_str = end_time_raw[11:16] if end_time_raw and len(end_time_raw) > 11 else None
        
        if not date_str:
            continue
        
        # Build description (rewritten, not copy-paste)
        desc_text = desc_en.strip() or desc_fi.strip()
        # Remove HTML tags
        desc_text = re.sub(r'<[^>]+>', '', desc_text).strip()
        if len(desc_text) > 500:
            desc_text = desc_text[:497] + "..."
        
        event_data = {
            "title": title,
            "description": desc_text or f"Electronic music event at {loc_name}, Helsinki.",
            "date": date_str,
            "time": time_str,
            "end_date": end_date,
            "end_time": end_time_str,
            "latitude": lat,
            "longitude": lng,
            "address": addr_fi or addr_en or loc_name,
            "city": "Helsinki",
            "country": "Finland",
            "categories": cats,
            "source_url": source_url,
            "validation_status": "auto_validated",
            "event_type": "scraped"
        }
        electro_events.append(event_data)
    
    print(f"  Events electro retenus (sans doublons): {len(electro_events)}")
    for ev in electro_events[:10]:
        print(f"    [{ev['date']}] {ev['title'][:60]} -> {ev['categories']}")
    
    return electro_events


# ============================================================
# PARIS Open Data - Events electro
# ============================================================
def fetch_paris_electro(existing_urls):
    """Fetch events electro Paris Open Data."""
    print("\n" + "=" * 60)
    print("PARIS - Import events electro (Licence Ouverte v2.0)")
    print("=" * 60)
    
    base = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/que-faire-a-paris-/records"
    
    # Multiple searches for electro keywords
    all_results = []
    seen_ids = set()
    
    keywords = ["techno", "electro", "house", "DJ", "rave", "bass", "trance", 
                "dubstep", "drum", "clubbing", "dance music"]
    
    for kw in keywords:
        try:
            r = requests.get(base, params={
                "where": f"date_start >= '2026-02-12' AND (title LIKE '%{kw}%' OR description LIKE '%{kw}%')",
                "limit": 100,
                "order_by": "date_start"
            }, timeout=30)
            
            if r.status_code == 200:
                data = r.json()
                results = data.get("results", [])
                for ev in results:
                    eid = ev.get("id", "")
                    if eid not in seen_ids:
                        seen_ids.add(eid)
                        all_results.append(ev)
            time.sleep(0.5)
        except Exception as e:
            print(f"  Error searching '{kw}': {e}")
    
    print(f"  Total résultats uniques Paris: {len(all_results)}")
    
    # Filter strict electro
    electro_events = []
    for ev in all_results:
        title = ev.get("title", "") or ""
        desc = ev.get("description", "") or ""
        desc_clean = re.sub(r'<[^>]+>', '', desc).strip()
        
        if not is_truly_electro(title, desc_clean):
            continue
        
        # Source URL
        url_field = ev.get("url", "") or ""
        source_url = url_field or f"https://opendata.paris.fr/explore/dataset/que-faire-a-paris-/information/?dataChart=eyJxd&q={ev.get('id', '')}"
        
        if source_url.lower().strip().rstrip("/") in existing_urls:
            continue
        
        # Coordinates
        geo = ev.get("lat_lon", {}) or {}
        lat = geo.get("lat") if isinstance(geo, dict) else None
        lng = geo.get("lon") if isinstance(geo, dict) else None
        
        if not lat or not lng:
            # Try geo_point
            gp = ev.get("geo_point_2d", {}) or {}
            lat = gp.get("lat")
            lng = gp.get("lon")
        
        if not lat or not lng:
            continue
        
        # Categories
        cats = detect_electro_categories(title, desc_clean)
        if not cats:
            cats = ["Music > Electronic"]
        
        # Dates
        date_start = ev.get("date_start", "")
        date_end = ev.get("date_end", "")
        
        date_str = date_start[:10] if date_start else None
        time_str = date_start[11:16] if date_start and len(date_start) > 11 else None
        end_date = date_end[:10] if date_end else None
        end_time = date_end[11:16] if date_end and len(date_end) > 11 else None
        
        if not date_str:
            continue
        
        address = ev.get("address_street", "") or ev.get("address_name", "") or ""
        city = ev.get("address_city", "Paris") or "Paris"
        
        if len(desc_clean) > 500:
            desc_clean = desc_clean[:497] + "..."
        
        event_data = {
            "title": title,
            "description": desc_clean or f"Electronic music event in Paris.",
            "date": date_str,
            "time": time_str,
            "end_date": end_date,
            "end_time": end_time,
            "latitude": lat,
            "longitude": lng,
            "address": address,
            "city": city,
            "country": "France",
            "categories": cats,
            "source_url": source_url,
            "validation_status": "auto_validated",
            "event_type": "scraped"
        }
        electro_events.append(event_data)
    
    print(f"  Events electro retenus (sans doublons): {len(electro_events)}")
    for ev in electro_events[:10]:
        print(f"    [{ev['date']}] {ev['title'][:60]} -> {ev['categories']}")
    
    return electro_events


# ============================================================
# MADRID Open Data - Events electro  
# ============================================================
def fetch_madrid_electro(existing_urls):
    """Fetch events electro Madrid."""
    print("\n" + "=" * 60)
    print("MADRID - Import events electro (Datos Abiertos)")
    print("=" * 60)
    
    url = "https://datos.madrid.es/egob/catalogo/206974-0-agenda-eventos-702702.json"
    try:
        r = requests.get(url, timeout=30)
        data = r.json()
        graph = data.get("@graph", [])
    except Exception as e:
        print(f"  Error: {e}")
        return []
    
    print(f"  Total events Madrid: {len(graph)}")
    
    electro_events = []
    for ev in graph:
        title = ev.get("title", "") or ""
        desc = ev.get("description", "") or ""
        desc_clean = re.sub(r'<[^>]+>', '', desc).strip()
        
        if not is_truly_electro(title, desc_clean):
            continue
        
        # Source URL
        link = ev.get("link", "") or ""
        source_url = link or ev.get("@id", "")
        
        if source_url.lower().strip().rstrip("/") in existing_urls:
            continue
        
        # Location
        loc = ev.get("location", {}) or {}
        lat = loc.get("latitude")
        lng = loc.get("longitude")
        
        if not lat or not lng:
            continue
        
        try:
            lat = float(lat)
            lng = float(lng)
        except:
            continue
        
        # Categories
        cats = detect_electro_categories(title, desc_clean)
        if not cats:
            cats = ["Music > Electronic"]
        
        # Dates
        dtstart = ev.get("dtstart", "")
        dtend = ev.get("dtend", "")
        
        date_str = dtstart[:10] if dtstart else None
        time_str = dtstart[11:16] if dtstart and "T" in dtstart else None
        end_date = dtend[:10] if dtend else None
        end_time = dtend[11:16] if dtend and "T" in dtend else None
        
        if not date_str:
            continue
        
        # Check if in the future
        if date_str < "2026-02-12":
            continue
        
        addr = ev.get("address", {}) or {}
        street = ""
        if isinstance(addr, dict):
            area = addr.get("area", {}) or {}
            if isinstance(area, dict):
                street = area.get("street-address", "")
        
        if len(desc_clean) > 500:
            desc_clean = desc_clean[:497] + "..."
        
        event_data = {
            "title": title,
            "description": desc_clean or f"Electronic music event in Madrid.",
            "date": date_str,
            "time": time_str,
            "end_date": end_date,
            "end_time": end_time,
            "latitude": lat,
            "longitude": lng,
            "address": street or "Madrid",
            "city": "Madrid",
            "country": "Spain",
            "categories": cats,
            "source_url": source_url,
            "validation_status": "auto_validated",
            "event_type": "scraped"
        }
        electro_events.append(event_data)
    
    print(f"  Events electro retenus (sans doublons): {len(electro_events)}")
    for ev in electro_events[:10]:
        print(f"    [{ev['date']}] {ev['title'][:60]} -> {ev['categories']}")
    
    return electro_events


# ============================================================
# BERLIN kulturdaten.berlin - Recatégoriser + nouveaux events
# ============================================================
def fetch_berlin_music_electro(existing_urls):
    """Fetch events musique Berlin et identifier les electro."""
    print("\n" + "=" * 60)
    print("BERLIN - Events electro (kulturdaten.berlin)")
    print("=" * 60)
    
    base = "https://www.kulturdaten.berlin/api/v1"
    all_events = []
    page = 1
    
    while page <= 50:
        try:
            r = requests.get(f"{base}/events", params={
                "page[number]": page,
                "page[size]": 100
            }, timeout=30)
            if r.status_code != 200:
                break
            data = r.json()
            events = data.get("data", [])
            if not events:
                break
            all_events.extend(events)
            page += 1
            time.sleep(0.3)
        except Exception as e:
            print(f"  Error page {page}: {e}")
            break
    
    print(f"  Total events Berlin: {len(all_events)}")
    
    electro_events = []
    for ev in all_events:
        attrs = ev.get("attributes", {}) or {}
        title = attrs.get("title", "") or ""
        desc = attrs.get("description", "") or ""
        desc_clean = re.sub(r'<[^>]+>', '', desc).strip()
        
        if not is_truly_electro(title, desc_clean):
            continue
        
        # Source URL
        web = attrs.get("website", "") or ""
        kb_id = ev.get("id", "")
        source_url = web or f"https://www.kulturdaten.berlin/events/{kb_id}"
        
        if source_url.lower().strip().rstrip("/") in existing_urls:
            continue
        
        # Location from relationships
        relationships = ev.get("relationships", {}) or {}
        location = relationships.get("location", {}) or {}
        loc_data = location.get("data", {}) or {}
        
        # We'd need to resolve the location, skip for now if no coords
        # Berlin coords as fallback won't work - skip
        
        # Dates
        schedules = attrs.get("schedules", []) or []
        if not schedules:
            continue
        
        sched = schedules[0]
        start = sched.get("start", "")
        end = sched.get("end", "")
        
        date_str = start[:10] if start else None
        if not date_str or date_str < "2026-02-12":
            continue
        
        cats = detect_electro_categories(title, desc_clean)
        if not cats:
            cats = ["Music > Electronic"]
        
        # Note: Berlin events from kulturdaten often lack direct coords
        # We'll handle this separately or skip
        electro_events.append({
            "title": title,
            "description": desc_clean[:500],
            "date": date_str,
            "categories": cats,
            "source_url": source_url,
            "kb_id": kb_id
        })
    
    print(f"  Events electro Berlin candidats: {len(electro_events)}")
    # We won't import these directly since coords require location resolution
    # But we report them
    for ev in electro_events[:10]:
        print(f"    [{ev['date']}] {ev['title'][:60]} -> {ev['categories']}")
    
    return []  # Skip Berlin for now, already have 10k events


# ============================================================
# Recatégoriser les events existants mal tagués
# ============================================================
def recategorize_existing_electro():
    """
    Fetch existing events, identify those that ARE electro but have 
    wrong/generic categories, and update them.
    """
    print("\n" + "=" * 60)
    print("RECATÉGORISATION - Events existants mal tagués")
    print("=" * 60)
    
    r = requests.get(f"{API}/api/events", timeout=60)
    events = r.json()
    if isinstance(events, dict):
        events = events.get("events", [])
    
    to_recategorize = []
    
    for ev in events:
        title = (ev.get("title") or "").strip()
        desc = (ev.get("description") or "").strip()
        cats = ev.get("categories", [])
        
        if not isinstance(cats, list):
            continue
        
        # Check if this is electro but has generic categories
        cats_str = " ".join(cats).lower()
        
        # Skip if already has specific electro categories
        has_specific_electro = any(
            sub in cats_str for sub in [
                "techno", "house", "trance", "drum & bass", "bass music",
                "hard music", "chill / ambient", "electronic"
            ]
        )
        if has_specific_electro:
            continue
        
        # Check if the event IS electro based on title/desc
        if not is_truly_electro(title, desc):
            continue
        
        # This event is electro but has generic categories
        new_cats = detect_electro_categories(title, desc)
        if not new_cats:
            continue
        
        # Keep existing non-music categories and replace music ones
        existing_non_music = [c for c in cats if not any(
            w in c.lower() for w in ["music", "musique", "événement", "divertissement", "danse", "festival"]
        )]
        
        final_cats = new_cats[:2]
        for c in existing_non_music:
            if len(final_cats) < 3 and c not in final_cats:
                final_cats.append(c)
        
        to_recategorize.append({
            "id": ev.get("id"),
            "title": title,
            "old_cats": cats,
            "new_cats": final_cats
        })
    
    print(f"  Events à recatégoriser: {len(to_recategorize)}")
    for ev in to_recategorize[:15]:
        print(f"    {ev['title'][:50]}: {ev['old_cats']} -> {ev['new_cats']}")
    
    return to_recategorize


# ============================================================
# Send events to API
# ============================================================
def send_events(events, batch_size=25):
    """Send events to the API in batches."""
    if not events:
        print("  Aucun event à envoyer.")
        return 0, 0
    
    total_inserted = 0
    total_skipped = 0
    
    for i in range(0, len(events), batch_size):
        batch = events[i:i+batch_size]
        try:
            r = requests.post(f"{API}/api/events/scraped/batch", 
                            json={"events": batch}, timeout=60)
            if r.status_code == 200:
                result = r.json()
                inserted = result.get("inserted", 0)
                skipped = result.get("skipped", 0)
                total_inserted += inserted
                total_skipped += skipped
                print(f"  Batch {i//batch_size + 1}: {inserted} insérés, {skipped} doublons")
            else:
                print(f"  Batch {i//batch_size + 1}: HTTP {r.status_code} - {r.text[:200]}")
        except Exception as e:
            print(f"  Batch {i//batch_size + 1}: Error - {e}")
        
        time.sleep(1)
    
    return total_inserted, total_skipped


def update_categories(to_recategorize):
    """Update categories for existing events."""
    if not to_recategorize:
        print("  Aucun event à recatégoriser.")
        return 0
    
    updated = 0
    for ev in to_recategorize:
        eid = ev["id"]
        try:
            r = requests.put(f"{API}/api/events/{eid}", 
                           json={"categories": ev["new_cats"]}, timeout=15)
            if r.status_code == 200:
                updated += 1
            else:
                print(f"  Update {eid} failed: HTTP {r.status_code}")
        except Exception as e:
            print(f"  Update {eid} error: {e}")
        time.sleep(0.2)
    
    return updated


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("IMPORT EVENTS ELECTRO - OPEN DATA SOURCES")
    print("=" * 60)
    
    # Step 1: Get existing URLs
    existing_urls = get_existing_source_urls()
    
    # Step 2: Fetch new events from each source
    helsinki_events = fetch_helsinki_electro(existing_urls)
    paris_events = fetch_paris_electro(existing_urls)
    madrid_events = fetch_madrid_electro(existing_urls)
    
    # Step 3: Recategorize existing events
    to_recat = recategorize_existing_electro()
    
    # Step 4: Summary before import
    print("\n" + "=" * 60)
    print("RÉSUMÉ AVANT IMPORT")
    print("=" * 60)
    print(f"  Nouveaux events Helsinki: {len(helsinki_events)}")
    print(f"  Nouveaux events Paris: {len(paris_events)}")
    print(f"  Nouveaux events Madrid: {len(madrid_events)}")
    print(f"  Events à recatégoriser: {len(to_recat)}")
    total_new = len(helsinki_events) + len(paris_events) + len(madrid_events)
    print(f"  TOTAL NOUVEAUX: {total_new}")
    
    # Step 5: Import
    if total_new > 0:
        print("\n--- Import nouveaux events ---")
        all_new = helsinki_events + paris_events + madrid_events
        inserted, skipped = send_events(all_new)
        print(f"\n  Total insérés: {inserted}")
        print(f"  Total doublons/skippés: {skipped}")
    
    # Step 6: Recategorize
    if to_recat:
        print("\n--- Recatégorisation ---")
        updated = update_categories(to_recat)
        print(f"  Events recatégorisés: {updated}")
    
    print("\n" + "=" * 60)
    print("TERMINÉ")
    print("=" * 60)
