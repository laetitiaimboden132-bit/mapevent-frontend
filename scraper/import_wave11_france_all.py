"""
Import Wave 11 - All remaining French regions from OpenAgenda + finish Berlin
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
    if not text: return ""
    text = re.sub(r'<[^>]+>', ' ', str(text))
    text = re.sub(r'&[a-z]+;', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    if len(text) > max_len: text = text[:max_len].rsplit(' ', 1)[0] + "..."
    return text


def categorize(title, desc="", kw=""):
    cats = []
    c = f"{title} {desc} {kw}".lower()
    if any(w in c for w in ["concert", "music", "musique", "orchestre", "chorale"]):
        if "jazz" in c: cats.append("Musique > Jazz")
        elif any(w in c for w in ["classique", "classical", "symphoni"]): cats.append("Musique > Classique")
        elif any(w in c for w in ["electro", "techno", "house", "dj"]): cats.append("Musique > Electronic")
        elif any(w in c for w in ["rock", "metal", "punk"]): cats.append("Musique > Rock")
        elif any(w in c for w in ["hip-hop", "rap"]): cats.append("Musique > Hip-Hop")
        else: cats.append("Musique > Concert")
    if any(w in c for w in ["théâtre", "theatre", "spectacle vivant", "comédie"]): cats.append("Spectacle > Théâtre")
    if any(w in c for w in ["danse", "ballet", "chorégraph"]): cats.append("Danse")
    if any(w in c for w in ["exposition", "exhibition", "galerie", "gallery"]): cats.append("Culture > Exposition")
    if any(w in c for w in ["cinéma", "cinema", "film", "projection"]): cats.append("Culture > Cinéma")
    if any(w in c for w in ["musée", "museum"]): cats.append("Culture > Musée")
    if any(w in c for w in ["sport", "marathon", "course", "trail", "cyclisme", "vélo", "football", "rugby"]): cats.append("Sport")
    if "festival" in c and not cats: cats.append("Festival")
    if any(w in c for w in ["marché", "brocante", "vide-grenier", "puces"]): cats.append("Marché & Brocante")
    if any(w in c for w in ["conférence", "débat", "rencontre", "table ronde"]): cats.append("Conférence")
    if any(w in c for w in ["atelier", "workshop", "stage"]): cats.append("Atelier")
    if any(w in c for w in ["enfant", "famille", "jeunesse", "conte"]): cats.append("Famille & Enfants")
    if any(w in c for w in ["humour", "one-man", "sketch", "comedy"]): cats.append("Spectacle > Humour")
    if any(w in c for w in ["fête", "soirée", "bal ", "carnaval"]): cats.append("Fête")
    if any(w in c for w in ["randonnée", "balade", "promenade", "nature"]): cats.append("Nature & Plein Air")
    if any(w in c for w in ["lecture", "livre", "auteur", "dédicace", "littéra"]): cats.append("Culture > Littérature")
    if any(w in c for w in ["gastronomie", "dégustation", "vin", "cuisine"]): cats.append("Gastronomie")
    if not cats: cats.append("Événement")
    return list(dict.fromkeys(cats))[:3]


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
# FRANCE - All regions from OpenAgenda
# ============================================
def fetch_france_all_regions():
    """Fetch all French events region by region from OpenAgenda."""
    print("\n🇫🇷 FRANCE - All regions via OpenAgenda")
    base = "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/evenements-publics-openagenda/records"
    
    # Use the exact region names from the facets
    regions_with_counts = [
        ("Centre-Val de Loire", 1918),
        ("Pays de la Loire", 1615),
        ("Nouvelle-Aquitaine", 1493),
        ("Occitanie", 1034),
        ("Bretagne", 861),
        ("Hauts-de-France", 767),
        ("Grand Est", 708),
        ("Auvergne-Rhône-Alpes", 475),
        ("Normandie", 356),
        ("Bourgogne-Franche-Comté", 141),
    ]
    
    all_events = []
    seen = set()
    
    for region, expected in regions_with_counts:
        region_count = 0
        # Use URL-safe encoding for the query - use ODSQL encoding
        # The trick: use search() function instead of exact match for accented names
        offset = 0
        max_records = min(expected, 500)  # Cap at 500 per region (quota compliance)
        
        while offset < max_records:
            try:
                # Use ODSQL with search to avoid encoding issues
                where_clause = f'location_region="{region}" AND firstdate_begin >= "{TODAY}"'
                
                r = requests.get(base, params={
                    "where": where_clause,
                    "limit": 100,
                    "offset": offset,
                    "select": "title,description,longdescription_fr,firstdate_begin,lastdate_end,location_coordinates,location_address,location_city,source_url,keywords_fr"
                }, headers=HEADERS, timeout=20)
                
                if r.status_code != 200:
                    print(f"  {region}: HTTP {r.status_code}")
                    break
                
                data = r.json()
                records = data.get("results", [])
                total = data.get("total_count", 0)
                if not records: break
                
                for record in records:
                    ev = parse_openagenda(record)
                    if ev:
                        key = f"{ev['title'][:40]}|{ev['date']}|{ev['latitude']:.3f}"
                        if key not in seen:
                            seen.add(key)
                            all_events.append(ev)
                            region_count += 1
                
                offset += 100
                if offset >= total: break
                time.sleep(0.5)
            except Exception as e:
                print(f"  {region} offset {offset}: {str(e)[:60]}")
                break
        
        if region_count > 0:
            print(f"  {region}: {region_count} new events (available: {expected})")
    
    # Also fetch Île-de-France (excluding Paris which we already have)
    print("  Fetching Île-de-France (non-Paris)...")
    offset = 0
    idf_count = 0
    while offset < 500:
        try:
            r = requests.get(base, params={
                "where": f'location_region="Île-de-France" AND firstdate_begin >= "{TODAY}" AND NOT location_city="Paris"',
                "limit": 100,
                "offset": offset,
                "select": "title,description,longdescription_fr,firstdate_begin,lastdate_end,location_coordinates,location_address,location_city,source_url,keywords_fr"
            }, headers=HEADERS, timeout=20)
            
            if r.status_code != 200: break
            data = r.json()
            records = data.get("results", [])
            if not records: break
            
            for record in records:
                ev = parse_openagenda(record)
                if ev:
                    key = f"{ev['title'][:40]}|{ev['date']}|{ev['latitude']:.3f}"
                    if key not in seen:
                        seen.add(key)
                        all_events.append(ev)
                        idf_count += 1
            
            offset += 100
            if offset >= data.get("total_count", 0): break
            time.sleep(0.5)
        except:
            break
    
    if idf_count > 0:
        print(f"  Île-de-France (non-Paris): {idf_count} events")
    
    # Also try PACA with escaped quote
    offset = 0
    paca_count = 0
    while offset < 500:
        try:
            r = requests.get(base, params={
                "where": f'search(location_region, "Provence") AND firstdate_begin >= "{TODAY}"',
                "limit": 100,
                "offset": offset,
                "select": "title,description,longdescription_fr,firstdate_begin,lastdate_end,location_coordinates,location_address,location_city,source_url,keywords_fr"
            }, headers=HEADERS, timeout=20)
            
            if r.status_code != 200: break
            data = r.json()
            records = data.get("results", [])
            if not records: break
            
            for record in records:
                ev = parse_openagenda(record)
                if ev:
                    key = f"{ev['title'][:40]}|{ev['date']}|{ev['latitude']:.3f}"
                    if key not in seen:
                        seen.add(key)
                        all_events.append(ev)
                        paca_count += 1
            
            offset += 100
            if offset >= data.get("total_count", 0): break
            time.sleep(0.5)
        except:
            break
    
    if paca_count > 0:
        print(f"  PACA: {paca_count} events")
    
    print(f"  Total France all: {len(all_events)}")
    return all_events


def parse_openagenda(record):
    title = record.get("title", "")
    if not title: return None
    
    desc = clean_html(record.get("longdescription_fr") or record.get("description") or "")
    
    first_date = record.get("firstdate_begin", "")
    last_date = record.get("lastdate_end", "")
    event_date = first_date[:10] if first_date else None
    end_date = last_date[:10] if last_date else None
    if not event_date: return None
    if end_date == event_date: end_date = None
    
    ev_time = None
    if first_date and "T" in first_date:
        t = first_date.split("T")[1][:5]
        if t not in ("00:00", "23:59"): ev_time = t
    
    try:
        check = end_date or event_date
        if datetime.strptime(check, "%Y-%m-%d").date() < date.today(): return None
    except: pass
    
    coords = record.get("location_coordinates", {})
    lat = lon = None
    if isinstance(coords, dict):
        lat = coords.get("lat")
        lon = coords.get("lon")
    elif isinstance(coords, list) and len(coords) >= 2:
        lat, lon = coords[0], coords[1]
    
    if not lat or not lon: return None
    try:
        lat, lon = float(lat), float(lon)
    except: return None
    if not (41.0 < lat < 51.5 and -5.5 < lon < 10.0): return None
    
    city = record.get("location_city", "")
    address = record.get("location_address", "")
    location_str = f"{address}, {city}" if address else city
    if not location_str: location_str = "France"
    if "France" not in location_str: location_str += ", France"
    
    source_url = record.get("source_url") or ""
    if not source_url: return None
    
    kw = " ".join(record.get("keywords_fr", []) or [])
    
    return {
        "title": title[:200], "description": desc[:350],
        "date": event_date, "end_date": end_date,
        "time": ev_time, "end_time": None,
        "location": location_str[:300],
        "latitude": round(lat, 6), "longitude": round(lon, 6),
        "categories": categorize(title, desc, kw),
        "source_url": source_url, "source": "OpenAgenda",
        "validation_status": "auto_validated"
    }


# ============================================
# MAIN
# ============================================
def main():
    print("=" * 60)
    print("IMPORT WAVE 11 - All French regions")
    print("=" * 60)
    
    results = {}
    
    # France all regions
    france = fetch_france_all_regions()
    if france:
        n = send_all(france, "France regions")
        results["France (all regions)"] = n
        print(f"  ✅ France: {n}")
    
    # Summary
    print(f"\n{'=' * 60}")
    print("RÉSUMÉ WAVE 11:")
    total = 0
    for source, count in results.items():
        print(f"  {source}: {count}")
        total += count
    print(f"  TOTAL: {total}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
