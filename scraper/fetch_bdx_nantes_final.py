"""
Fetch + import Bordeaux + Nantes avec les bons champs.
Bordeaux: title_fr, location_address, location_coordinates, firstdate_begin/lastdate_begin
Nantes: nom, adresse, latitude/longitude, date, heure_debut/heure_fin
"""
import requests, json, time, sys, re
from datetime import date

sys.stdout.reconfigure(line_buffering=True)
TODAY = date.today().isoformat()
HEADERS = {"User-Agent": "MapEventAI-Bot/1.0"}
API = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"

# Dedup
print("Chargement events existants...")
r = requests.get(f"{API}/api/events", timeout=60)
existing = r.json()
existing_titles = set()
for e in existing:
    existing_titles.add(re.sub(r'\s+', ' ', (e.get("title") or "").lower().strip()))
print(f"Events existants: {len(existing)}")


def classify_strict(title, description):
    text_lower = f"{title} {description}".lower()
    cats = []
    strict_electro = ["techno", "house music", "drum and bass", "dnb", "trance", "psytrance",
                       "dubstep", "hardstyle", "deep house", "minimal techno", "tech house", "acid house"]
    electro_context = ["dj set", "dj mix", "clubbing", "rave ", "soundsystem", "dancefloor"]
    electro_phrases = ["musique electro", "soiree electro", "nuit electro", "musique electronique"]
    
    is_electro = subgenre = None
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
    
    if any(k in text_lower for k in ["concert", "live ", "recital", "orchestre", "en concert"]) and not is_electro:
        if "jazz" in text_lower: cats.append("Musique > Jazz")
        elif re.search(r'classique|symphoni', text_lower): cats.append("Musique > Classique")
        elif re.search(r'\brock\b', text_lower): cats.append("Musique > Rock")
        elif re.search(r'hip.?hop|rap\b', text_lower): cats.append("Musique > Hip-Hop / Rap")
        elif "blues" in text_lower: cats.append("Musique > Blues")
        elif re.search(r'opera|lyrique', text_lower): cats.append("Musique > Opera")
        else: cats.append("Musique > Concert")
    
    if re.search(r'\bfestival\b', text_lower) and not cats: cats.append("Festival")
    if re.search(r'spectacle|theatre|théâtre|comédie', text_lower):
        if re.search(r'humour|stand.?up|humoriste', text_lower): cats.append("Culture > Humour / Stand-up")
        else: cats.append("Culture > Theatre / Spectacle")
    if re.search(r'exposition|vernissage|galerie|musée|musee', text_lower): cats.append("Culture > Exposition / Art")
    if re.search(r'danse|ballet', text_lower): cats.append("Culture > Danse")
    if re.search(r'enfant|famille|jeune public|conte', text_lower): cats.append("Famille / Enfants")
    if re.search(r'course|marathon|trail|sport|yoga|running', text_lower): cats.append("Sport")
    if re.search(r'gastronomie|degustation|cuisine|food|vin\b', text_lower): cats.append("Gastronomie")
    if re.search(r'conference|conférence|débat', text_lower): cats.append("Culture > Conference")
    if re.search(r'cinema|cinéma|film|projection', text_lower): cats.append("Culture > Cinema")
    if re.search(r'brocante|vide.?grenier', text_lower): cats.append("Marche / Brocante")
    if re.search(r'atelier|workshop', text_lower) and not any("Famille" in c for c in cats): cats.append("Atelier / Workshop")
    if re.search(r'carnaval|carnival', text_lower): cats.append("Fete / Carnaval")
    if re.search(r'cirque|acrobat', text_lower): cats.append("Culture > Cirque")
    
    if not cats: cats.append("Evenement")
    return cats[:3]


all_events = []

# ==========================================================================
# BORDEAUX - met_agenda
# ==========================================================================
print("\n" + "=" * 70)
print("BORDEAUX")
print("=" * 70)

bdx_count = 0
for offset in range(0, 600, 100):
    try:
        url = "https://opendata.bordeaux-metropole.fr/api/explore/v2.1/catalog/datasets/met_agenda/records"
        params = {
            "limit": 100, "offset": offset,
            "where": f"lastdate_begin >= '{TODAY}'",
            "order_by": "firstdate_begin",
        }
        r = requests.get(url, params=params, headers=HEADERS, timeout=30)
        if r.status_code != 200:
            print(f"  Erreur {r.status_code}: {r.text[:200]}")
            break
        
        data = r.json()
        records = data.get("results", [])
        total = data.get("total_count", 0)
        if offset == 0:
            print(f"  Total futur: {total}")
        if not records:
            break
        
        for rec in records:
            title = (rec.get("title_fr") or "").strip()
            if not title: continue
            
            title_key = re.sub(r'\s+', ' ', title.lower())
            if title_key in existing_titles: continue
            
            desc = (rec.get("description_fr") or "")
            longdesc = (rec.get("longdescription_fr") or "")
            desc_clean = re.sub(r'<[^>]+>', ' ', desc + " " + longdesc)
            desc_clean = re.sub(r'\s+', ' ', desc_clean).strip()[:500]
            
            coords = rec.get("location_coordinates") or {}
            lat = coords.get("lat")
            lng = coords.get("lon")
            if not lat or not lng: continue
            
            loc_name = rec.get("location_name", "") or ""
            loc_addr = rec.get("location_address", "") or ""
            loc_zip = rec.get("location_postalcode", "") or ""
            loc_city = rec.get("location_city", "") or ""
            
            parts = [p for p in [loc_name, loc_addr, f"{loc_zip} {loc_city}".strip()] if p.strip()]
            location = ", ".join(parts)
            if len(location) < 5: continue
            
            # Dates
            first_begin = (rec.get("firstdate_begin") or "")[:10]
            last_begin = (rec.get("lastdate_begin") or "")[:10]
            first_time = (rec.get("firstdate_begin") or "")[11:16] if len(rec.get("firstdate_begin") or "") > 11 else None
            
            date_start = first_begin if first_begin >= TODAY else last_begin
            if not date_start or date_start < TODAY: continue
            date_end = last_begin if last_begin != date_start else None
            
            # Source URL (OpenAgenda)
            slug = rec.get("slug", "")
            agenda_uid = rec.get("originagenda_uid", "")
            agenda_title = rec.get("originagenda_title", "")
            # Construire URL OpenAgenda
            source_url = f"https://openagenda.com/agendas/{agenda_uid}/events/{slug}" if agenda_uid and slug else ""
            
            categories = classify_strict(title, desc_clean)
            
            all_events.append({
                "title": title, "description": desc_clean, "location": location,
                "latitude": float(lat), "longitude": float(lng),
                "date": date_start, "time": first_time if first_time and first_time != "00:00" else None,
                "end_date": date_end, "end_time": None,
                "categories": categories, "source_url": source_url,
                "validation_status": "auto_validated",
            })
            existing_titles.add(title_key)
            bdx_count += 1
        
        print(f"  Offset {offset}: {bdx_count} total Bordeaux")
        time.sleep(1.5)
    except Exception as e:
        print(f"  Erreur: {e}")
        break

print(f"Bordeaux: {bdx_count} events")


# ==========================================================================
# NANTES v2
# ==========================================================================
print("\n" + "=" * 70)
print("NANTES")
print("=" * 70)

nts_count = 0
for offset in range(0, 500, 100):
    try:
        url = "https://data.nantesmetropole.fr/api/explore/v2.1/catalog/datasets/244400404_agenda-evenements-nantes-metropole_v2/records"
        params = {
            "limit": 100, "offset": offset,
            "where": f"date >= '{TODAY}'",
            "order_by": "date",
        }
        r = requests.get(url, params=params, headers=HEADERS, timeout=30)
        if r.status_code != 200:
            print(f"  Erreur {r.status_code}: {r.text[:200]}")
            break
        
        data = r.json()
        records = data.get("results", [])
        total = data.get("total_count", 0)
        if offset == 0:
            print(f"  Total futur: {total}")
        if not records:
            break
        
        for rec in records:
            title = (rec.get("nom") or "").strip()
            if not title: continue
            
            title_key = re.sub(r'\s+', ' ', title.lower())
            if title_key in existing_titles: continue
            
            desc = (rec.get("description_evt") or rec.get("description") or "")
            desc = re.sub(r'<[^>]+>', ' ', desc)
            desc = re.sub(r'\s+', ' ', desc).strip()[:500]
            
            lat = rec.get("latitude")
            lng = rec.get("longitude")
            if not lat or not lng: continue
            
            lieu = rec.get("lieu", "") or ""
            adresse = rec.get("adresse", "") or ""
            cp = rec.get("code_postal", "") or ""
            ville = rec.get("ville", "") or "Nantes"
            
            parts = [p for p in [lieu, adresse, f"{cp} {ville}".strip()] if p.strip()]
            location = ", ".join(parts)
            if len(location) < 5: continue
            
            date_start = (rec.get("date") or "")[:10]
            if not date_start or date_start < TODAY: continue
            
            time_start = rec.get("heure_debut")
            time_end = rec.get("heure_fin")
            
            # Source URL
            lien = rec.get("lien_agenda") or rec.get("url_site") or ""
            
            categories = classify_strict(title, desc)
            
            # Themes Nantes
            themes = rec.get("themes_libelles", []) or []
            types = rec.get("types_libelles", []) or []
            
            all_events.append({
                "title": title, "description": desc, "location": location,
                "latitude": float(lat), "longitude": float(lng),
                "date": date_start, "time": time_start if time_start else None,
                "end_date": None, "end_time": time_end if time_end else None,
                "categories": categories, "source_url": lien,
                "validation_status": "auto_validated",
            })
            existing_titles.add(title_key)
            nts_count += 1
        
        print(f"  Offset {offset}: {nts_count} total Nantes")
        time.sleep(1.5)
    except Exception as e:
        print(f"  Erreur: {e}")
        break

print(f"Nantes: {nts_count} events")


# ==========================================================================
# RESULTATS + IMPORT
# ==========================================================================
print("\n" + "=" * 70)
print("RESULTATS")
print("=" * 70)

print(f"Total a importer: {len(all_events)}")

cat_counts = {}
electro_list = []
for e in all_events:
    for c in e["categories"]:
        cat_counts[c] = cat_counts.get(c, 0) + 1
    if any("lectronique" in c or "Techno" in c or "House" in c for c in e["categories"]):
        electro_list.append(e)

print(f"Events electro: {len(electro_list)}")
print("Categories:")
for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1])[:15]:
    print(f"  {cat}: {count}")

if electro_list:
    print("\nElectro:")
    for e in electro_list[:10]:
        print(f"  {e['title'][:60]} | {e['date']} | {e['location'][:50]}")

# IMPORT
if len(all_events) > 0:
    print(f"\nIMPORT DE {len(all_events)} EVENTS...")
    imported = 0
    failed = 0
    
    for i in range(0, len(all_events), 10):
        batch = all_events[i:i+10]
        try:
            r = requests.post(f"{API}/api/events/scraped/batch",
                            json={"events": batch}, timeout=60)
            if r.status_code == 200:
                resp = r.json()
                imported += resp.get("results", {}).get("created", 0)
            else:
                failed += len(batch)
        except:
            failed += len(batch)
        
        if i % 100 == 0:
            print(f"  [{i}/{len(all_events)}] imported={imported} failed={failed}")
        time.sleep(1)
    
    print(f"\nIMPORT TERMINE: {imported} importes, {failed} echoues")

print("DONE!")
