"""
Round 2: Encore plus d'events open data.
1. Helsinki - les 6000 restants (pages 101-162)
2. data.gouv.fr - recherche de datasets français
3. OpenDataSoft public datasets (events)
"""
import requests
import time
import json
import re
from datetime import date
from urllib.parse import urlparse

API = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"
TODAY = date.today().isoformat()


def categorize_event(title, description, tags=None):
    """Assign categories based on title/description/tags."""
    text = f"{title} {description} {' '.join(tags or [])}".lower()
    cats = []
    
    if any(w in text for w in ["techno", "electronic", "electro", "house music", "trance", "dj set"]):
        cats.append("Music > Electronic")
    elif any(w in text for w in ["concert", "musique", "musik", "music", "live band", "orchest"]):
        if any(w in text for w in ["jazz", "swing"]): cats.append("Music > Jazz / Soul / Funk")
        elif any(w in text for w in ["rock", "punk", "metal"]): cats.append("Music > Rock / Metal")
        elif any(w in text for w in ["classique", "classical", "klassik", "symphon", "opera"]): cats.append("Music > Classique")
        elif any(w in text for w in ["folk", "acoustic"]): cats.append("Music > Folk / Acoustic")
        elif any(w in text for w in ["rap", "hip hop", "hip-hop"]): cats.append("Music > Urban")
        else: cats.append("Music > Pop / Variété")
    if any(w in text for w in ["exposition", "exhibition", "ausstellung", "galerie", "vernissage"]): cats.append("Culture > Expositions")
    elif any(w in text for w in ["théâtre", "theater", "theatre", "comédie"]): cats.append("Arts Vivants > Théâtre")
    elif any(w in text for w in ["cinéma", "cinema", "film", "kino"]): cats.append("Culture > Cinéma & Projections")
    elif any(w in text for w in ["conférence", "conference", "vortrag", "débat", "lecture"]): cats.append("Culture > Conférences & Rencontres")
    elif any(w in text for w in ["atelier", "workshop", "kurs", "cours"]): cats.append("Culture > Workshops")
    elif any(w in text for w in ["conte", "book", "littéra"]): cats.append("Culture > Littérature & Conte")
    elif any(w in text for w in ["humour", "humor", "stand-up", "comedy"]): cats.append("Culture > Humour")
    elif any(w in text for w in ["visite", "visit", "führung", "patrimoine"]): cats.append("Culture > Visites & Patrimoine")
    if any(w in text for w in ["danse", "dance", "tanz", "ballet"]): cats.append("Arts Vivants > Danse")
    if any(w in text for w in ["sport", "fitness", "marathon", "yoga", "match"]): cats.append("Sport")
    if any(w in text for w in ["festival", "open air"]): cats.append("Festivals & Grandes Fêtes")
    if any(w in text for w in ["enfant", "kinder", "children", "family", "famille", "kids"]): cats.append("Famille & Enfants")
    if any(w in text for w in ["dégustation", "tasting", "brunch", "food", "cuisine", "gastro"]): cats.append("Food & Drinks")
    if any(w in text for w in ["marché", "market", "markt", "brocante"]): cats.append("Loisirs & Animation > Défilés & Fêtes")
    if any(w in text for w in ["nature", "randonnée", "hiking", "jardin"]): cats.append("Nature & Plein Air")
    if not cats: cats.append("Culture > Conférences & Rencontres")
    return cats[:3]


def get_existing_urls():
    print("Récupération des source_urls existantes...")
    r = requests.get(f"{API}/api/events", timeout=60)
    events = r.json()
    if isinstance(events, dict): events = events.get("events", [])
    urls = set()
    for ev in events:
        url = ev.get("source_url", "")
        if url: urls.add(url.lower().strip().rstrip("/"))
    print(f"  {len(urls)} URLs existantes")
    return urls


def send_batch(events, batch_size=10):
    if not events: return 0, 0
    total_created = 0
    total_skipped = 0
    for i in range(0, len(events), batch_size):
        batch = events[i:i+batch_size]
        try:
            r = requests.post(f"{API}/api/events/scraped/batch", json={"events": batch}, timeout=30)
            resp = r.json()
            results = resp.get("results", resp)
            created = results.get("created", 0) or results.get("inserted", 0)
            skipped = results.get("skipped", 0) + results.get("failed", 0)
            total_created += created
            total_skipped += skipped
            if (i // batch_size + 1) % 20 == 0:
                print(f"  Batch {i//batch_size+1}: total +{total_created}")
        except Exception as e:
            print(f"  Batch {i//batch_size+1} ERREUR: {e}")
        time.sleep(0.3)
    return total_created, total_skipped


# ============================================================
# 1. HELSINKI - Pages 101+ (on a eu 100 pages, il en reste ~62)
# ============================================================
def fetch_helsinki_remaining(existing_urls):
    """Fetch remaining Helsinki events (pages we missed)."""
    print("=" * 60)
    print("HELSINKI - Events restants (CC BY 4.0)")
    print("=" * 60)
    
    base = "https://api.hel.fi/linkedevents/v1"
    all_events = []
    
    # Start from page 101 via offset
    page = 0
    next_url = f"{base}/event/"
    params = {
        "start": "2026-02-13",
        "end": "2026-12-31",
        "page_size": 100,
        "sort": "start_time",
        "include": "location",
        "super_event_type": "none",
        "page": 101  # Start from page 101
    }
    
    # Actually, let's just fetch ALL with a different approach - use offset
    for pg in range(101, 170):
        try:
            r = requests.get(f"{base}/event/", params={
                "start": "2026-02-13",
                "end": "2026-12-31",
                "page_size": 100,
                "sort": "start_time",
                "include": "location",
                "super_event_type": "none",
                "page": pg
            }, timeout=30)
            
            data = r.json()
            events = data.get("data", [])
            
            if not events:
                print(f"  Page {pg}: vide, arrêt.")
                break
            
            all_events.extend(events)
            
            if pg % 10 == 0:
                total = data.get("meta", {}).get("count", "?")
                print(f"  Page {pg}: {len(all_events)} events ({total} total)")
            
            time.sleep(0.2)
        except Exception as e:
            print(f"  Page {pg} error: {e}")
            break
    
    print(f"  Fetched: {len(all_events)} events from pages 101+")
    
    # Parse
    events = []
    for ev in all_events:
        name_en = (ev.get("name", {}) or {}).get("en", "") or ""
        name_fi = (ev.get("name", {}) or {}).get("fi", "") or ""
        title = name_en or name_fi
        if not title: continue
        
        desc_en = (ev.get("short_description", {}) or {}).get("en", "") or ""
        desc_fi = (ev.get("short_description", {}) or {}).get("fi", "") or ""
        desc = re.sub(r'<[^>]+>', '', (desc_en or desc_fi)).strip()
        
        info_url = (ev.get("info_url", {}) or {}).get("en", "") or \
                   (ev.get("info_url", {}) or {}).get("fi", "") or ""
        event_id = ev.get("id", "")
        source_url = info_url or f"https://linkedevents.hel.fi/en/events/{event_id}"
        
        if source_url.lower().strip().rstrip("/") in existing_urls:
            continue
        
        loc = ev.get("location", {}) or {}
        pos = loc.get("position", {}) or {}
        coords = pos.get("coordinates", [])
        lat = coords[1] if len(coords) >= 2 else None
        lng = coords[0] if len(coords) >= 2 else None
        if not lat or not lng: continue
        
        loc_name = (loc.get("name", {}) or {}).get("fi", "") or \
                   (loc.get("name", {}) or {}).get("en", "Helsinki")
        addr = (loc.get("street_address", {}) or {}).get("fi", "") or loc_name
        
        start_time = ev.get("start_time", "")
        end_time_raw = ev.get("end_time", "")
        date_str = start_time[:10] if start_time else None
        time_str = start_time[11:16] if start_time and len(start_time) > 11 else None
        end_date = end_time_raw[:10] if end_time_raw else None
        end_time_str = end_time_raw[11:16] if end_time_raw and len(end_time_raw) > 11 else None
        
        if not date_str or date_str < TODAY: continue
        
        keywords = []
        for kw in ev.get("keywords", []) or []:
            if isinstance(kw, dict):
                kw_name = (kw.get("name", {}) or {}).get("en", "") or \
                          (kw.get("name", {}) or {}).get("fi", "")
                if kw_name: keywords.append(kw_name)
        
        cats = categorize_event(title, f"{desc} {' '.join(keywords)}", keywords)
        if len(desc) > 500: desc = desc[:497] + "..."
        
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
    
    print(f"  Nouveaux events: {len(events)}")
    return events


# ============================================================
# 2. OpenDataSoft - Public event datasets
# ============================================================
def fetch_opendatasoft_events(existing_urls):
    """Fetch events from OpenDataSoft public datasets."""
    print("\n" + "=" * 60)
    print("OPENDATASOFT - Datasets publics d'events")
    print("=" * 60)
    
    # Known good datasets on OpenDataSoft domains
    datasets = [
        # Île-de-France
        ("https://data.iledefrance.fr/api/explore/v2.1/catalog/datasets/evenements-en-ile-de-france0/records",
         "Île-de-France", "FR"),
        # Loire Atlantique
        ("https://data.loire-atlantique.fr/api/explore/v2.1/catalog/datasets/224400028_agenda-culturel-departemental-702702/records",
         "Loire-Atlantique", "FR"),
    ]
    
    all_events = []
    
    for url, region, country in datasets:
        try:
            r = requests.get(url, params={"limit": 100, "offset": 0}, timeout=20)
            if r.status_code == 200:
                data = r.json()
                total = data.get("total_count", 0)
                results = data.get("results", [])
                print(f"  {region}: {total} events (fetched {len(results)})")
                
                # Fetch all pages
                fetched = results
                offset = 100
                while offset < min(total, 5000):
                    r2 = requests.get(url, params={"limit": 100, "offset": offset}, timeout=20)
                    if r2.status_code == 200:
                        more = r2.json().get("results", [])
                        if not more: break
                        fetched.extend(more)
                        offset += 100
                    else:
                        break
                    time.sleep(0.3)
                
                print(f"    Total fetched: {len(fetched)}")
                
                for rec in fetched:
                    title = rec.get("titre", rec.get("title", rec.get("nom", "")))
                    if not title: continue
                    
                    desc = rec.get("description", rec.get("descriptif", "")) or ""
                    desc = re.sub(r'<[^>]+>', '', str(desc)).strip()
                    
                    date_str = rec.get("date_debut", rec.get("date_start", rec.get("date", "")))
                    if isinstance(date_str, str): date_str = date_str[:10]
                    if not date_str or date_str < TODAY: continue
                    
                    end_date = rec.get("date_fin", rec.get("date_end", ""))
                    if isinstance(end_date, str): end_date = end_date[:10]
                    
                    # Geo
                    geo = rec.get("geo_point_2d", rec.get("geolocalisation", {}))
                    if isinstance(geo, dict):
                        lat = geo.get("lat", geo.get("latitude"))
                        lng = geo.get("lon", geo.get("longitude"))
                    else:
                        lat = rec.get("latitude")
                        lng = rec.get("longitude")
                    
                    if not lat or not lng: continue
                    
                    source_url = rec.get("url", rec.get("lien", rec.get("link", "")))
                    if not source_url:
                        source_url = f"{url}?id={rec.get('id', '')}"
                    
                    if source_url.lower().strip().rstrip("/") in existing_urls:
                        continue
                    
                    location = rec.get("lieu", rec.get("location", rec.get("adresse", region)))
                    cats = categorize_event(title, desc)
                    
                    if len(desc) > 500: desc = desc[:497] + "..."
                    
                    all_events.append({
                        "title": str(title)[:200],
                        "description": desc or f"Event in {region}",
                        "date": date_str,
                        "end_date": end_date if end_date else None,
                        "location": str(location) or region,
                        "latitude": float(lat),
                        "longitude": float(lng),
                        "categories": cats,
                        "source_url": source_url,
                        "source": f"OpenDataSoft {region}",
                        "validation_status": "auto_validated",
                        "country": country
                    })
            else:
                print(f"  {region}: HTTP {r.status_code}")
        except Exception as e:
            print(f"  {region}: ERREUR {e}")
    
    print(f"\n  Total events OpenDataSoft: {len(all_events)}")
    return all_events


# ============================================================
# 3. data.gouv.fr - Datasets publics JSON
# ============================================================
def fetch_datagouv(existing_urls):
    """Fetch events from data.gouv.fr resources."""
    print("\n" + "=" * 60)
    print("DATA.GOUV.FR - Licence Ouverte")
    print("=" * 60)
    
    # Search for event datasets with JSON resources
    try:
        r = requests.get("https://www.data.gouv.fr/api/1/datasets/", params={
            "q": "agenda evenements spectacles concerts",
            "page_size": 30,
        }, timeout=15)
        datasets = r.json().get("data", [])
        print(f"  Datasets trouvés: {len(datasets)}")
        
        all_events = []
        
        for ds in datasets:
            title = ds.get("title", "?")
            license = ds.get("license", "?")
            
            # Only open licenses
            if "ouverte" not in str(license).lower() and "open" not in str(license).lower() and "cc" not in str(license).lower():
                continue
            
            for res in ds.get("resources", []):
                fmt = (res.get("format", "") or "").upper()
                url = res.get("url", "")
                
                if fmt not in ["JSON", "GEOJSON"]:
                    continue
                
                print(f"\n  [{license}] {title[:60]} [{fmt}]")
                
                try:
                    r2 = requests.get(url, timeout=15)
                    if r2.status_code != 200:
                        print(f"    HTTP {r2.status_code}")
                        continue
                    
                    jdata = r2.json()
                    
                    # Handle different structures
                    records = []
                    if isinstance(jdata, list):
                        records = jdata
                    elif isinstance(jdata, dict):
                        for key in ["records", "results", "data", "events", "features"]:
                            if key in jdata and isinstance(jdata[key], list):
                                records = jdata[key]
                                break
                    
                    if not records:
                        print(f"    Pas de records exploitables")
                        continue
                    
                    print(f"    {len(records)} records")
                    
                    # Try to parse as events
                    parsed = 0
                    for rec in records:
                        if isinstance(rec, dict) and rec.get("properties"):
                            rec = rec["properties"]  # GeoJSON
                        
                        etitle = rec.get("titre", rec.get("title", rec.get("nom", rec.get("name", ""))))
                        if not etitle:
                            continue
                        
                        edate = rec.get("date_debut", rec.get("date", rec.get("start_date", rec.get("dtstart", ""))))
                        if isinstance(edate, str):
                            edate = edate[:10]
                        if not edate or edate < TODAY:
                            continue
                        
                        # Geo
                        lat = lng = None
                        geo = rec.get("geo_point_2d", rec.get("geolocalisation", rec.get("geometry", {})))
                        if isinstance(geo, dict):
                            if "coordinates" in geo:
                                coords = geo["coordinates"]
                                if len(coords) >= 2:
                                    lng, lat = coords[0], coords[1]
                            else:
                                lat = geo.get("lat", geo.get("latitude"))
                                lng = geo.get("lon", geo.get("longitude"))
                        
                        if not lat or not lng:
                            lat = rec.get("latitude", rec.get("lat"))
                            lng = rec.get("longitude", rec.get("lon", rec.get("lng")))
                        
                        if not lat or not lng:
                            continue
                        
                        source_url = rec.get("url", rec.get("lien", rec.get("link", "")))
                        if not source_url:
                            source_url = url
                        
                        if source_url.lower().strip().rstrip("/") in existing_urls:
                            continue
                        
                        edesc = rec.get("description", rec.get("descriptif", "")) or ""
                        edesc = re.sub(r'<[^>]+>', '', str(edesc)).strip()
                        if len(edesc) > 500: edesc = edesc[:497] + "..."
                        
                        eloc = rec.get("lieu", rec.get("location", rec.get("adresse", "")))
                        ecats = categorize_event(str(etitle), edesc)
                        
                        all_events.append({
                            "title": str(etitle)[:200],
                            "description": edesc or str(etitle),
                            "date": edate,
                            "location": str(eloc) or "France",
                            "latitude": float(lat),
                            "longitude": float(lng),
                            "categories": ecats,
                            "source_url": source_url,
                            "source": f"data.gouv.fr - {title[:30]}",
                            "validation_status": "auto_validated",
                            "country": "FR"
                        })
                        parsed += 1
                    
                    if parsed:
                        print(f"    -> {parsed} events parsés")
                except Exception as e:
                    print(f"    Erreur: {e}")
                break  # One resource per dataset
        
        print(f"\n  Total events data.gouv.fr: {len(all_events)}")
        return all_events
    except Exception as e:
        print(f"  ERREUR: {e}")
        return []


if __name__ == "__main__":
    print("=" * 60)
    print("ROUND 2 - PLUS D'EVENTS OPEN DATA")
    print(f"Date: {TODAY}")
    print("=" * 60)
    
    existing_urls = get_existing_urls()
    
    # 1. Helsinki remaining
    helsinki = fetch_helsinki_remaining(existing_urls)
    
    # 2. OpenDataSoft
    ods = fetch_opendatasoft_events(existing_urls)
    
    # 3. data.gouv.fr
    dgf = fetch_datagouv(existing_urls)
    
    # Summary
    print("\n" + "=" * 60)
    print("RÉSUMÉ ROUND 2")
    print("=" * 60)
    print(f"  Helsinki (restants): {len(helsinki)}")
    print(f"  OpenDataSoft: {len(ods)}")
    print(f"  data.gouv.fr: {len(dgf)}")
    total = len(helsinki) + len(ods) + len(dgf)
    print(f"  TOTAL: {total}")
    
    if total > 0:
        all_events = helsinki + ods + dgf
        print(f"\n--- Import de {len(all_events)} events ---")
        created, skipped = send_batch(all_events)
        print(f"\n  Insérés: {created}")
        print(f"  Skippés: {skipped}")
    
    print("\n" + "=" * 60)
    print("TERMINÉ")
    print("=" * 60)
