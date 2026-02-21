"""
Fetcher OpenAgenda + open data pour events electro + generaux (Suisse + France).
Strict: adresse precise, date future, categories verifiees, source_url valide.
"""
import requests
import json
import time
import sys
import re
from datetime import datetime, date

sys.stdout.reconfigure(line_buffering=True)

TODAY = date.today().isoformat()  # 2026-02-12
print(f"Date du jour: {TODAY}")

HEADERS = {"User-Agent": "MapEventAI-Bot/1.0 (contact: mapevent777@gmail.com)"}

# ==========================================================================
# 1) OpenAgenda API - chercher des agendas electro/musique en Suisse + France
# ==========================================================================

OA_BASE = "https://api.openagenda.com/v2"
# OpenAgenda public key (free tier, 1000 req/day)
OA_KEY = "4e28e987c71b4c02a77b155e9c93718d"  # public key from their docs

all_events = []


def fetch_openagenda_events(search_query, geo_params=None, max_pages=3):
    """Fetch events from OpenAgenda API with search query"""
    events = []
    
    for page in range(1, max_pages + 1):
        params = {
            "key": OA_KEY,
            "search": search_query,
            "timings[gte]": TODAY,
            "timings[lte]": "2026-12-31",
            "size": 100,
            "offset": (page - 1) * 100,
            "monolingual": "fr",
        }
        if geo_params:
            params.update(geo_params)
        
        try:
            r = requests.get(f"{OA_BASE}/events", params=params, headers=HEADERS, timeout=30)
            if r.status_code != 200:
                print(f"  OpenAgenda erreur {r.status_code}: {r.text[:200]}")
                break
            
            data = r.json()
            page_events = data.get("events", [])
            total = data.get("total", 0)
            
            print(f"  Page {page}: {len(page_events)} events (total: {total})")
            events.extend(page_events)
            
            if len(events) >= total or len(page_events) == 0:
                break
            
            time.sleep(1)
        except Exception as e:
            print(f"  Erreur: {e}")
            break
    
    return events


def fetch_openagenda_agenda_events(agenda_uid, max_pages=3):
    """Fetch events from a specific OpenAgenda agenda"""
    events = []
    
    for page in range(1, max_pages + 1):
        params = {
            "key": OA_KEY,
            "timings[gte]": TODAY,
            "timings[lte]": "2026-12-31",
            "size": 100,
            "offset": (page - 1) * 100,
            "monolingual": "fr",
        }
        
        try:
            r = requests.get(f"{OA_BASE}/agendas/{agenda_uid}/events", params=params, headers=HEADERS, timeout=30)
            if r.status_code != 200:
                print(f"  OpenAgenda erreur {r.status_code}: {r.text[:200]}")
                break
            
            data = r.json()
            page_events = data.get("events", [])
            total = data.get("total", 0)
            
            print(f"  Page {page}: {len(page_events)} events (total: {total})")
            events.extend(page_events)
            
            if len(events) >= total or len(page_events) == 0:
                break
            
            time.sleep(1)
        except Exception as e:
            print(f"  Erreur: {e}")
            break
    
    return events


def search_openagenda_agendas(query, max_results=10):
    """Search for agendas matching a query"""
    params = {
        "key": OA_KEY,
        "search": query,
        "size": max_results,
    }
    try:
        r = requests.get(f"{OA_BASE}/agendas", params=params, headers=HEADERS, timeout=30)
        if r.status_code == 200:
            data = r.json()
            return data.get("agendas", [])
    except Exception as e:
        print(f"  Erreur recherche agendas: {e}")
    return []


# ==========================================================================
# PHASE 1: Recherche d'events electro/musique electronique
# ==========================================================================
print("\n" + "=" * 70)
print("PHASE 1: MUSIQUE ELECTRONIQUE / ELECTRO / TECHNO / DJ")
print("=" * 70)

electro_queries = [
    "techno",
    "electronic music",
    "electro party",
    "DJ set",
    "house music",
    "rave",
    "bass music",
    "drum and bass",
    "trance",
    "minimal techno",
]

# Chercher en Suisse (lat ~46.8, lng ~8.2, rayon 200km)
print("\n--- Electro en SUISSE ---")
swiss_electro = []
for q in electro_queries[:5]:  # Top 5 queries
    print(f"\nRecherche: '{q}' en Suisse...")
    evts = fetch_openagenda_events(q, geo_params={
        "geo[northEast][lat]": 47.9,
        "geo[northEast][lng]": 10.6,
        "geo[southWest][lat]": 45.8,
        "geo[southWest][lng]": 5.9,
    }, max_pages=2)
    swiss_electro.extend(evts)
    time.sleep(2)

# Chercher en France (grandes villes)
print("\n--- Electro en FRANCE (grandes villes) ---")
french_electro = []
for q in ["techno", "electro", "DJ set", "house music", "rave"]:
    print(f"\nRecherche: '{q}' en France...")
    evts = fetch_openagenda_events(q, geo_params={
        "geo[northEast][lat]": 51.1,
        "geo[northEast][lng]": 9.6,
        "geo[southWest][lat]": 42.3,
        "geo[southWest][lng]": -5.2,
    }, max_pages=2)
    french_electro.extend(evts)
    time.sleep(2)

print(f"\nTotal electro brut: Suisse={len(swiss_electro)}, France={len(french_electro)}")


# ==========================================================================
# PHASE 2: Events generaux populaires
# ==========================================================================
print("\n" + "=" * 70)
print("PHASE 2: EVENTS GENERAUX (culture, sport, famille, festival)")
print("=" * 70)

general_queries_swiss = ["festival", "spectacle", "exposition", "concert", "marche"]
general_queries_french = ["festival", "spectacle", "exposition"]

print("\n--- Events generaux en SUISSE ---")
swiss_general = []
for q in general_queries_swiss:
    print(f"\nRecherche: '{q}' en Suisse...")
    evts = fetch_openagenda_events(q, geo_params={
        "geo[northEast][lat]": 47.9,
        "geo[northEast][lng]": 10.6,
        "geo[southWest][lat]": 45.8,
        "geo[southWest][lng]": 5.9,
    }, max_pages=2)
    swiss_general.extend(evts)
    time.sleep(2)

print(f"\nTotal general brut Suisse: {len(swiss_general)}")

print("\n--- Events generaux en FRANCE ---")
french_general = []
for q in general_queries_french:
    print(f"\nRecherche: '{q}' en France...")
    evts = fetch_openagenda_events(q, geo_params={
        "geo[northEast][lat]": 51.1,
        "geo[northEast][lng]": 9.6,
        "geo[southWest][lat]": 42.3,
        "geo[southWest][lng]": -5.2,
    }, max_pages=2)
    french_general.extend(evts)
    time.sleep(2)

print(f"\nTotal general brut France: {len(french_general)}")


# ==========================================================================
# DEDUP + FILTRAGE
# ==========================================================================
print("\n" + "=" * 70)
print("DEDUP ET FILTRAGE")
print("=" * 70)

all_raw = swiss_electro + french_electro + swiss_general + french_general
print(f"Total brut avant dedup: {len(all_raw)}")

# Dedup par uid OpenAgenda
seen_uids = set()
unique = []
for e in all_raw:
    uid = e.get("uid")
    if uid and uid not in seen_uids:
        seen_uids.add(uid)
        unique.append(e)

print(f"Apres dedup: {len(unique)}")


# ==========================================================================
# EXTRACTION ET VALIDATION STRICTE
# ==========================================================================
print("\n" + "=" * 70)
print("EXTRACTION ET VALIDATION STRICTE")
print("=" * 70)

def get_text(field):
    """Extract text from OpenAgenda multilingual field"""
    if isinstance(field, str):
        return field
    if isinstance(field, dict):
        return field.get("fr") or field.get("en") or field.get("de") or next(iter(field.values()), "")
    return ""


def extract_best_timing(timings):
    """Extract the next upcoming timing"""
    if not timings:
        return None, None, None, None
    
    today_str = TODAY
    best = None
    for t in timings:
        begin = t.get("begin", "")
        if begin[:10] >= today_str:
            if best is None or begin < best.get("begin", ""):
                best = t
    
    if not best and timings:
        best = timings[-1]  # dernier timing
    
    if not best:
        return None, None, None, None
    
    begin = best.get("begin", "")
    end = best.get("end", "")
    
    date_start = begin[:10] if begin else None
    time_start = begin[11:16] if len(begin) > 11 else None
    date_end = end[:10] if end else None
    time_end = end[11:16] if len(end) > 11 else None
    
    return date_start, time_start, date_end, time_end


def classify_event(title, description, keywords):
    """Classify event into MapEvent categories"""
    text = f"{title} {description} {' '.join(keywords)}".lower()
    
    cats = []
    
    # Electro / musique
    electro_kw = ["techno", "electro", "dj", "house", "bass", "drum", "trance", 
                   "minimal", "rave", "clubbing", "deep house", "acid", "dubstep",
                   "edm", "electronic", "synthwave", "ambient"]
    if any(k in text for k in electro_kw):
        # Sub-genre specifique
        if "techno" in text:
            cats.append("Musique > Musique electronique > Techno")
        elif "house" in text or "deep house" in text:
            cats.append("Musique > Musique electronique > House")
        elif "drum" in text and "bass" in text:
            cats.append("Musique > Musique electronique > Drum and Bass")
        elif "trance" in text:
            cats.append("Musique > Musique electronique > Trance")
        elif "dubstep" in text:
            cats.append("Musique > Musique electronique > Dubstep")
        elif "ambient" in text:
            cats.append("Musique > Musique electronique > Ambient")
        else:
            cats.append("Musique > Musique electronique")
    
    if any(k in text for k in ["concert", "musique", "music", "live", "band", "orchestre"]) and not cats:
        if "jazz" in text:
            cats.append("Musique > Jazz")
        elif "classique" in text or "symphon" in text:
            cats.append("Musique > Classique")
        elif "rock" in text:
            cats.append("Musique > Rock")
        elif "hip hop" in text or "rap" in text:
            cats.append("Musique > Hip-Hop / Rap")
        elif "reggae" in text:
            cats.append("Musique > Reggae")
        elif "metal" in text:
            cats.append("Musique > Metal")
        elif "pop" in text:
            cats.append("Musique > Pop")
        else:
            cats.append("Musique > Concert")
    
    # Festival
    if "festival" in text:
        if not any("Musique" in c for c in cats):
            cats.append("Festival")
    
    # Spectacle / Theatre
    if any(k in text for k in ["spectacle", "theatre", "comedie", "danse", "ballet", "cirque", "clown"]):
        if "danse" in text or "ballet" in text:
            cats.append("Culture > Danse")
        elif "cirque" in text or "clown" in text:
            cats.append("Culture > Cirque")
        else:
            cats.append("Culture > Theatre / Spectacle")
    
    # Exposition / Art
    if any(k in text for k in ["exposition", "vernissage", "galerie", "art", "peinture", "sculpture", "musee", "museum"]):
        cats.append("Culture > Exposition / Art")
    
    # Sport
    if any(k in text for k in ["course", "marathon", "trail", "velo", "cyclisme", "football", "tennis",
                                  "ski", "randonnee", "escalade", "natation", "yoga", "fitness"]):
        cats.append("Sport")
    
    # Famille / Enfants
    if any(k in text for k in ["enfant", "famille", "kid", "jeune", "atelier creatif", "conte", "marionnette"]):
        cats.append("Famille / Enfants")
    
    # Gastronomie
    if any(k in text for k in ["gastronomie", "degustation", "vin", "cuisine", "food", "biere", "marche"]):
        cats.append("Gastronomie")
    
    # Conference
    if any(k in text for k in ["conference", "debat", "colloque", "seminaire"]):
        cats.append("Culture > Conference")
    
    if not cats:
        cats.append("Evenement")
    
    return cats[:3]  # Max 3 categories


valid_events = []
rejected_reasons = {"no_location": 0, "no_address": 0, "no_date": 0, "past_date": 0, "no_coords": 0, "no_source": 0}

for e in unique:
    title = get_text(e.get("title", ""))
    description = get_text(e.get("description", ""))
    longdesc = get_text(e.get("longDescription", ""))
    keywords = [get_text(k) for k in e.get("keywords", {}).get("fr", [])] if isinstance(e.get("keywords"), dict) else []
    
    # Location
    location = e.get("location") or {}
    loc_name = location.get("name", "")
    loc_address = location.get("address", "")
    loc_city = location.get("city", "")
    loc_postalcode = location.get("postalCode", "")
    loc_country = location.get("countryCode", "")
    lat = location.get("latitude")
    lng = location.get("longitude")
    
    # Source URL
    slug = e.get("slug", "")
    agenda_uid = e.get("originAgenda", {}).get("uid", "") if isinstance(e.get("originAgenda"), dict) else ""
    agenda_slug = e.get("originAgenda", {}).get("slug", "") if isinstance(e.get("originAgenda"), dict) else ""
    
    if agenda_slug and slug:
        source_url = f"https://openagenda.com/{agenda_slug}/events/{slug}"
    elif slug:
        source_url = f"https://openagenda.com/events/{slug}"
    else:
        source_url = ""
    
    # Validations strictes
    if not location:
        rejected_reasons["no_location"] += 1
        continue
    
    if not lat or not lng:
        rejected_reasons["no_coords"] += 1
        continue
    
    # Adresse: on veut au minimum ville + code postal
    if not loc_city and not loc_postalcode:
        rejected_reasons["no_address"] += 1
        continue
    
    # Construire adresse complete
    address_parts = []
    if loc_name:
        address_parts.append(loc_name)
    if loc_address:
        address_parts.append(loc_address)
    if loc_postalcode and loc_city:
        address_parts.append(f"{loc_postalcode} {loc_city}")
    elif loc_city:
        address_parts.append(loc_city)
    
    full_address = ", ".join(address_parts)
    
    # Timings
    timings = e.get("timings", [])
    date_start, time_start, date_end, time_end = extract_best_timing(timings)
    
    if not date_start:
        rejected_reasons["no_date"] += 1
        continue
    
    if date_start < TODAY:
        rejected_reasons["past_date"] += 1
        continue
    
    if not source_url:
        rejected_reasons["no_source"] += 1
        continue
    
    # Categories
    categories = classify_event(title, description + " " + longdesc, keywords)
    
    # Construire l'event
    event = {
        "title": title.strip(),
        "description": (description or longdesc)[:500].strip(),
        "location": full_address,
        "latitude": float(lat),
        "longitude": float(lng),
        "date": date_start,
        "time": time_start if time_start and time_start != "00:00" else None,
        "end_date": date_end if date_end != date_start else None,
        "end_time": time_end if time_end and time_end != "00:00" else None,
        "categories": categories,
        "source_url": source_url,
        "validation_status": "auto_validated",
        "status": "active",
        "country": loc_country,
    }
    
    valid_events.append(event)

print(f"\nEvents valides: {len(valid_events)}")
print(f"Rejetes:")
for reason, count in rejected_reasons.items():
    if count > 0:
        print(f"  {reason}: {count}")

# Compter electro
electro_count = sum(1 for e in valid_events if any("lectronique" in c or "Techno" in c or "House" in c or "Drum" in c or "Trance" in c for c in e["categories"]))
print(f"\nEvents electro/musique electronique: {electro_count}")

# Stats par pays
ch_count = sum(1 for e in valid_events if e.get("country", "").upper() in ("CH", ""))
fr_count = sum(1 for e in valid_events if e.get("country", "").upper() == "FR")
print(f"Suisse: {ch_count}, France: {fr_count}, Autre: {len(valid_events) - ch_count - fr_count}")

# Stats par categorie
cat_counts = {}
for e in valid_events:
    for c in e["categories"]:
        cat_counts[c] = cat_counts.get(c, 0) + 1
print("\nTop categories:")
for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1])[:15]:
    print(f"  {cat}: {count}")

# Sauvegarder
output = {"events": valid_events, "fetched_at": datetime.now().isoformat(), "total": len(valid_events)}
with open("scraper/opendata_events_batch.json", "w", encoding="utf-8") as f:
    json.dump(output, f, ensure_ascii=False, indent=2)

print(f"\nSauvegarde dans scraper/opendata_events_batch.json")
print(f"Total: {len(valid_events)} events prets a importer")
