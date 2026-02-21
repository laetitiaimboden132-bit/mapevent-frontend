"""
Import events from newly discovered sources:
1. Lisbon (Agenda Cultural + Sports) - dados.cm-lisboa.pt
2. Nantes (Agenda événements + animations) - data.nantesmetropole.fr
3. Vienna - data.wien.gv.at
4. Paris - additional datasets from opendata.paris.fr
"""
import requests
import json
import re
import time
from datetime import date

API = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"
TODAY = date.today().isoformat()
HEADERS = {"User-Agent": "MapEventAI-Bot/1.0"}

# Get existing URLs
print("Récupération des events existants...", flush=True)
r = requests.get(f"{API}/api/events", timeout=60)
events = r.json()
if isinstance(events, dict):
    events = events.get("events", [])
existing_urls = set()
for ev in events:
    url = ev.get("source_url", "")
    if url:
        existing_urls.add(url.lower().strip().rstrip("/"))
print(f"  {len(existing_urls)} URLs existantes", flush=True)


def categorize(title, desc, tags=None):
    text = f"{title} {desc} {' '.join(tags or [])}".lower()
    cats = []
    if any(w in text for w in ["techno", "house music", "dj set", "electronic", "electro", "rave", "trance"]):
        if not any(w in text for w in ["technolog", "informatique"]): cats.append("Music > Electronic")
    elif any(w in text for w in ["jazz", "swing", "blues", "fado"]): cats.append("Music > Jazz / Soul / Funk")
    elif any(w in text for w in ["rock", "punk", "metal"]): cats.append("Music > Rock / Metal")
    elif any(w in text for w in ["classique", "classical", "clássica", "klassik", "symphon", "opéra", "opera", "orchest"]): cats.append("Music > Classique")
    elif any(w in text for w in ["rap", "hip hop", "hip-hop"]): cats.append("Music > Urban")
    elif any(w in text for w in ["concert", "musique", "música", "musik", "music", "récital"]): cats.append("Music > Pop / Variété")
    
    if any(w in text for w in ["exposição", "exposition", "exhibition", "galeria", "galerie", "vernissage"]): cats.append("Culture > Expositions")
    elif any(w in text for w in ["teatro", "théâtre", "theater", "theatre"]): cats.append("Arts Vivants > Théâtre")
    elif any(w in text for w in ["cinema", "cinéma", "film", "projeção", "projection"]): cats.append("Culture > Cinéma & Projections")
    elif any(w in text for w in ["conferência", "conférence", "conference", "palestra", "debate", "débat"]): cats.append("Culture > Conférences & Rencontres")
    elif any(w in text for w in ["oficina", "atelier", "workshop"]): cats.append("Culture > Workshops")
    elif any(w in text for w in ["humor", "humour", "stand-up", "comédia"]): cats.append("Culture > Humour")
    elif any(w in text for w in ["visita", "visite", "patrimón", "patrimoine"]): cats.append("Culture > Visites & Patrimoine")
    elif any(w in text for w in ["museu", "musée", "museum"]): cats.append("Culture > Expositions")
    
    if any(w in text for w in ["dança", "danse", "dance", "ballet"]): cats.append("Arts Vivants > Danse")
    if any(w in text for w in ["desporto", "sport", "fitness", "corrida", "marathon", "yoga", "natação"]): cats.append("Sport")
    if any(w in text for w in ["festival", "festa", "fête"]): cats.append("Festivals & Grandes Fêtes")
    if any(w in text for w in ["criança", "enfant", "família", "famille", "infantil"]): cats.append("Famille & Enfants")
    if any(w in text for w in ["gastronomia", "dégustation", "food", "vinho", "vin"]): cats.append("Food & Drinks")
    if any(w in text for w in ["feira", "marché", "mercado", "brocante"]): cats.append("Loisirs & Animation > Défilés & Fêtes")
    if any(w in text for w in ["natureza", "nature", "jardim", "jardin"]): cats.append("Nature & Plein Air")
    
    if not cats: cats.append("Culture > Conférences & Rencontres")
    seen = set()
    return [c for c in cats if not (c in seen or seen.add(c))][:3]


def send_batch(events_list, batch_size=20):
    if not events_list: return 0, 0
    total_c, total_s = 0, 0
    total_batches = (len(events_list) + batch_size - 1) // batch_size
    for i in range(0, len(events_list), batch_size):
        batch = events_list[i:i+batch_size]
        try:
            r = requests.post(f"{API}/api/events/scraped/batch", json={"events": batch}, timeout=60)
            resp = r.json()
            results = resp.get("results", resp)
            c = results.get("created", 0) or results.get("inserted", 0)
            s = results.get("skipped", 0) + results.get("failed", 0)
            total_c += c
            total_s += s
        except Exception as e:
            print(f"    Batch erreur: {e}", flush=True)
        time.sleep(0.2)
    return total_c, total_s


# ============================================================
# 1. LISBON - Agenda Cultural
# ============================================================
def import_lisbon():
    print("\n" + "=" * 60, flush=True)
    print("LISBON - Agenda Cultural + Sports", flush=True)
    print("=" * 60, flush=True)
    
    all_events = []
    
    # Get datasets
    for ds_query in ["Agenda Cultural de Lisboa", "Eventos e Programas Desportivos"]:
        try:
            r = requests.get("https://dados.cm-lisboa.pt/api/3/action/package_search", 
                           params={"q": ds_query, "rows": 3}, timeout=15, headers=HEADERS)
            if r.status_code != 200:
                continue
            
            datasets = r.json().get("result", {}).get("results", [])
            for ds in datasets:
                ds_title = ds.get("title", "?")
                resources = ds.get("resources", [])
                
                # Find JSON or CSV resource
                for res in resources:
                    fmt = (res.get("format", "") or "").lower()
                    if fmt in ["json", "geojson", "csv"]:
                        res_url = res.get("url", "")
                        if not res_url:
                            continue
                        
                        print(f"\n  Dataset: {ds_title}", flush=True)
                        print(f"  Resource: {res_url[:80]} ({fmt})", flush=True)
                        
                        try:
                            r2 = requests.get(res_url, timeout=30, headers=HEADERS)
                            if r2.status_code != 200:
                                print(f"  HTTP {r2.status_code}", flush=True)
                                continue
                            
                            if fmt == "json" or fmt == "geojson":
                                data = r2.json()
                                if isinstance(data, dict):
                                    if "features" in data:
                                        records = [f.get("properties", {}) for f in data["features"]]
                                        # Add geometry
                                        for i, f in enumerate(data["features"]):
                                            geom = f.get("geometry", {})
                                            if geom:
                                                coords = geom.get("coordinates", [])
                                                if coords and len(coords) >= 2:
                                                    records[i]["_lng"] = coords[0]
                                                    records[i]["_lat"] = coords[1]
                                    elif "result" in data:
                                        records = data["result"].get("records", data["result"])
                                    elif "records" in data:
                                        records = data["records"]
                                    else:
                                        records = [data]
                                elif isinstance(data, list):
                                    records = data
                                else:
                                    records = []
                            else:
                                # CSV - skip for now
                                continue
                            
                            print(f"  Records: {len(records)}", flush=True)
                            if records and isinstance(records[0], dict):
                                print(f"  Sample keys: {list(records[0].keys())[:15]}", flush=True)
                            
                            for rec in records:
                                if not isinstance(rec, dict):
                                    continue
                                
                                title = rec.get("DESIGNACAO", rec.get("nome", rec.get("title", rec.get("name", "")))) or ""
                                if not title:
                                    continue
                                
                                desc = rec.get("DESCRICAO", rec.get("description", rec.get("descricao", ""))) or ""
                                desc = re.sub(r'<[^>]+>', '', str(desc)).strip()
                                if len(desc) > 500:
                                    desc = desc[:497] + "..."
                                
                                lat = rec.get("_lat", rec.get("LATITUDE", rec.get("latitude", rec.get("lat"))))
                                lng = rec.get("_lng", rec.get("LONGITUDE", rec.get("longitude", rec.get("lon", rec.get("lng")))))
                                
                                if not lat or not lng:
                                    geo = rec.get("geo_point_2d", rec.get("geom", {}))
                                    if isinstance(geo, dict):
                                        lat = geo.get("lat", geo.get("latitude"))
                                        lng = lng or geo.get("lon", geo.get("longitude"))
                                
                                if not lat or not lng:
                                    continue
                                
                                try:
                                    lat = float(lat)
                                    lng = float(lng)
                                except:
                                    continue
                                
                                # Check coordinates are in Lisbon area
                                if not (38.5 < lat < 39.0 and -9.5 < lng < -8.8):
                                    continue
                                
                                date_start = rec.get("DATA_INICIO", rec.get("date_start", rec.get("data_inicio", ""))) or ""
                                date_end = rec.get("DATA_FIM", rec.get("date_end", rec.get("data_fim", ""))) or ""
                                
                                date_str = str(date_start)[:10] if date_start else None
                                time_str = str(date_start)[11:16] if date_start and len(str(date_start)) > 11 else None
                                end_date = str(date_end)[:10] if date_end else None
                                
                                if not date_str or date_str < TODAY:
                                    continue
                                
                                source_url = rec.get("URL", rec.get("url", rec.get("link", ""))) or ""
                                if not source_url:
                                    ev_id = rec.get("ID", rec.get("id", rec.get("OBJECTID", "")))
                                    if ev_id:
                                        source_url = f"https://www.agendalx.pt/evento/{ev_id}"
                                    else:
                                        continue
                                
                                if source_url.lower().strip().rstrip("/") in existing_urls:
                                    continue
                                
                                local = rec.get("LOCAL", rec.get("local", rec.get("morada", ""))) or ""
                                morada = rec.get("MORADA", rec.get("address", "")) or ""
                                location_str = f"{local}, {morada}" if local and morada else (local or morada or "Lisboa")
                                
                                cats = categorize(title, desc)
                                
                                all_events.append({
                                    "title": title[:200],
                                    "description": desc or title,
                                    "date": date_str,
                                    "time": time_str,
                                    "end_date": end_date,
                                    "end_time": None,
                                    "location": location_str[:200],
                                    "latitude": lat,
                                    "longitude": lng,
                                    "categories": cats,
                                    "source_url": source_url,
                                    "source": "OpenData Lisboa",
                                    "validation_status": "auto_validated",
                                })
                        except Exception as e:
                            print(f"  Parse error: {e}", flush=True)
                        break  # Only process first valid resource
        except Exception as e:
            print(f"  Error: {e}", flush=True)
    
    print(f"\n  Total: {len(all_events)} events candidats", flush=True)
    if all_events:
        created, skipped = send_batch(all_events)
        print(f"  Insérés: {created}, Skippés: {skipped}", flush=True)
        for ev in all_events:
            existing_urls.add(ev["source_url"].lower().strip().rstrip("/"))
        return created
    return 0


# ============================================================
# 2. NANTES - Agenda événements
# ============================================================
def import_nantes():
    print("\n" + "=" * 60, flush=True)
    print("NANTES - Agenda événements + animations culturelles", flush=True)
    print("=" * 60, flush=True)
    
    all_events = []
    
    dataset_ids = [
        "244400404_agenda-evenements-nantes-metro",
        "244400404_agenda-animations-culturelles-",
    ]
    
    for ds_id in dataset_ids:
        offset = 0
        while True:
            url = f"https://data.nantesmetropole.fr/api/explore/v2.1/catalog/datasets/{ds_id}/records"
            r = requests.get(url, params={"limit": 100, "offset": offset}, timeout=30, headers=HEADERS)
            
            if r.status_code != 200:
                print(f"  {ds_id}: HTTP {r.status_code}", flush=True)
                break
            
            data = r.json()
            results = data.get("results", [])
            total = data.get("total_count", 0)
            
            if not results:
                break
            
            if offset == 0:
                print(f"\n  Dataset: {ds_id}", flush=True)
                print(f"  Total: {total} records", flush=True)
                if results:
                    print(f"  Sample keys: {list(results[0].keys())[:15]}", flush=True)
            
            for rec in results:
                title = rec.get("nom", rec.get("title", rec.get("titre", ""))) or ""
                if not title:
                    continue
                
                desc = rec.get("description", rec.get("resume", "")) or ""
                desc = re.sub(r'<[^>]+>', '', desc).strip()
                if len(desc) > 500:
                    desc = desc[:497] + "..."
                
                # Geo
                geo = rec.get("location", rec.get("geo_point_2d", rec.get("geolocalisation", {})))
                if isinstance(geo, dict):
                    lat = geo.get("lat", geo.get("latitude"))
                    lng = geo.get("lon", geo.get("longitude"))
                elif isinstance(geo, str) and "," in geo:
                    parts = geo.split(",")
                    try:
                        lat, lng = float(parts[0]), float(parts[1])
                    except:
                        lat = lng = None
                else:
                    lat = rec.get("latitude")
                    lng = rec.get("longitude")
                
                if not lat or not lng:
                    continue
                
                try:
                    lat = float(lat)
                    lng = float(lng)
                except:
                    continue
                
                # Dates
                date_start = rec.get("date", rec.get("date_debut", rec.get("date_start", ""))) or ""
                date_end = rec.get("date_fin", rec.get("date_end", "")) or ""
                
                date_str = str(date_start)[:10] if date_start else None
                time_str = str(date_start)[11:16] if date_start and len(str(date_start)) > 11 else None
                end_date = str(date_end)[:10] if date_end else None
                
                if not date_str or date_str < TODAY:
                    continue
                
                # Source URL
                source_url = rec.get("url", rec.get("lien", "")) or ""
                if not source_url:
                    ev_id = rec.get("recordid", rec.get("id", ""))
                    if ev_id:
                        source_url = f"https://metropole.nantes.fr/events/{ev_id}"
                    else:
                        continue
                
                if source_url.lower().strip().rstrip("/") in existing_urls:
                    continue
                
                lieu = rec.get("lieu", rec.get("adresse", "")) or ""
                location_str = lieu if lieu else "Nantes"
                
                type_evt = rec.get("type", rec.get("categorie", "")) or ""
                cats = categorize(title, desc, [type_evt] if type_evt else None)
                
                all_events.append({
                    "title": title[:200],
                    "description": desc or title,
                    "date": date_str,
                    "time": time_str,
                    "end_date": end_date,
                    "end_time": None,
                    "location": location_str[:200],
                    "latitude": lat,
                    "longitude": lng,
                    "categories": cats,
                    "source_url": source_url,
                    "source": "OpenData Nantes",
                    "validation_status": "auto_validated",
                })
            
            offset += len(results)
            if offset >= total or offset >= 5000:
                break
            time.sleep(0.5)
    
    print(f"\n  Total: {len(all_events)} events candidats", flush=True)
    if all_events:
        created, skipped = send_batch(all_events)
        print(f"  Insérés: {created}, Skippés: {skipped}", flush=True)
        for ev in all_events:
            existing_urls.add(ev["source_url"].lower().strip().rstrip("/"))
        return created
    return 0


# ============================================================
# 3. MORE OPENAGENDA - New agendas from discovery
# ============================================================
def import_more_oa():
    """Import from additional OpenAgenda agendas found during discovery."""
    print("\n" + "=" * 60, flush=True)
    print("OPENAGENDA - Agendas supplémentaires", flush=True)
    print("=" * 60, flush=True)
    
    OA_API = "https://openagenda.com/api/agendas/slug/{slug}/events"
    
    try:
        with open("oa_active_agendas.json", "r", encoding="utf-8") as f:
            discovered = json.load(f)
    except:
        print("  Pas de fichier oa_active_agendas.json", flush=True)
        return 0
    
    # Get agendas with >5 events, sort by count
    big_agendas = [a for a in discovered if a.get("events", a.get("real_upcoming", 0)) > 5]
    big_agendas.sort(key=lambda a: a.get("events", a.get("real_upcoming", 0)), reverse=True)
    
    # Skip already-known agendas
    known_slugs = {
        "francetravail", "ile-de-france", "scare", "cmf", "hello-lille",
        "semainepetiteenfance", "lerif", "sites-cites", "dioceseparis",
        "tableau-de-bord", "agenda-temps-libres", "roissy-pays-de-france",
        "freres-de-saint-jean-en-france", "marseille-alive", "francenum",
        "rof", "universite-paris-saclay", "europeenfrance", "saint-marcel",
        "seineouest", "acp-la-manufacture-chanson", "info-jeunes-france",
        "montreuil", "calendrier-musique", "france-belgique-calendrier",
        "jassclub-paris", "grand-theatre-geneve", "ariana-ville-geneve",
        "chateau-de-voltaire-a-ferney", "orchestre-de-la-suisse-romande",
        "music-line-productions-saison", "eurometropolis-lille-kortrijk-tournai",
        "musique-sacree-a-notre-dame-de-paris", "conservatoires",
        "librairie-le-divan",
    }
    
    new_agendas = [a for a in big_agendas if a["slug"] not in known_slugs]
    print(f"  {len(new_agendas)} nouveaux agendas avec >5 events", flush=True)
    
    total_imported = 0
    
    for ag in new_agendas[:80]:  # Process up to 80 new agendas
        slug = ag["slug"]
        name = ag.get("title", slug)[:40]
        expected = ag.get("events", ag.get("real_upcoming", 0))
        
        try:
            # Fetch events
            all_events = []
            offset = 0
            while offset < 1000:
                r = requests.get(OA_API.format(slug=slug), params={
                    "size": 50,
                    "from": offset,
                    "relative[]": ["current", "upcoming"],
                    "sort": "lastTimingWithFeatured.asc",
                    "includeFields[]": [
                        "uid", "slug", "title", "description",
                        "nextTiming", "lastTiming", "keywords",
                        "location.name", "location.address", "location.city",
                        "location.postalCode", "location.countryCode",
                        "location.latitude", "location.longitude",
                    ]
                }, timeout=15, headers=HEADERS)
                
                if r.status_code != 200:
                    break
                
                data = r.json()
                events = data.get("events", [])
                total = data.get("total", 0)
                
                if not events:
                    break
                
                for ev in events:
                    td = ev.get("title", {})
                    title = (td.get("fr", "") or td.get("en", "") or td.get("de", "")) if isinstance(td, dict) else str(td)
                    if not title: continue
                    
                    dd = ev.get("description", {})
                    desc = (dd.get("fr", "") or dd.get("en", "")) if isinstance(dd, dict) else (str(dd) if dd else "")
                    desc = re.sub(r'<[^>]+>', '', desc).strip()
                    if len(desc) > 500: desc = desc[:497] + "..."
                    
                    loc = ev.get("location", {}) or {}
                    lat, lng = loc.get("latitude"), loc.get("longitude")
                    if not lat or not lng: continue
                    
                    ev_slug = ev.get("slug", "")
                    ev_uid = ev.get("uid", "")
                    source_url = f"https://openagenda.com/fr/{slug}/events/{ev_slug or ev_uid}"
                    
                    if source_url.lower().strip().rstrip("/") in existing_urls:
                        continue
                    
                    timing = ev.get("nextTiming", {}) or ev.get("lastTiming", {}) or {}
                    begin, end = timing.get("begin", ""), timing.get("end", "")
                    
                    date_str = begin[:10] if begin else None
                    if not date_str or date_str < TODAY: continue
                    time_str = begin[11:16] if begin and len(begin) > 11 else None
                    end_date = end[:10] if end else None
                    end_time = end[11:16] if end and len(end) > 11 else None
                    
                    loc_str = loc.get("name", "") or ""
                    if loc.get("address"): loc_str += f", {loc['address']}" if loc_str else loc["address"]
                    if loc.get("city") and loc["city"] not in loc_str: loc_str += f", {loc['city']}"
                    
                    kw = ev.get("keywords", {})
                    tags = []
                    if isinstance(kw, dict):
                        for v in kw.values():
                            if isinstance(v, list): tags.extend(v)
                    
                    cats = categorize(title, desc, tags)
                    
                    all_events.append({
                        "title": title[:200],
                        "description": desc or title,
                        "date": date_str,
                        "time": time_str,
                        "end_date": end_date,
                        "end_time": end_time,
                        "location": loc_str[:200] or "France",
                        "latitude": float(lat),
                        "longitude": float(lng),
                        "categories": cats,
                        "source_url": source_url,
                        "source": "OpenAgenda",
                        "validation_status": "auto_validated",
                    })
                
                offset += len(events)
                if offset >= total: break
                time.sleep(0.3)
            
            if all_events:
                created, skipped = send_batch(all_events)
                if created > 0:
                    print(f"  ✓ {name}: +{created} ({skipped} skip)", flush=True)
                total_imported += created
                for ev in all_events:
                    existing_urls.add(ev["source_url"].lower().strip().rstrip("/"))
            
            time.sleep(0.3)
        except Exception as e:
            pass
    
    print(f"\n  Total importé: {total_imported}", flush=True)
    return total_imported


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("=" * 60, flush=True)
    print(f"IMPORT NOUVELLES SOURCES - {TODAY}", flush=True)
    print("=" * 60, flush=True)
    
    total = 0
    total += import_lisbon()
    total += import_nantes()
    total += import_more_oa()
    
    print(f"\n{'=' * 60}", flush=True)
    print(f"RÉSULTAT FINAL: {total} events importés", flush=True)
    print("=" * 60, flush=True)
