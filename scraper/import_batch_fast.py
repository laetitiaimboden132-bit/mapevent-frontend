"""Import rapide par batch de 10 via /api/events/scraped/batch"""
import requests
import json
import time
import sys
import re
from datetime import date

sys.stdout.reconfigure(line_buffering=True)

TODAY = date.today().isoformat()
API = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"

# Charger events
with open("scraper/opendata_events_batch.json", "r", encoding="utf-8") as f:
    raw_events = json.load(f)

print(f"Events charges: {len(raw_events)}")

# Charger existants pour dedup
print("Chargement events existants...")
r = requests.get(f"{API}/api/events", timeout=60)
existing = r.json()
print(f"Events existants: {len(existing)}")

existing_titles = set()
existing_urls = set()
for e in existing:
    t = re.sub(r'\s+', ' ', (e.get("title") or "").lower().strip())
    existing_titles.add(t)
    url = (e.get("source_url") or "").strip()
    if url:
        existing_urls.add(url)


def classify_strict(title, description):
    text_lower = f"{title} {description}".lower()
    cats = []
    
    strict_electro = ["techno", "house music", "drum and bass", "drum'n'bass", "dnb",
                       "trance", "psytrance", "dubstep", "hardstyle",
                       "acid house", "deep house", "minimal techno",
                       "progressive house", "tech house"]
    electro_context = ["dj set", "dj mix", "clubbing", "afterparty",
                        "rave party", "rave ", "b2b dj", "soundsystem"]
    electro_phrases = ["musique electro", "soiree electro", "nuit electro",
                        "festival electro", "electro party", "electro club",
                        "musique electronique"]
    
    is_electro = False
    subgenre = None
    
    for kw in strict_electro:
        if kw in text_lower:
            is_electro = True
            if "minimal" in kw: subgenre = "Minimal Techno"
            elif "tech house" == kw: subgenre = "Tech House"
            elif "deep house" == kw: subgenre = "Deep House"
            elif "techno" in kw: subgenre = "Techno"
            elif "house" in kw: subgenre = "House"
            elif "drum" in kw or "dnb" == kw: subgenre = "Drum and Bass"
            elif "trance" in kw: subgenre = "Trance"
            elif "dubstep" in kw: subgenre = "Dubstep"
            elif "acid" in kw: subgenre = "Acid House"
            break
    
    if not is_electro:
        for kw in electro_context + electro_phrases:
            if kw in text_lower:
                is_electro = True
                break
    
    if is_electro:
        cats.append(f"Musique > Musique electronique > {subgenre}" if subgenre else "Musique > Musique electronique")
    
    music_kw = ["concert", "live ", "recital", "orchestre", "en concert", "showcase"]
    if any(k in text_lower for k in music_kw) and not is_electro:
        if "jazz" in text_lower: cats.append("Musique > Jazz")
        elif re.search(r'classique|symphoni|philharmon', text_lower): cats.append("Musique > Classique")
        elif re.search(r'\brock\b', text_lower): cats.append("Musique > Rock")
        elif re.search(r'hip.?hop|rap\b', text_lower): cats.append("Musique > Hip-Hop / Rap")
        elif "reggae" in text_lower: cats.append("Musique > Reggae")
        elif "blues" in text_lower: cats.append("Musique > Blues")
        elif re.search(r'\bpop\b|chanson', text_lower): cats.append("Musique > Pop")
        elif "metal" in text_lower: cats.append("Musique > Metal")
        elif re.search(r'opera|lyrique', text_lower): cats.append("Musique > Opera")
        else: cats.append("Musique > Concert")
    
    if re.search(r'\bfestival\b', text_lower) and not cats: cats.append("Festival")
    if re.search(r'spectacle|theatre|théâtre|comédie', text_lower):
        if re.search(r'humour|stand.?up|humoriste', text_lower): cats.append("Culture > Humour / Stand-up")
        else: cats.append("Culture > Theatre / Spectacle")
    if re.search(r'exposition|vernissage|galerie|musée|musee', text_lower): cats.append("Culture > Exposition / Art")
    if re.search(r'danse|ballet|choregraph', text_lower): cats.append("Culture > Danse")
    if re.search(r'enfant|famille|jeune public|conte|marionnette', text_lower): cats.append("Famille / Enfants")
    if re.search(r'course|marathon|trail|sport|fitness|yoga|running', text_lower): cats.append("Sport")
    if re.search(r'gastronomie|degustation|cuisine|food|vin\b', text_lower): cats.append("Gastronomie")
    if re.search(r'conference|conférence|débat|debat|colloque', text_lower): cats.append("Culture > Conference")
    if re.search(r'cinema|cinéma|film|projection', text_lower): cats.append("Culture > Cinema")
    if re.search(r'brocante|vide.?grenier|puces', text_lower): cats.append("Marche / Brocante")
    if re.search(r'atelier|workshop|masterclass', text_lower) and not any("Famille" in c for c in cats): cats.append("Atelier / Workshop")
    if re.search(r'carnaval|carnival|cortège', text_lower): cats.append("Fete / Carnaval")
    if re.search(r'cirque|acrobat', text_lower): cats.append("Culture > Cirque")
    
    if not cats: cats.append("Evenement")
    return cats[:3]


# Filtrer et nettoyer
to_import = []
for e in raw_events:
    title = e.get("title", "").strip()
    if not title: continue
    
    title_key = re.sub(r'\s+', ' ', title.lower())
    if title_key in existing_titles: continue
    
    source_url = (e.get("source_url") or "").strip()
    if source_url and source_url in existing_urls: continue
    
    event_date = e.get("date", "")
    if not event_date or event_date < TODAY: continue
    
    desc = e.get("description", "")
    categories = classify_strict(title, desc)
    
    to_import.append({
        "title": title,
        "description": (desc or "")[:500],
        "location": e.get("location", ""),
        "latitude": float(e.get("latitude", 0)),
        "longitude": float(e.get("longitude", 0)),
        "date": event_date,
        "time": e.get("time"),
        "end_date": e.get("end_date"),
        "end_time": e.get("end_time"),
        "categories": categories,
        "source_url": source_url,
        "validation_status": "auto_validated",
    })
    
    existing_titles.add(title_key)
    if source_url: existing_urls.add(source_url)

print(f"Events a importer (apres dedup): {len(to_import)}")

# Supprimer les 2 tests
print("\nSuppression des 2 events de test...")
r = requests.post(f"{API}/api/admin/delete-events", json={"ids": [8991, 8992]}, timeout=15)
print(f"  {r.status_code}: {r.text[:100]}")

# Import par batch de 10
BATCH_SIZE = 10
imported = 0
failed = 0
errors = []

print(f"\nImport par batch de {BATCH_SIZE}...")
for i in range(0, len(to_import), BATCH_SIZE):
    batch = to_import[i:i+BATCH_SIZE]
    
    try:
        r = requests.post(f"{API}/api/events/scraped/batch", 
                         json={"events": batch}, 
                         timeout=60)
        
        if r.status_code == 200:
            resp = r.json()
            created = resp.get("results", {}).get("created", 0)
            imported += created
            errs = resp.get("results", {}).get("errors", [])
            if errs:
                for err in errs[:2]:
                    errors.append(str(err)[:100])
        else:
            failed += len(batch)
            if len(errors) < 5:
                errors.append(f"Batch {i}: status {r.status_code} - {r.text[:100]}")
    except Exception as e:
        failed += len(batch)
        if len(errors) < 5:
            errors.append(f"Batch {i}: {str(e)[:100]}")
    
    if i % 50 == 0:
        print(f"  [{i}/{len(to_import)}] imported={imported}, failed={failed}")
    
    time.sleep(1)

print(f"\n{'=' * 70}")
print(f"IMPORT TERMINE")
print(f"  Importes: {imported}")
print(f"  Echoues: {failed}")
if errors:
    print(f"  Erreurs:")
    for err in errors[:5]:
        print(f"    {err}")

# Stats electro
electro_count = sum(1 for e in to_import if any("lectronique" in c or "Techno" in c or "House" in c for c in e["categories"]))
print(f"\n  Dont electro: {electro_count}")
print("DONE!")
