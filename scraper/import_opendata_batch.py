"""
BATCH IMPORT from confirmed open data sources:
1. Paris "Que faire à Paris" (3188 events) - Licence Ouverte
2. Madrid Open Data (1515 events) - Open data
3. Barcelona Cultural Agenda - CC BY
4. Toulouse manifestations culturelles - Licence Ouverte
5. OpenAgenda internal API (top agendas as discovered)

All sources are verified open data with permissive licenses.
"""
import requests
import json
import re
import time
from datetime import date, datetime

API = "https://ctp67u5hgni2rbfr3kp4p74kxa0gxycf.lambda-url.eu-west-1.on.aws"
TODAY = date.today().isoformat()
HEADERS = {"User-Agent": "MapEventAI-Bot/1.0"}

# Get existing URLs
print("Récupération des events existants...")
r = requests.get(f"{API}/api/events", timeout=60)
events = r.json()
if isinstance(events, dict):
    events = events.get("events", [])
existing_urls = set()
for ev in events:
    url = ev.get("source_url", "")
    if url:
        existing_urls.add(url.lower().strip().rstrip("/"))
print(f"  {len(existing_urls)} URLs existantes, {len(events)} events total")


def categorize_event(title, desc, tags=None):
    """Universal event categorizer."""
    text = f"{title} {desc} {' '.join(tags or [])}".lower()
    cats = []
    
    # Music
    if any(w in text for w in ["techno", "house music", "dj set", "electronic", "electro", "rave", "trance"]):
        if not any(w in text for w in ["technolog", "informatique", "electroménager"]):
            cats.append("Music > Electronic")
    elif any(w in text for w in ["jazz", "swing", "blues"]):
        cats.append("Music > Jazz / Soul / Funk")
    elif any(w in text for w in ["rock", "punk", "metal", "grunge"]):
        cats.append("Music > Rock / Metal")
    elif any(w in text for w in ["classique", "classical", "symphon", "opéra", "opera", "orchestre"]):
        cats.append("Music > Classique")
    elif any(w in text for w in ["rap", "hip hop", "hip-hop", "r&b"]):
        cats.append("Music > Urban")
    elif any(w in text for w in ["folk", "acoustic", "acoustique"]):
        cats.append("Music > Folk / Acoustic")
    elif any(w in text for w in ["concert", "musique", "musik", "music", "live band", "récital"]):
        cats.append("Music > Pop / Variété")
    
    # Culture
    if any(w in text for w in ["exposition", "exhibition", "galerie", "gallery", "vernissage", "exposición"]):
        cats.append("Culture > Expositions")
    elif any(w in text for w in ["théâtre", "theater", "theatre", "teatro", "comédie", "comedia"]):
        cats.append("Arts Vivants > Théâtre")
    elif any(w in text for w in ["cinéma", "cinema", "cine", "film", "projection", "película"]):
        cats.append("Culture > Cinéma & Projections")
    elif any(w in text for w in ["conférence", "conferencia", "conference", "débat", "debate", "table ronde"]):
        cats.append("Culture > Conférences & Rencontres")
    elif any(w in text for w in ["atelier", "taller", "workshop", "masterclass"]):
        cats.append("Culture > Workshops")
    elif any(w in text for w in ["lecture", "conte", "littéra", "poésie", "literatura", "slam"]):
        cats.append("Culture > Littérature & Conte")
    elif any(w in text for w in ["humour", "humor", "stand-up", "comedia"]):
        cats.append("Culture > Humour")
    elif any(w in text for w in ["visite guidée", "visite", "patrimoine", "visita", "guided tour"]):
        cats.append("Culture > Visites & Patrimoine")
    elif any(w in text for w in ["musée", "museo", "museum"]):
        cats.append("Culture > Expositions")
    
    # Dance
    if any(w in text for w in ["danse", "dance", "ballet", "danza", "chorégraph", "coreograf"]):
        cats.append("Arts Vivants > Danse")
    
    # Sport
    if any(w in text for w in ["sport", "fitness", "marathon", "course", "deporte", "fútbol", "futbol", "rugby", "basket", "natation", "yoga"]):
        cats.append("Sport")
    
    # Festival
    if any(w in text for w in ["festival", "open air", "fête", "fiesta"]):
        cats.append("Festivals & Grandes Fêtes")
    
    # Family
    if any(w in text for w in ["enfant", "jeune public", "famille", "niños", "kids", "infantil"]):
        cats.append("Famille & Enfants")
    
    # Food
    if any(w in text for w in ["dégustation", "brunch", "food", "cuisine", "gastro", "vin", "gastronomía", "cocina"]):
        cats.append("Food & Drinks")
    
    # Markets
    if any(w in text for w in ["marché", "brocante", "mercado", "foire", "feria"]):
        cats.append("Loisirs & Animation > Défilés & Fêtes")
    
    # Nature
    if any(w in text for w in ["nature", "jardin", "botanique", "randonnée", "plein air", "senderismo"]):
        cats.append("Nature & Plein Air")
    
    if not cats:
        cats.append("Culture > Conférences & Rencontres")
    
    # Deduplicate while preserving order
    seen = set()
    unique = []
    for c in cats:
        if c not in seen:
            seen.add(c)
            unique.append(c)
    return unique[:3]


def send_batch(events_list, batch_size=15):
    """Send events in batches."""
    if not events_list:
        return 0, 0
    total_created = 0
    total_skipped = 0
    for i in range(0, len(events_list), batch_size):
        batch = events_list[i:i+batch_size]
        try:
            r = requests.post(f"{API}/api/events/scraped/batch", json={"events": batch}, timeout=30)
            resp = r.json()
            results = resp.get("results", resp)
            created = results.get("created", 0) or results.get("inserted", 0)
            skipped = results.get("skipped", 0) + results.get("failed", 0)
            total_created += created
            total_skipped += skipped
        except Exception as e:
            print(f"    Batch erreur: {e}")
        time.sleep(0.3)
    return total_created, total_skipped


# ============================================================
# SOURCE 1: Paris "Que faire à Paris"
# ============================================================
def import_paris():
    print("\n" + "=" * 60)
    print("SOURCE 1: Paris - Que faire à Paris")
    print("  Licence: Licence Ouverte (Open License)")
    print("=" * 60)
    
    all_events = []
    offset = 0
    batch = 100
    
    while True:
        url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/que-faire-a-paris-/records"
        r = requests.get(url, params={
            "limit": batch,
            "offset": offset,
            "order_by": "date_start DESC",
        }, timeout=30, headers=HEADERS)
        
        if r.status_code != 200:
            print(f"  Erreur HTTP {r.status_code}")
            break
        
        data = r.json()
        results = data.get("results", [])
        total = data.get("total_count", 0)
        
        if not results:
            break
        
        print(f"  Fetch {offset}-{offset+len(results)} / {total}")
        
        for rec in results:
            title = rec.get("title", "")
            if not title:
                continue
            
            desc = rec.get("description", "") or ""
            desc = re.sub(r'<[^>]+>', '', desc).strip()
            if len(desc) > 500:
                desc = desc[:497] + "..."
            
            # Location
            geo = rec.get("lat_lon", {}) or {}
            lat = geo.get("lat") if isinstance(geo, dict) else None
            lng = geo.get("lon") if isinstance(geo, dict) else None
            
            if not lat or not lng:
                # Try alternative geo field
                lat = rec.get("latitude")
                lng = rec.get("longitude")
            
            if not lat or not lng:
                continue
            
            # Address
            addr = rec.get("address_street", "") or ""
            addr_zip = rec.get("address_zipcode", "") or ""
            addr_city = rec.get("address_city", "") or "Paris"
            place = rec.get("address_name", "") or ""
            
            location_str = place
            if addr:
                location_str += f", {addr}" if location_str else addr
            if addr_zip:
                location_str += f", {addr_zip}"
            if addr_city:
                location_str += f" {addr_city}"
            location_str = location_str.strip().strip(",").strip()
            
            # Dates
            date_start = rec.get("date_start", "")
            date_end = rec.get("date_end", "")
            
            date_str = date_start[:10] if date_start else None
            time_str = date_start[11:16] if date_start and len(date_start) > 11 else None
            end_date = date_end[:10] if date_end else None
            end_time = date_end[11:16] if date_end and len(date_end) > 11 else None
            
            if not date_str or date_str < TODAY:
                continue
            
            # Source URL
            source_url = rec.get("url", "") or rec.get("access_link", "")
            if not source_url:
                slug = rec.get("id", rec.get("recordid", ""))
                source_url = f"https://quefaire.paris.fr/event/{slug}" if slug else ""
            
            if not source_url:
                continue
            
            if source_url.lower().strip().rstrip("/") in existing_urls:
                continue
            
            # Tags
            tags = []
            for field in ["tags", "category", "type"]:
                val = rec.get(field, "")
                if val:
                    if isinstance(val, list):
                        tags.extend(val)
                    else:
                        tags.append(str(val))
            
            cats = categorize_event(title, desc, tags)
            
            all_events.append({
                "title": title[:200],
                "description": desc or title,
                "date": date_str,
                "time": time_str,
                "end_date": end_date,
                "end_time": end_time,
                "location": location_str or "Paris",
                "latitude": float(lat),
                "longitude": float(lng),
                "categories": cats,
                "source_url": source_url,
                "source": "OpenData Paris",
                "validation_status": "auto_validated",
            })
        
        offset += len(results)
        if offset >= total or offset >= 5000:  # Cap at 5000
            break
        time.sleep(0.5)
    
    print(f"\n  {len(all_events)} events candidats")
    if all_events:
        created, skipped = send_batch(all_events)
        print(f"  Insérés: {created}, Skippés: {skipped}")
        for ev in all_events:
            existing_urls.add(ev["source_url"].lower().strip().rstrip("/"))
        return created
    return 0


# ============================================================
# SOURCE 2: Madrid Open Data
# ============================================================
def import_madrid():
    print("\n" + "=" * 60)
    print("SOURCE 2: Madrid Open Data")
    print("  Licence: Datos abiertos (Open Data)")
    print("=" * 60)
    
    url = "https://datos.madrid.es/egob/catalogo/300107-0-agenda-actividades-eventos.json"
    r = requests.get(url, timeout=30, headers=HEADERS)
    
    if r.status_code != 200:
        print(f"  Erreur: {r.status_code}")
        return 0
    
    data = r.json()
    graph = data.get("@graph", [])
    print(f"  {len(graph)} events bruts")
    
    all_events = []
    for rec in graph:
        title = rec.get("title", "")
        if not title:
            continue
        
        desc = rec.get("description", "") or ""
        desc = re.sub(r'<[^>]+>', '', desc).strip()
        if len(desc) > 500:
            desc = desc[:497] + "..."
        
        # Location
        loc = rec.get("location", {}) or {}
        lat = loc.get("latitude")
        lng = loc.get("longitude")
        
        if not lat or not lng:
            continue
        
        # Address
        addr = rec.get("address", {}) or {}
        street = addr.get("street-address", "") or ""
        locality = addr.get("locality", "") or "Madrid"
        postal = addr.get("postal-code", "") or ""
        
        location_str = street
        if postal:
            location_str += f", {postal}" if location_str else postal
        if locality:
            location_str += f" {locality}" if location_str else locality
        location_str = location_str.strip().strip(",").strip()
        
        # Dates
        dtstart = rec.get("dtstart", "")
        dtend = rec.get("dtend", "")
        
        date_str = dtstart[:10] if dtstart else None
        time_str = dtstart[11:16] if dtstart and "T" in dtstart else None
        end_date = dtend[:10] if dtend else None
        end_time = dtend[11:16] if dtend and "T" in dtend else None
        
        if not date_str or date_str < TODAY:
            continue
        
        # Source URL
        source_url = rec.get("link", "") or rec.get("@id", "")
        if not source_url:
            continue
        
        if source_url.lower().strip().rstrip("/") in existing_urls:
            continue
        
        cats = categorize_event(title, desc)
        
        all_events.append({
            "title": title[:200],
            "description": desc or title,
            "date": date_str,
            "time": time_str,
            "end_date": end_date,
            "end_time": end_time,
            "location": location_str or "Madrid",
            "latitude": float(lat),
            "longitude": float(lng),
            "categories": cats,
            "source_url": source_url,
            "source": "OpenData Madrid",
            "validation_status": "auto_validated",
        })
    
    print(f"  {len(all_events)} events candidats")
    if all_events:
        created, skipped = send_batch(all_events)
        print(f"  Insérés: {created}, Skippés: {skipped}")
        for ev in all_events:
            existing_urls.add(ev["source_url"].lower().strip().rstrip("/"))
        return created
    return 0


# ============================================================
# SOURCE 3: Barcelona Open Data
# ============================================================
def import_barcelona():
    print("\n" + "=" * 60)
    print("SOURCE 3: Barcelona Open Data")
    print("  Licence: CC BY 4.0")
    print("=" * 60)
    
    # Get the dataset resources
    datasets = [
        "https://opendata-ajuntament.barcelona.cat/data/api/3/action/package_show?id=agenda-cultural",
        "https://opendata-ajuntament.barcelona.cat/data/api/3/action/package_show?id=agenda-esportiva",
        "https://opendata-ajuntament.barcelona.cat/data/api/3/action/package_show?id=activitats-702",
    ]
    
    all_events = []
    
    for ds_url in datasets:
        try:
            r = requests.get(ds_url, timeout=15, headers=HEADERS)
            if r.status_code != 200:
                continue
            
            ds = r.json().get("result", {})
            ds_title = ds.get("title", "?")
            resources = ds.get("resources", [])
            
            json_res = [res for res in resources if "json" in (res.get("format", "") or "").lower()]
            
            for res in json_res[:1]:  # Take first JSON resource
                res_url = res.get("url", "")
                if not res_url:
                    continue
                
                print(f"\n  Dataset: {ds_title}")
                print(f"  URL: {res_url[:80]}")
                
                r2 = requests.get(res_url, timeout=30, headers=HEADERS)
                if r2.status_code != 200:
                    print(f"  Erreur: {r2.status_code}")
                    continue
                
                events_data = r2.json()
                if isinstance(events_data, dict):
                    events_data = events_data.get("events", events_data.get("results", events_data.get("data", [events_data])))
                
                if not isinstance(events_data, list):
                    print(f"  Format inattendu: {type(events_data).__name__}")
                    continue
                
                print(f"  {len(events_data)} events bruts")
                
                for ev in events_data:
                    if not isinstance(ev, dict):
                        continue
                    
                    title = ev.get("name", ev.get("title", ev.get("nom", "")))
                    if isinstance(title, dict):
                        title = title.get("ca", title.get("es", title.get("en", "")))
                    if not title:
                        continue
                    
                    desc = ev.get("description", ev.get("body", "")) or ""
                    if isinstance(desc, dict):
                        desc = desc.get("ca", desc.get("es", desc.get("en", "")))
                    desc = re.sub(r'<[^>]+>', '', str(desc)).strip()
                    if len(desc) > 500:
                        desc = desc[:497] + "..."
                    
                    lat = ev.get("latitude", ev.get("geo_epgs_4326_latitud"))
                    lng = ev.get("longitude", ev.get("geo_epgs_4326_longitud"))
                    
                    # Try nested location
                    if not lat:
                        loc = ev.get("location", ev.get("equipament", {})) or {}
                        if isinstance(loc, dict):
                            lat = loc.get("latitude", loc.get("latitud"))
                            lng = lng or loc.get("longitude", loc.get("longitud"))
                    
                    if not lat or not lng:
                        continue
                    
                    try:
                        lat = float(lat)
                        lng = float(lng)
                    except:
                        continue
                    
                    # Dates
                    start = ev.get("start_date", ev.get("data_ini", ev.get("date_start", ""))) or ""
                    end = ev.get("end_date", ev.get("data_fi", ev.get("date_end", ""))) or ""
                    
                    date_str = str(start)[:10] if start else None
                    time_str = str(start)[11:16] if start and len(str(start)) > 11 else None
                    end_date = str(end)[:10] if end else None
                    end_time = str(end)[11:16] if end and len(str(end)) > 11 else None
                    
                    if not date_str or date_str < TODAY:
                        continue
                    
                    source_url = ev.get("url", ev.get("link", "")) or ""
                    if not source_url:
                        ev_id = ev.get("id", ev.get("register_id", ""))
                        if ev_id:
                            source_url = f"https://www.barcelona.cat/event/{ev_id}"
                        else:
                            continue
                    
                    if source_url.lower().strip().rstrip("/") in existing_urls:
                        continue
                    
                    addr = ev.get("address", ev.get("adreça", ev.get("direccio", ""))) or ""
                    if isinstance(addr, dict):
                        addr = addr.get("street_address", str(addr))
                    place = ev.get("place", ev.get("nom_equipament", "")) or ""
                    location_str = f"{place}, {addr}" if place and addr else (place or addr or "Barcelona")
                    
                    cats = categorize_event(title, desc)
                    
                    all_events.append({
                        "title": str(title)[:200],
                        "description": desc or str(title),
                        "date": date_str,
                        "time": time_str,
                        "end_date": end_date,
                        "end_time": end_time,
                        "location": location_str[:200],
                        "latitude": lat,
                        "longitude": lng,
                        "categories": cats,
                        "source_url": source_url,
                        "source": "OpenData Barcelona",
                        "validation_status": "auto_validated",
                    })
                
                time.sleep(1)
        except Exception as e:
            print(f"  Erreur: {e}")
    
    print(f"\n  Total Barcelona: {len(all_events)} events candidats")
    if all_events:
        created, skipped = send_batch(all_events)
        print(f"  Insérés: {created}, Skippés: {skipped}")
        for ev in all_events:
            existing_urls.add(ev["source_url"].lower().strip().rstrip("/"))
        return created
    return 0


# ============================================================
# SOURCE 4: Toulouse manifestations culturelles
# ============================================================
def import_toulouse():
    print("\n" + "=" * 60)
    print("SOURCE 4: Toulouse - Manifestations culturelles")
    print("  Licence: Licence Ouverte / Open License")
    print("=" * 60)
    
    all_events = []
    offset = 0
    
    while True:
        url = "https://data.toulouse-metropole.fr/api/explore/v2.1/catalog/datasets/agenda-des-manifestations-culturelles-702702/records"
        r = requests.get(url, params={
            "limit": 100,
            "offset": offset,
        }, timeout=30, headers=HEADERS)
        
        if r.status_code != 200:
            print(f"  Erreur: {r.status_code}")
            # Try alternative dataset IDs
            for ds_id in [
                "agenda-des-manifestations-culturelles",
                "agenda-manifestations-culturelles",
                "evenements-toulouse",
                "manifestations-culturelles-702702",
            ]:
                url2 = f"https://data.toulouse-metropole.fr/api/explore/v2.1/catalog/datasets/{ds_id}/records"
                r2 = requests.get(url2, params={"limit": 5}, timeout=10, headers=HEADERS)
                if r2.status_code == 200:
                    print(f"  Trouvé: {ds_id}")
                    url = url2
                    r = r2
                    break
            if r.status_code != 200:
                break
        
        data = r.json()
        results = data.get("results", [])
        total = data.get("total_count", 0)
        
        if not results:
            break
        
        print(f"  Fetch {offset}-{offset+len(results)} / {total}")
        
        for rec in results:
            title = rec.get("nom_de_la_manifestation", rec.get("title", rec.get("nom", ""))) or ""
            if not title:
                continue
            
            desc = rec.get("descriptif_court", rec.get("description", "")) or ""
            desc = re.sub(r'<[^>]+>', '', desc).strip()
            if len(desc) > 500:
                desc = desc[:497] + "..."
            
            # Geo
            geo = rec.get("geo_point_2d", rec.get("geo_point", {})) or {}
            if isinstance(geo, dict):
                lat = geo.get("lat")
                lng = geo.get("lon")
            elif isinstance(geo, list) and len(geo) >= 2:
                lat = geo[0]
                lng = geo[1]
            else:
                lat = rec.get("latitude")
                lng = rec.get("longitude")
            
            if not lat or not lng:
                continue
            
            # Dates
            date_str = rec.get("date_debut", rec.get("date_start", ""))
            if date_str:
                date_str = str(date_str)[:10]
            end_str = rec.get("date_fin", rec.get("date_end", ""))
            
            if not date_str or date_str < TODAY:
                continue
            
            # Location
            lieu = rec.get("lieu", rec.get("place", "")) or ""
            adresse = rec.get("adresse", rec.get("address", "")) or ""
            location_str = f"{lieu}, {adresse}" if lieu and adresse else (lieu or adresse or "Toulouse")
            
            # Source URL
            source_url = rec.get("lien", rec.get("url", "")) or ""
            if not source_url:
                rec_id = rec.get("recordid", rec.get("identifiant", ""))
                source_url = f"https://data.toulouse-metropole.fr/events/{rec_id}" if rec_id else ""
            if not source_url:
                continue
            
            if source_url.lower().strip().rstrip("/") in existing_urls:
                continue
            
            type_manif = rec.get("type_de_manifestation", "") or ""
            cats = categorize_event(title, desc, [type_manif] if type_manif else None)
            
            all_events.append({
                "title": title[:200],
                "description": desc or title,
                "date": date_str,
                "time": None,
                "end_date": str(end_str)[:10] if end_str else None,
                "end_time": None,
                "location": location_str[:200],
                "latitude": float(lat),
                "longitude": float(lng),
                "categories": cats,
                "source_url": source_url,
                "source": "OpenData Toulouse",
                "validation_status": "auto_validated",
            })
        
        offset += len(results)
        if offset >= total or offset >= 3000:
            break
        time.sleep(0.5)
    
    print(f"\n  {len(all_events)} events candidats")
    if all_events:
        created, skipped = send_batch(all_events)
        print(f"  Insérés: {created}, Skippés: {skipped}")
        for ev in all_events:
            existing_urls.add(ev["source_url"].lower().strip().rstrip("/"))
        return created
    return 0


# ============================================================
# SOURCE 5: OpenAgenda - Top agendas
# ============================================================
def import_openagenda_top():
    print("\n" + "=" * 60)
    print("SOURCE 5: OpenAgenda - Top agendas")
    print("  Licence: Licence Ouverte v1.0")
    print("=" * 60)
    
    OA_EVENTS_URL = "https://openagenda.com/api/agendas/slug/{slug}/events"
    
    # Known large agendas (from discovery)
    top_agendas = [
        "francetravail",        # 5293 events
        "ile-de-france",        # 2308 events
        "scare",                # 728 events
        "cmf",                  # 475 events
        "hello-lille",          # 434 events
        "semainepetiteenfance", # 353 events
        "lerif",                # 318 events
        "sites-cites",         # 290 events
        "dioceseparis",        # 228 events
        "tableau-de-bord",     # 193 events
        "agenda-temps-libres", # 179 events
        "roissy-pays-de-france",# 150 events
        "freres-de-saint-jean-en-france", # 147 events
        "marseille-alive",     # 119 events
        "francenum",           # 112 events
        "rof",                 # 88 events
        "universite-paris-saclay", # 65 events
        "europeenfrance",      # 52 events
        "saint-marcel",        # 52 events
        "seineouest",          # 50 events
        "acp-la-manufacture-chanson", # 47 events
        "info-jeunes-france",  # 44 events
        "montreuil",           # 43 events
        "calendrier-musique",  # 42 events
        "france-belgique-calendrier", # 39 events
        "team-france-allemagne", # 38 events
        "chateau-de-voltaire-a-ferney", # 35 events
        "jassclub-paris",      # 35 events
        "grand-theatre-geneve", # 9 events
        "ariana-ville-geneve", # 20 events
    ]
    
    total_imported = 0
    
    for slug in top_agendas:
        print(f"\n  --- {slug} ---")
        
        offset = 0
        agenda_events = []
        
        while True:
            try:
                r = requests.get(OA_EVENTS_URL.format(slug=slug), params={
                    "size": 50,
                    "from": offset,
                    "relative[]": ["current", "upcoming"],
                    "sort": "lastTimingWithFeatured.asc",
                    "includeFields[]": [
                        "uid", "slug", "title", "description", "longDescription",
                        "dateRange", "timings", "nextTiming", "lastTiming",
                        "keywords", "status",
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
                    title_dict = ev.get("title", {})
                    if isinstance(title_dict, dict):
                        title = title_dict.get("fr", "") or title_dict.get("en", "") or title_dict.get("de", "")
                    else:
                        title = str(title_dict)
                    if not title:
                        continue
                    
                    desc_dict = ev.get("description", {})
                    if isinstance(desc_dict, dict):
                        desc = desc_dict.get("fr", "") or desc_dict.get("en", "")
                    else:
                        desc = str(desc_dict) if desc_dict else ""
                    desc = re.sub(r'<[^>]+>', '', desc).strip()
                    if len(desc) > 500:
                        desc = desc[:497] + "..."
                    
                    loc = ev.get("location", {}) or {}
                    lat = loc.get("latitude")
                    lng = loc.get("longitude")
                    if not lat or not lng:
                        continue
                    
                    ev_slug = ev.get("slug", "")
                    ev_uid = ev.get("uid", "")
                    source_url = f"https://openagenda.com/fr/{slug}/events/{ev_slug or ev_uid}"
                    
                    if source_url.lower().strip().rstrip("/") in existing_urls:
                        continue
                    
                    # Timing
                    timing = ev.get("nextTiming", {}) or ev.get("lastTiming", {}) or {}
                    begin = timing.get("begin", "")
                    end = timing.get("end", "")
                    
                    date_str = begin[:10] if begin else None
                    time_str = begin[11:16] if begin and len(begin) > 11 else None
                    end_date = end[:10] if end else None
                    end_time = end[11:16] if end and len(end) > 11 else None
                    
                    if not date_str or date_str < TODAY:
                        continue
                    
                    loc_name = loc.get("name", "") or ""
                    loc_addr = loc.get("address", "") or ""
                    loc_city = loc.get("city", "") or ""
                    location_str = loc_name
                    if loc_addr:
                        location_str += f", {loc_addr}" if location_str else loc_addr
                    if loc_city and loc_city not in location_str:
                        location_str += f", {loc_city}"
                    
                    # Keywords
                    kw = ev.get("keywords", {})
                    tags = []
                    if isinstance(kw, dict):
                        for lang_kw in kw.values():
                            if isinstance(lang_kw, list):
                                tags.extend(lang_kw)
                    
                    cats = categorize_event(title, desc, tags)
                    
                    agenda_events.append({
                        "title": title[:200],
                        "description": desc or title,
                        "date": date_str,
                        "time": time_str,
                        "end_date": end_date,
                        "end_time": end_time,
                        "location": location_str[:200] or "France",
                        "latitude": float(lat),
                        "longitude": float(lng),
                        "categories": cats,
                        "source_url": source_url,
                        "source": "OpenAgenda",
                        "validation_status": "auto_validated",
                    })
                
                offset += len(events)
                if offset >= total:
                    break
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"    Erreur: {e}")
                break
        
        if agenda_events:
            print(f"    {len(agenda_events)} events candidats")
            created, skipped = send_batch(agenda_events)
            print(f"    Insérés: {created}, Skippés: {skipped}")
            total_imported += created
            for ev in agenda_events:
                existing_urls.add(ev["source_url"].lower().strip().rstrip("/"))
        
        time.sleep(0.5)
    
    return total_imported


# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("IMPORT BATCH - OPEN DATA SOURCES")
    print(f"Date: {TODAY}")
    print("=" * 60)
    
    total = 0
    
    total += import_paris()
    total += import_madrid()
    total += import_barcelona()
    total += import_toulouse()
    total += import_openagenda_top()
    
    print(f"\n{'=' * 60}")
    print(f"RÉSULTAT FINAL:")
    print(f"  Total events importés: {total}")
    print(f"{'=' * 60}")
