"""
Fetcher events depuis des sources open data PUBLIQUES accessibles sans cle API.
Sources: data.gouv.fr, OpenAgenda agendas publics, RSS feeds, etc.
Focus: electro/musique + events generaux, Suisse + France.
"""
import requests
import json
import time
import sys
import re
from datetime import datetime, date

sys.stdout.reconfigure(line_buffering=True)

TODAY = date.today().isoformat()
HEADERS = {"User-Agent": "MapEventAI-Bot/1.0 (contact: mapevent777@gmail.com)"}

all_events = []

# ==========================================================================
# SOURCE 1: OpenAgenda - acces public via les pages JSON des agendas
# Chaque agenda public a un endpoint JSON accessible
# ==========================================================================
print("=" * 70)
print("SOURCE 1: OpenAgenda agendas publics (JSON)")
print("=" * 70)

# Agendas connus avec events electro/musique/culture
# Format: (slug, description)
AGENDAS_TO_CHECK = [
    # Electro / Clubs / Musique
    ("agenda-des-soirees-electro", "Soirees electro"),
    ("clubbing-france", "Clubbing France"),
    ("quai-des-arts-argenteuil", "Quai des Arts Argenteuil"),
    # Villes suisses
    ("ville-de-geneve-agenda-public", "Geneve agenda public"),
    ("geneve-tourisme", "Geneve tourisme"),
    # Villes francaises grandes
    ("nantes", "Nantes"),
    ("mairie-de-paris", "Paris"),
    ("ville-de-lyon", "Lyon"),
    ("ville-de-marseille", "Marseille"),
    ("metropole-de-lyon", "Metropole Lyon"),
    ("ville-de-bordeaux", "Bordeaux"),
    ("ville-de-toulouse", "Toulouse"),
    ("ville-de-strasbourg", "Strasbourg"),
    ("ville-de-lille", "Lille"),
    ("ville-de-montpellier", "Montpellier"),
    ("ville-de-nice", "Nice"),
    ("ville-de-rennes", "Rennes"),
    ("ville-de-nantes", "Nantes v2"),
]

def fetch_oa_agenda_json(slug):
    """Fetch events from an OpenAgenda public agenda page"""
    events = []
    for offset in [0, 100]:
        url = f"https://openagenda.com/{slug}/events.json?oaq[from]={TODAY}&oaq[to]=2026-12-31&offset={offset}&limit=100"
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            if r.status_code != 200:
                if offset == 0:
                    print(f"  [{slug}] Erreur {r.status_code}")
                break
            data = r.json()
            evts = data.get("events", [])
            total = data.get("total", 0)
            if offset == 0:
                print(f"  [{slug}] {total} events futurs")
            events.extend(evts)
            if len(events) >= total:
                break
            time.sleep(1)
        except Exception as e:
            if offset == 0:
                print(f"  [{slug}] Erreur: {e}")
            break
    return events

oa_events = []
for slug, desc in AGENDAS_TO_CHECK:
    print(f"\nFetch: {desc} ({slug})...")
    evts = fetch_oa_agenda_json(slug)
    oa_events.extend(evts)
    time.sleep(2)

print(f"\nTotal OpenAgenda brut: {len(oa_events)}")


# ==========================================================================
# SOURCE 2: data.gouv.fr - Datasets evenementiels
# ==========================================================================
print("\n" + "=" * 70)
print("SOURCE 2: data.gouv.fr - Datasets evenements")
print("=" * 70)

datagouv_events = []

# Dataset: "Que faire a Paris" (evenements Paris) - tres riche
print("\nFetch: Que faire a Paris (OpenData Paris)...")
try:
    url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/que-faire-a-paris-/records"
    params = {
        "where": f"date_start >= '{TODAY}'",
        "order_by": "date_start",
        "limit": 100,
        "offset": 0,
    }
    r = requests.get(url, params=params, headers=HEADERS, timeout=30)
    if r.status_code == 200:
        data = r.json()
        records = data.get("results", [])
        total = data.get("total_count", 0)
        print(f"  Paris: {total} events futurs, {len(records)} recuperes")
        datagouv_events.extend([{"source": "paris", **rec} for rec in records])
        
        # Page 2
        if total > 100:
            params["offset"] = 100
            r = requests.get(url, params=params, headers=HEADERS, timeout=30)
            if r.status_code == 200:
                data = r.json()
                records2 = data.get("results", [])
                print(f"  Paris page 2: {len(records2)} recuperes")
                datagouv_events.extend([{"source": "paris", **rec} for rec in records2])
    else:
        print(f"  Paris: Erreur {r.status_code}")
except Exception as e:
    print(f"  Paris: Erreur {e}")

time.sleep(2)

# Dataset: Nantes evenements
print("\nFetch: Nantes (OpenData)...")
try:
    url = "https://data.nantesmetropole.fr/api/explore/v2.1/catalog/datasets/244400404_agenda-evenements-nantes-nantes-metropole/records"
    params = {
        "where": f"date >= '{TODAY}'",
        "order_by": "date",
        "limit": 100,
    }
    r = requests.get(url, params=params, headers=HEADERS, timeout=30)
    if r.status_code == 200:
        data = r.json()
        records = data.get("results", [])
        total = data.get("total_count", 0)
        print(f"  Nantes: {total} events, {len(records)} recuperes")
        datagouv_events.extend([{"source": "nantes", **rec} for rec in records])
    else:
        print(f"  Nantes: Erreur {r.status_code}")
except Exception as e:
    print(f"  Nantes: Erreur {e}")

time.sleep(2)

# Dataset: Lyon evenements
print("\nFetch: Lyon (data.grandlyon.com)...")
try:
    url = "https://data.grandlyon.com/api/explore/v2.1/catalog/datasets/eve_agenda_entree/records"
    params = {
        "limit": 100,
        "order_by": "date_debut",
    }
    r = requests.get(url, params=params, headers=HEADERS, timeout=30)
    if r.status_code == 200:
        data = r.json()
        records = data.get("results", [])
        total = data.get("total_count", 0)
        print(f"  Lyon: {total} events, {len(records)} recuperes")
        datagouv_events.extend([{"source": "lyon", **rec} for rec in records])
    else:
        print(f"  Lyon: Erreur {r.status_code}: {r.text[:200]}")
except Exception as e:
    print(f"  Lyon: Erreur {e}")

time.sleep(2)

# Dataset: Bordeaux evenements
print("\nFetch: Bordeaux (OpenData)...")
try:
    url = "https://opendata.bordeaux-metropole.fr/api/explore/v2.1/catalog/datasets/bor_evtam/records"
    params = {
        "limit": 100,
        "order_by": "date_debut",
    }
    r = requests.get(url, params=params, headers=HEADERS, timeout=30)
    if r.status_code == 200:
        data = r.json()
        records = data.get("results", [])
        total = data.get("total_count", 0)
        print(f"  Bordeaux: {total} events, {len(records)} recuperes")
        datagouv_events.extend([{"source": "bordeaux", **rec} for rec in records])
    else:
        print(f"  Bordeaux: Erreur {r.status_code}: {r.text[:200]}")
except Exception as e:
    print(f"  Bordeaux: Erreur {e}")

time.sleep(2)

print(f"\nTotal data.gouv.fr brut: {len(datagouv_events)}")


# ==========================================================================
# SOURCE 3: Recherche specifique electro via le web
# ==========================================================================
print("\n" + "=" * 70)
print("SOURCE 3: Resident Advisor (evenements electro)")
print("=" * 70)

# RA a un site public mais pas d'API ouverte - on va chercher via d'autres sources
# Shotgun.live a des events electro publics

print("\nFetch: Shotgun.live events electro Suisse/France...")
shotgun_events = []
try:
    # Shotgun API publique pour events
    for city in ["geneva", "zurich", "paris", "lyon", "marseille", "bordeaux", "toulouse", "nantes", "lille"]:
        url = f"https://shotgun.live/api/v1/cities/{city}/events?page=1&per_page=50"
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, list):
                print(f"  Shotgun {city}: {len(data)} events")
                shotgun_events.extend([{"source": "shotgun", "city": city, **e} for e in data])
            elif isinstance(data, dict):
                evts = data.get("events", data.get("data", []))
                print(f"  Shotgun {city}: {len(evts)} events")
                shotgun_events.extend([{"source": "shotgun", "city": city, **e} for e in evts])
        else:
            print(f"  Shotgun {city}: {r.status_code}")
        time.sleep(1)
except Exception as e:
    print(f"  Shotgun erreur: {e}")

print(f"\nTotal Shotgun brut: {len(shotgun_events)}")


# ==========================================================================
# NORMALISATION ET VALIDATION
# ==========================================================================
print("\n" + "=" * 70)
print("NORMALISATION ET VALIDATION STRICTE")
print("=" * 70)

valid_events = []
rejected = {"no_title": 0, "no_location": 0, "no_date": 0, "past": 0, "no_coords": 0, "duplicate": 0}
seen_titles = set()


def normalize_oa_event(e):
    """Normalise un event OpenAgenda"""
    def get_text(field):
        if isinstance(field, str): return field
        if isinstance(field, dict): return field.get("fr") or field.get("en") or next(iter(field.values()), "")
        return ""
    
    title = get_text(e.get("title", ""))
    desc = get_text(e.get("description", "")) or get_text(e.get("longDescription", ""))
    
    loc = e.get("location") or {}
    loc_name = loc.get("name", "")
    loc_addr = loc.get("address", "")
    loc_city = loc.get("city", "")
    loc_zip = loc.get("postalCode", "")
    lat = loc.get("latitude")
    lng = loc.get("longitude")
    country = loc.get("countryCode", "").upper()
    
    # Construire adresse
    parts = []
    if loc_name: parts.append(loc_name)
    if loc_addr: parts.append(loc_addr)
    if loc_zip and loc_city: parts.append(f"{loc_zip} {loc_city}")
    elif loc_city: parts.append(loc_city)
    address = ", ".join(parts)
    
    # Timing
    timings = e.get("timings", [])
    date_start = time_start = date_end = time_end = None
    for t in timings:
        begin = t.get("begin", "")
        if begin[:10] >= TODAY:
            date_start = begin[:10]
            time_start = begin[11:16] if len(begin) > 11 else None
            end = t.get("end", "")
            date_end = end[:10] if end else None
            time_end = end[11:16] if len(end) > 11 else None
            break
    
    # Source URL
    slug = e.get("slug", "")
    agenda = e.get("originAgenda", {})
    if isinstance(agenda, dict):
        agenda_slug = agenda.get("slug", "")
    else:
        agenda_slug = ""
    
    source_url = f"https://openagenda.com/{agenda_slug}/events/{slug}" if agenda_slug and slug else ""
    
    return {
        "title": title, "description": desc[:500], "location": address,
        "latitude": lat, "longitude": lng, "date": date_start,
        "time": time_start if time_start != "00:00" else None,
        "end_date": date_end if date_end != date_start else None,
        "end_time": time_end if time_end != "00:00" else None,
        "source_url": source_url, "country": country,
    }


def normalize_paris_event(e):
    """Normalise un event Paris OpenData"""
    title = e.get("title", "")
    desc = e.get("description", "")
    if isinstance(desc, str) and len(desc) > 500:
        desc = desc[:500]
    
    addr = e.get("address_name", "") or ""
    street = e.get("address_street", "") or ""
    zipcode = e.get("address_zipcode", "") or ""
    city = e.get("address_city", "") or "Paris"
    
    parts = [p for p in [addr, street, f"{zipcode} {city}".strip()] if p]
    location = ", ".join(parts)
    
    geo = e.get("lat_lon") or e.get("geom") or {}
    if isinstance(geo, dict):
        lat = geo.get("lat")
        lng = geo.get("lon") or geo.get("lng")
    elif isinstance(geo, list) and len(geo) == 2:
        lat, lng = geo[0], geo[1]
    else:
        lat = e.get("latitude") or e.get("lat")
        lng = e.get("longitude") or e.get("lon") or e.get("lng")
    
    date_start = (e.get("date_start") or "")[:10]
    date_end = (e.get("date_end") or "")[:10]
    
    source_url = e.get("url") or e.get("link") or ""
    
    return {
        "title": title, "description": desc[:500] if desc else "", "location": location,
        "latitude": lat, "longitude": lng, "date": date_start,
        "time": None, "end_date": date_end if date_end != date_start else None, "end_time": None,
        "source_url": source_url, "country": "FR",
    }


def normalize_nantes_event(e):
    """Normalise un event Nantes OpenData"""
    title = e.get("nom", "") or e.get("title", "")
    desc = (e.get("description", "") or "")[:500]
    
    lieu = e.get("lieu", "") or e.get("nom_lieu", "") or ""
    adresse = e.get("adresse", "") or ""
    ville = e.get("commune", "") or "Nantes"
    cp = e.get("code_postal", "") or ""
    
    parts = [p for p in [lieu, adresse, f"{cp} {ville}".strip()] if p]
    location = ", ".join(parts)
    
    geo = e.get("location") or e.get("geom") or e.get("geo_shape") or {}
    lat = lng = None
    if isinstance(geo, dict):
        lat = geo.get("lat")
        lng = geo.get("lon") or geo.get("lng")
        if not lat and "geometry" in geo:
            coords = geo["geometry"].get("coordinates", [])
            if coords:
                lng, lat = coords[0], coords[1]
    
    if not lat:
        lat = e.get("latitude")
        lng = e.get("longitude")
    
    date_start = (e.get("date", "") or e.get("date_debut", ""))[:10]
    date_end = (e.get("date_fin", "") or "")[:10]
    
    source_url = e.get("url") or e.get("lien", "") or ""
    
    return {
        "title": title, "description": desc, "location": location,
        "latitude": lat, "longitude": lng, "date": date_start,
        "time": None, "end_date": date_end if date_end and date_end != date_start else None, "end_time": None,
        "source_url": source_url, "country": "FR",
    }


# Normaliser tous les events
print("\nNormalisation OpenAgenda events...")
for e in oa_events:
    norm = normalize_oa_event(e)
    if norm["title"]:
        all_events.append(norm)

print(f"  {len(all_events)} events OpenAgenda normalises")

print("\nNormalisation Paris events...")
paris_before = len(all_events)
for e in datagouv_events:
    if e.get("source") == "paris":
        norm = normalize_paris_event(e)
        if norm["title"]:
            all_events.append(norm)
print(f"  {len(all_events) - paris_before} events Paris normalises")

print("\nNormalisation Nantes events...")
nantes_before = len(all_events)
for e in datagouv_events:
    if e.get("source") == "nantes":
        norm = normalize_nantes_event(e)
        if norm["title"]:
            all_events.append(norm)
print(f"  {len(all_events) - nantes_before} events Nantes normalises")

# Lyon, Bordeaux si disponibles
for src in ["lyon", "bordeaux"]:
    count = sum(1 for e in datagouv_events if e.get("source") == src)
    if count > 0:
        print(f"  {src}: {count} events bruts (normalisation a implementer)")


# Validation stricte
print(f"\nValidation stricte sur {len(all_events)} events...")

def classify_event(title, description):
    """Classify into MapEvent categories"""
    text = f"{title} {description}".lower()
    cats = []
    
    electro_kw = ["techno", "electro", "dj", "house", "bass", "drum", "trance",
                   "minimal", "rave", "clubbing", "deep house", "acid", "dubstep",
                   "edm", "electronic", "synthwave", "ambient", "disco"]
    if any(k in text for k in electro_kw):
        if "techno" in text: cats.append("Musique > Musique electronique > Techno")
        elif "house" in text: cats.append("Musique > Musique electronique > House")
        elif "drum" in text and "bass" in text: cats.append("Musique > Musique electronique > Drum and Bass")
        elif "trance" in text: cats.append("Musique > Musique electronique > Trance")
        elif "disco" in text: cats.append("Musique > Musique electronique > Disco")
        else: cats.append("Musique > Musique electronique")
    
    if any(k in text for k in ["concert", "live", "orchestre"]) and not cats:
        if "jazz" in text: cats.append("Musique > Jazz")
        elif "classique" in text: cats.append("Musique > Classique")
        elif "rock" in text: cats.append("Musique > Rock")
        elif "hip" in text and "hop" in text: cats.append("Musique > Hip-Hop / Rap")
        elif "reggae" in text: cats.append("Musique > Reggae")
        else: cats.append("Musique > Concert")
    
    if "festival" in text and not cats: cats.append("Festival")
    if any(k in text for k in ["spectacle", "theatre", "comedie"]): cats.append("Culture > Theatre / Spectacle")
    if any(k in text for k in ["exposition", "vernissage", "art", "musee"]): cats.append("Culture > Exposition / Art")
    if any(k in text for k in ["danse", "ballet"]): cats.append("Culture > Danse")
    if any(k in text for k in ["enfant", "famille", "kid", "jeune"]): cats.append("Famille / Enfants")
    if any(k in text for k in ["course", "marathon", "trail", "sport"]): cats.append("Sport")
    if any(k in text for k in ["gastronomie", "degustation", "cuisine", "food"]): cats.append("Gastronomie")
    if any(k in text for k in ["conference", "debat"]): cats.append("Culture > Conference")
    if any(k in text for k in ["cinema", "film", "projection"]): cats.append("Culture > Cinema")
    if any(k in text for k in ["marche", "brocante", "vide-grenier"]): cats.append("Marche / Brocante")
    
    if not cats: cats.append("Evenement")
    return cats[:3]


for e in all_events:
    title = e.get("title", "").strip()
    
    if not title:
        rejected["no_title"] += 1
        continue
    
    # Dedup par titre normalise
    title_key = re.sub(r'\s+', ' ', title.lower().strip())
    if title_key in seen_titles:
        rejected["duplicate"] += 1
        continue
    seen_titles.add(title_key)
    
    if not e.get("location") or len(e["location"]) < 5:
        rejected["no_location"] += 1
        continue
    
    if not e.get("date") or len(e["date"]) < 10:
        rejected["no_date"] += 1
        continue
    
    if e["date"] < TODAY:
        rejected["past"] += 1
        continue
    
    if not e.get("latitude") or not e.get("longitude"):
        rejected["no_coords"] += 1
        continue
    
    try:
        lat = float(e["latitude"])
        lng = float(e["longitude"])
    except:
        rejected["no_coords"] += 1
        continue
    
    # Verifier coords dans zone Suisse/France
    if not (41.0 <= lat <= 52.0 and -6.0 <= lng <= 11.0):
        rejected["no_coords"] += 1
        continue
    
    categories = classify_event(title, e.get("description", ""))
    
    valid_events.append({
        "title": title,
        "description": e.get("description", "")[:500],
        "location": e["location"],
        "latitude": lat,
        "longitude": lng,
        "date": e["date"],
        "time": e.get("time"),
        "end_date": e.get("end_date"),
        "end_time": e.get("end_time"),
        "categories": categories,
        "source_url": e.get("source_url", ""),
        "validation_status": "auto_validated",
        "status": "active",
    })


print(f"\nEvents valides: {len(valid_events)}")
print(f"Rejetes: {json.dumps(rejected, indent=2)}")

# Stats
electro_count = sum(1 for e in valid_events if any("lectronique" in c or "Techno" in c or "House" in c for c in e["categories"]))
print(f"\nEvents electro: {electro_count}")

cat_counts = {}
for e in valid_events:
    for c in e["categories"]:
        top = c.split(" > ")[0]
        cat_counts[top] = cat_counts.get(top, 0) + 1
print("\nCategories:")
for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1]):
    print(f"  {cat}: {count}")

# Sauvegarder
with open("scraper/opendata_events_batch.json", "w", encoding="utf-8") as f:
    json.dump(valid_events, f, ensure_ascii=False, indent=2)

print(f"\nSauvegarde: scraper/opendata_events_batch.json ({len(valid_events)} events)")
