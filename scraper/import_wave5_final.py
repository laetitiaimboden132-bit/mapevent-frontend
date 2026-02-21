"""
Import Wave 5 - Montreal + more Helsinki + opendata.paris.fr specific
"""

import requests
import json
import time
import re
import hashlib
from datetime import datetime, date

API_BASE = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws/api"
HEADERS = {"User-Agent": "MapEventAI-Bot/1.0 (open data consumer)"}
TODAY = date.today().strftime("%Y-%m-%d")


def clean_html(text, max_len=350):
    if not text:
        return ""
    text = re.sub(r'<[^>]+>', ' ', str(text))
    text = re.sub(r'&[a-z]+;', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) > max_len:
        text = text[:max_len].rsplit(' ', 1)[0] + "..."
    return text


def categorize(title, desc, kw=""):
    cats = []
    c = f"{title} {desc} {kw}".lower()
    if any(w in c for w in ["concert", "music", "musique"]): 
        if "jazz" in c: cats.append("Musique > Jazz")
        elif any(w in c for w in ["classique", "classical"]): cats.append("Musique > Classique")
        elif any(w in c for w in ["electro", "techno"]): cats.append("Musique > Electronic")
        elif any(w in c for w in ["rock", "metal"]): cats.append("Musique > Rock")
        else: cats.append("Musique > Concert")
    if any(w in c for w in ["théâtre", "theatre"]): cats.append("Spectacle > Théâtre")
    if any(w in c for w in ["danse", "dance", "ballet"]): cats.append("Danse")
    if any(w in c for w in ["exposition", "exhibition"]): cats.append("Culture > Exposition")
    if any(w in c for w in ["cinéma", "cinema", "film"]): cats.append("Culture > Cinéma")
    if any(w in c for w in ["sport", "marathon", "course"]): cats.append("Sport")
    if "festival" in c and not cats: cats.append("Festival")
    if any(w in c for w in ["marché", "market"]): cats.append("Marché & Brocante")
    if any(w in c for w in ["conférence", "conference"]): cats.append("Conférence")
    if any(w in c for w in ["atelier", "workshop"]): cats.append("Atelier")
    if any(w in c for w in ["enfant", "famille", "children"]): cats.append("Famille & Enfants")
    if any(w in c for w in ["humour", "comedy"]): cats.append("Spectacle > Humour")
    if any(w in c for w in ["consultation", "séance d'information", "assemblée"]): cats.append("Conférence")
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


# ============================================
# MONTREAL - donnees.montreal.ca GeoJSON
# ============================================
def fetch_montreal_events(max_events=500):
    """Fetch Montreal events from open data GeoJSON."""
    print("\n🇨🇦 MONTRÉAL - donnees.montreal.ca")
    
    url = "https://donnees.montreal.ca/dataset/6a4cbf2c-c9b7-413a-86b1-e8f7081e2578/resource/35307457-a00f-4912-9941-8095ead51f6e/download/evenements.geojson"
    
    try:
        r = requests.get(url, headers=HEADERS, timeout=60)
        if r.status_code != 200:
            print(f"  HTTP {r.status_code}")
            return []
        
        data = r.json()
        features = data.get("features", [])
        print(f"  Total features: {len(features)}")
    except Exception as e:
        print(f"  Error: {e}")
        return []
    
    events = []
    seen = set()
    
    for feat in features:
        if len(events) >= max_events:
            break
        
        props = feat.get("properties", {})
        geo = feat.get("geometry")
        
        # Must have title and future date
        title = props.get("titre", "")
        if not title:
            continue
        
        date_debut = props.get("date_debut", "")
        date_fin = props.get("date_fin", "")
        
        if not date_debut:
            continue
        
        # Check future
        check = (date_fin or date_debut)[:10]
        try:
            if check < TODAY:
                continue
        except:
            continue
        
        # Coordinates
        lat = props.get("lat")
        lon = props.get("long")
        
        if not lat or not lon or str(lat) == "None" or str(lon) == "None":
            # Try from geometry
            if geo and geo.get("coordinates"):
                coords = geo["coordinates"]
                lon = float(coords[0])
                lat = float(coords[1])
            else:
                # Use Montreal center with offset
                h = int(hashlib.md5(title.encode()).hexdigest()[:8], 16)
                lat = 45.5017 + ((h % 200) - 100) / 6000.0
                lon = -73.5673 + ((h // 200 % 200) - 100) / 6000.0
        
        try:
            lat = float(lat)
            lon = float(lon)
        except:
            continue
        
        # Montreal bounds
        if not (44.5 <= lat <= 46.5 and -75.0 <= lon <= -72.0):
            continue
        
        # Description
        desc = clean_html(props.get("description", ""))
        event_type = props.get("type_evenement", "")
        
        # Location
        adresse = props.get("adresse_principale", "")
        arr = props.get("arrondissement", "")
        titre_addr = props.get("titre_adresse", "")
        
        location_str = titre_addr or ""
        if adresse and str(adresse) != "nan":
            location_str = f"{location_str}, {adresse}" if location_str else adresse
        if arr and str(arr) != "nan" and arr not in location_str:
            location_str += f", {arr}"
        location_str += ", Montréal, Canada"
        
        # Source URL
        source_url = props.get("url_fiche", "")
        if not source_url:
            continue
        
        event_date = date_debut[:10]
        end_date = date_fin[:10] if date_fin else None
        if end_date == event_date:
            end_date = None
        
        # Dedup
        key = f"{title[:40]}|{event_date}|{lat:.3f}"
        if key in seen:
            continue
        seen.add(key)
        
        categories = categorize(title, desc, event_type)
        
        events.append({
            "title": title[:200],
            "description": desc if desc else f"{event_type} à Montréal",
            "date": event_date,
            "end_date": end_date,
            "time": None,
            "end_time": None,
            "location": location_str[:300],
            "latitude": round(lat, 6),
            "longitude": round(lon, 6),
            "categories": categories,
            "source_url": source_url,
            "source": "Données Montréal",
            "validation_status": "auto_validated"
        })
    
    print(f"  Total Montreal: {len(events)} events")
    return events


# ============================================
# Paris specific - opendata.paris.fr
# ============================================
def fetch_paris_events():
    """Fetch more Paris events from opendata.paris.fr."""
    print("\n🇫🇷 PARIS - opendata.paris.fr")
    
    # Que Faire à Paris dataset
    url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/que-faire-a-paris-/records"
    
    events = []
    seen = set()
    offset = 0
    
    while len(events) < 300:
        try:
            params = {
                "where": f'date_start >= "{TODAY}"',
                "limit": 100,
                "offset": offset,
                "order_by": "date_start"
            }
            r = requests.get(url, params=params, headers=HEADERS, timeout=30)
            if r.status_code != 200:
                print(f"  HTTP {r.status_code}: {r.text[:200]}")
                break
            
            data = r.json()
            results = data.get("results", [])
            if not results:
                break
            
            for rec in results:
                ev = parse_paris(rec)
                if ev:
                    key = f"{ev['title'][:40]}|{ev['date']}|{ev['latitude']:.3f}"
                    if key not in seen:
                        seen.add(key)
                        events.append(ev)
            
            offset += len(results)
            if len(results) < 100:
                break
            time.sleep(1)
        except Exception as e:
            print(f"  Error: {e}")
            break
    
    print(f"  Total Paris: {len(events)} events")
    return events


def parse_paris(rec):
    """Parse Paris opendata record."""
    title = rec.get("title") or rec.get("titre") or ""
    if not title:
        return None
    
    desc = clean_html(rec.get("description") or rec.get("lead_text") or "")
    
    # Coords
    geo = rec.get("lat_lon") or rec.get("geo_point_2d")
    if not geo:
        return None
    
    if isinstance(geo, dict):
        lat = geo.get("lat")
        lon = geo.get("lon")
    elif isinstance(geo, list) and len(geo) >= 2:
        lat = geo[0]
        lon = geo[1]
    else:
        return None
    
    try:
        lat = float(lat)
        lon = float(lon)
    except:
        return None
    
    if not (48.5 <= lat <= 49.2 and 1.8 <= lon <= 3.0):
        return None
    
    # Dates
    date_start = rec.get("date_start") or ""
    date_end = rec.get("date_end") or ""
    
    event_date = str(date_start)[:10] if date_start else None
    end_date = str(date_end)[:10] if date_end else None
    
    if not event_date:
        return None
    if end_date == event_date:
        end_date = None
    
    try:
        check = end_date or event_date
        if datetime.strptime(check, "%Y-%m-%d").date() < date.today():
            return None
    except:
        pass
    
    # Location
    address = rec.get("address_street") or rec.get("address_name") or ""
    zipcode = rec.get("address_zipcode") or ""
    city = rec.get("address_city") or "Paris"
    
    location_str = address
    if zipcode:
        location_str += f", {zipcode}"
    if city and city not in location_str:
        location_str += f", {city}"
    if "France" not in location_str:
        location_str += ", France"
    
    # Source URL
    source_url = rec.get("url") or rec.get("access_link") or ""
    if not source_url:
        event_id = rec.get("id") or rec.get("recordid") or ""
        if event_id:
            source_url = f"https://quefaire.paris.fr/fiche/{event_id}"
    if not source_url:
        return None
    
    tags = rec.get("tags") or ""
    category = rec.get("category") or ""
    categories = categorize(title, desc, f"{tags} {category}")
    
    return {
        "title": title[:200],
        "description": desc,
        "date": event_date,
        "end_date": end_date,
        "time": None,
        "end_time": None,
        "location": location_str[:300],
        "latitude": round(lat, 6),
        "longitude": round(lon, 6),
        "categories": categories,
        "source_url": source_url,
        "source": "opendata.paris.fr",
        "validation_status": "auto_validated"
    }


# ============================================
# More Helsinki (pages 16+)
# ============================================
def fetch_helsinki_extra():
    """Even more Helsinki events."""
    print("\n🇫🇮 FINLAND EXTRA - Pages 16-25")
    events = []
    seen = set()
    
    for page in range(16, 26):
        try:
            r = requests.get("https://api.hel.fi/linkedevents/v1/event/",
                params={"start": TODAY, "page_size": 100, "page": page, "format": "json", "include": "location"},
                headers=HEADERS, timeout=30)
            if r.status_code != 200:
                break
            data = r.json()
            items = data.get("data", [])
            if not items:
                break
            
            for item in items:
                name = item.get("name", {})
                title = name.get("fi") or name.get("en") or name.get("sv") or ""
                if not title: continue
                
                location = item.get("location", {})
                if not isinstance(location, dict): continue
                position = location.get("position")
                if not position: continue
                coords = position.get("coordinates", [])
                if len(coords) < 2: continue
                lon, lat = float(coords[0]), float(coords[1])
                if not (59.0 <= lat <= 70.5 and 19.0 <= lon <= 32.0): continue
                
                start_time = item.get("start_time", "")
                event_date = start_time[:10] if start_time else None
                if not event_date: continue
                
                try:
                    if datetime.strptime(event_date, "%Y-%m-%d").date() < date.today(): continue
                except: continue
                
                desc = item.get("short_description", {}) or {}
                description = clean_html(desc.get("fi") or desc.get("en") or "")
                
                loc_name = (location.get("name", {}) or {}).get("fi") or ""
                city = (location.get("address_locality", {}) or {}).get("fi") or "Helsinki"
                location_str = f"{loc_name}, {city}, Finland"
                
                info_url = item.get("info_url", {}) or {}
                source_url = info_url.get("fi") or info_url.get("en") or f"https://linkedevents.hel.fi/fi/event/{item.get('id', '')}"
                if not source_url: continue
                
                end_time = item.get("end_time", "")
                event_end = end_time[:10] if end_time else None
                if event_end == event_date: event_end = None
                
                key = f"{title[:40]}|{event_date}|{lat:.3f}"
                if key in seen: continue
                seen.add(key)
                
                events.append({
                    "title": title[:200], "description": description,
                    "date": event_date, "end_date": event_end,
                    "time": None, "end_time": None,
                    "location": location_str[:300],
                    "latitude": round(lat, 6), "longitude": round(lon, 6),
                    "categories": categorize(title, description),
                    "source_url": source_url,
                    "source": f"LinkedEvents - {city}",
                    "validation_status": "auto_validated"
                })
            
            print(f"  Page {page}: +{len(items)} items")
            if not data.get("meta", {}).get("next"): break
            time.sleep(1)
        except Exception as e:
            print(f"  Page {page} error: {e}")
            break
    
    print(f"  Total Finland extra: {len(events)}")
    return events


# ============================================
# MAIN
# ============================================
def main():
    print("=" * 60)
    print("IMPORT WAVE 5 - Montreal + Paris specific + More Finland")
    print("=" * 60)
    
    results = {}
    
    # Montreal
    mtl_events = fetch_montreal_events(max_events=500)
    if mtl_events:
        n = send_all(mtl_events, "Montreal")
        results["Montreal"] = n
        print(f"  ✅ Montreal: {n}")
    
    # Paris
    paris_events = fetch_paris_events()
    if paris_events:
        n = send_all(paris_events, "Paris")
        results["Paris extra"] = n
        print(f"  ✅ Paris: {n}")
    
    # More Finland
    fi_events = fetch_helsinki_extra()
    if fi_events:
        n = send_all(fi_events, "Finland extra")
        results["Finland extra"] = n
        print(f"  ✅ Finland extra: {n}")
    
    # Summary
    print(f"\n{'=' * 60}")
    print("RÉSUMÉ WAVE 5:")
    total = 0
    for source, count in results.items():
        print(f"  {source}: {count}")
        total += count
    print(f"  TOTAL: {total}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
