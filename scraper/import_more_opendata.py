"""
Import supplementaire d'events open data SAFE
Sources:
1. Helsinki LinkedEvents API - CC BY 4.0 (17000+ events)
2. Paris Que Faire a Paris - Licence Ouverte v2.0
3. OpenAgenda France (regions peu couvertes)
"""

import requests
import json
import time
import re
from datetime import datetime, date

API_BASE = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api"
TODAY = date.today().isoformat()

CATEGORY_KEYWORDS = {
    "Music > Electronic > Techno": ["techno", "acid techno"],
    "Music > Electronic > House": ["house music", "deep house", "tech house"],
    "Music > Electronic > Trance": ["trance", "psytrance"],
    "Music > Electronic": ["electronic", "electro", "edm", "dj", "rave", "club"],
    "Music > Rock": ["rock", "metal", "punk", "grunge", "indie rock"],
    "Music > Jazz & Blues": ["jazz", "blues", "swing"],
    "Music > Classical": ["classical", "orchestra", "symphony", "opera", "chamber music", "philharmonic", "choir", "chorale"],
    "Music > Hip-Hop & Rap": ["hip-hop", "hip hop", "rap", "trap"],
    "Music > Pop": ["pop music", "k-pop"],
    "Music > Reggae": ["reggae", "dancehall", "dub"],
    "Music > World Music": ["world music", "afro", "latin", "flamenco", "fado", "salsa"],
    "Music > Live Concert": ["concert", "live music", "gig", "recital", "konsertti", "musiikki"],
    "Art > Exhibition": ["exhibition", "exposition", "art show", "gallery", "museum", "nayttely", "museo", "taide", "vernissage", "musee"],
    "Art > Photography": ["photography", "valokuva", "photographie"],
    "Theater & Performance > Theater": ["theatre", "theater", "play", "drama", "spectacle", "teatteri", "nayttelma"],
    "Theater & Performance > Dance": ["dance", "ballet", "contemporary dance", "tanssi", "danse"],
    "Theater & Performance > Comedy": ["comedy", "stand-up", "standup", "humour", "komedia"],
    "Theater & Performance > Circus": ["circus", "cirque", "sirkus"],
    "Cinema & Film": ["cinema", "film", "movie", "screening", "elokuva"],
    "Festival": ["festival", "festivities", "festivaali"],
    "Food & Drink > Market": ["market", "marche", "tori", "brocante", "kirpputori"],
    "Food & Drink > Wine & Beer": ["wine", "beer", "tasting", "olut", "viini"],
    "Food & Drink > Food Festival": ["food", "gastronomie", "cuisine", "ruoka"],
    "Sports > Running": ["marathon", "running", "juoksu", "trail"],
    "Sports > Cycling": ["cycling", "pyoraily", "velo"],
    "Sports > Football": ["football", "soccer", "jalkapallo"],
    "Sports > Swimming": ["swimming", "uinti"],
    "Sports > Winter Sports": ["ski", "snowboard", "luistelu", "hiihto"],
    "Sports": ["sport", "competition", "tournament", "urheilu", "liikunta"],
    "Education > Conference": ["conference", "seminar", "symposium", "colloque", "luento"],
    "Education > Workshop": ["workshop", "atelier", "masterclass", "tyopaja", "kurssi"],
    "Community > Charity": ["charity", "solidaire", "hyvantekvaisyys"],
    "Community > Festival": ["fete", "carnival", "juhla", "karnevaali", "kermesse"],
    "Family & Kids": ["kids", "children", "family", "lapset", "perhe", "enfants", "famille"],
    "Nature & Outdoor": ["nature", "hiking", "outdoor", "luonto", "retkeily", "jardin", "randonnee"],
    "Technology": ["tech", "hackathon", "startup", "innovation", "coding", "digital"],
}

def categorize_event(title, description=""):
    text = f"{title} {description}".lower()
    found = []
    for cat, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in text:
                found.append(cat)
                break
    seen = set()
    unique = []
    for c in found:
        if c not in seen:
            seen.add(c)
            unique.append(c)
    return unique[:3] if unique else ["Community > Festival"]

def get_existing_source_urls():
    try:
        resp = requests.get(f"{API_BASE}/events", timeout=60)
        if resp.status_code != 200:
            return set()
        data = resp.json()
        urls = set()
        if 'k' in data and 'd' in data:
            keys = data['k']
            src_idx = keys.index('source_url') if 'source_url' in keys else None
            if src_idx is not None:
                for row in data['d']:
                    if len(row) > src_idx and row[src_idx]:
                        urls.add(row[src_idx])
        print(f"[CHECK] {len(urls)} source_urls existantes")
        return urls
    except Exception as e:
        print(f"Erreur: {e}")
        return set()

# ============================
# HELSINKI - CC BY 4.0
# ============================
def import_helsinki(existing_urls, max_events=500):
    print("\n=== HELSINKI LinkedEvents (CC BY 4.0) ===")
    base = "https://api.hel.fi/linkedevents/v1/event/"
    events = []
    page = 1
    
    while page <= 10 and len(events) < max_events:
        try:
            resp = requests.get(base, params={
                "start": TODAY,
                "sort": "start_time",
                "page_size": 100,
                "page": page,
                "include": "location"
            }, timeout=30)
            
            if resp.status_code != 200:
                print(f"  Page {page}: erreur {resp.status_code}")
                break
            
            data = resp.json()
            results = data.get("data", [])
            if not results:
                break
            
            for r in results:
                try:
                    name = r.get("name", {})
                    title = name.get("en") or name.get("fi") or name.get("sv") or ""
                    if not title or len(title) < 3:
                        continue
                    
                    loc = r.get("location", {})
                    if not isinstance(loc, dict):
                        continue
                    pos = loc.get("position", {})
                    if not pos:
                        continue
                    coords = pos.get("coordinates", [])
                    if not coords or len(coords) < 2:
                        continue
                    lng, lat = float(coords[0]), float(coords[1])
                    
                    if not (59.0 < lat < 71.0 and 19.0 < lng < 32.0):
                        continue
                    
                    # Adresse
                    street = loc.get("street_address", {})
                    loc_name = loc.get("name", {})
                    address = (street.get("en") or street.get("fi") or "") if isinstance(street, dict) else ""
                    venue = (loc_name.get("en") or loc_name.get("fi") or "") if isinstance(loc_name, dict) else ""
                    city_d = loc.get("address_locality", {})
                    city = (city_d.get("en") or city_d.get("fi") or "Helsinki") if isinstance(city_d, dict) else "Helsinki"
                    parts = [p for p in [venue, address, city] if p]
                    full_loc = ", ".join(parts)
                    
                    start = r.get("start_time", "")
                    end = r.get("end_time", "")
                    event_date = str(start)[:10] if start else ""
                    event_end = str(end)[:10] if end else None
                    if not event_date or event_date < TODAY:
                        continue
                    
                    time_str = None
                    if start and "T" in str(start):
                        t = str(start).split("T")[1][:5]
                        if t != "00:00":
                            time_str = t
                    
                    event_id = r.get("id", "")
                    source_url = f"https://api.hel.fi/linkedevents/v1/event/{event_id}/"
                    if not event_id or source_url in existing_urls:
                        continue
                    
                    desc_obj = r.get("description", {}) or {}
                    desc = desc_obj.get("en") or desc_obj.get("fi") or ""
                    desc = re.sub(r'<[^>]+>', ' ', desc).strip()
                    if len(desc) > 500:
                        desc = desc[:497] + "..."
                    
                    kws = [kw.get("name", {}).get("en", "") for kw in r.get("keywords", []) if isinstance(kw, dict)]
                    categories = categorize_event(title, f"{desc} {' '.join(kws)}")
                    
                    events.append({
                        "title": title[:200],
                        "description": desc,
                        "location": full_loc[:300],
                        "latitude": lat,
                        "longitude": lng,
                        "date": event_date,
                        "end_date": event_end,
                        "time": time_str,
                        "end_time": None,
                        "categories": categories,
                        "source_url": source_url,
                        "validation_status": "auto_validated",
                        "status": "active"
                    })
                    existing_urls.add(source_url)
                    
                except Exception:
                    continue
            
            page += 1
            time.sleep(1)
            
        except Exception as e:
            print(f"  Erreur page {page}: {e}")
            break
    
    print(f"  {len(events)} nouveaux events Helsinki/Finland")
    return events

# ============================
# PARIS Que Faire - Licence Ouverte v2.0
# ============================
def import_paris(existing_urls, max_events=300):
    print("\n=== PARIS Que Faire (Licence Ouverte v2.0) ===")
    base = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/que-faire-a-paris-/records"
    events = []
    offset = 0
    
    while offset < max_events:
        try:
            resp = requests.get(base, params={
                "limit": 100,
                "offset": offset,
                "where": f'date_start >= "{TODAY}"',
                "order_by": "date_start ASC"
            }, timeout=30)
            
            if resp.status_code != 200:
                print(f"  Erreur API: {resp.status_code}")
                break
            
            data = resp.json()
            results = data.get("results", [])
            if not results:
                break
            
            for r in results:
                try:
                    title = r.get("title") or ""
                    if not title or len(title) < 3:
                        continue
                    
                    lat_lon = r.get("lat_lon")
                    if not lat_lon:
                        continue
                    lat = lat_lon.get("lat")
                    lng = lat_lon.get("lon")
                    if not lat or not lng:
                        continue
                    
                    event_date = str(r.get("date_start", ""))[:10]
                    event_end = str(r.get("date_end", ""))[:10] if r.get("date_end") else None
                    if not event_date or event_date < TODAY:
                        continue
                    
                    address = r.get("address_name") or ""
                    street = r.get("address_street") or ""
                    zipcode = r.get("address_zipcode") or ""
                    full_loc = f"{address}, {street}, {zipcode} Paris".strip(", ")
                    
                    url = r.get("url") or r.get("link")
                    event_id = r.get("id") or ""
                    source_url = url or f"https://quefaire.paris.fr/event/{event_id}"
                    if not source_url or source_url in existing_urls:
                        continue
                    
                    desc = r.get("description") or r.get("lead_text") or ""
                    desc = re.sub(r'<[^>]+>', ' ', str(desc)).strip()
                    if len(desc) > 500:
                        desc = desc[:497] + "..."
                    
                    tags = r.get("tags") or ""
                    category = r.get("category") or ""
                    categories = categorize_event(title, f"{desc} {tags} {category}")
                    
                    events.append({
                        "title": title[:200],
                        "description": desc,
                        "location": full_loc[:300],
                        "latitude": float(lat),
                        "longitude": float(lng),
                        "date": event_date,
                        "end_date": event_end,
                        "time": None,
                        "end_time": None,
                        "categories": categories,
                        "source_url": source_url,
                        "validation_status": "auto_validated",
                        "status": "active"
                    })
                    existing_urls.add(source_url)
                    
                except Exception:
                    continue
            
            offset += 100
            time.sleep(1)
            
        except Exception as e:
            print(f"  Erreur: {e}")
            break
    
    print(f"  {len(events)} nouveaux events Paris")
    return events

# ============================
# BATCH SEND
# ============================
def send_batch(events, batch_size=25):
    total_ok = 0
    for i in range(0, len(events), batch_size):
        batch = events[i:i+batch_size]
        try:
            resp = requests.post(
                f"{API_BASE}/events/scraped/batch",
                json={"events": batch},
                timeout=60
            )
            if resp.status_code in (200, 201):
                result = resp.json()
                results = result.get("results", result)
                created = results.get("created", results.get("inserted", 0))
                skipped = results.get("skipped", 0)
                total_ok += created
                print(f"  Batch {i//batch_size + 1}: {created} crees, {skipped} ignores")
            else:
                print(f"  Batch {i//batch_size + 1}: ERREUR {resp.status_code}")
        except Exception as e:
            print(f"  Batch {i//batch_size + 1}: ERREUR {e}")
        time.sleep(1)
    return total_ok

# ============================
# MAIN
# ============================
if __name__ == "__main__":
    print("=" * 60)
    print("IMPORT OPEN DATA - Helsinki + Paris")
    print("=" * 60)
    
    existing = get_existing_source_urls()
    
    helsinki_events = import_helsinki(existing, max_events=500)
    paris_events = import_paris(existing, max_events=300)
    
    all_events = helsinki_events + paris_events
    
    print(f"\n{'=' * 60}")
    print(f"TOTAL: {len(all_events)} nouveaux events")
    print(f"  Helsinki: {len(helsinki_events)}")
    print(f"  Paris: {len(paris_events)}")
    
    if all_events:
        # Quelques exemples
        print("\nExemples:")
        for e in all_events[:6]:
            print(f"  {e['date']} | {e['title'][:45]} | {e['location'][:30]} | {e['categories'][:2]}")
        
        # Verif qualite rapide
        bad = [e for e in all_events if e["date"] < TODAY or not (-90 <= e["latitude"] <= 90)]
        if bad:
            print(f"\n[QC] {len(bad)} events problematiques retires")
            all_events = [e for e in all_events if e not in bad]
        
        print(f"\nEnvoi de {len(all_events)} events...")
        ok = send_batch(all_events)
        print(f"\nResultat: {ok}/{len(all_events)} events inseres")
    else:
        print("\nAucun nouvel event.")
    
    print("\nTermine!")
