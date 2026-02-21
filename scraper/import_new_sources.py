"""
Import d'events depuis de nouvelles sources open data:
1. Basel (data.bs.ch) - 3 datasets
2. Helsinki - TOUTES les catégories (pas juste musique)
3. data.gouv.fr - datasets d'events français

Sans doublons, avec bonnes catégories.
"""
import requests
import time
import json
import re
from datetime import date, datetime
from urllib.parse import urlparse

API = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"
TODAY = date.today().isoformat()

# ============================================================
# Catégories mapping
# ============================================================
def categorize_event(title, description, tags=None):
    """Assign categories based on title/description/tags."""
    text = f"{title} {description} {' '.join(tags or [])}".lower()
    cats = []
    
    # Music
    if any(w in text for w in ["techno", "electronic", "electro", "house music", "trance", "dj set"]):
        cats.append("Music > Electronic")
    elif any(w in text for w in ["concert", "musique", "musik", "music", "live band", "orchest"]):
        if any(w in text for w in ["jazz", "swing"]):
            cats.append("Music > Jazz / Soul / Funk")
        elif any(w in text for w in ["rock", "punk", "metal"]):
            cats.append("Music > Rock / Metal")
        elif any(w in text for w in ["classique", "classical", "klassik", "symphon", "opera", "opéra"]):
            cats.append("Music > Classique")
        elif any(w in text for w in ["folk", "acoustic", "akustik", "country"]):
            cats.append("Music > Folk / Acoustic")
        elif any(w in text for w in ["rap", "hip hop", "hip-hop", "trap", "drill"]):
            cats.append("Music > Urban")
        else:
            cats.append("Music > Pop / Variété")
    
    # Culture
    if any(w in text for w in ["exposition", "exhibition", "ausstellung", "galerie", "gallery", "vernissage"]):
        cats.append("Culture > Expositions")
    elif any(w in text for w in ["théâtre", "theater", "theatre", "comédie", "comedy", "bühne"]):
        cats.append("Arts Vivants > Théâtre")
    elif any(w in text for w in ["cinéma", "cinema", "film", "kino", "projection"]):
        cats.append("Culture > Cinéma & Projections")
    elif any(w in text for w in ["conférence", "conference", "vortrag", "débat", "debate", "lecture"]):
        cats.append("Culture > Conférences & Rencontres")
    elif any(w in text for w in ["atelier", "workshop", "kurs", "cours"]):
        cats.append("Culture > Workshops")
    elif any(w in text for w in ["lecture", "lesung", "conte", "book", "buch", "littéra"]):
        cats.append("Culture > Littérature & Conte")
    elif any(w in text for w in ["humour", "humor", "stand-up", "stand up", "comedy show"]):
        cats.append("Culture > Humour")
    elif any(w in text for w in ["visite", "visit", "führung", "guided", "patrimoine"]):
        cats.append("Culture > Visites & Patrimoine")
    
    # Danse
    if any(w in text for w in ["danse", "dance", "tanz", "ballet", "ballett"]):
        cats.append("Arts Vivants > Danse")
    
    # Sport
    if any(w in text for w in ["sport", "fitness", "marathon", "running", "yoga", "lauf", "rennen", "match"]):
        cats.append("Sport")
    
    # Festival
    if any(w in text for w in ["festival", "fest ", "grande fête", "open air"]):
        cats.append("Festivals & Grandes Fêtes")
    
    # Family
    if any(w in text for w in ["enfant", "kinder", "children", "family", "famille", "kids", "jeune"]):
        cats.append("Famille & Enfants")
    
    # Food
    if any(w in text for w in ["dégustation", "tasting", "degustation", "brunch", "food", "cuisine", "gastro", "vin"]):
        cats.append("Food & Drinks")
    
    # Market
    if any(w in text for w in ["marché", "market", "markt", "brocante", "foire"]):
        cats.append("Loisirs & Animation > Défilés & Fêtes")
    
    # Nature
    if any(w in text for w in ["nature", "randonnée", "wanderung", "hiking", "jardin", "garden"]):
        cats.append("Nature & Plein Air")
    
    # Default
    if not cats:
        cats.append("Culture > Conférences & Rencontres")
    
    return cats[:3]


def get_existing_urls():
    """Get existing source URLs."""
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
    print(f"  {len(urls)} URLs existantes")
    return urls


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
            if (i // batch_size + 1) % 10 == 0:
                print(f"  Batch {i//batch_size+1}: total +{total_created}")
        except Exception as e:
            print(f"  Batch {i//batch_size+1} ERREUR: {e}")
        time.sleep(0.3)
    return total_created, total_skipped


# ============================================================
# 1. BASEL - data.bs.ch
# ============================================================
def fetch_basel(existing_urls):
    """Fetch events from Basel open data."""
    print("\n" + "=" * 60)
    print("BASEL - data.bs.ch (Open Government Data Licence)")
    print("=" * 60)
    
    dataset_ids = ["100247", "100074", "100419"]
    all_events = []
    
    for ds_id in dataset_ids:
        url = f"https://data.bs.ch/api/v2/catalog/datasets/{ds_id}/exports/json"
        try:
            r = requests.get(url, timeout=30)
            if r.status_code == 200:
                data = r.json()
                print(f"  Dataset {ds_id}: {len(data)} records")
                if data and isinstance(data, list):
                    # Check structure
                    keys = list(data[0].keys())
                    print(f"    Keys: {keys[:10]}")
                    for rec in data[:2]:
                        print(f"    Sample: {json.dumps(rec, ensure_ascii=False)[:200]}")
                    all_events.extend([(ds_id, rec) for rec in data])
            else:
                print(f"  Dataset {ds_id}: HTTP {r.status_code}")
        except Exception as e:
            print(f"  Dataset {ds_id}: ERREUR {e}")
    
    print(f"\n  Total records Basel: {len(all_events)}")
    
    # Parse and create events
    events = []
    for ds_id, rec in all_events:
        # Try common field names
        title = rec.get("titel", rec.get("title", rec.get("name", rec.get("bezeichnung", ""))))
        if not title:
            continue
        
        desc = rec.get("beschreibung", rec.get("description", rec.get("text", ""))) or ""
        desc = re.sub(r'<[^>]+>', '', str(desc)).strip()
        
        # Date
        date_str = rec.get("datum", rec.get("date", rec.get("start_date", rec.get("beginn", ""))))
        if not date_str:
            continue
        if isinstance(date_str, str):
            date_str = date_str[:10]
        if date_str < TODAY:
            continue
        
        # Time
        time_str = rec.get("zeit", rec.get("time", rec.get("start_time", rec.get("beginn_zeit", None))))
        
        # Location/geo
        geo = rec.get("geo_point_2d", {})
        if isinstance(geo, dict):
            lat = rec.get("latitude", rec.get("lat", geo.get("lat", None)))
            lng = rec.get("longitude", rec.get("lon", rec.get("lng", geo.get("lon", None))))
        else:
            lat = rec.get("latitude", rec.get("lat", None))
            lng = rec.get("longitude", rec.get("lon", rec.get("lng", None)))
        
        location = rec.get("ort", rec.get("location", rec.get("standort", rec.get("adresse", "Basel"))))
        
        if not lat or not lng:
            # Default to Basel center
            lat = 47.5596
            lng = 7.5886
        
        source_url = rec.get("url", rec.get("link", rec.get("website", f"https://data.bs.ch/explore/dataset/{ds_id}")))
        
        if isinstance(source_url, str) and source_url.lower().strip().rstrip("/") in existing_urls:
            continue
        
        cats = categorize_event(title, desc)
        
        if len(desc) > 500:
            desc = desc[:497] + "..."
        
        events.append({
            "title": str(title)[:200],
            "description": desc or f"Event in Basel: {title}",
            "date": date_str,
            "time": str(time_str)[:5] if time_str and str(time_str) != "None" else None,
            "location": str(location) if location else "Basel",
            "latitude": float(lat),
            "longitude": float(lng),
            "categories": cats,
            "source_url": source_url or f"https://data.bs.ch/explore/dataset/{ds_id}",
            "source": "data.bs.ch",
            "validation_status": "auto_validated",
            "country": "CH"
        })
    
    print(f"  Events Basel à importer: {len(events)}")
    for ev in events[:5]:
        print(f"    [{ev['date']}] {ev['title'][:50]} -> {ev['categories']}")
    
    return events


# ============================================================
# 2. HELSINKI - Toutes catégories (pas juste musique)
# ============================================================
def fetch_helsinki_all(existing_urls):
    """Fetch ALL event categories from Helsinki LinkedEvents."""
    print("\n" + "=" * 60)
    print("HELSINKI - ALL categories (CC BY 4.0)")
    print("=" * 60)
    
    base = "https://api.hel.fi/linkedevents/v1"
    all_events = []
    next_url = f"{base}/event/"
    params = {
        "start": "2026-02-13",
        "end": "2026-12-31",
        "page_size": 100,
        "sort": "start_time",
        "include": "location",
        "super_event_type": "none",  # Skip umbrella events
    }
    
    page = 0
    MAX_PAGES = 100  # Helsinki has thousands
    while next_url and page < MAX_PAGES:
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
            
            if page % 10 == 0:
                total = data.get("meta", {}).get("count", "?")
                print(f"  Page {page}: {len(all_events)}/{total}")
            
            time.sleep(0.2)
        except Exception as e:
            print(f"  Error page {page}: {e}")
            break
    
    print(f"  Total events Helsinki: {len(all_events)}")
    
    # Filter and parse
    events = []
    for ev in all_events:
        name_en = (ev.get("name", {}) or {}).get("en", "") or ""
        name_fi = (ev.get("name", {}) or {}).get("fi", "") or ""
        title = name_en or name_fi
        if not title:
            continue
        
        desc_en = (ev.get("short_description", {}) or {}).get("en", "") or ""
        desc_fi = (ev.get("short_description", {}) or {}).get("fi", "") or ""
        desc = desc_en or desc_fi
        desc = re.sub(r'<[^>]+>', '', desc).strip()
        
        # Source URL
        info_url = (ev.get("info_url", {}) or {}).get("en", "") or \
                   (ev.get("info_url", {}) or {}).get("fi", "") or ""
        event_id = ev.get("id", "")
        source_url = info_url or f"https://linkedevents.hel.fi/en/events/{event_id}"
        
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
        addr = (loc.get("street_address", {}) or {}).get("fi", "") or loc_name
        
        # Dates
        start_time = ev.get("start_time", "")
        end_time_raw = ev.get("end_time", "")
        date_str = start_time[:10] if start_time else None
        time_str = start_time[11:16] if start_time and len(start_time) > 11 else None
        end_date = end_time_raw[:10] if end_time_raw else None
        end_time_str = end_time_raw[11:16] if end_time_raw and len(end_time_raw) > 11 else None
        
        if not date_str or date_str < TODAY:
            continue
        
        # Keywords for categorization
        keywords = []
        for kw in ev.get("keywords", []) or []:
            if isinstance(kw, dict):
                kw_name = (kw.get("name", {}) or {}).get("en", "") or \
                          (kw.get("name", {}) or {}).get("fi", "")
                if kw_name:
                    keywords.append(kw_name)
            elif isinstance(kw, str):
                keywords.append(kw)
        
        cats = categorize_event(title, f"{desc} {' '.join(keywords)}", keywords)
        
        if len(desc) > 500:
            desc = desc[:497] + "..."
        
        events.append({
            "title": title[:200],
            "description": desc or f"Event at {loc_name}, Helsinki.",
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
    
    print(f"  Nouveaux events Helsinki: {len(events)}")
    
    # Category breakdown
    cat_counts = {}
    for ev in events:
        for c in ev["categories"]:
            cat_counts[c] = cat_counts.get(c, 0) + 1
    print(f"\n  Par catégorie:")
    for c, n in sorted(cat_counts.items(), key=lambda x: -x[1])[:15]:
        print(f"    {c}: {n}")
    
    return events


# ============================================================
# 3. DATA.GOUV.FR - French event datasets
# ============================================================
def fetch_datagouv_events(existing_urls):
    """Search and fetch events from data.gouv.fr."""
    print("\n" + "=" * 60)
    print("FRANCE - data.gouv.fr (Licence Ouverte)")
    print("=" * 60)
    
    # Search for event datasets
    try:
        r = requests.get("https://www.data.gouv.fr/api/1/datasets/", params={
            "q": "agenda evenements culture spectacles",
            "page_size": 20,
            "sort": "-created"
        }, timeout=15)
        
        data = r.json()
        datasets = data.get("data", [])
        print(f"  Datasets trouvés: {len(datasets)}")
        
        all_events = []
        
        for ds in datasets:
            title = ds.get("title", "?")
            resources = ds.get("resources", [])
            
            # Find JSON or CSV resources
            for res in resources:
                fmt = (res.get("format", "") or "").upper()
                url = res.get("url", "")
                
                if fmt == "JSON" and "agenda" in title.lower():
                    print(f"\n  Trying: {title} [{fmt}]")
                    try:
                        r2 = requests.get(url, timeout=15)
                        if r2.status_code == 200:
                            jdata = r2.json()
                            if isinstance(jdata, list):
                                print(f"    -> {len(jdata)} records")
                                if jdata and len(jdata) > 5:
                                    all_events.extend([(title, rec) for rec in jdata])
                            elif isinstance(jdata, dict):
                                records = jdata.get("records", jdata.get("results", jdata.get("data", [])))
                                if isinstance(records, list):
                                    print(f"    -> {len(records)} records")
                                    all_events.extend([(title, rec) for rec in records])
                        time.sleep(0.5)
                    except Exception as e:
                        print(f"    -> Error: {e}")
                    break  # One resource per dataset
        
        print(f"\n  Total records data.gouv.fr: {len(all_events)}")
        return all_events
    except Exception as e:
        print(f"  ERREUR: {e}")
        return []


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("IMPORT NOUVELLES SOURCES OPEN DATA")
    print(f"Date: {TODAY}")
    print("=" * 60)
    
    existing_urls = get_existing_urls()
    
    # 1. Basel
    basel_events = fetch_basel(existing_urls)
    
    # 2. Helsinki ALL
    helsinki_events = fetch_helsinki_all(existing_urls)
    
    # Summary
    print("\n" + "=" * 60)
    print("RÉSUMÉ")
    print("=" * 60)
    print(f"  Basel: {len(basel_events)} nouveaux")
    print(f"  Helsinki: {len(helsinki_events)} nouveaux")
    total = len(basel_events) + len(helsinki_events)
    print(f"  TOTAL: {total}")
    
    # Import
    if total > 0:
        all_events = basel_events + helsinki_events
        print(f"\n--- Import de {len(all_events)} events ---")
        created, skipped = send_batch(all_events)
        print(f"\n  Insérés: {created}")
        print(f"  Skippés: {skipped}")
    
    print("\n" + "=" * 60)
    print("TERMINÉ")
    print("=" * 60)
