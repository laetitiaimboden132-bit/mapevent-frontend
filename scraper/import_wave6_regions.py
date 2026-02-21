"""
Import Wave 6 - More France by REGION (departments with most events)
+ More Ile-de-France suburbs
"""

import requests
import json
import time
import re
from datetime import datetime, date

API_BASE = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api"
HEADERS = {"User-Agent": "MapEventAI-Bot/1.0 (open data consumer)"}
TODAY = date.today().strftime("%Y-%m-%d")
ODS_BASE = "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/evenements-publics-openagenda/records"


def clean_html(text, max_len=350):
    if not text: return ""
    text = re.sub(r'<[^>]+>', ' ', str(text))
    text = re.sub(r'&[a-z]+;', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) > max_len: text = text[:max_len].rsplit(' ', 1)[0] + "..."
    return text


def categorize(title, desc, kw=""):
    cats = []
    c = f"{title} {desc} {kw}".lower()
    if any(w in c for w in ["concert", "musique", "music"]):
        if "jazz" in c: cats.append("Musique > Jazz")
        elif any(w in c for w in ["classique", "classical"]): cats.append("Musique > Classique")
        elif any(w in c for w in ["electro", "techno"]): cats.append("Musique > Electronic")
        elif any(w in c for w in ["rock", "metal"]): cats.append("Musique > Rock")
        else: cats.append("Musique > Concert")
    if any(w in c for w in ["théâtre", "theatre"]): cats.append("Spectacle > Théâtre")
    if any(w in c for w in ["danse", "dance"]): cats.append("Danse")
    if any(w in c for w in ["exposition", "exhibition"]): cats.append("Culture > Exposition")
    if any(w in c for w in ["cinéma", "film"]): cats.append("Culture > Cinéma")
    if any(w in c for w in ["sport", "marathon", "course"]): cats.append("Sport")
    if "festival" in c and not cats: cats.append("Festival")
    if any(w in c for w in ["marché", "brocante"]): cats.append("Marché & Brocante")
    if any(w in c for w in ["conférence"]): cats.append("Conférence")
    if any(w in c for w in ["atelier", "workshop"]): cats.append("Atelier")
    if any(w in c for w in ["enfant", "famille"]): cats.append("Famille & Enfants")
    if any(w in c for w in ["humour", "stand-up"]): cats.append("Spectacle > Humour")
    if any(w in c for w in ["spectacle"]): 
        if not any("Spectacle" in cc for cc in cats): cats.append("Spectacle")
    if not cats: cats.append("Événement")
    return cats[:3]


def send_all(events, name):
    total = 0
    for i in range(0, len(events), 10):
        batch = events[i:i+10]
        try:
            r = requests.post(f"{API_BASE}/events/scraped/batch", json={"events": batch}, headers=HEADERS, timeout=60)
            if r.status_code in (200, 201):
                total += r.json().get("inserted", r.json().get("count", len(batch)))
        except:
            pass
        if i + 10 < len(events):
            time.sleep(0.5)
    return total


def parse_oa(record):
    """Parse OpenAgenda record."""
    title = record.get("title_fr") or record.get("title") or ""
    if not title: return None
    
    desc = clean_html(record.get("description_fr") or record.get("description") or "")
    
    loc_name = record.get("location_name") or ""
    loc_addr = record.get("location_address") or ""
    loc_city = record.get("location_city") or ""
    loc_dept = record.get("location_department") or ""
    
    location_str = loc_name
    if loc_addr: location_str += f", {loc_addr}" if location_str else loc_addr
    if loc_city and loc_city not in location_str: location_str += f", {loc_city}"
    if not location_str: location_str = f"{loc_city or loc_dept}, France"
    elif "France" not in location_str: location_str += ", France"
    
    coords = record.get("location_coordinates")
    if not coords: return None
    if isinstance(coords, dict):
        lat, lon = coords.get("lat"), coords.get("lon")
    elif isinstance(coords, list) and len(coords) >= 2:
        lat, lon = coords[0], coords[1]
    else: return None
    try: lat, lon = float(lat), float(lon)
    except: return None
    if lat == 0 and lon == 0: return None
    # France + DOM-TOM bounds
    if not ((41.0 <= lat <= 51.5 and -5.5 <= lon <= 10.0) or  # France métro
            (14.0 <= lat <= 16.5 and -62.0 <= lon <= -60.5) or  # Antilles
            (-21.5 <= lat <= -20.5 and 55.0 <= lon <= 56.0)):  # Réunion
        return None
    
    fb = record.get("firstdate_begin") or ""
    le = record.get("lastdate_end") or ""
    event_date = fb[:10] if fb else None
    end_date = le[:10] if le else None
    ev_time = None
    if not event_date: return None
    if end_date == event_date: end_date = None
    if fb and "T" in fb and len(fb) >= 16:
        h = fb[11:16]
        if h != "00:00": ev_time = h
    try:
        check = end_date or event_date
        if datetime.strptime(check, "%Y-%m-%d").date() < date.today(): return None
    except: pass
    
    source_url = record.get("canonicalurl") or ""
    if not source_url: return None
    
    kw = record.get("keywords_fr") or []
    if isinstance(kw, str): kw = [k.strip() for k in kw.split(",")]
    cats = categorize(title, desc, " ".join(kw) if isinstance(kw, list) else "")
    
    return {
        "title": title[:200], "description": desc,
        "date": event_date, "end_date": end_date,
        "time": ev_time, "end_time": None,
        "location": location_str[:300],
        "latitude": round(lat, 6), "longitude": round(lon, 6),
        "categories": cats,
        "source_url": source_url,
        "source": f"OpenAgenda - {loc_city or loc_dept}",
        "validation_status": "auto_validated"
    }


def fetch_by_department(department, max_events=100):
    """Fetch events for a department."""
    events = []
    seen = set()
    offset = 0
    
    while len(events) < max_events:
        try:
            params = {
                "where": f'location_department="{department}" AND firstdate_begin >= "{TODAY}"',
                "limit": min(100, max_events - len(events)),
                "offset": offset,
                "order_by": "firstdate_begin"
            }
            r = requests.get(ODS_BASE, params=params, headers=HEADERS, timeout=20)
            if r.status_code != 200: break
            data = r.json()
            results = data.get("results", [])
            if not results: break
            
            for rec in results:
                ev = parse_oa(rec)
                if ev:
                    key = f"{ev['title'][:40]}|{ev['date']}|{ev['latitude']:.3f}"
                    if key not in seen:
                        seen.add(key)
                        events.append(ev)
            
            offset += len(results)
            if len(results) < 100: break
            time.sleep(0.5)
        except:
            break
    
    return events


def main():
    print("=" * 60)
    print("IMPORT WAVE 6 - France by department (extra)")
    print("=" * 60)
    
    # Departments with most events (excluding already well-covered cities)
    departments = [
        ("Seine-Saint-Denis", 80),
        ("Hauts-de-Seine", 80),
        ("Val-de-Marne", 80),
        ("Essonne", 60),
        ("Yvelines", 80),
        ("Seine-et-Marne", 60),
        ("Val-d'Oise", 50),
        ("Bouches-du-Rhône", 100),
        ("Nord", 100),
        ("Gironde", 100),
        ("Haute-Garonne", 100),
        ("Loire-Atlantique", 100),
        ("Hérault", 80),
        ("Ille-et-Vilaine", 80),
        ("Var", 80),
        ("Finistère", 80),
        ("Isère", 80),
        ("Morbihan", 50),
        ("Côtes-d'Armor", 50),
        ("Maine-et-Loire", 50),
        ("Calvados", 50),
        ("Haute-Savoie", 50),
        ("Savoie", 50),
        ("Drôme", 50),
        ("Vaucluse", 50),
        ("Pyrénées-Atlantiques", 50),
        ("Charente-Maritime", 50),
        ("Vendée", 50),
        ("Sarthe", 50),
        ("Indre-et-Loire", 50),
        ("Loiret", 50),
        ("Pas-de-Calais", 50),
        ("Somme", 30),
        ("Oise", 30),
        ("Aisne", 30),
        ("Marne", 30),
    ]
    
    results = {}
    total_events = []
    seen_global = set()
    
    for dept, limit in departments:
        events = fetch_by_department(dept, limit)
        new_events = []
        for ev in events:
            key = f"{ev['title'][:40]}|{ev['date']}|{ev['latitude']:.3f}"
            if key not in seen_global:
                seen_global.add(key)
                new_events.append(ev)
        
        if new_events:
            total_events.extend(new_events)
            print(f"  {dept}: {len(new_events)} new events")
        time.sleep(0.3)
    
    print(f"\nTotal new events: {len(total_events)}")
    
    if total_events:
        n = send_all(total_events, "France departments")
        results["France departments"] = n
        print(f"  ✅ France departments: {n}")
    
    # Summary
    print(f"\n{'=' * 60}")
    print("RÉSUMÉ WAVE 6:")
    total = sum(results.values())
    for source, count in results.items():
        print(f"  {source}: {count}")
    print(f"  TOTAL: {total}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
