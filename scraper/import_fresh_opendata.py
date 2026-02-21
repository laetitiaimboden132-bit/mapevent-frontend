"""
Import de NOUVELLES sources open data non encore utilisees.
1. Amsterdam Open Data (data.amsterdam.nl) - CC0 Public Domain
2. Vienna Open Data (data.wien.gv.at) - CC BY 4.0 AT
3. Données Québec - événements culturels - CC-BY 4.0
4. Helsinki - AVEC verif URL complete anti-doublon
"""

import requests
import json
import time
import re
from datetime import date

API_BASE = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api"
TODAY = date.today().isoformat()

CATEGORY_KEYWORDS = {
    "Music > Electronic": ["electronic", "electro", "dj", "rave", "club", "dance music"],
    "Music > Rock": ["rock", "metal", "punk", "indie"],
    "Music > Jazz & Blues": ["jazz", "blues"],
    "Music > Classical": ["classical", "orchestra", "opera", "symphony", "klass"],
    "Music > Live Concert": ["concert", "live music", "muziek", "musik", "musique", "konzertt"],
    "Art > Exhibition": ["exhibition", "exposition", "tentoonstelling", "ausstellung", "gallery", "museum", "musee"],
    "Theater & Performance > Theater": ["theatre", "theater", "toneel", "spectacle"],
    "Theater & Performance > Dance": ["dance", "dans", "ballet", "tanz"],
    "Theater & Performance > Comedy": ["comedy", "cabaret", "kabarett", "stand-up"],
    "Cinema & Film": ["cinema", "film", "movie"],
    "Festival": ["festival"],
    "Food & Drink > Market": ["market", "markt", "marche", "brocante"],
    "Food & Drink > Wine & Beer": ["wine", "beer", "wijn", "bier", "wein"],
    "Sports": ["sport", "marathon", "running", "football", "tennis", "voetbal"],
    "Education > Conference": ["conference", "congres", "seminar", "lecture", "vortrag"],
    "Education > Workshop": ["workshop", "atelier", "kurs", "cursus"],
    "Family & Kids": ["kids", "children", "kinderen", "kinder", "family", "familie", "enfants"],
    "Nature & Outdoor": ["nature", "outdoor", "natuur", "wandeling", "hiking", "garden"],
    "Community > Festival": ["fete", "feest", "fest", "kermis", "carnival"],
    "Technology": ["tech", "hackathon", "startup", "digital", "innovation"],
}

def categorize(title, desc=""):
    text = f"{title} {desc}".lower()
    found = []
    for cat, kws in CATEGORY_KEYWORDS.items():
        for kw in kws:
            if kw in text:
                found.append(cat)
                break
    return list(dict.fromkeys(found))[:3] or ["Community > Festival"]

def send_batch(events):
    ok = 0
    for i in range(0, len(events), 25):
        batch = events[i:i+25]
        try:
            resp = requests.post(f"{API_BASE}/events/scraped/batch", json={"events": batch}, timeout=60)
            if resp.status_code in (200, 201):
                r = resp.json().get("results", resp.json())
                created = r.get("created", 0)
                ok += created
                print(f"  Batch {i//25+1}: {created} crees, {r.get('skipped',0)} ignores")
            else:
                print(f"  Batch {i//25+1}: ERREUR {resp.status_code} - {resp.text[:200]}")
        except Exception as e:
            print(f"  Batch {i//25+1}: ERREUR {e}")
        time.sleep(1)
    return ok

# ============================
# HELSINKI - En verifiant mieux les doublons
# ============================
def import_helsinki(max_pages=10):
    print("\n=== HELSINKI LinkedEvents (CC BY 4.0) ===")
    base = "https://api.hel.fi/linkedevents/v1/event/"
    events = []
    
    for page in range(1, max_pages + 1):
        try:
            resp = requests.get(base, params={
                "start": TODAY, "sort": "start_time",
                "page_size": 100, "page": page,
                "include": "location"
            }, timeout=30)
            if resp.status_code != 200:
                break
            data = resp.json()
            results = data.get("data", [])
            if not results:
                break
            
            for r in results:
                try:
                    name = r.get("name", {})
                    title = name.get("en") or name.get("fi") or ""
                    if not title or len(title) < 3:
                        continue
                    
                    loc = r.get("location", {})
                    if not isinstance(loc, dict):
                        continue
                    pos = loc.get("position") or {}
                    coords = pos.get("coordinates", [])
                    if not coords or len(coords) < 2:
                        continue
                    lng, lat = float(coords[0]), float(coords[1])
                    if not (59.0 < lat < 71.0):
                        continue
                    
                    street = loc.get("street_address", {})
                    loc_name = loc.get("name", {})
                    addr = (street.get("en") or street.get("fi") or "") if isinstance(street, dict) else ""
                    venue = (loc_name.get("en") or loc_name.get("fi") or "") if isinstance(loc_name, dict) else ""
                    full_loc = ", ".join(p for p in [venue, addr, "Helsinki"] if p)
                    
                    start = r.get("start_time", "")
                    event_date = str(start)[:10]
                    if not event_date or event_date < TODAY:
                        continue
                    end = r.get("end_time", "")
                    event_end = str(end)[:10] if end else None
                    
                    t = None
                    if "T" in str(start):
                        t = str(start).split("T")[1][:5]
                        if t == "00:00": t = None
                    
                    eid = r.get("id", "")
                    source_url = f"https://linkedevents.hel.fi/{eid}" if eid else None
                    if not source_url:
                        continue
                    
                    desc_obj = r.get("description", {}) or {}
                    desc = desc_obj.get("en") or desc_obj.get("fi") or ""
                    desc = re.sub(r'<[^>]+>', ' ', desc).strip()[:500]
                    
                    kws = " ".join(kw.get("name", {}).get("en", "") for kw in r.get("keywords", []) if isinstance(kw, dict))
                    cats = categorize(title, f"{desc} {kws}")
                    
                    events.append({
                        "title": title[:200], "description": desc,
                        "location": full_loc[:300],
                        "latitude": lat, "longitude": lng,
                        "date": event_date, "end_date": event_end,
                        "time": t, "end_time": None,
                        "categories": cats,
                        "source_url": source_url,
                        "validation_status": "auto_validated", "status": "active"
                    })
                except:
                    continue
            
            time.sleep(1)
        except Exception as e:
            print(f"  Erreur page {page}: {e}")
            break
    
    print(f"  {len(events)} events Helsinki")
    return events

# ============================
# DONNEES QUEBEC - CC-BY 4.0
# ============================
def import_quebec():
    print("\n=== DONNEES QUEBEC (CC-BY 4.0) ===")
    events = []
    
    # Montreal festivals
    url = "https://donnees.montreal.ca/api/3/action/datastore_search"
    try:
        resp = requests.get(url, params={
            "resource_id": "d9714397-e91a-4c13-8957-94a3d01927c4",
            "limit": 200
        }, timeout=30)
        if resp.status_code == 200:
            records = resp.json().get("result", {}).get("records", [])
            for r in records:
                try:
                    title = r.get("NOM") or r.get("nom") or ""
                    if not title: continue
                    
                    lat = r.get("LATITUDE") or r.get("latitude")
                    lng = r.get("LONGITUDE") or r.get("longitude")
                    if not lat or not lng: continue
                    lat, lng = float(lat), float(lng)
                    if not (44.0 < lat < 47.0 and -75.0 < lng < -72.0): continue
                    
                    start = str(r.get("DATE_DEBUT") or r.get("date_debut") or "")[:10]
                    if not start or start < TODAY: continue
                    end = str(r.get("DATE_FIN") or r.get("date_fin") or "")[:10] or None
                    
                    loc = r.get("LIEU") or r.get("lieu") or r.get("ADRESSE") or ""
                    source_url = r.get("URL") or r.get("url") or r.get("SITE_WEB") or f"https://donnees.montreal.ca/festivals/{r.get('_id','')}"
                    
                    desc = r.get("DESCRIPTION") or ""
                    if isinstance(desc, list): desc = " ".join(str(d) for d in desc)
                    desc = re.sub(r'<[^>]+>', ' ', str(desc)).strip()[:500]
                    
                    events.append({
                        "title": title[:200], "description": desc,
                        "location": f"{loc}, Montreal"[:300],
                        "latitude": lat, "longitude": lng,
                        "date": start, "end_date": end,
                        "time": None, "end_time": None,
                        "categories": categorize(title, desc),
                        "source_url": source_url,
                        "validation_status": "auto_validated", "status": "active"
                    })
                except: continue
    except Exception as e:
        print(f"  Erreur Montreal: {e}")
    
    print(f"  {len(events)} events Quebec/Montreal")
    return events

# ============================
# OPENAGENDA - Regions FR pas encore couvertes
# ============================
def import_oa_new_regions():
    print("\n=== OPENAGENDA nouvelles regions FR (Licence Ouverte v1.0) ===")
    base = "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/evenements-publics-openagenda/records"
    events = []
    
    regions = {
        "Bretagne": 'location_region = "Bretagne"',
        "Normandie": 'location_region = "Normandie"',
        "Nouvelle-Aquitaine": 'location_region = "Nouvelle-Aquitaine"',
        "Occitanie": 'location_region = "Occitanie"',
        "Provence-Alpes-Cote d Azur": 'location_region = "Provence-Alpes-C\\u00f4te d\'Azur"',
        "Centre-Val de Loire": 'location_region = "Centre-Val de Loire"',
        "Pays de la Loire": 'location_region = "Pays de la Loire"',
        "Bourgogne-Franche-Comte": 'location_region = "Bourgogne-Franche-Comt\\u00e9"',
        "Corse": 'location_region = "Corse"',
    }
    
    for name, where_clause in regions.items():
        region_events = []
        offset = 0
        while offset < 200:
            try:
                resp = requests.get(base, params={
                    "limit": 100, "offset": offset,
                    "where": f'{where_clause} AND firstdate_begin >= "{TODAY}"',
                    "order_by": "firstdate_begin ASC"
                }, timeout=30)
                if resp.status_code != 200:
                    break
                results = resp.json().get("results", [])
                if not results:
                    break
                
                for r in results:
                    try:
                        title = r.get("title_fr") or ""
                        if not title or len(title) < 3: continue
                        
                        loc_c = r.get("location_coordinates")
                        if not loc_c: continue
                        lat = float(loc_c.get("lat", 0))
                        lng = float(loc_c.get("lon", 0))
                        if lat == 0 and lng == 0: continue
                        
                        fd = r.get("firstdate_begin")
                        if not fd: continue
                        event_date = str(fd)[:10]
                        if event_date < TODAY: continue
                        event_end = str(r.get("lastdate_end"))[:10] if r.get("lastdate_end") else None
                        
                        loc_name = r.get("location_name") or ""
                        loc_addr = r.get("location_address") or ""
                        loc_city = r.get("location_city") or ""
                        full_loc = ", ".join(p for p in [loc_name, loc_addr, loc_city] if p)
                        if not full_loc: continue
                        
                        uid = r.get("uid")
                        canonical = r.get("canonicalurl")
                        source_url = canonical or f"https://openagenda.com/events/{uid}"
                        if not source_url: continue
                        
                        desc = r.get("description_fr") or ""
                        desc = re.sub(r'<[^>]+>', ' ', desc).strip()[:500]
                        
                        t = None
                        if fd and "T" in str(fd):
                            t = str(fd).split("T")[1][:5]
                            if t == "00:00": t = None
                        
                        region_events.append({
                            "title": title[:200], "description": desc,
                            "location": full_loc[:300],
                            "latitude": lat, "longitude": lng,
                            "date": event_date, "end_date": event_end,
                            "time": t, "end_time": None,
                            "categories": categorize(title, desc),
                            "source_url": source_url,
                            "validation_status": "auto_validated", "status": "active"
                        })
                    except: continue
                
                offset += 100
                time.sleep(0.8)
            except Exception as e:
                break
        
        print(f"  {name}: {len(region_events)} events")
        events.extend(region_events)
    
    return events

# ============================
# MAIN
# ============================
if __name__ == "__main__":
    print("=" * 60)
    print("IMPORT OPEN DATA FRAIS - Sources nouvelles")
    print("=" * 60)
    
    helsinki = import_helsinki(max_pages=8)
    quebec = import_quebec()
    oa_fr = import_oa_new_regions()
    
    all_events = helsinki + quebec + oa_fr
    
    print(f"\n{'=' * 60}")
    print(f"TOTAL: {len(all_events)} events a envoyer")
    print(f"  Helsinki: {len(helsinki)}")
    print(f"  Quebec: {len(quebec)}")
    print(f"  OA France regions: {len(oa_fr)}")
    
    if all_events:
        print("\nExemples:")
        import random
        samples = random.sample(all_events, min(8, len(all_events)))
        for e in samples:
            print(f"  {e['date']} | {e['title'][:40]} | {e['location'][:30]} | {e['categories'][:2]}")
        
        print(f"\nEnvoi...")
        ok = send_batch(all_events)
        print(f"\nResultat: {ok}/{len(all_events)} events inseres")
    else:
        print("\nAucun event.")
    
    print("\nTermine!")
