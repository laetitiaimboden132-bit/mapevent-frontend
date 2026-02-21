"""
Import events electro depuis Goabase API (gratuit, pas de cle).
Focus: Suisse (80 events) + France (3) + frontaliers.
"""
import requests, json, time, sys, re
from datetime import date
sys.stdout.reconfigure(line_buffering=True)

TODAY = date.today().isoformat()
HEADERS = {"User-Agent": "MapEventAI-Bot/1.0 (contact: mapevent777@gmail.com)"}
API_BACKEND = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"
BASE = "https://www.goabase.net/api/party"

# Dedup
print("Chargement events existants...")
r = requests.get(f"{API_BACKEND}/api/events", timeout=60)
existing = r.json()
existing_titles = set()
for e in existing:
    existing_titles.add(re.sub(r'\s+', ' ', (e.get("title") or "").lower().strip()))
print(f"Events existants: {len(existing)}")


def classify_goabase(name, lineup, eventtype, keywords=""):
    """Classifie un event Goabase en categories MapEvent"""
    text = f"{name} {lineup} {keywords}".lower()
    cats = []
    
    if "techno" in text and "minimal" in text: cats.append("Musique > Musique electronique > Minimal Techno")
    elif "hard techno" in text: cats.append("Musique > Musique electronique > Techno")
    elif "techno" in text: cats.append("Musique > Musique electronique > Techno")
    elif "deep house" in text: cats.append("Musique > Musique electronique > Deep House")
    elif "tech house" in text: cats.append("Musique > Musique electronique > Tech House")
    elif "house" in text: cats.append("Musique > Musique electronique > House")
    elif "psytrance" in text or "goa" in text or "psy" in text: cats.append("Musique > Musique electronique > Psytrance")
    elif "trance" in text: cats.append("Musique > Musique electronique > Trance")
    elif "drum" in text and "bass" in text or "dnb" in text: cats.append("Musique > Musique electronique > Drum and Bass")
    elif "dubstep" in text: cats.append("Musique > Musique electronique > Dubstep")
    elif "hardstyle" in text: cats.append("Musique > Musique electronique > Hardstyle")
    elif "ambient" in text: cats.append("Musique > Musique electronique > Ambient")
    elif "disco" in text: cats.append("Musique > Musique electronique > Disco")
    else: cats.append("Musique > Musique electronique")
    
    etype = (eventtype or "").lower()
    if "festival" in etype or "festival" in text.lower():
        cats.append("Festival")
    
    return cats[:3]


# ==========================================================================
# FETCH: Suisse + France + geoloc
# ==========================================================================
all_parties = []

# Suisse (80 events)
print("\n--- Goabase Suisse ---")
r = requests.get(f"{BASE}/json/?country=CH&limit=500", headers=HEADERS, timeout=30)
if r.status_code == 200:
    ch_parties = r.json().get("partylist", [])
    print(f"Suisse: {len(ch_parties)} events")
    all_parties.extend(ch_parties)
time.sleep(1)

# France (3 events)
print("--- Goabase France ---")
r = requests.get(f"{BASE}/json/?country=FR&limit=500", headers=HEADERS, timeout=30)
if r.status_code == 200:
    fr_parties = r.json().get("partylist", [])
    print(f"France: {len(fr_parties)} events")
    all_parties.extend(fr_parties)
time.sleep(1)

# Aussi events frontaliers (Geneve n'a rien retourne, essayons autrement)
for city in ["Basel", "Lausanne", "Bern", "Lyon", "Strasbourg", "Marseille", "Bordeaux"]:
    r = requests.get(f"{BASE}/json/?geoloc={city}&radius=150&limit=100", headers=HEADERS, timeout=20)
    if r.status_code == 200:
        parties = r.json().get("partylist", [])
        if parties:
            print(f"  {city} (150km): {len(parties)} events")
            all_parties.extend(parties)
    time.sleep(1)

# Dedup par ID Goabase
seen_ids = set()
unique_parties = []
for p in all_parties:
    pid = p.get("id")
    if pid and pid not in seen_ids:
        seen_ids.add(pid)
        unique_parties.append(p)

print(f"\nTotal unique: {len(unique_parties)}")


# ==========================================================================
# NORMALISATION + VALIDATION
# ==========================================================================
print("\n--- Normalisation ---")
to_import = []

for p in unique_parties:
    pid = p.get("id", "?")
    name = (p.get("nameParty") or "").strip()
    if not name:
        continue
    
    # Nettoyage du titre (enlever emojis excessifs)
    name = re.sub(r'[^\w\s\-:&/().,!\'"+@#]', '', name).strip()
    name = re.sub(r'\s+', ' ', name)
    if not name or len(name) < 3:
        continue
    
    title_key = re.sub(r'\s+', ' ', name.lower())
    if title_key in existing_titles:
        continue
    
    # Coords
    lat = p.get("geoLat")
    lng = p.get("geoLon")
    if not lat or not lng:
        continue
    try:
        lat = float(lat)
        lng = float(lng)
    except:
        continue
    
    # Filtrer: Suisse + France uniquement
    country = p.get("nameCountry", "")
    iso = p.get("isoCountry", "")
    if iso not in ("CH", "FR"):
        # Verifier par coords
        if not (41.0 <= lat <= 52.0 and -6.0 <= lng <= 11.0):
            continue
    
    # Date
    date_start_raw = p.get("dateStart", "")
    date_end_raw = p.get("dateEnd", "")
    date_start = str(date_start_raw)[:10]
    date_end = str(date_end_raw)[:10] if date_end_raw else None
    
    if not date_start or date_start < TODAY:
        continue
    
    # Heure
    time_start = str(date_start_raw)[11:16] if len(str(date_start_raw)) > 11 else None
    time_end = str(date_end_raw)[11:16] if date_end_raw and len(str(date_end_raw)) > 11 else None
    
    # Location
    town = p.get("nameTown", "")
    loc_parts = [town, country] if town else [country]
    location = ", ".join([x for x in loc_parts if x])
    if not location:
        continue
    
    # Description (lineup)
    lineup = p.get("urlOrganizer", "")  # Parfois le lineup est dans un autre champ
    organizer = p.get("nameOrganizer", "")
    event_type = p.get("nameType", "")
    
    desc_parts = []
    if event_type:
        desc_parts.append(f"Type: {event_type}")
    if organizer:
        desc_parts.append(f"Organisateur: {organizer}")
    desc = ". ".join(desc_parts) if desc_parts else f"Soiree {event_type.lower()} a {town}."
    
    # Source URL
    source_url = f"https://www.goabase.net/party/{pid}"
    
    # Keywords from the JSON-LD endpoint
    keywords = p.get("keywords", "")
    
    # Categories
    categories = classify_goabase(name, lineup, event_type, keywords)
    
    event = {
        "title": name,
        "description": desc[:500],
        "location": location,
        "latitude": lat,
        "longitude": lng,
        "date": date_start,
        "time": time_start if time_start and time_start != "00:00" else None,
        "end_date": date_end if date_end and date_end != date_start else None,
        "end_time": time_end if time_end and time_end != "00:00" else None,
        "categories": categories,
        "source_url": source_url,
        "validation_status": "auto_validated",
    }
    
    to_import.append(event)
    existing_titles.add(title_key)

print(f"Events a importer: {len(to_import)}")

# Stats
ch_import = sum(1 for e in to_import if 45.8 <= e["latitude"] <= 47.9 and 5.9 <= e["longitude"] <= 10.6)
fr_import = len(to_import) - ch_import
print(f"  Suisse: {ch_import}, France/frontalier: {fr_import}")

# Categories
cat_counts = {}
for e in to_import:
    for c in e["categories"]:
        sub = c.split(">")[-1].strip()
        cat_counts[sub] = cat_counts.get(sub, 0) + 1
print("  Sous-genres:")
for sub, cnt in sorted(cat_counts.items(), key=lambda x: -x[1]):
    print(f"    {sub}: {cnt}")

# Echantillon
print("\n  Echantillon:")
for e in to_import[:15]:
    cats_short = e["categories"][0].split(">")[-1].strip()
    print(f"    [{cats_short}] {e['title'][:55]} | {e['date']} | {e['location'][:35]}")


# ==========================================================================
# ENRICHIR avec details (JSON-LD pour keywords/lineup)
# ==========================================================================
print("\n--- Enrichissement via JSON-LD (genres) ---")
enriched = 0
for e in to_import[:50]:  # Limiter pour respecter le rate limit
    pid = e["source_url"].split("/")[-1]
    try:
        r = requests.get(f"{BASE}/jsonld/{pid}", headers=HEADERS, timeout=10)
        if r.status_code == 200:
            detail = r.json()
            # Keywords = genres
            kw = detail.get("keywords", "")
            performers = detail.get("performer", detail.get("performers", ""))
            
            if kw:
                # Re-classifier avec les keywords
                new_cats = classify_goabase(e["title"], str(performers), "", kw)
                if new_cats:
                    e["categories"] = new_cats
            
            if performers and isinstance(performers, str) and len(performers) > 5:
                e["description"] = f"Line-up: {performers[:300]}. " + e["description"]
                e["description"] = e["description"][:500]
            
            enriched += 1
        time.sleep(0.5)
    except:
        pass

print(f"  Enrichis: {enriched}/{min(len(to_import), 50)}")


# ==========================================================================
# IMPORT
# ==========================================================================
if to_import:
    print(f"\n--- Import de {len(to_import)} events electro Goabase ---")
    imported = 0
    failed = 0
    
    for i in range(0, len(to_import), 10):
        batch = to_import[i:i+10]
        try:
            r = requests.post(f"{API_BACKEND}/api/events/scraped/batch",
                            json={"events": batch}, timeout=60)
            if r.status_code == 200:
                resp = r.json()
                imported += resp.get("results", {}).get("created", 0)
            else:
                failed += len(batch)
                print(f"  Erreur batch {i}: {r.status_code} {r.text[:100]}")
        except Exception as ex:
            failed += len(batch)
            print(f"  Exception batch {i}: {ex}")
        
        if i % 30 == 0:
            print(f"  [{i}/{len(to_import)}] imported={imported} failed={failed}")
        time.sleep(1)
    
    print(f"\n  IMPORT: {imported} importes, {failed} echoues")

print("\nDONE!")
