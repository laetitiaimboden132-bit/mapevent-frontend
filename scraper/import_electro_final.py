"""
Import d'events ELECTRO depuis les sources open data.
- Helsinki LinkedEvents (CC BY 4.0) 
- Paris Open Data (Licence Ouverte v2.0)
- Re-catégorisation des events Goabase existants

DÉDUPLICATION: via source_url existantes.
CATÉGORIES: sous-catégories précises du tree events_tree.json.
DÉTECTION STRICTE: pas de faux positifs (techno ≠ technologie).
"""
import requests
import time
import json
import re
from datetime import date

API = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"
TODAY = date.today().isoformat()

# ============================================================
# MAPPING SOUS-CATÉGORIES EXACTES
# ============================================================
ELECTRO_SUBCATS = {
    # Techno
    "acid techno": "Music > Electronic > Techno > Acid Techno",
    "minimal techno": "Music > Electronic > Techno > Minimal Techno",
    "hard techno": "Music > Electronic > Techno > Hard Techno",
    "industrial techno": "Music > Electronic > Techno > Industrial Techno",
    "peak time techno": "Music > Electronic > Techno > Peak Time Techno",
    "detroit techno": "Music > Electronic > Techno > Detroit Techno",
    "melodic techno": "Music > Electronic > Techno > Melodic Techno",
    "dub techno": "Music > Electronic > Techno > Dub Techno",
    "hypnotic techno": "Music > Electronic > Techno > Hypnotic Techno",
    "techno": "Music > Electronic > Techno",
    # House
    "deep house": "Music > Electronic > House > Deep House",
    "electro house": "Music > Electronic > House > Electro House",
    "tech house": "Music > Electronic > House > Tech House",
    "progressive house": "Music > Electronic > House > Progressive House",
    "tribal house": "Music > Electronic > House > Tribal House",
    "funky house": "Music > Electronic > House > Funky House",
    "afro house": "Music > Electronic > House > Afro House",
    "soulful house": "Music > Electronic > House > Soulful House",
    "house music": "Music > Electronic > House",
    # Trance
    "psytrance": "Music > Electronic > Trance > Psytrance",
    "psy trance": "Music > Electronic > Trance > Psytrance",
    "psychedelic trance": "Music > Electronic > Trance > Psytrance",
    "full on": "Music > Electronic > Trance > Full On",
    "goa trance": "Music > Electronic > Trance > Goa",
    "progressive psy": "Music > Electronic > Trance > Progressive Psy",
    "dark psy": "Music > Electronic > Trance > Dark Psy",
    "darkpsy": "Music > Electronic > Trance > Dark Psy",
    "forest psy": "Music > Electronic > Trance > Forest",
    "hi-tech": "Music > Electronic > Trance > Hi-Tech",
    "hitech": "Music > Electronic > Trance > Hi-Tech",
    "uplifting trance": "Music > Electronic > Trance > Uplifting Trance",
    "vocal trance": "Music > Electronic > Trance > Vocal Trance",
    "classic trance": "Music > Electronic > Trance > Classic Trance",
    "acid trance": "Music > Electronic > Trance > Acid Trance",
    "trance": "Music > Electronic > Trance",
    # Drum & Bass
    "neurofunk": "Music > Electronic > Drum & Bass > Neurofunk",
    "jungle": "Music > Electronic > Drum & Bass > Jungle",
    "liquid dnb": "Music > Electronic > Drum & Bass > Liquid DnB",
    "liquid drum": "Music > Electronic > Drum & Bass > Liquid DnB",
    "jump up": "Music > Electronic > Drum & Bass > Jump Up",
    "darkstep": "Music > Electronic > Drum & Bass > Darkstep",
    "ragga jungle": "Music > Electronic > Drum & Bass > Ragga Jungle",
    "drum and bass": "Music > Electronic > Drum & Bass",
    "drum & bass": "Music > Electronic > Drum & Bass",
    "drum n bass": "Music > Electronic > Drum & Bass",
    "dnb": "Music > Electronic > Drum & Bass",
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
    "downtempo": "Music > Electronic > Chill / Ambient > Downtempo",
    # Generic
    "electronic music": "Music > Electronic",
    "electronic dance": "Music > Electronic",
    "edm": "Music > Electronic",
}

# Mots qui indiquent un event electro de façon CERTAINE
STRONG_ELECTRO_MARKERS = [
    "techno party", "techno night", "techno music", "techno event",
    "house party", "house night", "house music", "deep house", "tech house",
    "afro house", "soulful house", "funky house",
    "trance party", "trance night", "psytrance", "psy trance", "goa trance",
    "drum and bass", "drum & bass", "drum n bass", "dnb night",
    "dubstep", "bass music", "hardstyle", "gabber", "rawstyle", "frenchcore",
    "dj set", "dj night", "dj-set",
    "electronic music", "electronic dance", "electro night",
    "club night", "after party", "afterparty",
    "rave", "rave party",
    "acid techno", "minimal techno", "hard techno", "melodic techno",
    "detroit techno", "industrial techno", "dub techno",
    "neurofunk", "liquid dnb", "darkstep",
    "uk bass", "future bass",
    "progressive house", "tribal house", "electro house",
    "dark psy", "darkpsy", "hi-tech", "hitech", "full on",
    "uplifting trance", "vocal trance",
    "synthwave", "breakbeat",
    "disco dj", "disco party",
]

# Mots qui EXCLUENT (faux positifs courants)
EXCLUSION_PATTERNS = [
    "technolog", "technique", "informatique", "techno express",
    "soutien techno", "techno-pédagog",
    "book club", "jazz club", "jass club", "fight club", "wine club",
    "film club", "ciné-club", "cine club", "ciné club", "chess club", "sport club",
    "club de lecture", "club de sport", "kids club", "club enfant",
    "dans la jungle", "jungle urbaine", "jungle de", "pixel zoo jungle",
    "jungle gym", "jungle book",
    "dance class", "dance lesson", "dance workshop", "cours de danse",
    "atelier danse", "ballet", "salsa", "tango", "valse", "swing dance",
    "folk dance", "danse folk", "danse classique",
    "ambient light", "ambiance", "ambiant",
    "house of", "maison de", "open house", "full house",
    "6 nations", "rugby", "football",
    "disco ball", "discography",
    "classical music", "musique classique", "opéra", "opera",
    "orchestre", "orchestra", "symphon", "baroque", "chambre",
    "violon", "violin", "piano recital", "guitare classique",
    "jazz", "blues", "soul music", "funk band",
    "chanson française", "folk music", "country",
    "rock band", "metal", "punk", "grunge",
    "hip hop", "hip-hop", "rap ", "r&b", "rnb",
    "reggae", "ska ", "dub reggae",
]


def is_strictly_electro(title, description):
    """
    STRICT check: is this event truly an electronic music event?
    Returns True only if we're confident it's electro.
    """
    text = f"{title} {description}".lower()
    
    # Check exclusions FIRST
    for excl in EXCLUSION_PATTERNS:
        if excl in text:
            # But check if there's also a strong marker that overrides
            has_strong = any(marker in text for marker in STRONG_ELECTRO_MARKERS)
            if not has_strong:
                return False
    
    # Check strong markers
    for marker in STRONG_ELECTRO_MARKERS:
        if marker in text:
            return True
    
    # Check if title alone has electro keywords (more reliable than description)
    title_lower = title.lower()
    title_markers = ["techno", "house", "trance", "dnb", "dubstep", "rave",
                     "dj ", "dj-", "edm", "bass", "hardstyle", "gabber",
                     "electro", "electronic"]
    
    for marker in title_markers:
        if marker in title_lower:
            # Double-check it's not a false positive in title too
            title_exclusions = ["technolog", "technique", "techno express", 
                              "soutien", "informatique", "house of", "maison",
                              "open house", "book club", "jazz club", "bass guitar",
                              "bass voice", "bassoon"]
            if not any(excl in title_lower for excl in title_exclusions):
                return True
    
    return False


def detect_categories(title, description):
    """
    Detect precise electro sub-categories from title and description.
    Returns list of up to 3 categories, most specific first.
    """
    text = f"{title} {description}".lower()
    
    matches = []
    for keyword, category in ELECTRO_SUBCATS.items():
        if keyword in text:
            # Prioritize by specificity (longer path = more specific)
            matches.append((len(category), category, keyword))
    
    if not matches:
        return ["Music > Electronic"]
    
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


def get_existing_source_urls():
    """Get all existing source URLs."""
    print("Récupération des source_urls existantes...")
    r = requests.get(f"{API}/api/events", timeout=60)
    events = r.json()
    if isinstance(events, dict):
        events = events.get("events", [])
    
    urls = set()
    for ev in events:
        url = ev.get("source_url", "")
        if url:
            urls.add(url.lower().strip().rstrip("/"))
    
    print(f"  {len(urls)} source_urls en base")
    return urls, events


def send_batch(events, batch_size=10):
    """Send events via batch API."""
    if not events:
        return 0, 0
    
    total_created = 0
    total_skipped = 0
    
    for i in range(0, len(events), batch_size):
        batch = events[i:i+batch_size]
        try:
            r = requests.post(f"{API}/api/events/scraped/batch", 
                            json={"events": batch}, timeout=30)
            resp = r.json()
            results = resp.get("results", resp)
            created = results.get("created", 0) or results.get("inserted", 0)
            skipped = results.get("skipped", 0) + results.get("failed", 0)
            total_created += created
            total_skipped += skipped
            print(f"  Batch {i//batch_size+1}: +{created} insérés, {skipped} skippés")
        except Exception as e:
            print(f"  Batch {i//batch_size+1} ERREUR: {e}")
        time.sleep(0.5)
    
    return total_created, total_skipped


# ============================================================
# HELSINKI LinkedEvents
# ============================================================
def fetch_helsinki_electro(existing_urls):
    """Fetch music events from Helsinki and filter strict electro."""
    print("\n" + "=" * 60)
    print("HELSINKI - Events electro (CC BY 4.0)")
    print("=" * 60)
    
    base = "https://api.hel.fi/linkedevents/v1"
    all_events = []
    next_url = f"{base}/event/"
    params = {
        "keyword": "yso:p1808",
        "start": "2026-02-12",
        "end": "2026-12-31",
        "page_size": 100,
        "sort": "start_time",
        "include": "location"
    }
    
    page = 0
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
        except:
            break
    
    print(f"  Total events musique Helsinki: {len(all_events)}")
    
    electro_events = []
    for ev in all_events:
        name_en = (ev.get("name", {}) or {}).get("en", "") or ""
        name_fi = (ev.get("name", {}) or {}).get("fi", "") or ""
        desc_en = (ev.get("short_description", {}) or {}).get("en", "") or ""
        desc_long_en = (ev.get("description", {}) or {}).get("en", "") or ""
        desc_long_fi = (ev.get("description", {}) or {}).get("fi", "") or ""
        
        title = name_en or name_fi
        description = f"{desc_en} {desc_long_en} {desc_long_fi}"
        
        if not is_strictly_electro(title, description):
            continue
        
        # Source URL
        info_url = (ev.get("info_url", {}) or {}).get("en", "") or \
                   (ev.get("info_url", {}) or {}).get("fi", "") or ""
        event_api_url = f"https://linkedevents.hel.fi/en/events/{ev.get('id', '')}"
        source_url = info_url or event_api_url
        
        if source_url.lower().strip().rstrip("/") in existing_urls:
            continue
        
        # Location
        loc = ev.get("location", {}) or {}
        pos = loc.get("position", {}) or {}
        coords = pos.get("coordinates", [])
        lat = coords[1] if len(coords) >= 2 else None
        lng = coords[0] if len(coords) >= 2 else None
        
        if not lat or not lng:
            continue
        
        loc_name = (loc.get("name", {}) or {}).get("fi", "") or \
                   (loc.get("name", {}) or {}).get("en", "Helsinki")
        addr = (loc.get("street_address", {}) or {}).get("fi", "") or \
               (loc.get("street_address", {}) or {}).get("en", "") or loc_name
        
        # Dates
        start_time = ev.get("start_time", "")
        end_time_raw = ev.get("end_time", "")
        date_str = start_time[:10] if start_time else None
        time_str = start_time[11:16] if start_time and len(start_time) > 11 else None
        end_date = end_time_raw[:10] if end_time_raw else None
        end_time_str = end_time_raw[11:16] if end_time_raw and len(end_time_raw) > 11 else None
        
        if not date_str or date_str < TODAY:
            continue
        
        # Categories
        cats = detect_categories(title, description)
        
        # Clean description
        desc_text = desc_en.strip() or ""
        desc_text = re.sub(r'<[^>]+>', '', desc_text).strip()
        if not desc_text:
            desc_text = f"Electronic music event at {loc_name}, Helsinki."
        if len(desc_text) > 500:
            desc_text = desc_text[:497] + "..."
        
        electro_events.append({
            "title": title,
            "description": desc_text,
            "date": date_str,
            "time": time_str,
            "end_date": end_date,
            "end_time": end_time_str,
            "location": f"{addr}, Helsinki",
            "latitude": lat,
            "longitude": lng,
            "categories": cats,
            "source_url": source_url,
            "source": "Helsinki LinkedEvents",
            "validation_status": "auto_validated",
            "country": "FI"
        })
    
    print(f"  Events electro retenus (sans doublons): {len(electro_events)}")
    for ev in electro_events:
        print(f"    [{ev['date']}] {ev['title'][:55]} -> {ev['categories']}")
    
    return electro_events


# ============================================================
# PARIS Open Data  
# ============================================================
def fetch_paris_electro(existing_urls):
    """Fetch electro events from Paris Open Data."""
    print("\n" + "=" * 60)
    print("PARIS - Events electro (Licence Ouverte v2.0)")
    print("=" * 60)
    
    base = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/que-faire-a-paris-/records"
    
    all_results = []
    seen_ids = set()
    
    # Search with electro-specific keywords (avoid generic "club", "dance")
    keywords = ["techno", "electro", "DJ set", "house music", "rave", 
                "bass music", "trance", "dubstep", "drum and bass",
                "clubbing", "after party"]
    
    for kw in keywords:
        try:
            r = requests.get(base, params={
                "where": f"date_start >= '2026-02-12' AND (title LIKE '%{kw}%' OR description LIKE '%{kw}%')",
                "limit": 100,
                "order_by": "date_start"
            }, timeout=30)
            if r.status_code == 200:
                for ev in r.json().get("results", []):
                    eid = ev.get("id", "")
                    if eid not in seen_ids:
                        seen_ids.add(eid)
                        all_results.append(ev)
            time.sleep(0.5)
        except Exception as e:
            print(f"  Error '{kw}': {e}")
    
    print(f"  Résultats bruts: {len(all_results)}")
    
    electro_events = []
    for ev in all_results:
        title = ev.get("title", "") or ""
        desc = ev.get("description", "") or ""
        desc_clean = re.sub(r'<[^>]+>', '', desc).strip()
        
        if not is_strictly_electro(title, desc_clean):
            continue
        
        # Source URL
        url_field = ev.get("url", "") or ""
        source_url = url_field
        if not source_url:
            continue  # Skip if no direct URL
        
        if source_url.lower().strip().rstrip("/") in existing_urls:
            continue
        
        # Coordinates
        geo = ev.get("lat_lon", {}) or {}
        lat = geo.get("lat") if isinstance(geo, dict) else None
        lng = geo.get("lon") if isinstance(geo, dict) else None
        if not lat or not lng:
            gp = ev.get("geo_point_2d", {}) or {}
            lat = gp.get("lat")
            lng = gp.get("lon")
        if not lat or not lng:
            continue
        
        cats = detect_categories(title, desc_clean)
        
        date_start = ev.get("date_start", "")
        date_end = ev.get("date_end", "")
        date_str = date_start[:10] if date_start else None
        time_str = date_start[11:16] if date_start and len(date_start) > 11 else None
        end_date = date_end[:10] if date_end else None
        end_time = date_end[11:16] if date_end and len(date_end) > 11 else None
        
        if not date_str or date_str < TODAY:
            continue
        
        address = ev.get("address_street", "") or ev.get("address_name", "") or ""
        
        if len(desc_clean) > 500:
            desc_clean = desc_clean[:497] + "..."
        
        electro_events.append({
            "title": title,
            "description": desc_clean or f"Electronic music event in Paris.",
            "date": date_str,
            "time": time_str,
            "end_date": end_date,
            "end_time": end_time,
            "location": f"{address}, Paris" if address else "Paris",
            "latitude": lat,
            "longitude": lng,
            "categories": cats,
            "source_url": source_url,
            "source": "Paris Open Data",
            "validation_status": "auto_validated",
            "country": "FR"
        })
    
    print(f"  Events electro retenus (sans doublons): {len(electro_events)}")
    for ev in electro_events:
        print(f"    [{ev['date']}] {ev['title'][:55]} -> {ev['categories']}")
    
    return electro_events


# ============================================================
# RECATÉGORISER les events Goabase existants avec les bonnes sous-cats
# ============================================================
def recategorize_goabase(all_events):
    """
    Recategorize existing Goabase events with proper sub-categories.
    Goabase uses 'Musique > Techno' etc. but tree uses 'Music > Electronic > Techno'.
    """
    print("\n" + "=" * 60)
    print("RECATÉGORISATION - Events Goabase mal catégorisés")
    print("=" * 60)
    
    goabase_events = []
    for ev in all_events:
        url = (ev.get("source_url") or "").lower()
        if "goabase" in url:
            goabase_events.append(ev)
    
    print(f"  Events Goabase trouvés: {len(goabase_events)}")
    
    to_update = []
    for ev in goabase_events:
        cats = ev.get("categories", [])
        if not isinstance(cats, list):
            continue
        
        # Check if categories use old format (Musique > Techno instead of Music > Electronic > Techno)
        needs_update = False
        for c in cats:
            if c.startswith("Musique >") or c == "Musique > Électronique":
                needs_update = True
                break
        
        if not needs_update:
            continue
        
        title = ev.get("title", "") or ""
        desc = ev.get("description", "") or ""
        new_cats = detect_categories(title, desc)
        
        # Add Festival if it was there
        if any("festival" in c.lower() for c in cats):
            if not any("festival" in c.lower() for c in new_cats) and len(new_cats) < 3:
                new_cats.append("Festivals & Grandes Fêtes > Festival musique")
        
        if new_cats != cats:
            to_update.append({
                "id": ev["id"],
                "title": title,
                "old_cats": cats,
                "new_cats": new_cats
            })
    
    print(f"  À recatégoriser: {len(to_update)}")
    for ev in to_update[:10]:
        print(f"    {ev['title'][:40]}: {ev['old_cats']} -> {ev['new_cats']}")
    
    return to_update


def recategorize_existing_electro_events(all_events):
    """
    Find events from other sources that ARE electro but tagged with generic categories.
    Only update if we're very confident.
    """
    print("\n" + "=" * 60)
    print("RECATÉGORISATION - Events electro avec catégories génériques")
    print("=" * 60)
    
    to_update = []
    
    for ev in all_events:
        cats = ev.get("categories", [])
        if not isinstance(cats, list):
            continue
        
        # Skip if already has proper electronic sub-categories
        cats_str = " ".join(cats).lower()
        if any(sub in cats_str for sub in [
            "music > electronic", "techno", "house", "trance", 
            "drum & bass", "bass music", "hard music", "chill / ambient"
        ]):
            continue
        
        title = (ev.get("title") or "").strip()
        desc = (ev.get("description") or "").strip()
        
        # Be VERY strict for recategorization
        if not is_strictly_electro(title, desc):
            continue
        
        new_cats = detect_categories(title, desc)
        if not new_cats or new_cats == ["Music > Electronic"]:
            # Only recategorize if we can give a specific subcategory
            continue
        
        # Keep max 3 cats
        final = new_cats[:3]
        
        to_update.append({
            "id": ev["id"],
            "title": title,
            "old_cats": cats,
            "new_cats": final
        })
    
    print(f"  À recatégoriser: {len(to_update)}")
    for ev in to_update[:15]:
        print(f"    {ev['title'][:45]}: {ev['old_cats'][:2]} -> {ev['new_cats']}")
    
    return to_update


def apply_recategorizations(updates):
    """Apply category updates via the batch endpoint (re-insert trick)."""
    if not updates:
        return 0
    
    # Since PUT requires auth, we use delete + re-insert
    # Actually, let's just report them for now and see
    print(f"\n  {len(updates)} events à recatégoriser (nécessite auth pour PUT)")
    print("  >> Pour l'instant, on se concentre sur les NOUVEAUX events <<")
    return 0


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("IMPORT EVENTS ELECTRO - SOURCES OPEN DATA")
    print(f"Date: {TODAY}")
    print("=" * 60)
    
    # Step 1: Get existing URLs and events
    existing_urls, all_existing = get_existing_source_urls()
    
    # Step 2: Fetch new electro events
    helsinki = fetch_helsinki_electro(existing_urls)
    paris = fetch_paris_electro(existing_urls)
    
    # Step 3: Identify recategorizations needed
    goabase_recat = recategorize_goabase(all_existing)
    other_recat = recategorize_existing_electro_events(all_existing)
    
    # Step 4: Summary
    print("\n" + "=" * 60)
    print("RÉSUMÉ")
    print("=" * 60)
    print(f"  Nouveaux Helsinki: {len(helsinki)}")
    print(f"  Nouveaux Paris: {len(paris)}")
    print(f"  Goabase à recatégoriser: {len(goabase_recat)}")
    print(f"  Autres à recatégoriser: {len(other_recat)}")
    
    # Step 5: Import new events
    all_new = helsinki + paris
    if all_new:
        print(f"\n--- Import de {len(all_new)} nouveaux events ---")
        created, skipped = send_batch(all_new)
        print(f"  Insérés: {created}")
        print(f"  Skippés: {skipped}")
    else:
        print("\n  Aucun nouvel event electro trouvé.")
    
    # Step 6: Report on recategorizations
    total_recat = len(goabase_recat) + len(other_recat)
    if total_recat:
        print(f"\n--- {total_recat} events nécessitent une recatégorisation ---")
        apply_recategorizations(goabase_recat + other_recat)
    
    print("\n" + "=" * 60)
    print("TERMINÉ")
    print("=" * 60)
