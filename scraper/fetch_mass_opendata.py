"""
Fetch massif depuis les APIs open data qui marchent.
Paris (2278 events), + recherche correcte OpenAgenda, + autres villes.
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
all_valid = []
seen_titles = set()

def classify_event(title, description):
    text = f"{title} {description}".lower()
    cats = []
    
    electro_kw = ["techno", "electro", "dj", "house music", "bass music", "drum and bass", "trance",
                   "minimal techno", "rave", "clubbing", "deep house", "acid house", "dubstep",
                   "edm", "electronic", "synthwave", "ambient electronic", "disco", "hardstyle",
                   "hardcore techno", "psytrance", "progressive house"]
    if any(k in text for k in electro_kw):
        if "techno" in text and "minimal" in text: cats.append("Musique > Musique electronique > Minimal Techno")
        elif "techno" in text: cats.append("Musique > Musique electronique > Techno")
        elif "deep house" in text: cats.append("Musique > Musique electronique > Deep House")
        elif "house" in text: cats.append("Musique > Musique electronique > House")
        elif "drum" in text and "bass" in text: cats.append("Musique > Musique electronique > Drum and Bass")
        elif "trance" in text: cats.append("Musique > Musique electronique > Trance")
        elif "disco" in text: cats.append("Musique > Musique electronique > Disco")
        elif "dubstep" in text: cats.append("Musique > Musique electronique > Dubstep")
        elif "ambient" in text: cats.append("Musique > Musique electronique > Ambient")
        else: cats.append("Musique > Musique electronique")
    
    if any(k in text for k in ["concert", "live music", "orchestre", "recital"]) and not any("Musique" in c for c in cats):
        if "jazz" in text: cats.append("Musique > Jazz")
        elif "classique" in text or "symphoni" in text or "philharmon" in text: cats.append("Musique > Classique")
        elif "rock" in text: cats.append("Musique > Rock")
        elif "hip hop" in text or "rap " in text or "hip-hop" in text: cats.append("Musique > Hip-Hop / Rap")
        elif "reggae" in text: cats.append("Musique > Reggae")
        elif "blues" in text: cats.append("Musique > Blues")
        elif "pop " in text or "chanson" in text: cats.append("Musique > Pop")
        elif "metal" in text: cats.append("Musique > Metal")
        elif "world" in text or "musique du monde" in text: cats.append("Musique > World")
        else: cats.append("Musique > Concert")
    
    if "festival" in text and not cats: cats.append("Festival")
    if any(k in text for k in ["spectacle", "theatre", "comedie", "one man", "one woman", "humour", "stand-up", "humoriste"]):
        if "humour" in text or "stand-up" in text or "humoriste" in text: cats.append("Culture > Humour / Stand-up")
        else: cats.append("Culture > Theatre / Spectacle")
    if any(k in text for k in ["exposition", "vernissage", "galerie", "art contemporain", "musee", "photo", "sculpture", "peinture"]):
        cats.append("Culture > Exposition / Art")
    if any(k in text for k in ["danse", "ballet", "hip hop dance", "contemporaine"]): cats.append("Culture > Danse")
    if any(k in text for k in ["enfant", "famille", "kid", "jeune public", "atelier creatif", "conte", "marionnette"]):
        cats.append("Famille / Enfants")
    if any(k in text for k in ["course", "marathon", "trail", "sport", "fitness", "yoga", "running", "velo", "cyclisme"]):
        cats.append("Sport")
    if any(k in text for k in ["gastronomie", "degustation", "cuisine", "food", "vin", "biere", "brunch"]):
        cats.append("Gastronomie")
    if any(k in text for k in ["conference", "debat", "rencontre", "table ronde"]): cats.append("Culture > Conference")
    if any(k in text for k in ["cinema", "film", "projection", "seance"]): cats.append("Culture > Cinema")
    if any(k in text for k in ["marche", "brocante", "vide-grenier", "puces"]): cats.append("Marche / Brocante")
    if any(k in text for k in ["atelier", "workshop", "stage", "masterclass"]) and not any("Famille" in c for c in cats):
        cats.append("Atelier / Workshop")
    if any(k in text for k in ["carnaval", "fete", "carnival", "cortege"]): cats.append("Fete / Carnaval")
    if any(k in text for k in ["opera", "lyrique"]): cats.append("Musique > Opera")
    
    if not cats: cats.append("Evenement")
    return cats[:3]


# ==========================================================================
# PARIS - Fetch complet (2278 events)
# ==========================================================================
print("=" * 70)
print("PARIS - OpenData Paris (que-faire-a-paris)")
print("=" * 70)

paris_events = []
total_paris = 0

for offset in range(0, 2300, 100):
    url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/que-faire-a-paris-/records"
    params = {
        "where": f"date_start >= '{TODAY}'",
        "order_by": "date_start",
        "limit": 100,
        "offset": offset,
    }
    try:
        r = requests.get(url, params=params, headers=HEADERS, timeout=30)
        if r.status_code != 200:
            print(f"  Erreur {r.status_code} a offset {offset}")
            break
        data = r.json()
        records = data.get("results", [])
        if offset == 0:
            total_paris = data.get("total_count", 0)
            print(f"Total disponible: {total_paris}")
        
        if not records:
            break
        
        paris_events.extend(records)
        print(f"  Offset {offset}: +{len(records)} (total: {len(paris_events)})")
        
        if len(paris_events) >= total_paris:
            break
        
        time.sleep(1.5)
    except Exception as e:
        print(f"  Erreur: {e}")
        break

print(f"\nParis brut: {len(paris_events)} events")

# Normaliser Paris
for e in paris_events:
    title = (e.get("title") or "").strip()
    if not title:
        continue
    
    title_key = re.sub(r'\s+', ' ', title.lower())
    if title_key in seen_titles:
        continue
    seen_titles.add(title_key)
    
    desc = (e.get("description") or e.get("lead_text") or "")
    # Nettoyer HTML
    desc = re.sub(r'<[^>]+>', ' ', desc)
    desc = re.sub(r'\s+', ' ', desc).strip()[:500]
    
    addr_name = e.get("address_name", "") or ""
    addr_street = e.get("address_street", "") or ""
    addr_zip = e.get("address_zipcode", "") or ""
    addr_city = e.get("address_city", "") or "Paris"
    
    parts = [p for p in [addr_name, addr_street, f"{addr_zip} {addr_city}".strip()] if p.strip()]
    location = ", ".join(parts)
    
    if not location or len(location) < 5:
        continue
    
    # Coords
    geo = e.get("lat_lon") or {}
    lat = lng = None
    if isinstance(geo, dict):
        lat = geo.get("lat")
        lng = geo.get("lon") or geo.get("lng")
    
    if not lat or not lng:
        continue
    
    try:
        lat = float(lat)
        lng = float(lng)
    except:
        continue
    
    if not (48.7 <= lat <= 49.0 and 2.1 <= lng <= 2.6):
        continue
    
    date_start = (e.get("date_start") or "")[:10]
    date_end = (e.get("date_end") or "")[:10]
    
    if not date_start or date_start < TODAY:
        continue
    
    source_url = e.get("url") or ""
    
    categories = classify_event(title, desc)
    
    all_valid.append({
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
        "status": "active",
    })

print(f"Paris valides: {len(all_valid)}")


# ==========================================================================
# OPENAGENDA - Trouver les bons slugs via recherche
# ==========================================================================
print("\n" + "=" * 70)
print("OPENAGENDA - Recherche des agendas par ville")
print("=" * 70)

# Essayons les URLs directes connues d'OpenAgenda
OA_SLUGS_TO_TRY = [
    # Format: https://openagenda.com/SLUG/events.json
    "agenda-culturel-de-geneve",
    "ville-de-geneve",
    "geneve-agenda",
    "sortir-a-geneve",
    "agenda-geneve",
    "fribourg-tourisme",
    "lausanne-tourisme",
    "montreux-riviera",
    "bern-events",
    "zurich-events",
    # France - grandes villes
    "agenda-culturel-de-lyon",
    "sortir-a-lyon",
    "lyon-events",
    "que-faire-a-lyon",
    "agenda-nantes-metropole",
    "nantes-tourisme",
    "sortir-a-nantes",
    "bordeaux-tourisme",
    "sortir-a-bordeaux",
    "toulouse-tourisme",
    "sortir-a-toulouse",
    "strasbourg-tourisme",
    "sortir-a-strasbourg",
    "marseille-tourisme",
    "sortir-a-marseille",
    "agenda-de-marseille",
    "lille-tourisme",
    "sortir-a-lille",
    "nice-tourisme",
    "montpellier-tourisme",
    "rennes-tourisme",
]

working_agendas = []
for slug in OA_SLUGS_TO_TRY:
    try:
        url = f"https://openagenda.com/{slug}/events.json?limit=1&oaq[from]={TODAY}"
        r = requests.get(url, headers=HEADERS, timeout=10, allow_redirects=True)
        if r.status_code == 200:
            data = r.json()
            total = data.get("total", 0)
            if total > 0:
                print(f"  FOUND: {slug} -> {total} events!")
                working_agendas.append((slug, total))
        time.sleep(0.5)
    except:
        pass

print(f"\nAgendas trouves: {len(working_agendas)}")

# Fetch les events des agendas trouves
for slug, total in working_agendas:
    print(f"\nFetch {slug} ({total} events)...")
    before = len(all_valid)
    
    for offset in range(0, min(total, 300), 100):
        url = f"https://openagenda.com/{slug}/events.json?limit=100&offset={offset}&oaq[from]={TODAY}&oaq[to]=2026-12-31"
        try:
            r = requests.get(url, headers=HEADERS, timeout=20)
            if r.status_code != 200:
                break
            data = r.json()
            events = data.get("events", [])
            
            for e in events:
                title = ""
                title_field = e.get("title", "")
                if isinstance(title_field, dict):
                    title = title_field.get("fr") or title_field.get("en") or next(iter(title_field.values()), "")
                elif isinstance(title_field, str):
                    title = title_field
                title = title.strip()
                
                if not title:
                    continue
                
                title_key = re.sub(r'\s+', ' ', title.lower())
                if title_key in seen_titles:
                    continue
                seen_titles.add(title_key)
                
                desc = ""
                desc_field = e.get("description", e.get("longDescription", ""))
                if isinstance(desc_field, dict):
                    desc = desc_field.get("fr") or desc_field.get("en") or next(iter(desc_field.values()), "")
                elif isinstance(desc_field, str):
                    desc = desc_field
                desc = re.sub(r'<[^>]+>', ' ', desc)
                desc = re.sub(r'\s+', ' ', desc).strip()[:500]
                
                loc = e.get("location") or {}
                loc_name = loc.get("name", "")
                loc_addr = loc.get("address", "")
                loc_city = loc.get("city", "")
                loc_zip = loc.get("postalCode", "")
                lat = loc.get("latitude")
                lng = loc.get("longitude")
                
                if not lat or not lng:
                    continue
                
                try:
                    lat = float(lat)
                    lng = float(lng)
                except:
                    continue
                
                if not (41.0 <= lat <= 52.0 and -6.0 <= lng <= 11.0):
                    continue
                
                parts = []
                if loc_name: parts.append(loc_name)
                if loc_addr: parts.append(loc_addr)
                if loc_zip and loc_city: parts.append(f"{loc_zip} {loc_city}")
                elif loc_city: parts.append(loc_city)
                location = ", ".join(parts)
                
                if not location or len(location) < 5:
                    continue
                
                # Timing
                timings = e.get("timings", [])
                date_start = None
                time_start = None
                date_end = None
                time_end = None
                
                for t in timings:
                    begin = t.get("begin", "")
                    if begin and begin[:10] >= TODAY:
                        date_start = begin[:10]
                        time_start = begin[11:16] if len(begin) > 11 else None
                        end = t.get("end", "")
                        date_end = end[:10] if end else None
                        time_end = end[11:16] if len(end) > 11 else None
                        break
                
                if not date_start:
                    continue
                
                # Source URL
                e_slug = e.get("slug", "")
                source_url = f"https://openagenda.com/{slug}/events/{e_slug}" if e_slug else ""
                
                categories = classify_event(title, desc)
                
                all_valid.append({
                    "title": title,
                    "description": desc,
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
                    "status": "active",
                })
            
            if len(events) < 100:
                break
            time.sleep(1.5)
        except Exception as ex:
            print(f"  Erreur: {ex}")
            break
    
    added = len(all_valid) - before
    print(f"  +{added} events valides de {slug}")
    time.sleep(2)


# ==========================================================================
# Recherche specifique electro via API publique data.culture.gouv.fr
# ==========================================================================
print("\n" + "=" * 70)
print("DATASOURCES SUPPLEMENTAIRES POUR ELECTRO")
print("=" * 70)

# API datatourisme.fr - events en France
print("\nFetch: DATAtourisme (datatourisme.fr) - evenements musicaux...")
try:
    # DATAtourisme SPARQL endpoint
    sparql_url = "https://diffuseur.datatourisme.fr/webservice/search"
    params = {
        "query": "techno electro dj house festival musique electronique",
        "type": "Event",
        "size": 100,
        "from": 0,
    }
    r = requests.get(sparql_url, params=params, headers=HEADERS, timeout=30)
    if r.status_code == 200:
        data = r.json()
        results = data.get("results", [])
        print(f"  DATAtourisme: {len(results)} resultats")
    else:
        print(f"  DATAtourisme: {r.status_code}")
except Exception as e:
    print(f"  DATAtourisme: {e}")


# ==========================================================================
# RESULTATS FINAUX
# ==========================================================================
print("\n" + "=" * 70)
print("RESULTATS FINAUX")
print("=" * 70)

print(f"\nTotal events valides: {len(all_valid)}")

# Stats electro
electro = [e for e in all_valid if any("lectronique" in c or "Techno" in c or "House" in c or "Drum" in c or "Trance" in c or "Disco" in c or "Dubstep" in c for c in e["categories"])]
print(f"Events electro/musique electronique: {len(electro)}")

# Stats musique
musique = [e for e in all_valid if any("Musique" in c for c in e["categories"])]
print(f"Events musique total: {len(musique)}")

# Top categories
cat_counts = {}
for e in all_valid:
    for c in e["categories"]:
        cat_counts[c] = cat_counts.get(c, 0) + 1

print("\nTop 20 categories:")
for cat, count in sorted(cat_counts.items(), key=lambda x: -x[1])[:20]:
    print(f"  {cat}: {count}")

# Echantillon electro
print("\nEchantillon events electro:")
for e in electro[:10]:
    print(f"  - {e['title'][:60]} | {e['date']} | {e['location'][:50]}")

# Sauvegarder
with open("scraper/opendata_events_batch.json", "w", encoding="utf-8") as f:
    json.dump(all_valid, f, ensure_ascii=False, indent=2)

print(f"\nSauvegarde: scraper/opendata_events_batch.json ({len(all_valid)} events)")
print("Pret pour import!")
