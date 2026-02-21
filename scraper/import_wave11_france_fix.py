"""
Import Wave 11 (FIXED) - All remaining French regions from OpenAgenda.
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
    if any(w in c for w in ["exposition", "exhibition", "galerie"]): cats.append("Culture > Exposition")
    if any(w in c for w in ["cinéma", "cinema", "film", "projection"]): cats.append("Culture > Cinéma")
    if any(w in c for w in ["musée", "museum"]): cats.append("Culture > Musée")
    if any(w in c for w in ["sport", "marathon", "course", "trail", "cyclisme", "football", "rugby"]): cats.append("Sport")
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


def parse_openagenda(record):
    # Fields are suffixed with _fr in this dataset
    title = record.get("title_fr") or record.get("title", "")
    if not title: return None
    
    desc = clean_html(record.get("longdescription_fr") or record.get("description_fr") or "")
    
    first_date = record.get("firstdate_begin", "")
    last_date = record.get("lastdate_end", "")
    event_date = first_date[:10] if first_date else None
    end_date = last_date[:10] if last_date else None
    if not event_date: return None
    if end_date == event_date: end_date = None
    
    ev_time = None
    if first_date and "T" in first_date:
        t = first_date.split("T")[1][:5]
        if t not in ("00:00", "23:59", "01:00"): ev_time = t
    
    try:
        check = end_date or event_date
        if datetime.strptime(check, "%Y-%m-%d").date() < date.today(): return None
    except: pass
    
    # Skip events far in the future (likely placeholder data)
    try:
        if datetime.strptime(event_date, "%Y-%m-%d").date().year > 2027: return None
    except: pass
    
    coords = record.get("location_coordinates", {})
    lat = lon = None
    if isinstance(coords, dict):
        lat = coords.get("lat")
        lon = coords.get("lon")
    elif isinstance(coords, list) and len(coords) >= 2:
        lat, lon = coords[0], coords[1]
    
    if not lat or not lon: return None
    try: lat, lon = float(lat), float(lon)
    except: return None
    if not (41.0 < lat < 51.5 and -5.5 < lon < 10.0): return None
    
    city = record.get("location_city", "")
    address = record.get("location_address", "")
    location_str = f"{address}, {city}" if address else city
    if not location_str: location_str = "France"
    if "France" not in location_str: location_str += ", France"
    
    # Use canonicalurl as source_url
    source_url = record.get("canonicalurl") or ""
    if not source_url: return None
    
    kw_list = record.get("keywords_fr") or []
    kw = " ".join(kw_list) if isinstance(kw_list, list) else str(kw_list)
    
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


def fetch_region(region_name, max_events=500):
    """Fetch events for one French region."""
    base = "https://public.opendatasoft.com/api/explore/v2.1/catalog/datasets/evenements-publics-openagenda/records"
    events = []
    seen = set()
    offset = 0
    
    while offset < max_events:
        try:
            where = f"location_region='{region_name}' AND firstdate_begin >= '{TODAY}'"
            
            r = requests.get(base, params={
                "where": where,
                "limit": 100,
                "offset": offset,
            }, headers=HEADERS, timeout=20)
            
            if r.status_code != 200:
                print(f"    HTTP {r.status_code} at offset {offset}")
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
                        events.append(ev)
            
            offset += 100
            if offset >= total: break
            time.sleep(0.5)
        except Exception as e:
            print(f"    Error at offset {offset}: {str(e)[:60]}")
            break
    
    return events


def main():
    print("=" * 60)
    print("IMPORT WAVE 11 - All French regions (FIXED)")
    print("=" * 60)
    
    regions = [
        "Centre-Val de Loire",
        "Pays de la Loire",
        "Nouvelle-Aquitaine",
        "Île-de-France",
        "Occitanie",
        "Bretagne",
        "Hauts-de-France",
        "Grand Est",
        "Auvergne-Rhône-Alpes",
        "Normandie",
        "Provence-Alpes-Côte d'Azur",
        "Bourgogne-Franche-Comté",
        "Corse",
    ]
    
    all_events = []
    seen_global = set()
    results = {}
    
    for region in regions:
        print(f"\n  📍 {region}...")
        events = fetch_region(region)
        new = 0
        for ev in events:
            key = f"{ev['title'][:40]}|{ev['date']}|{ev['latitude']:.3f}"
            if key not in seen_global:
                seen_global.add(key)
                all_events.append(ev)
                new += 1
        if new > 0:
            print(f"    → {new} new events")
            results[region] = new
    
    # Send all at once
    total_sent = 0
    if all_events:
        print(f"\n  Sending {len(all_events)} events...")
        total_sent = send_all(all_events, "France regions")
    
    print(f"\n{'=' * 60}")
    print("RÉSUMÉ WAVE 11:")
    for region, count in results.items():
        print(f"  {region}: {count}")
    print(f"  TOTAL ENVOYÉ: {total_sent}")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
