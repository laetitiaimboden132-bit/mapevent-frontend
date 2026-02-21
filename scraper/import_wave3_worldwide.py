"""
Import Wave 3 - Fill the world map with more events.
Sources:
- Helsinki LinkedEvents (more pages)
- OpenAgenda expanded (more French cities, DOM-TOM)  
- Barcelona sports + cultural (more data)
- More diverse French cities from OpenAgenda
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
ODS_BASE = "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/evenements-publics-openagenda/records"


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
    if any(w in c for w in ["concert", "music", "musique", "orchest", "choir"]):
        if "jazz" in c: cats.append("Musique > Jazz")
        elif any(w in c for w in ["classique", "classical", "symphon"]): cats.append("Musique > Classique")
        elif any(w in c for w in ["electro", "techno", "house", "dj"]): cats.append("Musique > Electronic")
        elif any(w in c for w in ["rock", "metal"]): cats.append("Musique > Rock")
        elif any(w in c for w in ["hip-hop", "rap"]): cats.append("Musique > Hip-Hop")
        elif "folk" in c: cats.append("Musique > Folk")
        else: cats.append("Musique > Concert")
    if any(w in c for w in ["théâtre", "theatre", "theater"]): cats.append("Spectacle > Théâtre")
    if any(w in c for w in ["dance", "danse", "ballet"]): cats.append("Danse")
    if any(w in c for w in ["exposition", "exhibition", "exhibit", "galerie", "gallery"]): cats.append("Culture > Exposition")
    if any(w in c for w in ["cinéma", "cinema", "film"]): cats.append("Culture > Cinéma")
    if any(w in c for w in ["sport", "football", "soccer", "basket", "tennis", "rugby", "running", "marathon"]): cats.append("Sport")
    if "festival" in c and not cats: cats.append("Festival")
    if any(w in c for w in ["marché", "market", "brocante"]): cats.append("Marché & Brocante")
    if any(w in c for w in ["conférence", "conference"]): cats.append("Conférence")
    if any(w in c for w in ["atelier", "workshop"]): cats.append("Atelier")
    if any(w in c for w in ["enfant", "children", "famille", "family"]): cats.append("Famille & Enfants")
    if any(w in c for w in ["humour", "comedy", "stand-up"]): cats.append("Spectacle > Humour")
    if any(w in c for w in ["fête", "party", "carnaval"]): cats.append("Fête")
    if any(w in c for w in ["gastronomie", "food", "vin", "wine", "dégustation"]): cats.append("Gastronomie > Dégustation")
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
# FRANCE EXPANDED - Smaller cities from OpenAgenda
# ============================================
def fetch_france_expanded():
    """Get events from more French cities."""
    print("\n🇫🇷 FRANCE EXPANDED - More cities")
    
    # Cities not covered or with more events available
    cities = [
        # Smaller interesting cities
        "Bayonne", "Biarritz", "Pau", "Tarbes", "Lourdes",
        "Angoulême", "Poitiers", "La Roche-sur-Yon", "Lorient", "Vannes",
        "Saint-Malo", "Saint-Brieuc", "Quimper", "Chambéry", "Annecy",
        "Valence", "Gap", "Digne-les-Bains", "Bastia", "Ajaccio",
        "Colmar", "Mulhouse", "Troyes", "Chartres", "Blois",
        "Bourges", "Nevers", "Auxerre", "Châteauroux", "Niort",
        "La Rochelle", "Rochefort", "Saintes", "Cognac", "Périgueux",
        "Bergerac", "Agen", "Mont-de-Marsan", "Dax", "Auch",
        "Albi", "Castres", "Cahors", "Rodez", "Aurillac",
        "Le Puy-en-Velay", "Saint-Flour", "Moulins", "Vichy", "Montluçon",
        "Thonon-les-Bains", "Évian-les-Bains", "Chamonix", "Albertville",
        "Saint-Étienne", "Villeurbanne", "Vénissieux", "Villefranche-sur-Saône",
        "Dunkerque", "Calais", "Boulogne-sur-Mer", "Arras", "Lens",
        "Douai", "Valenciennes", "Cambrai", "Saint-Quentin", "Laon",
        "Compiègne", "Beauvais", "Senlis", "Fontainebleau", "Melun",
        "Versailles", "Saint-Germain-en-Laye", "Sceaux", "Créteil",
        "Saint-Denis", "Montreuil", "Nanterre", "Boulogne-Billancourt",
        "Issy-les-Moulineaux", "Vincennes", "Ivry-sur-Seine"
    ]
    
    events = []
    seen = set()
    
    for city in cities:
        try:
            r = requests.get(ODS_BASE, params={
                "where": f'location_city="{city}" AND firstdate_begin >= "{TODAY}"',
                "limit": 20,
                "order_by": "firstdate_begin"
            }, headers=HEADERS, timeout=15)
            
            if r.status_code != 200:
                continue
            
            data = r.json()
            results = data.get("results", [])
            
            city_count = 0
            for rec in results:
                ev = parse_oa(rec, city, "France")
                if ev:
                    key = f"{ev['title'][:40]}|{ev['date']}|{ev['latitude']:.3f}"
                    if key not in seen:
                        seen.add(key)
                        events.append(ev)
                        city_count += 1
            
            if city_count > 0:
                print(f"  {city}: {city_count}")
            time.sleep(0.3)
        except:
            continue
    
    print(f"  Total France expanded: {len(events)}")
    return events


# ============================================
# More Helsinki events (pages 7+)
# ============================================
def fetch_helsinki_more():
    """Fetch more Helsinki events (pages 7-15)."""
    print("\n🇫🇮 FINLAND EXPANDED - More pages")
    events = []
    seen = set()
    
    for page in range(7, 16):
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
                ev = parse_linkedevent(item)
                if ev:
                    key = f"{ev['title'][:40]}|{ev['date']}|{ev['latitude']:.3f}"
                    if key not in seen:
                        seen.add(key)
                        events.append(ev)
            
            print(f"  Page {page}: +{len(items)} items")
            
            if not data.get("meta", {}).get("next"):
                break
            time.sleep(1)
        except Exception as e:
            print(f"  Page {page} error: {e}")
            break
    
    print(f"  Total Finland more: {len(events)}")
    return events


def parse_linkedevent(item):
    """Parse LinkedEvents item."""
    name = item.get("name", {})
    title = name.get("fi") or name.get("en") or name.get("sv") or ""
    if not title:
        return None
    
    desc = item.get("short_description", {}) or item.get("description", {})
    description = clean_html(desc.get("fi") or desc.get("en") or "")
    
    location = item.get("location", {})
    if not isinstance(location, dict):
        return None
    
    position = location.get("position")
    if not position:
        return None
    coords = position.get("coordinates", [])
    if len(coords) < 2:
        return None
    
    lon, lat = float(coords[0]), float(coords[1])
    if not (59.0 <= lat <= 70.5 and 19.0 <= lon <= 32.0):
        return None
    
    loc_name = (location.get("name", {}) or {}).get("fi") or (location.get("name", {}) or {}).get("en") or ""
    street = (location.get("street_address", {}) or {}).get("fi") or ""
    location_str = f"{loc_name}, {street}" if street else loc_name
    
    city = (location.get("address_locality", {}) or {}).get("fi") or "Helsinki"
    if city not in location_str:
        location_str += f", {city}"
    location_str += ", Finland"
    
    start_time = item.get("start_time", "")
    end_time = item.get("end_time", "")
    
    event_date = start_time[:10] if start_time else None
    event_end = end_time[:10] if end_time else None
    ev_time = None
    
    if not event_date:
        return None
    if event_end == event_date:
        event_end = None
    
    if start_time and "T" in start_time:
        h = start_time[11:16]
        if h != "00:00": ev_time = h
    
    try:
        check = event_end or event_date
        if datetime.strptime(check, "%Y-%m-%d").date() < date.today():
            return None
    except: pass
    
    info_url = item.get("info_url", {}) or {}
    source_url = info_url.get("fi") or info_url.get("en") or ""
    if not source_url:
        eid = item.get("id", "")
        source_url = f"https://linkedevents.hel.fi/fi/event/{eid}" if eid else ""
    if not source_url:
        return None
    
    kw_names = []
    for kw in item.get("keywords", []):
        if isinstance(kw, dict):
            n = kw.get("name", {})
            kw_names.append(n.get("fi") or n.get("en") or "")
    
    categories = categorize(title, description, " ".join(kw_names))
    
    return {
        "title": title[:200], "description": description,
        "date": event_date, "end_date": event_end,
        "time": ev_time, "end_time": None,
        "location": location_str[:300],
        "latitude": round(lat, 6), "longitude": round(lon, 6),
        "categories": categories,
        "source_url": source_url,
        "source": f"LinkedEvents - {city}",
        "validation_status": "auto_validated"
    }


# ============================================
# Barcelona extra datasets (sport + cultural)
# ============================================
def fetch_barcelona_extra():
    """Fetch extra Barcelona events from sport and cultural agendas."""
    print("\n🇪🇸 BARCELONA EXPANDED - Sport + Cultural agenda")
    events = []
    seen = set()
    
    # Sport activities
    sport_url = "https://opendata-ajuntament.barcelona.cat/data/dataset/agenda-esportiva-de-la-ciutat-de-barcelona/resource/5e62f3ca-52d2-42b5-b6bb-6b6ee32b4a78/download"
    # Cultural agenda (more data)
    cultural_url = "https://opendata-ajuntament.barcelona.cat/data/dataset/agenda-cultural-702f/resource/84a7e9d7-5f5d-43cb-aba5-e1f43e6e45d0/download"
    
    for url, label in [(cultural_url, "cultural"), (sport_url, "sport")]:
        try:
            r = requests.get(url, headers=HEADERS, timeout=30)
            if r.status_code != 200:
                print(f"  {label}: HTTP {r.status_code}")
                continue
            
            data = r.json()
            if isinstance(data, dict):
                items = data.get("@graph", data.get("results", data.get("data", [])))
            elif isinstance(data, list):
                items = data
            else:
                continue
            
            count = 0
            for item in items:
                ev = parse_bcn_extra(item, label)
                if ev:
                    key = f"{ev['title'][:40]}|{ev['date']}|{ev['latitude']:.3f}"
                    if key not in seen:
                        seen.add(key)
                        events.append(ev)
                        count += 1
            
            print(f"  Barcelona {label}: {count} events")
        except Exception as e:
            print(f"  Barcelona {label} error: {e}")
    
    print(f"  Total Barcelona extra: {len(events)}")
    return events


def parse_bcn_extra(item, label):
    """Parse Barcelona open data item."""
    name = item.get("name") or item.get("title") or ""
    if isinstance(name, dict):
        name = name.get("ca") or name.get("es") or name.get("en") or ""
    if not name:
        return None
    
    # Geo
    geo = item.get("geo_epgs_4326_latlon") or item.get("location") or {}
    if not geo or not isinstance(geo, dict):
        return None
    
    lat = geo.get("lat") or geo.get("latitude")
    lon = geo.get("lon") or geo.get("longitude")
    if not lat or not lon:
        return None
    
    try:
        lat = float(lat)
        lon = float(lon)
    except:
        return None
    
    if not (41.0 <= lat <= 41.6 and 1.8 <= lon <= 2.4):
        return None
    
    # Dates
    start = item.get("start_date") or item.get("dtstart") or ""
    end = item.get("end_date") or item.get("dtend") or ""
    
    event_date = str(start)[:10] if start else None
    end_date = str(end)[:10] if end else None
    
    if not event_date:
        return None
    if end_date == event_date:
        end_date = None
    
    try:
        check = end_date or event_date
        if datetime.strptime(check, "%Y-%m-%d").date() < date.today():
            return None
    except:
        return None
    
    # Description
    body = item.get("body") or item.get("description") or ""
    if isinstance(body, dict):
        body = body.get("ca") or body.get("es") or ""
    description = clean_html(body)
    
    # Address
    addresses = item.get("addresses") or []
    location_str = "Barcelona, España"
    if isinstance(addresses, list) and addresses:
        addr = addresses[0] if isinstance(addresses[0], dict) else {}
        street = addr.get("address_name") or addr.get("street_name") or ""
        district = addr.get("district_name") or ""
        location_str = f"{street}, {district}, Barcelona, España" if street else location_str
    
    # Source URL
    source_url = ""
    values = item.get("values") or []
    if isinstance(values, list):
        for v in values:
            if isinstance(v, dict) and v.get("url_value"):
                source_url = v["url_value"]
                break
    if not source_url:
        source_url = item.get("url") or item.get("link") or ""
    if not source_url:
        return None
    
    categories = categorize(name, description, label)
    
    return {
        "title": name[:200], "description": description,
        "date": event_date, "end_date": end_date,
        "time": None, "end_time": None,
        "location": location_str[:300],
        "latitude": round(lat, 6), "longitude": round(lon, 6),
        "categories": categories,
        "source_url": source_url,
        "source": f"BCN Open Data - {label}",
        "validation_status": "auto_validated"
    }


def parse_oa(record, city, country):
    """Parse OpenAgenda record."""
    title = record.get("title_fr") or record.get("title") or ""
    if not title:
        return None
    
    desc = clean_html(record.get("description_fr") or record.get("description") or "")
    
    loc_name = record.get("location_name") or ""
    loc_addr = record.get("location_address") or ""
    loc_city = record.get("location_city") or city
    location_str = loc_name
    if loc_addr:
        location_str += f", {loc_addr}" if location_str else loc_addr
    if loc_city and loc_city not in location_str:
        location_str += f", {loc_city}"
    if country and country not in location_str:
        location_str += f", {country}"
    
    coords = record.get("location_coordinates")
    if not coords:
        return None
    if isinstance(coords, dict):
        lat, lon = coords.get("lat"), coords.get("lon")
    elif isinstance(coords, list) and len(coords) >= 2:
        lat, lon = coords[0], coords[1]
    else:
        return None
    try:
        lat, lon = float(lat), float(lon)
    except:
        return None
    if lat == 0 and lon == 0:
        return None
    
    fb = record.get("firstdate_begin") or ""
    le = record.get("lastdate_end") or ""
    event_date = fb[:10] if fb else None
    end_date = le[:10] if le else None
    ev_time = None
    if not event_date:
        return None
    if end_date == event_date:
        end_date = None
    if fb and "T" in fb and len(fb) >= 16:
        h = fb[11:16]
        if h != "00:00": ev_time = h
    try:
        check = end_date or event_date
        if datetime.strptime(check, "%Y-%m-%d").date() < date.today():
            return None
    except: pass
    
    source_url = record.get("canonicalurl") or ""
    if not source_url:
        return None
    
    kw = record.get("keywords_fr") or []
    if isinstance(kw, str): kw = [k.strip() for k in kw.split(",")]
    categories = categorize(title, desc, " ".join(kw) if isinstance(kw, list) else "")
    
    return {
        "title": title[:200], "description": desc,
        "date": event_date, "end_date": end_date,
        "time": ev_time, "end_time": None,
        "location": location_str[:300],
        "latitude": round(lat, 6), "longitude": round(lon, 6),
        "categories": categories,
        "source_url": source_url,
        "source": f"OpenAgenda - {loc_city or city}",
        "validation_status": "auto_validated"
    }


# ============================================
# MAIN
# ============================================
def main():
    print("=" * 60)
    print("IMPORT WAVE 3 - Fill the world")
    print("=" * 60)
    
    results = {}
    
    # France expanded
    fr_events = fetch_france_expanded()
    if fr_events:
        n = send_all(fr_events, "France expanded")
        results["France expanded"] = n
        print(f"  ✅ France expanded: {n}")
    
    # Finland more
    fi_events = fetch_helsinki_more()
    if fi_events:
        n = send_all(fi_events, "Finland expanded")
        results["Finland expanded"] = n
        print(f"  ✅ Finland expanded: {n}")
    
    # Barcelona extra
    bcn_events = fetch_barcelona_extra()
    if bcn_events:
        n = send_all(bcn_events, "Barcelona expanded")
        results["Barcelona expanded"] = n
        print(f"  ✅ Barcelona expanded: {n}")
    
    # Summary
    print(f"\n{'=' * 60}")
    print("RÉSUMÉ WAVE 3:")
    total = 0
    for source, count in results.items():
        print(f"  {source}: {count}")
        total += count
    print(f"  TOTAL: {total}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
