"""
Recherche approfondie d'events electro sur les sources open data.
Phase 2: Extraction détaillée.
"""
import requests
import time
import json

# ============================================================
# 1. Helsinki LinkedEvents - Filtrer les 2581 events musique
#    pour trouver les electro spécifiquement
# ============================================================
def explore_helsinki_music():
    """Fetch toutes les pages d'events musique Helsinki et filtrer electro."""
    print("=" * 60)
    print("HELSINKI - Events musique (CC BY 4.0)")
    print("=" * 60)
    
    base = "https://api.hel.fi/linkedevents/v1"
    all_events = []
    url = f"{base}/event/"
    params = {
        "keyword": "yso:p1808",  # music
        "start": "2026-02-12",
        "end": "2026-12-31",
        "page_size": 100,
        "sort": "start_time",
        "include": "location"
    }
    
    page = 0
    while url and page < 30:
        page += 1
        try:
            r = requests.get(url, params=params if page == 1 else None, timeout=30)
            data = r.json()
            events = data.get("data", [])
            all_events.extend(events)
            url = data.get("meta", {}).get("next", None)
            print(f"  Page {page}: {len(events)} events (total: {len(all_events)})")
            time.sleep(0.5)
        except Exception as e:
            print(f"  Error page {page}: {e}")
            break
    
    print(f"\n  Total events musique Helsinki: {len(all_events)}")
    
    # Filtrer les electro
    electro_keywords = ["techno", "electronic", "electro", "house music", "deep house",
                       "tech house", "minimal", "trance", "drum and bass", "dnb", "d'n'b",
                       "dubstep", "bass music", "dj set", "dj-", "club night", "clubbing",
                       "rave", "edm", "dance music", "synthwave", "ambient", "hardstyle",
                       "gabber", "jungle", "breakbeat", "garage", "uk bass", "disco"]
    
    electro_events = []
    for ev in all_events:
        name_fi = (ev.get("name", {}) or {}).get("fi", "") or ""
        name_en = (ev.get("name", {}) or {}).get("en", "") or ""
        name_sv = (ev.get("name", {}) or {}).get("sv", "") or ""
        desc_fi = (ev.get("short_description", {}) or {}).get("fi", "") or ""
        desc_en = (ev.get("short_description", {}) or {}).get("en", "") or ""
        desc_long_en = (ev.get("description", {}) or {}).get("en", "") or ""
        desc_long_fi = (ev.get("description", {}) or {}).get("fi", "") or ""
        
        text = f"{name_fi} {name_en} {name_sv} {desc_fi} {desc_en} {desc_long_en} {desc_long_fi}".lower()
        
        if any(kw in text for kw in electro_keywords):
            electro_events.append(ev)
    
    print(f"  Events electro identifiés: {len(electro_events)}")
    
    # Afficher les 20 premiers
    for ev in electro_events[:20]:
        name = (ev.get("name", {}) or {}).get("en", "") or (ev.get("name", {}) or {}).get("fi", "?")
        start = ev.get("start_time", "?")[:10]
        loc = ev.get("location", {}) or {}
        loc_name = (loc.get("name", {}) or {}).get("fi", "") or (loc.get("name", {}) or {}).get("en", "?")
        print(f"    [{start}] {name} @ {loc_name}")
    
    if len(electro_events) > 20:
        print(f"    ... et {len(electro_events) - 20} de plus")
    
    return electro_events


# ============================================================
# 2. Madrid - Extraire les events electro
# ============================================================
def explore_madrid_electro():
    """Extraire events electro de Madrid Open Data."""
    print("\n" + "=" * 60)
    print("MADRID - Events electro (Datos abiertos)")
    print("=" * 60)
    
    url = "https://datos.madrid.es/egob/catalogo/206974-0-agenda-eventos-702702.json"
    try:
        r = requests.get(url, timeout=30)
        data = r.json()
        graph = data.get("@graph", [])
        
        electro_kw = ["electrónica", "techno", "dj", "electro", "house", "club", 
                      "dance", "hip hop", "rap", "trap", "reggaeton", "disco",
                      "drum", "bass", "rave", "fiesta", "noche", "session"]
        
        electro = []
        for ev in graph:
            title = (ev.get("title", "") or "").lower()
            desc = (ev.get("description", "") or "").lower()
            if any(kw in title or kw in desc for kw in electro_kw):
                electro.append(ev)
        
        print(f"  Total events Madrid: {len(graph)}")
        print(f"  Events electro/musique: {len(electro)}")
        
        for ev in electro[:15]:
            title = ev.get("title", "?")
            dtstart = ev.get("dtstart", "?")[:10] if ev.get("dtstart") else "?"
            addr = ev.get("address", {}) or {}
            loc = addr.get("area", {}).get("street-address", "?") if isinstance(addr, dict) else "?"
            print(f"    [{dtstart}] {title[:80]}")
        
        return electro
    except Exception as e:
        print(f"  Error: {e}")
        return []


# ============================================================
# 3. Paris - Events musique/concert pas encore importés
# ============================================================
def explore_paris_electro():
    """Chercher events musique electro sur Paris Open Data."""
    print("\n" + "=" * 60)
    print("PARIS - Events electro (Licence Ouverte v2.0)")
    print("=" * 60)
    
    url = "https://opendata.paris.fr/api/explore/v2.1/catalog/datasets/que-faire-a-paris-/records"
    electro_kw_sql = " OR ".join([
        f'title LIKE "%{kw}%"' for kw in ["techno", "electro", "DJ", "house", "club", "rave", "bass", "trance"]
    ])
    
    try:
        r = requests.get(url, params={
            "where": f"date_start >= '2026-02-12' AND ({electro_kw_sql})",
            "limit": 100,
            "order_by": "date_start"
        }, timeout=30)
        
        if r.status_code == 200:
            data = r.json()
            total = data.get("total_count", 0)
            results = data.get("results", [])
            print(f"  Events electro Paris: {total} (fetched: {len(results)})")
            
            for ev in results[:15]:
                title = ev.get("title", "?")
                date = ev.get("date_start", "?")[:10] if ev.get("date_start") else "?"
                print(f"    [{date}] {title[:80]}")
            
            return results
        else:
            print(f"  HTTP {r.status_code}: {r.text[:200]}")
            return []
    except Exception as e:
        print(f"  Error: {e}")
        return []


# ============================================================
# 4. Montréal - Events musique
# ============================================================
def explore_montreal_electro():
    """Chercher events musique sur Montréal Open Data."""
    print("\n" + "=" * 60)
    print("MONTRÉAL - Events electro (Données ouvertes)")
    print("=" * 60)
    
    # The Montreal API - search for music/electro events
    url = "https://donnees.montreal.ca/api/3/action/datastore_search"
    
    try:
        r = requests.get(url, params={
            "resource_id": "6b3a2e2a-e547-4b8a-bb6e-4c13ae1b5956",
            "q": "electro techno DJ house club rave",
            "limit": 100
        }, timeout=30)
        
        if r.status_code == 200:
            data = r.json()
            records = data.get("result", {}).get("records", [])
            total = data.get("result", {}).get("total", 0)
            print(f"  Events electro Montréal: {total} (fetched: {len(records)})")
            
            for ev in records[:10]:
                title = ev.get("titre", ev.get("title", "?"))
                print(f"    {title[:80]}")
        else:
            print(f"  HTTP {r.status_code}")
    except Exception as e:
        print(f"  Error: {e}")


# ============================================================
# 5. Vérifier aussi: NYC, Toronto 
# ============================================================
def explore_nyc_electro():
    """NYC Open Data - music events."""
    print("\n" + "=" * 60)
    print("NYC - Events musique (NYC Open Data)")
    print("=" * 60)
    
    url = "https://data.cityofnewyork.us/resource/tvpp-9vvx.json"
    try:
        r = requests.get(url, params={
            "$where": "start_date_time > '2026-02-12T00:00:00'",
            "$q": "electronic techno DJ house club dance music",
            "$limit": 100
        }, timeout=30)
        
        if r.status_code == 200:
            events = r.json()
            print(f"  Events NYC: {len(events)}")
            for ev in events[:10]:
                title = ev.get("event_name", ev.get("title", "?"))
                date = ev.get("start_date_time", "?")[:10]
                print(f"    [{date}] {title[:80]}")
        else:
            print(f"  HTTP {r.status_code}")
    except Exception as e:
        print(f"  Error: {e}")


# ============================================================
# 6. Cologne/Köln Open Data (NRW has big club scene)
# ============================================================
def explore_cologne_events():
    """Cologne/Köln - Open Data events."""
    print("\n" + "=" * 60)
    print("COLOGNE - Events (Open Data)")
    print("=" * 60)
    
    url = "https://www.offenedaten-koeln.de/api/3/action/datastore_search"
    try:
        r = requests.get(url, params={
            "resource_id": "veranstaltungskalender-koeln",
            "q": "electronic techno DJ club",
            "limit": 50
        }, timeout=15)
        if r.status_code == 200:
            data = r.json()
            records = data.get("result", {}).get("records", [])
            print(f"  Events Cologne: {len(records)}")
        else:
            print(f"  HTTP {r.status_code}")
    except Exception as e:
        print(f"  Error: {e}")


# ============================================================
# 7. OpenAgenda - Chercher des agendas avec upcoming events
#    par catégorie musique
# ============================================================
def explore_openagenda_by_category():
    """OpenAgenda - events filtrés par relative:music."""
    print("\n" + "=" * 60)
    print("OPENAGENDA - Catégorie musique + filtres")
    print("=" * 60)
    
    OA_KEY = "0e3b442455894aa09e7b8acb7d43c69c"
    
    # Try with relative=music
    try:
        r = requests.get("https://api.openagenda.com/v2/events", params={
            "key": OA_KEY,
            "relative[]": "current",
            "keyword[]": "music",
            "size": 50,
            "sort": "timingsStart.asc"
        }, timeout=30)
        data = r.json()
        total = data.get("total", 0)
        events = data.get("events", [])
        print(f"  keyword=music: {total} events (page: {len(events)})")
        
        for ev in events[:10]:
            title = ev.get("title", {}).get("fr", "") or ev.get("title", {}).get("en", "?")
            loc = ev.get("location", {}) or {}
            city = loc.get("city", "?")
            country = loc.get("countryCode", "?")
            print(f"    {title[:60]} ({city}, {country})")
        
    except Exception as e:
        print(f"  Error: {e}")


if __name__ == "__main__":
    explore_openagenda_by_category()
    hel = explore_helsinki_music()
    madrid = explore_madrid_electro()
    paris = explore_paris_electro()
    explore_montreal_electro()
    explore_nyc_electro()
    
    print("\n\n" + "=" * 60)
    print("RÉSUMÉ")
    print("=" * 60)
    print(f"  Helsinki electro: {len(hel)}")
    print(f"  Madrid electro: {len(madrid)}")
    print(f"  Paris electro: {len(paris)}")
