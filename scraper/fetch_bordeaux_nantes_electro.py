"""
Fetch Bordeaux (met_agenda - 34613 events) + Nantes (v2) + Toulouse.
Focus: electro + events variés.
"""
import requests
import json
import time
import sys
import re
from datetime import date

sys.stdout.reconfigure(line_buffering=True)

TODAY = date.today().isoformat()
HEADERS = {"User-Agent": "MapEventAI-Bot/1.0 (contact: mapevent777@gmail.com)"}
API = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"

# Charger titres existants
print("Chargement events existants...")
r = requests.get(f"{API}/api/events", timeout=60)
existing = r.json()
existing_titles = set()
for e in existing:
    t = re.sub(r'\s+', ' ', (e.get("title") or "").lower().strip())
    existing_titles.add(t)
print(f"Events existants: {len(existing)}")

all_events = []


def classify_strict(title, description):
    text_lower = f"{title} {description}".lower()
    cats = []
    
    strict_electro = ["techno", "house music", "drum and bass", "drum'n'bass", "dnb",
                       "trance", "psytrance", "dubstep", "hardstyle",
                       "acid house", "deep house", "minimal techno",
                       "progressive house", "tech house"]
    electro_context = ["dj set", "dj mix", "clubbing", "afterparty",
                        "rave party", "rave ", "b2b dj", "soundsystem", "dancefloor"]
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


# ==========================================================================
# BORDEAUX - met_agenda (34613 events - on prend les 500 prochains)
# ==========================================================================
print("\n" + "=" * 70)
print("BORDEAUX (met_agenda)")
print("=" * 70)

bdx_count = 0
for offset in range(0, 500, 100):
    try:
        url = "https://opendata.bordeaux-metropole.fr/api/explore/v2.1/catalog/datasets/met_agenda/records"
        params = {
            "limit": 100,
            "offset": offset,
            "order_by": "date_debut",
            "where": f"date_debut >= '{TODAY}'",
        }
        r = requests.get(url, params=params, headers=HEADERS, timeout=30)
        if r.status_code != 200:
            print(f"  Erreur {r.status_code} a offset {offset}")
            # Essayer sans filtre date
            if offset == 0:
                params.pop("where", None)
                r = requests.get(url, params=params, headers=HEADERS, timeout=30)
                if r.status_code != 200:
                    print(f"  Toujours erreur {r.status_code}")
                    break
        
        data = r.json()
        records = data.get("results", [])
        total = data.get("total_count", 0)
        if offset == 0:
            print(f"  Total disponible: {total}")
        
        if not records:
            break
        
        for rec in records:
            title = (rec.get("nom", rec.get("titre", rec.get("title", ""))) or "").strip()
            if not title: continue
            
            title_key = re.sub(r'\s+', ' ', title.lower())
            if title_key in existing_titles: continue
            
            desc = (rec.get("description", rec.get("descriptif", "")) or "")
            desc = re.sub(r'<[^>]+>', ' ', desc)
            desc = re.sub(r'\s+', ' ', desc).strip()[:500]
            
            lieu = rec.get("lieu", rec.get("nom_lieu", "")) or ""
            adresse = rec.get("adresse", rec.get("adresse_lieu", "")) or ""
            commune = rec.get("commune", "") or "Bordeaux"
            cp = rec.get("code_postal", "") or ""
            
            geo = rec.get("geo_point_2d") or rec.get("point_geo") or {}
            lat = lng = None
            if isinstance(geo, dict):
                lat = geo.get("lat") or geo.get("latitude")
                lng = geo.get("lon") or geo.get("lng") or geo.get("longitude")
            if not lat or not lng: continue
            
            try:
                lat = float(lat)
                lng = float(lng)
            except: continue
            
            # Verifier zone Bordeaux
            if not (44.7 <= lat <= 45.0 and -0.8 <= lng <= -0.3):
                continue
            
            parts = [p for p in [lieu, adresse, f"{cp} {commune}".strip()] if p.strip()]
            location = ", ".join(parts) if parts else "Bordeaux"
            if len(location) < 5: continue
            
            date_start = (rec.get("date_debut", rec.get("date", "")) or "")[:10]
            date_end = (rec.get("date_fin", "") or "")[:10]
            if not date_start: continue
            if date_start < TODAY: continue
            
            source_url = rec.get("url", rec.get("lien", "")) or ""
            
            categories = classify_strict(title, desc)
            
            all_events.append({
                "title": title,
                "description": desc,
                "location": location,
                "latitude": lat,
                "longitude": lng,
                "date": date_start,
                "time": None,
                "end_date": date_end if date_end and date_end != date_start else None,
                "end_time": None,
                "categories": categories,
                "source_url": source_url,
                "validation_status": "auto_validated",
            })
            existing_titles.add(title_key)
            bdx_count += 1
        
        print(f"  Offset {offset}: +{bdx_count} events Bordeaux")
        time.sleep(1.5)
    except Exception as e:
        print(f"  Erreur: {e}")
        break

print(f"\nBordeaux total: {bdx_count} events")


# ==========================================================================
# NANTES v2
# ==========================================================================
print("\n" + "=" * 70)
print("NANTES (agenda-evenements v2)")
print("=" * 70)

nantes_count = 0
for offset in range(0, 300, 100):
    try:
        url = "https://data.nantesmetropole.fr/api/explore/v2.1/catalog/datasets/244400404_agenda-evenements-nantes-metropole_v2/records"
        params = {"limit": 100, "offset": offset}
        r = requests.get(url, params=params, headers=HEADERS, timeout=30)
        if r.status_code != 200:
            print(f"  Erreur {r.status_code}: {r.text[:200]}")
            break
        
        data = r.json()
        records = data.get("results", [])
        total = data.get("total_count", 0)
        if offset == 0:
            print(f"  Total disponible: {total}")
        
        if not records:
            break
        
        for rec in records:
            title = (rec.get("nom", rec.get("titre", rec.get("title", ""))) or "").strip()
            if not title: continue
            
            title_key = re.sub(r'\s+', ' ', title.lower())
            if title_key in existing_titles: continue
            
            desc = (rec.get("description", rec.get("resume", "")) or "")
            desc = re.sub(r'<[^>]+>', ' ', desc)
            desc = re.sub(r'\s+', ' ', desc).strip()[:500]
            
            lieu = rec.get("nom_lieu", rec.get("lieu", "")) or ""
            adresse = rec.get("adresse", "") or ""
            commune = rec.get("commune", "") or "Nantes"
            cp = rec.get("code_postal", "") or ""
            
            geo = rec.get("location") or rec.get("geo_point_2d") or {}
            lat = lng = None
            if isinstance(geo, dict):
                lat = geo.get("lat")
                lng = geo.get("lon") or geo.get("lng")
            if not lat or not lng: continue
            
            try:
                lat = float(lat)
                lng = float(lng)
            except: continue
            
            if not (47.0 <= lat <= 47.5 and -1.8 <= lng <= -1.3):
                continue
            
            parts = [p for p in [lieu, adresse, f"{cp} {commune}".strip()] if p.strip()]
            location = ", ".join(parts) if parts else "Nantes"
            if len(location) < 5: continue
            
            date_start = (rec.get("date", rec.get("date_debut", "")) or "")[:10]
            date_end = (rec.get("date_fin", "") or "")[:10]
            if not date_start or date_start < TODAY: continue
            
            source_url = rec.get("url", rec.get("lien", "")) or ""
            
            categories = classify_strict(title, desc)
            
            all_events.append({
                "title": title,
                "description": desc,
                "location": location,
                "latitude": lat,
                "longitude": lng,
                "date": date_start,
                "time": None,
                "end_date": date_end if date_end and date_end != date_start else None,
                "end_time": None,
                "categories": categories,
                "source_url": source_url,
                "validation_status": "auto_validated",
            })
            existing_titles.add(title_key)
            nantes_count += 1
        
        print(f"  Offset {offset}: +{nantes_count} events Nantes")
        time.sleep(1.5)
    except Exception as e:
        print(f"  Erreur: {e}")
        break

print(f"\nNantes total: {nantes_count} events")


# ==========================================================================
# TOULOUSE - recherche du bon dataset
# ==========================================================================
print("\n" + "=" * 70)
print("TOULOUSE (recherche dataset)")
print("=" * 70)

try:
    url = "https://data.toulouse-metropole.fr/api/explore/v2.1/catalog/datasets?q=agenda+evenement+manifestation&limit=10"
    r = requests.get(url, headers=HEADERS, timeout=15)
    if r.status_code == 200:
        data = r.json()
        for ds in data.get("results", []):
            ds_id = ds.get("dataset_id", "?")
            title_meta = ""
            if isinstance(ds.get("metas"), dict):
                title_meta = ds["metas"].get("default", {}).get("title", "?")
            print(f"  Toulouse dataset: {ds_id} - {title_meta}")
except Exception as e:
    print(f"  Toulouse: {e}")


# ==========================================================================
# RESULTATS FINAUX
# ==========================================================================
print("\n" + "=" * 70)
print("RESULTATS FINAUX")
print("=" * 70)

print(f"Total events a importer: {len(all_events)}")

# Stats categories
cat_counts = {}
electro_events = []
for e in all_events:
    for c in e["categories"]:
        cat_counts[c] = cat_counts.get(c, 0) + 1
    if any("lectronique" in c or "Techno" in c or "House" in c or "Trance" in c for c in e["categories"]):
        electro_events.append(e)

print(f"Events electro: {len(electro_events)}")
print(f"\nCategories:")
for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1])[:15]:
    print(f"  {cat}: {count}")

if electro_events:
    print(f"\nEvents electro:")
    for e in electro_events[:10]:
        print(f"  {e['title'][:60]} | {e['date']} | {e['location'][:50]}")

# Sauvegarder
with open("scraper/extra_events_batch.json", "w", encoding="utf-8") as f:
    json.dump(all_events, f, ensure_ascii=False, indent=2)

print(f"\nSauvegarde: scraper/extra_events_batch.json ({len(all_events)} events)")


# ==========================================================================
# IMPORT
# ==========================================================================
if len(all_events) > 0:
    print("\n" + "=" * 70)
    print(f"IMPORT DE {len(all_events)} EVENTS")
    print("=" * 70)
    
    BATCH_SIZE = 10
    imported = 0
    failed = 0
    
    for i in range(0, len(all_events), BATCH_SIZE):
        batch = all_events[i:i+BATCH_SIZE]
        
        try:
            r = requests.post(f"{API}/api/events/scraped/batch",
                            json={"events": batch},
                            timeout=60)
            
            if r.status_code == 200:
                resp = r.json()
                created = resp.get("results", {}).get("created", 0)
                imported += created
            else:
                failed += len(batch)
        except Exception as e:
            failed += len(batch)
        
        if i % 50 == 0:
            print(f"  [{i}/{len(all_events)}] imported={imported}, failed={failed}")
        
        time.sleep(1)
    
    print(f"\nIMPORT TERMINE: {imported} importes, {failed} echoues")
else:
    print("\nAucun event a importer.")

print("DONE!")
