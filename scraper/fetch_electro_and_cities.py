"""
Recherche specifique d'events electro + autres villes francaises.
Sources: 
- OpenData Toulouse, Montpellier, Strasbourg, Lyon, Bordeaux, Nantes
- Recherche specifique electro dans Paris avec filtre tags
- MySwitzerland developer API
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

all_events = []

# ==========================================================================
# Charger titres existants pour dedup
# ==========================================================================
print("Chargement events existants pour dedup...")
r = requests.get(f"{API}/api/events", timeout=60)
existing = r.json()
existing_titles = set()
for e in existing:
    t = re.sub(r'\s+', ' ', (e.get("title") or "").lower().strip())
    existing_titles.add(t)
print(f"Events existants: {len(existing)}, titres uniques: {len(existing_titles)}")


# ==========================================================================
# 1. PARIS - Events electro specifiques (filtre par tags/categories)
# ==========================================================================
print("\n" + "=" * 70)
print("PARIS - Events ELECTRO (filtre tags)")
print("=" * 70)

# Paris OpenData a des tags - chercher les events avec tags electro/musique
for tag in ["Musique", "Concert", "Clubbing", "DJ", "Festival"]:
    print(f"\nParis tag '{tag}'...")
    try:
        url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/que-faire-a-paris-/records"
        params = {
            "where": f"date_start >= '{TODAY}' AND tags LIKE '%{tag}%'",
            "order_by": "date_start",
            "limit": 100,
        }
        r = requests.get(url, params=params, headers=HEADERS, timeout=30)
        if r.status_code == 200:
            data = r.json()
            records = data.get("results", [])
            total = data.get("total_count", 0)
            print(f"  {total} events avec tag '{tag}', {len(records)} recuperes")
            for rec in records:
                title = (rec.get("title") or "").strip()
                desc = (rec.get("description") or rec.get("lead_text") or "")
                desc = re.sub(r'<[^>]+>', ' ', desc)
                desc = re.sub(r'\s+', ' ', desc).strip()[:500]
                tags = (rec.get("tags") or "")
                
                # Check si c'est electro
                combined = f"{title} {desc} {tags}".lower()
                is_electro = any(k in combined for k in ["techno", "house music", "electro", "dj set", 
                    "clubbing", "deep house", "minimal", "trance", "dubstep", "rave",
                    "drum and bass", "acid", "disco"])
                
                if not is_electro:
                    continue
                
                geo = rec.get("lat_lon") or {}
                lat = geo.get("lat") if isinstance(geo, dict) else None
                lng = (geo.get("lon") or geo.get("lng")) if isinstance(geo, dict) else None
                if not lat or not lng: continue
                
                addr_name = rec.get("address_name", "") or ""
                addr_street = rec.get("address_street", "") or ""
                addr_zip = rec.get("address_zipcode", "") or ""
                addr_city = rec.get("address_city", "") or "Paris"
                parts = [p for p in [addr_name, addr_street, f"{addr_zip} {addr_city}".strip()] if p.strip()]
                location = ", ".join(parts)
                
                date_start = (rec.get("date_start") or "")[:10]
                if date_start < TODAY: continue
                
                all_events.append({
                    "title": title, "description": desc, "location": location,
                    "latitude": float(lat), "longitude": float(lng),
                    "date": date_start,
                    "end_date": (rec.get("date_end") or "")[:10] or None,
                    "source_url": rec.get("url") or "",
                    "is_electro": True,
                })
        time.sleep(1)
    except Exception as e:
        print(f"  Erreur: {e}")

print(f"\nEvents electro Paris trouves: {len(all_events)}")


# ==========================================================================
# 2. AUTRES VILLES - Open Data
# ==========================================================================
print("\n" + "=" * 70)
print("AUTRES VILLES FRANCAISES")
print("=" * 70)

# Toulouse
print("\nToulouse (data.toulouse-metropole.fr)...")
try:
    url = "https://data.toulouse-metropole.fr/api/explore/v2.1/catalog/datasets/agenda-des-manifestations-702702/records"
    params = {"limit": 100, "order_by": "date_debut"}
    r = requests.get(url, params=params, headers=HEADERS, timeout=30)
    if r.status_code == 200:
        data = r.json()
        records = data.get("results", [])
        total = data.get("total_count", 0)
        print(f"  Toulouse: {total} events, {len(records)} recuperes")
        for rec in records:
            title = rec.get("nom", rec.get("title", "")).strip()
            if not title: continue
            desc = (rec.get("descriptif", rec.get("description", "")) or "")[:500]
            lieu = rec.get("lieu", "") or ""
            adresse = rec.get("adresse", "") or ""
            cp = rec.get("code_postal", "") or "31000"
            commune = rec.get("commune", "") or "Toulouse"
            
            geo = rec.get("geo_point_2d") or rec.get("geometry") or {}
            lat = lng = None
            if isinstance(geo, dict):
                lat = geo.get("lat") or geo.get("latitude")
                lng = geo.get("lon") or geo.get("lng") or geo.get("longitude")
            if not lat or not lng: continue
            
            parts = [p for p in [lieu, adresse, f"{cp} {commune}".strip()] if p.strip()]
            location = ", ".join(parts) if parts else f"Toulouse"
            
            date_start = (rec.get("date_debut", "") or "")[:10]
            date_end = (rec.get("date_fin", "") or "")[:10]
            if not date_start or date_start < TODAY: continue
            
            source_url = rec.get("url", rec.get("lien", "")) or ""
            
            all_events.append({
                "title": title, "description": desc, "location": location,
                "latitude": float(lat), "longitude": float(lng),
                "date": date_start, "end_date": date_end if date_end != date_start else None,
                "source_url": source_url,
            })
    else:
        print(f"  Toulouse: {r.status_code}: {r.text[:200]}")
except Exception as e:
    print(f"  Toulouse: {e}")

time.sleep(2)

# Montpellier
print("\nMontpellier (data.montpellier3m.fr)...")
try:
    url = "https://data.montpellier3m.fr/api/explore/v2.1/catalog/datasets/evenements-de-montpellier-mediterranee-metropole/records"
    params = {"limit": 100}
    r = requests.get(url, params=params, headers=HEADERS, timeout=30)
    if r.status_code == 200:
        data = r.json()
        records = data.get("results", [])
        total = data.get("total_count", 0)
        print(f"  Montpellier: {total} events, {len(records)} recuperes")
        for rec in records:
            title = (rec.get("titre", rec.get("nom", "")) or "").strip()
            if not title: continue
            desc = (rec.get("description", "") or "")[:500]
            lieu = rec.get("lieu", "") or ""
            adresse = rec.get("adresse", "") or ""
            
            geo = rec.get("geo_point_2d") or rec.get("geometry") or {}
            lat = lng = None
            if isinstance(geo, dict):
                lat = geo.get("lat")
                lng = geo.get("lon") or geo.get("lng")
            if not lat or not lng: continue
            
            location = ", ".join([p for p in [lieu, adresse, "Montpellier"] if p.strip()])
            date_start = (rec.get("date_debut", rec.get("date", "")) or "")[:10]
            if not date_start or date_start < TODAY: continue
            
            all_events.append({
                "title": title, "description": desc, "location": location,
                "latitude": float(lat), "longitude": float(lng),
                "date": date_start, "source_url": rec.get("url", "") or "",
            })
    else:
        print(f"  Montpellier: {r.status_code}: {r.text[:200]}")
except Exception as e:
    print(f"  Montpellier: {e}")

time.sleep(2)

# Strasbourg
print("\nStrasbourg (data.strasbourg.eu)...")
try:
    url = "https://data.strasbourg.eu/api/explore/v2.1/catalog/datasets/lieux_culture_et_loisir/records"
    params = {"limit": 100}
    r = requests.get(url, params=params, headers=HEADERS, timeout=30)
    if r.status_code == 200:
        data = r.json()
        total = data.get("total_count", 0)
        print(f"  Strasbourg culture: {total} lieux (pas un agenda)")
    else:
        print(f"  Strasbourg: {r.status_code}")
except Exception as e:
    print(f"  Strasbourg: {e}")

time.sleep(2)

# Lille
print("\nLille (opendata.lillemetropole.fr)...")
try:
    url = "https://opendata.lillemetropole.fr/api/explore/v2.1/catalog/datasets/evenements-ede-lille/records"
    params = {"limit": 100}
    r = requests.get(url, params=params, headers=HEADERS, timeout=30)
    if r.status_code == 200:
        data = r.json()
        total = data.get("total_count", 0)
        print(f"  Lille: {total} events")
    else:
        print(f"  Lille: {r.status_code}: {r.text[:150]}")
except Exception as e:
    print(f"  Lille: {e}")

time.sleep(2)

# Nice
print("\nNice (opendata.nicecotedazur.org)...")
try:
    url = "https://opendata.nicecotedazur.org/api/explore/v2.1/catalog/datasets/evenements-nice-cote-dazur/records"
    params = {"limit": 100}
    r = requests.get(url, params=params, headers=HEADERS, timeout=30)
    if r.status_code == 200:
        data = r.json()
        total = data.get("total_count", 0)
        print(f"  Nice: {total} events")
    else:
        print(f"  Nice: {r.status_code}: {r.text[:150]}")
except Exception as e:
    print(f"  Nice: {e}")

time.sleep(2)

# Rennes 
print("\nRennes (data.rennesmetropole.fr)...")
try:
    url = "https://data.rennesmetropole.fr/api/explore/v2.1/catalog/datasets/evenements-a-rennes/records"
    params = {"limit": 100}
    r = requests.get(url, params=params, headers=HEADERS, timeout=30)
    if r.status_code == 200:
        data = r.json()
        total = data.get("total_count", 0)
        print(f"  Rennes: {total} events")
    else:
        print(f"  Rennes: {r.status_code}: {r.text[:150]}")
except Exception as e:
    print(f"  Rennes: {e}")

time.sleep(2)

# Nantes (bon endpoint)
print("\nNantes (data.nantesmetropole.fr - bon endpoint)...")
try:
    # Essayer plusieurs noms de dataset
    for ds in ["244400404_agenda-evenements-nantes-nantes-metropole", 
                "agenda-des-manifestations-de-nantes-metropole",
                "244400404_agenda-des-manifestations"]:
        url = f"https://data.nantesmetropole.fr/api/explore/v2.1/catalog/datasets/{ds}/records"
        params = {"limit": 100}
        r = requests.get(url, params=params, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            data = r.json()
            total = data.get("total_count", 0)
            print(f"  Nantes ({ds}): {total} events")
            records = data.get("results", [])
            for rec in records:
                title = (rec.get("nom", rec.get("title", "")) or "").strip()
                if not title: continue
                desc = (rec.get("description", "") or "")[:500]
                desc = re.sub(r'<[^>]+>', ' ', desc)
                
                lieu = rec.get("lieu", rec.get("nom_lieu", "")) or ""
                adresse = rec.get("adresse", "") or ""
                commune = rec.get("commune", "") or "Nantes"
                
                geo = rec.get("location") or rec.get("geo_point_2d") or {}
                lat = lng = None
                if isinstance(geo, dict):
                    lat = geo.get("lat")
                    lng = geo.get("lon") or geo.get("lng")
                if not lat or not lng: continue
                
                location = ", ".join([p for p in [lieu, adresse, commune] if p.strip()])
                date_start = (rec.get("date", rec.get("date_debut", "")) or "")[:10]
                if not date_start or date_start < TODAY: continue
                
                all_events.append({
                    "title": title, "description": desc, "location": location,
                    "latitude": float(lat), "longitude": float(lng),
                    "date": date_start, "source_url": rec.get("url", "") or "",
                })
            break
        elif r.status_code == 404:
            continue
        else:
            print(f"  Nantes ({ds}): {r.status_code}")
except Exception as e:
    print(f"  Nantes: {e}")

time.sleep(2)

# Lyon
print("\nLyon (data.grandlyon.com - recherche datasets)...")
try:
    for ds in ["eve_agenda_entree", "agenda_evenements", "agenda-des-manifestations-culturelles",
                "agd_agendamanif", "evenements-grand-lyon"]:
        url = f"https://data.grandlyon.com/api/explore/v2.1/catalog/datasets/{ds}/records"
        params = {"limit": 100}
        r = requests.get(url, params=params, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            data = r.json()
            total = data.get("total_count", 0)
            print(f"  Lyon ({ds}): {total} records")
            break
        elif r.status_code != 404:
            print(f"  Lyon ({ds}): {r.status_code}")
except Exception as e:
    print(f"  Lyon: {e}")

time.sleep(2)

# Bordeaux
print("\nBordeaux (opendata.bordeaux-metropole.fr)...")
try:
    for ds in ["bor_evtam", "agenda-des-manifestations", "evenements-bordeaux-metropole",
                "met_agenda"]:
        url = f"https://opendata.bordeaux-metropole.fr/api/explore/v2.1/catalog/datasets/{ds}/records"
        params = {"limit": 100}
        r = requests.get(url, params=params, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            data = r.json()
            total = data.get("total_count", 0)
            print(f"  Bordeaux ({ds}): {total} records")
            break
        elif r.status_code != 404:
            print(f"  Bordeaux ({ds}): {r.status_code}")
except Exception as e:
    print(f"  Bordeaux: {e}")


# ==========================================================================
# 3. MySwitzerland API (events Suisse)
# ==========================================================================
print("\n" + "=" * 70)
print("MYSWITZERLAND API (events Suisse)")
print("=" * 70)

try:
    # MySwitzerland OpenData API - events endpoint
    url = "https://www.myswitzerland.com/api/search"
    params = {
        "q": "festival concert techno electro",
        "type": "event",
        "lang": "fr",
        "limit": 50,
    }
    r = requests.get(url, params=params, headers=HEADERS, timeout=30)
    if r.status_code == 200:
        data = r.json()
        print(f"  MySwitzerland: {json.dumps(data)[:300]}")
    else:
        print(f"  MySwitzerland: {r.status_code}")
except Exception as e:
    print(f"  MySwitzerland: {e}")


# ==========================================================================
# 4. Lister les datasets disponibles sur les portails
# ==========================================================================
print("\n" + "=" * 70)
print("RECHERCHE DE DATASETS AGENDA SUR LES PORTAILS")
print("=" * 70)

portals = [
    ("Nantes", "https://data.nantesmetropole.fr/api/explore/v2.1/catalog/datasets?where=keyword%3D%27agenda%27&limit=10"),
    ("Lyon", "https://data.grandlyon.com/api/explore/v2.1/catalog/datasets?where=keyword%3D%27agenda%27%20OR%20keyword%3D%27evenement%27&limit=10"),
    ("Bordeaux", "https://opendata.bordeaux-metropole.fr/api/explore/v2.1/catalog/datasets?where=keyword%3D%27agenda%27%20OR%20keyword%3D%27evenement%27&limit=10"),
    ("Lille", "https://opendata.lillemetropole.fr/api/explore/v2.1/catalog/datasets?where=keyword%3D%27agenda%27%20OR%20keyword%3D%27evenement%27&limit=10"),
    ("Toulouse", "https://data.toulouse-metropole.fr/api/explore/v2.1/catalog/datasets?where=keyword%3D%27agenda%27%20OR%20keyword%3D%27manifestation%27&limit=10"),
    ("Nice", "https://opendata.nicecotedazur.org/api/explore/v2.1/catalog/datasets?where=keyword%3D%27agenda%27%20OR%20keyword%3D%27evenement%27&limit=10"),
    ("Strasbourg", "https://data.strasbourg.eu/api/explore/v2.1/catalog/datasets?where=keyword%3D%27agenda%27%20OR%20keyword%3D%27evenement%27&limit=10"),
    ("Rennes", "https://data.rennesmetropole.fr/api/explore/v2.1/catalog/datasets?where=keyword%3D%27agenda%27%20OR%20keyword%3D%27evenement%27&limit=10"),
    ("Montpellier", "https://data.montpellier3m.fr/api/explore/v2.1/catalog/datasets?where=keyword%3D%27agenda%27%20OR%20keyword%3D%27evenement%27&limit=10"),
]

found_datasets = {}
for city, url in portals:
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            data = r.json()
            datasets = data.get("results", [])
            if datasets:
                found_datasets[city] = []
                for ds in datasets:
                    ds_id = ds.get("dataset_id", ds.get("datasetid", "?"))
                    ds_title = ds.get("metas", {}).get("default", {}).get("title", "?") if isinstance(ds.get("metas"), dict) else "?"
                    found_datasets[city].append({"id": ds_id, "title": ds_title})
                    print(f"  {city}: {ds_id} - {ds_title}")
        time.sleep(1)
    except Exception as e:
        print(f"  {city}: {e}")


# ==========================================================================
# RESULTATS
# ==========================================================================
print("\n" + "=" * 70)
print("RESULTATS")
print("=" * 70)

# Dedup
clean = []
for e in all_events:
    title_key = re.sub(r'\s+', ' ', e.get("title", "").lower())
    if title_key in existing_titles:
        continue
    existing_titles.add(title_key)
    clean.append(e)

print(f"Events bruts: {len(all_events)}")
print(f"Events apres dedup: {len(clean)}")

electro = [e for e in clean if e.get("is_electro")]
print(f"Events electro: {len(electro)}")

# Sauvegarder
with open("scraper/extra_events_batch.json", "w", encoding="utf-8") as f:
    json.dump(clean, f, ensure_ascii=False, indent=2)

with open("scraper/found_datasets.json", "w", encoding="utf-8") as f:
    json.dump(found_datasets, f, ensure_ascii=False, indent=2)

print(f"\nSauvegarde: scraper/extra_events_batch.json ({len(clean)} events)")
print(f"Datasets trouves: scraper/found_datasets.json")

# Echantillons
if electro:
    print("\nEchantillon electro:")
    for e in electro[:10]:
        print(f"  {e['title'][:60]} | {e['date']} | {e['location'][:50]}")

if clean:
    print(f"\nEchantillon tous:")
    for e in clean[:10]:
        print(f"  {e['title'][:60]} | {e['date']} | {e['location'][:50]}")
